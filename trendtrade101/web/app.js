const $ = id => document.getElementById(id);
let currentStatus = null;
function node(tag, text, cls) { const e=document.createElement(tag); e.textContent=text; if(cls)e.className=cls; return e; }
function render(s){
  currentStatus=s;
  $('connection').textContent=s.snapshot_mode?'Read-only snapshot':(s.run_status==='blocked'?'Research blocked':'Research status');
  $('connection').className='badge '+(s.run_status==='blocked'?'blocked':'complete');
  $('version').textContent='Configuration '+s.version;
  $('updated').textContent=(s.snapshot_mode?'Snapshot captured ':'Refreshed ')+new Date(s.snapshot_at||s.updated_at).toLocaleString();
  $('membership').textContent=s.inputs.membership_count ?? '—';
  $('membership-note').textContent=s.inputs.membership_count ? s.inputs.unique_securities+' securities · '+s.inputs.verification_kind.replaceAll('_',' ') : '201 expected · bytes unverified';
  $('stages').replaceChildren(...s.stages.map((x,i)=>{
    const e=node('div','','stage'); e.append(node('span',String(i+1).padStart(2,'0'),'step'),node('span',x.name,'stage-name'),node('span',x.detail,'stage-detail'),node('span',x.status.replaceAll('_',' '),'badge '+x.status));return e;
  }));
  $('files').replaceChildren(...s.inputs.files.map(f=>{
    const e=node('div','','file'), h=node('div','','file-head');
    h.append(node('span',f.name),node('span',f.verified?'Verified':(f.actual_sha256?'Mismatch':'Missing'),'badge '+(f.verified?'complete':'blocked')));
    e.append(h,node('div','Expected SHA256 '+f.expected_sha256,'hash'));return e;
  }));
  const p=s.parameters;
  const i=p.indicators,e=p.execution;
  const values=[['Signal bars','5 minutes / daily'],['SMA / MACD',[i.sma_fast,i.sma_slow].join(', ')+' / '+[i.macd_fast,i.macd_slow,i.macd_signal].join(', ')],['ADX gate','Strictly greater than '+i.adx_threshold],['Cross window',i.cross_window+' bars'],['Histogram drawdown',100*i.hist_drawdown+'% of running peak'],['Intraday delay',e.delay_minutes+' minutes · fixed per round'],['Primary allocation','1/15 of initial capital'],['Daily execution','Next-session Open']];
  $('parameters').replaceChildren(...values.flatMap(([k,v])=>[node('dt',k),node('dd',v)]));
  $('pending').replaceChildren(...s.pending.map(x=>node('li','Pending: '+x.replaceAll('_',' '))),
    ...(s.accepted_definitions||[]).map(x=>node('li','Approved in '+s.version+': '+x.replaceAll('_',' '))),
    ...(s.accepted_pending_canonical_sync||[]).map(x=>node('li','Accepted; awaiting canonical sync: '+x.replaceAll('_',' '))));
  $('biases').replaceChildren(...s.biases.map(x=>node('li',x)));
  const v=s.verification;
  $('verification').textContent=v.tests_passed ? v.tests_passed+' software tests passed · '+v.checked_at : 'No completed test record.';
  renderResults();
}
function renderResults(){
  if(!currentStatus)return;
  const results=currentStatus.results.filter(r=>r.market===$('market').value&&r.frequency===$('frequency').value);
  const area=$('results-content'); area.replaceChildren();
  if(!results.length){
    area.className='empty';
    area.append(node('div','↗','empty-icon'),node('h3','No '+$('market').value+' '+$('frequency').value+' results yet'),
      node('p','Only audited historical runs appear here. Synthetic fixtures are excluded.'));
    return;
  }
  area.className='result-list';
  for(const r of results){
    const row=node('article','','result-row'),m=r.metrics;
    row.append(node('h3',r.universe+' · '+r.arm),node('p',r.phase.replaceAll('_',' ')+' · '+r.configuration_version));
    const values=node('dl');
    for(const [label,value] of [['Gross return',m.gross_return],['After-fee return',m.after_fee_return],['After-tax return',m.after_tax_return],['Maximum drawdown',m.max_drawdown],['Win rate',m.win_rate],['Calendar-time capital utilization',m.calendar_time_weighted_capital_utilization],['Maximum single-position share',m.maximum_single_position_equity_share]]){
      if(value!==undefined&&value!==null)values.append(node('dt',label),node('dd',(100*value).toFixed(2)+'%'));
    }
    if(m.closed_trades!==undefined)values.append(node('dt','Completed closures'),node('dd',String(m.closed_trades)));
    row.append(values);
    if(m.sparse)row.append(node('p','Sparse sample: fewer than five complete aggregate closures.','badge blocked'));
    const diagnostics=node('details'),diagnosticValues=node('dl');
    diagnostics.append(node('summary','Execution diagnostics'));
    for(const [label,key] of [['Orders with missing prices','orders_with_missing_price'],['Unfilled at segment ends','orders_unfilled_at_segment_end'],['Below-lot orders','below_lot_orders'],['Cash-shortfall orders','cash_shortfall_orders'],['Canceled orders','canceled_orders'],['Unsuccessful scheduled liquidations','unsuccessful_scheduled_liquidations']]){
      if(m[key]!==undefined)diagnosticValues.append(node('dt',label),node('dd',String(m[key])));
    }
    diagnostics.append(diagnosticValues);row.append(diagnostics);
    if(r.folds){
      const folds=node('details');folds.append(node('summary','Walk-forward selections and test returns'));
      for(const f of r.folds)folds.append(node('p','Fold '+(f.fold+1)+' · '+(f.selected?JSON.stringify(f.selected.parameters):'No eligible candidate; no new entries')+' · after-tax '+(100*f.metrics.after_tax_return).toFixed(2)+'%'));
      row.append(folds);
    }
    if(r.equity.length>1){
      const points=r.equity,ys=points.map(p=>p.equity),low=Math.min(...ys),high=Math.max(...ys),span=high-low||1;
      const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
      svg.setAttribute('viewBox','0 0 700 160');svg.setAttribute('role','img');svg.setAttribute('aria-label','Account equity over the recorded test interval');
      const line=document.createElementNS('http://www.w3.org/2000/svg','polyline');
      line.setAttribute('fill','none');line.setAttribute('stroke','#117d76');line.setAttribute('stroke-width','2');
      line.setAttribute('points',points.map((p,i)=>(8+684*i/(points.length-1))+','+(150-140*(p.equity-low)/span)).join(' '));
      svg.append(line);row.append(svg,node('p',points[0].time+' → '+points.at(-1).time,'small'));
    }
    area.append(row);
  }
}
async function refresh(){
  try { const r=await fetch('/api/status'); if(!r.ok)throw Error('HTTP '+r.status);render(await r.json()); }
  catch(e){$('connection').textContent='Connection unavailable';$('connection').className='badge blocked';$('updated').textContent='Status refresh failed; no new results inferred';}
}
if(window.TRENDTRADE_SNAPSHOT){render(window.TRENDTRADE_SNAPSHOT);}else{refresh();setInterval(refresh,5000);}
$('market').addEventListener('change',renderResults);
$('frequency').addEventListener('change',renderResults);
