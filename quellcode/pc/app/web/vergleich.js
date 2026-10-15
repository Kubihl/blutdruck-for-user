const container=document.getElementById('vergleich');
const status=document.getElementById('status');
const title=document.getElementById('titel');
function box(name,rows){
 const section=document.createElement('section');
 const heading=document.createElement('h2');heading.textContent=name;section.append(heading);
 const count=document.createElement('p');count.textContent=rows.length+(rows.length===1?' sichtbare Messung':' sichtbare Messungen');section.append(count);
 const average=document.createElement('p');average.textContent=rows.length?'Durchschnitt: '+Math.round(rows.reduce((n,r)=>n+r.systolic,0)/rows.length)+' / '+Math.round(rows.reduce((n,r)=>n+r.diastolic,0)/rows.length)+' mmHg':'Durchschnitt: –';section.append(average);
 const latest=document.createElement('p');latest.textContent=rows.length?'Neueste Messung: '+new Date(rows[0].measuredAt).toLocaleString('de-DE'):'Neueste Messung: keine';section.append(latest);
 return section;
}
function refresh(){
 status.textContent='Werte werden geladen …';
 return fetch('/api/measurements',{cache:'no-store'}).then(response=>{
 if(!response.ok)throw Error('Bitte zuerst das PC-Tagebuch entsperren.');
 return response.json();
}).then(data=>{
 container.replaceChildren();
 status.textContent='';
 const groups=new Map();
 const registered=new Map((data.profiles||[]).map(p=>[String(p.profile),String(p.name||'').trim()]));
 for(const row of data.readings||[]){
  const slot=String(row.profile||'1');
  if(!groups.has(slot))groups.set(slot,[]);
  groups.get(slot).push(row);
 }
 for(const slot of ['1','2','3','4']){
  if(!groups.has(slot))groups.set(slot,[]);
 }
 const names=[];
 for(const [slot,rows] of [...groups].sort(([a],[b])=>Number(a)-Number(b))){
  rows.sort((a,b)=>new Date(b.measuredAt)-new Date(a.measuredAt));
  const name=registered.get(slot)||String(rows.find(r=>String(r.profileName||'').trim())?.profileName||'').trim()||'Benutzer '+slot;
  names.push(name);
  container.append(box(name,rows));
 }
 title.textContent='Benutzer vergleichen';
 if(!(data.readings||[]).length)status.textContent='Noch keine sichtbaren Messungen.';
 }).catch(error=>{status.textContent=error.message});
}
document.getElementById('aktualisieren').addEventListener('click',refresh);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh()});
refresh();
