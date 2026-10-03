const $ = id => document.getElementById(id);
function node(tag, text, cls) { const e=document.createElement(tag); e.textContent=text; if(cls)e.className=cls; return e; }
function render(s){
  $('connection').textContent='Research blocked'; $('connection').className='badge blocked';
  $('version').textContent='Configuration '+s.version;
  $('updated').textContent='Refreshed '+new Date(s.updated_at).toLocaleTimeString();
  $('membership').textContent=s.inputs.membership_count ?? '—';
  $('membership-note').textContent=s.inputs.membership_count ? s.inputs.unique_securities+' unique securities · verified' : '201 expected · bytes unverified';
  $('stages').replaceChildren(...s.stages.map((x,i)=>{
    const e=node('div','','stage'); e.append(node('span',String(i+1).padStart(2,'0'),'step'),node('span',x.name,'stage-name'),node('span',x.detail,'stage-detail'),node('span',x.status.replaceAll('_',' '),'badge '+x.status));return e;
  }));
  $('files').replaceChildren(...s.inputs.files.map(f=>{
    const e=node('div','','file'), h=node('div','','file-head');
    h.append(node('span',f.name),node('span',f.verified?'Verified':(f.actual_sha256?'Mismatch':'Missing'),'badge '+(f.verified?'complete':'blocked')));
    e.append(h,node('div','Expected SHA256 '+f.expected_sha256,'hash'));return e;
  }));
  const p=s.parameters;
  const values=[['Signal bars','5 minutes / daily'],['SMA / MACD','5, 20 / 12, 26, 9'],['ADX gate','Strictly greater than 25'],['Cross window','5 bars'],['Histogram drawdown','40% of running peak'],['Intraday delay','20 minutes · fixed per round'],['Primary allocation','1/15 of initial capital'],['Daily execution','Next-session Open']];
  $('parameters').replaceChildren(...values.flatMap(([k,v])=>[node('dt',k),node('dd',v)]));
  $('pending').replaceChildren(...s.pending.map(x=>node('li','Pending: '+x.replaceAll('_',' '))),
    ...(s.accepted_definitions||[]).map(x=>node('li','Approved in '+s.version+': '+x.replaceAll('_',' '))),
    ...(s.accepted_pending_canonical_sync||[]).map(x=>node('li','Accepted; awaiting canonical sync: '+x.replaceAll('_',' '))));
  $('biases').replaceChildren(...s.biases.map(x=>node('li',x)));
  const v=s.verification;
  $('verification').textContent=v.tests_passed ? v.tests_passed+' software tests passed · '+v.checked_at : 'No completed test record.';
}
async function refresh(){
  try { const r=await fetch('/api/status'); if(!r.ok)throw Error('HTTP '+r.status);render(await r.json()); }
  catch(e){$('connection').textContent='Connection unavailable';$('connection').className='badge blocked';$('updated').textContent='Status refresh failed; no new results inferred';}
}
refresh();setInterval(refresh,5000);
$('market').addEventListener('change',()=>{$('results-content').querySelector('h3').textContent='No '+$('market').value+' '+$('frequency').value+' results yet';});
$('frequency').addEventListener('change',()=>{$('results-content').querySelector('h3').textContent='No '+$('market').value+' '+$('frequency').value+' results yet';});
