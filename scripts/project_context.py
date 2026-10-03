"""Read-only continuity checks. No price requests, strategy approvals or writes."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib,json,re,subprocess
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
HEX40=re.compile(r'[0-9a-f]{40}')
HEX64=re.compile(r'[0-9a-f]{64}')
CI_URL=re.compile(r'https://github\.com/kyon-phy/TrendTrade101/actions/runs/[0-9]+')
RECORDS=('AGENTS.md','PROJECT_STATE.md','docs/decisions.md',
         '.agents/skills/maintain-project-context/SKILL.md',
         '.agents/skills/maintain-project-context/references/record-format.md')
PRIVATE_PATTERNS=(r'(?:libfile|file)_[a-f0-9]{24,}',r'\bgh[pousr]_[A-Za-z0-9]{20,}',
    r'github_pat_[A-Za-z0-9_]{20,}',r'\bAKIA[A-Z0-9]{16}\b',r'\bsk-[A-Za-z0-9]{20,}',
    r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
    r'source_thread_id|<transcript_evidence>|<codex_delegation>',
    r'(?m)^(?:User|Assistant):',r'/Users/|/home/[^\s/]+/',
    r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',
    r'\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def blocks(text):return [json.loads(x) for x in re.findall(r'^```json\s*\n(.*?)\n```',text,re.M|re.S)]
def git(root,*args):
    return subprocess.check_output(['git','--no-optional-locks',*args],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
def utc(value):
    at=datetime.fromisoformat(value.replace('Z','+00:00'))
    if not at.tzinfo:raise ValueError('Timestamp must include timezone')
    return at.astimezone(timezone.utc)

def local_path(root,value,base=None):
    if not isinstance(value,str) or not value:raise ValueError('Empty evidence path')
    clean=value.split('#',1)[0]
    if clean.startswith('https://'):
        url=urlsplit(clean)
        if url.username or url.password or url.query:raise ValueError('Public evidence URLs must not contain credentials or query tokens')
        return None
    if clean.startswith(('/', '\\')) or '://' in clean:raise ValueError('Use public relative paths or HTTPS URLs')
    target=((base or root)/clean).resolve()
    if not target.is_relative_to(root.resolve()):raise ValueError('Evidence escapes repository')
    if any(part in ('.private','data','runs','.git') for part in target.relative_to(root.resolve()).parts):
        raise ValueError('Private paths cannot be public record evidence')
    if not target.is_file():raise ValueError('Evidence file is missing: '+clean)
    return target

def read_records(root):
    state_blocks=blocks((root/'PROJECT_STATE.md').read_text())
    if len(state_blocks)!=1 or not isinstance(state_blocks[0],dict):raise ValueError('State requires exactly one JSON object block')
    decisions=blocks((root/'docs/decisions.md').read_text())
    if not decisions or any(not isinstance(d,dict) for d in decisions):raise ValueError('Decision entries must be JSON objects')
    return state_blocks[0],decisions

def preserve_decisions(previous,current):
    if current[:len(previous)]!=previous:
        return ['Prior decision entries were edited, removed or reordered; append a superseding entry instead']
    return []

def prior_decisions(root,current):
    """Use available local history only; never fetch to fill a shallow clone."""
    try:
        previous=blocks(git(root,'show','HEAD:docs/decisions.md'))
        if previous==current:
            previous=blocks(git(root,'show','HEAD^:docs/decisions.md'))
        return previous
    except subprocess.CalledProcessError:
        return []  # Initial adoption or unavailable history; not proof of an entire past log.

def lint(root):
    problems=[]
    def need(condition,message):
        if not condition:problems.append(message)
    try:
        for name in RECORDS:
            path=root/name;text=path.read_text()
            if name=='PROJECT_STATE.md':need(len(text.encode())<=12000,'State exceeds 12 KB; link details instead')
            if any(re.search(p,text) for p in PRIVATE_PATTERNS):problems.append('Potential private content in '+name)
            need(not re.search(r'[\u3400-\u9fff]',text),'Repository records must use English: '+name)
            for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):local_path(root,link,path.parent)
            if name.endswith('/SKILL.md'):
                need(bool(re.match(r'---\nname: maintain-project-context\ndescription: [^\n]+\n---',text)),'Skill needs valid name/description frontmatter')
        state,decisions=read_records(root)
        problems.extend(preserve_decisions(prior_decisions(root,decisions),decisions))
        required={'schema_version','recorded_at','verified_checkpoint','configuration','research','results','blockers','pending_decisions','next_actions'}
        need(required<=state.keys(),'Missing required state fields')
        need(state['schema_version']==1,'Unsupported state schema');utc(state['recorded_at'])
        checkpoint=state['verified_checkpoint'];config=state['configuration']
        need(bool(HEX40.fullmatch(checkpoint['commit'])),'Checkpoint needs exact commit')
        need(checkpoint['test_scope']=='synthetic_software','Software test scope must remain explicit')
        need(type(checkpoint['tests_passed']) is int and checkpoint['tests_passed']>=0,'Invalid test count')
        need(bool(CI_URL.fullmatch(checkpoint['ci_url'])),'Checkpoint CI URL is not repository-scoped')
        need(bool(HEX64.fullmatch(checkpoint['artifact_sha256'])),'Missing artifact digest')
        need(checkpoint['artifact_name']=='research-dashboard','Unexpected checkpoint artifact')
        source=local_path(root,config['public_path']);provenance=local_path(root,config['provenance_path'])
        machine=local_path(root,config['implementation_path'])
        need(sha(source)==config['public_sha256'],'Public configuration hash changed')
        need(sha(provenance)==config['provenance_sha256'],'Provenance hash changed')
        need(sha(machine)==config['implementation_sha256'],'Machine configuration hash changed')
        policy=json.loads(machine.read_text());origin=json.loads(provenance.read_text())
        entry=next(f for f in origin['files'] if f['name']==source.name)
        need(config['source_sha256']==entry['source_sha256']==policy['source_sha256'],'Original configuration identity differs')
        need(config['public_sha256']==entry['public_sha256'],'Original/public hashes conflated')
        need(config['version']==policy['source_version']==origin['source_configuration_version'],'Configuration versions differ')
        ids=set()
        for d in decisions:
            need(d['id'] not in ids,'Duplicate decision ID');ids.add(d['id']);utc(d['recorded_at'])
            need(d['domain'] in ('strategy','workflow','software','data'),'Unknown decision domain')
            need(d['status'] in ('proposed','approved','implemented','verified','blocked'),'Unknown decision status')
            need(bool(d['evidence']),'Decision needs evidence links')
            for path in d['evidence']:local_path(root,path)
            if d.get('supersedes'):need(d['supersedes'] in ids and d['supersedes']!=d['id'],'Supersession must refer to an earlier retained entry')
            if d['domain']=='strategy' and d['status'] in ('approved','verified'):
                need(config['public_path'] in d['evidence'],'Strategy approval must cite configuration authority')
                need(not set(d.get('pending_fields',[]))&set(policy['pending']),'Unapproved proposal promoted to approved/verified')
            if d['status']=='verified' and d['domain']=='software':
                need(d.get('verification_scope')=='synthetic_software','Software verification scope missing')
        need(set(state['pending_decisions'])<=ids,'Unknown pending decision ID')
        for identifier in state['pending_decisions']:
            record=next(d for d in decisions if d['id']==identifier)
            need(record['status'] in ('proposed','blocked'),'Pending decision already marked approved')
        need(isinstance(state['blockers'],list) and isinstance(state['next_actions'],list),'Blockers/next actions must be explicit lists')
        for blocker in state['blockers']:local_path(root,blocker['evidence'])
        for phase in ('baseline','optimization','holdout'):
            value=state['research'][phase];need(value in ('not_run','in_progress','completed'),'Unknown research state')
            if value=='completed':
                need(policy['execution_ready'],'Historical completion conflicts with closed execution gate')
                need(any(r['phase']==phase for r in state['results']),'Historical completion needs result evidence')
                need(bool(state['research']['dataset_sha256']),'Historical completion needs a dataset hash')
        need(state['research']['holdout_dates'] in ('not_frozen','frozen'),'Holdout-date status must be explicit')
        for result in state['results']:
            need(result['kind']=='audited_historical','Synthetic tests cannot be historical results')
            need(bool(HEX40.fullmatch(result['code_commit'])),'Result needs exact code commit')
            for key in ('dataset_sha256','configuration_source_sha256','configuration_public_sha256','implementation_sha256'):
                need(bool(HEX64.fullmatch(result[key])),'Result needs exact '+key)
            local_path(root,result['summary_path'])
        need(state['research']['dataset_sha256'] is None or bool(HEX64.fullmatch(state['research']['dataset_sha256'])),'Invalid dataset hash')
    except (OSError,ValueError,KeyError,TypeError,StopIteration) as exc:
        problems.append('Record validation failed: '+str(exc))
    return problems

def recover(root,observations=None,remote=False,now=None):
    errors=lint(root);warnings=[]
    output={'errors':errors,'warnings':warnings,'historical_success_certified':False,
            'recovery_checks_complete':False,
            'remote_status':'unverified','ci_artifact_status':'unverified',
            'limitation':'Supplied observations are not authenticated by this offline checker.'}
    if errors:return output
    state,_=read_records(root);checkpoint=state['verified_checkpoint']['commit']
    try:
        head=git(root,'rev-parse','HEAD');dirty=bool(git(root,'status','--porcelain'))
        output.update(actual_head=head,working_tree_dirty=dirty,recorded_checkpoint=checkpoint,
                      recorded_checkpoint_tests=state['verified_checkpoint']['tests_passed'])
        try:git(root,'cat-file','-e',checkpoint+'^{commit}');git(root,'merge-base','--is-ancestor',checkpoint,head)
        except subprocess.CalledProcessError:warnings.append('Checkpoint is missing or not an ancestor; reconcile rather than guessing')
        if head!=checkpoint:warnings.append('Checkpoint is not HEAD; its test count does not verify HEAD')
        if dirty:warnings.append('Working tree differs from committed evidence')
        actual_remote=git(root,'ls-remote','origin','refs/heads/main').split()[0] if remote else None
        if actual_remote:
            output.update(remote_head=actual_remote,remote_status='matched' if actual_remote==head else 'different')
        if observations:
            at=utc(observations['observed_at']);age=((now or datetime.now(timezone.utc))-at).total_seconds()
            ci=observations['ci'];artifacts=observations['artifacts']
            matched=(0<=age<=3600 and observations['remote_head_sha']==head and
                ci['head_sha']==head and ci['conclusion']=='success' and bool(CI_URL.fullmatch(ci['html_url'])) and
                any(a['name']=='research-dashboard' and a['head_sha']==head and a['expired'] is False and
                    re.fullmatch(r'sha256:[0-9a-f]{64}',a['digest']) for a in artifacts))
            output['ci_artifact_status']='matched_supplied_observation' if matched else 'mismatch_or_stale'
            if not matched:warnings.append('CI/artifact observation is stale, incomplete, failed or for another commit')
        else:warnings.append('Fresh CI/artifact observations are required before remote success claims')
        plans=list((root/'.private/runs').glob('*/plan.json'))
        real=[p for p in plans if json.loads(p.read_text()).get('dataset_kind')=='yahoo_audited']
        output['local_real_run_plan_count']=len(real)
        if real:warnings.append('Inspect actual private run manifests and results separately; this checker does not validate market data')
        output['recovery_checks_complete']=(not dirty and output['remote_status']=='matched' and
            output['ci_artifact_status']=='matched_supplied_observation')
    except (OSError,ValueError,KeyError,TypeError,IndexError,subprocess.CalledProcessError) as exc:
        errors.append('Recovery observation unavailable: '+str(exc))
    return output

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['lint','recover'])
    p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--remote',action='store_true')
    p.add_argument('--observations',type=Path);args=p.parse_args(argv)
    if args.command=='lint':
        errors=lint(args.root);print(json.dumps({'errors':errors,'status':'consistent' if not errors else 'needs_reconciliation'},indent=2))
        return bool(errors)
    observations=json.loads(args.observations.read_text()) if args.observations else None
    report=recover(args.root,observations,args.remote);print(json.dumps(report,indent=2))
    return 0 if report.get('recovery_checks_complete') else 2

if __name__=='__main__':raise SystemExit(main())
