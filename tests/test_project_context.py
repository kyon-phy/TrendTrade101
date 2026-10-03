"""Fresh-context recovery from files only; all remote observations are synthetic."""
import copy,importlib.util,json,shutil,subprocess,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('project_context',ROOT/'scripts/project_context.py')
context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context)
NOW=datetime(2026,10,3,16,tzinfo=timezone.utc)

class ContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        for directory in ('config','docs','.agents'):
            shutil.copytree(ROOT/directory,self.root/directory)
        for name in ('AGENTS.md','PROJECT_STATE.md','README.md'):
            shutil.copyfile(ROOT/name,self.root/name)
        self.state,self.decisions=context.read_records(self.root)
        self.head=self.state['verified_checkpoint']['commit']

    def tearDown(self):self.tmp.cleanup()

    def state_write(self):
        (self.root/'PROJECT_STATE.md').write_text('```json\n'+json.dumps(self.state)+'\n```\n')

    def decision_write(self):
        (self.root/'docs/decisions.md').write_text('\n'.join('```json\n'+json.dumps(d)+'\n```' for d in self.decisions))

    def observations(self):
        return {'observed_at':NOW.isoformat(),'remote_head_sha':self.head,
                'ci':{'head_sha':self.head,'conclusion':'success',
                      'html_url':'https://github.com/kyon-phy/TrendTrade101/actions/runs/123'},
                'artifacts':[{'name':'research-dashboard','head_sha':self.head,
                              'digest':'sha256:'+'a'*64,'expired':False}]}

    def git(self,root,*args):
        if args==('rev-parse','HEAD'):return self.head
        if args==('status','--porcelain'):return ''
        if args==('ls-remote','origin','refs/heads/main'):return self.head+'\trefs/heads/main'
        if args[0] in ('cat-file','merge-base'):return ''
        if args[0]=='show':raise subprocess.CalledProcessError(128,['git',*args])
        raise AssertionError('Unexpected Git action: '+str(args))

    def test_checked_repository_records_are_structurally_consistent(self):
        self.assertEqual(context.lint(self.root),[])

    def test_fresh_context_without_observations_does_not_claim_ci_or_write_files(self):
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(context,'git',side_effect=self.git) as calls:
            report=context.recover(self.root,now=NOW)
        self.assertEqual(report['ci_artifact_status'],'unverified')
        self.assertEqual(report['remote_status'],'unverified')
        self.assertFalse(report['recovery_checks_complete'])
        self.assertFalse(any(c.args[1]=='ls-remote' for c in calls.call_args_list))
        after={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_stale_handoff_does_not_attach_old_test_count_to_new_head(self):
        self.head='b'*40
        with patch.object(context,'git',side_effect=self.git):
            report=context.recover(self.root,self.observations(),True,NOW)
        self.assertEqual(report['actual_head'],self.head)
        self.assertNotEqual(report['recorded_checkpoint'],self.head)
        self.assertTrue(any('test count does not verify HEAD' in w for w in report['warnings']))
        self.assertNotIn('current_head_tests',report)
        self.assertFalse(report['historical_success_certified'])

    def test_unapproved_technical_proposal_cannot_be_promoted_by_a_handoff(self):
        d=next(d for d in self.decisions if d['id']=='D002')
        d['status']='approved';d['evidence'].append(self.state['configuration']['public_path'])
        self.decision_write()
        self.assertTrue(any('Unapproved proposal promoted' in e for e in context.lint(self.root)))

    def test_software_only_success_cannot_become_historical_baseline_success(self):
        self.state['research']['baseline']='completed';self.state_write()
        with patch.object(context,'git',side_effect=self.git):
            report=context.recover(self.root,self.observations(),True,NOW)
        self.assertTrue(report['errors'])
        self.assertFalse(report['historical_success_certified'])

    def test_expired_or_wrong_commit_artifacts_remain_unverified(self):
        for change in ({'expired':True},{'head_sha':'c'*40}):
            evidence=self.observations();evidence['artifacts'][0].update(change)
            with patch.object(context,'git',side_effect=self.git):
                report=context.recover(self.root,evidence,True,NOW)
            self.assertFalse(report['recovery_checks_complete'])
            self.assertEqual(report['ci_artifact_status'],'mismatch_or_stale')

    def test_stale_observations_do_not_count_as_fresh_remote_evidence(self):
        evidence=self.observations();evidence['observed_at']=(NOW-timedelta(hours=2)).isoformat()
        with patch.object(context,'git',side_effect=self.git):
            report=context.recover(self.root,evidence,True,NOW)
        self.assertFalse(report['recovery_checks_complete'])

    def test_missing_evidence_and_changed_config_are_flagged_not_repaired(self):
        (self.root/'docs/network-access.md').unlink()
        self.assertTrue(context.lint(self.root))
        shutil.copyfile(ROOT/'docs/network-access.md',self.root/'docs/network-access.md')
        p=self.root/'config/baseline.json';p.write_text(p.read_text()+'\n')
        self.assertIn('Machine configuration hash changed',context.lint(self.root))

    def test_private_identifiers_are_rejected_in_public_records(self):
        with (self.root/'PROJECT_STATE.md').open('a') as f:f.write('\n'+'libfile_'+'a'*32)
        self.assertTrue(any('private content' in e for e in context.lint(self.root)))

    def test_supersession_preserves_old_entry_and_requires_existing_id(self):
        entry=copy.deepcopy(self.decisions[1]);entry.update(id='D-next',supersedes='D002')
        self.decisions.append(entry);self.decision_write()
        self.assertEqual(context.lint(self.root),[])
        self.assertTrue(any(d['id']=='D002' for d in context.read_records(self.root)[1]))
        entry['supersedes']='D-missing';self.decision_write()
        self.assertTrue(any('Supersession' in e for e in context.lint(self.root)))

    def test_prior_decisions_cannot_be_erased_or_rewritten(self):
        previous=copy.deepcopy(self.decisions)
        self.assertTrue(context.preserve_decisions(previous,self.decisions[1:]))
        self.decisions[0]['summary']='A rewritten history claim'
        self.assertTrue(context.preserve_decisions(previous,self.decisions))
