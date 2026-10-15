function renderProfile(target,p){target.replaceChildren();if(!p){target.textContent='Noch keine Profilangaben aus der Handydatei übernommen.';return;}const line=document.createElement('p');line.textContent='Größe: '+(p.heightCm==null?'nicht angegeben':p.heightCm+' cm')+' · Gewicht: '+(p.weightKg==null?'nicht angegeben':p.weightKg.toLocaleString('de-DE')+' kg')+(p.weightDate?' · vom '+new Date(p.weightDate+'T12:00:00').toLocaleDateString('de-DE'):'');target.append(line);}
const msg=document.querySelector('#meldung');async function refresh(){const r=await fetch('/api/profiles',{cache:'no-store'});const d=await r.json();if(!r.ok)throw Error(d.error||'Benutzer konnten nicht geladen werden.');for(const p of d.profiles){const e=document.querySelector('#name'+p.profile);if(e){e.value=p.name;const old=e.parentElement.querySelector('.profile-info');if(old)old.remove();const info=document.createElement('details');info.className='profile-info';const summary=document.createElement('summary');summary.textContent='Profil';const values=document.createElement('div');renderProfile(values,p.profileData);addProfileEditor(values,p);info.append(summary,values);const rows=p.profileData?.weightHistory||[];if(rows.length){const history=document.createElement('details');const label=document.createElement('summary');label.textContent='Gewichtsverlauf';history.append(label);const table=document.createElement('table');for(const item of [...rows].reverse()){const tr=document.createElement('tr');for(const text of [item.date?new Date(item.date+'T12:00:00').toLocaleDateString('de-DE'):'Datum unbekannt',item.weightKg.toLocaleString('de-DE')+' kg']){const td=document.createElement('td');td.textContent=text;tr.append(td);}table.append(tr);}history.append(table);info.append(history);}let actions=e.parentElement.querySelector('.user-card-actions');if(!actions){actions=document.createElement('div');actions.className='user-card-actions';const button=e.parentElement.querySelector('button');button.before(actions);actions.append(button);}actions.append(info);}}}document.querySelectorAll('button[data-profile]').forEach(b=>b.addEventListener('click',async()=>{try{const profile=b.dataset.profile;const name=document.querySelector('#name'+profile).value.trim();const r=await fetch('/api/profile-name',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({profile,name})});const d=await r.json();if(!r.ok)throw Error(d.error||'Speichern fehlgeschlagen.');msg.textContent=d.name+' gespeichert.';}catch(e){msg.textContent=e.message;}}));refresh().catch(e=>msg.textContent=e.message);function addProfileEditor(target, profile) {
  const form = document.createElement('form');
  const data = profile.profileData || {};
  const fields = {};
  const today = new Date();
  const localDate = today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2,'0')+'-'+String(today.getDate()).padStart(2,'0');
  for (const [key, title, type, min, max] of [
    ['heightCm','Größe (cm)','number','50','250'],
    ['weightKg','Gewicht (kg)','number','20','400'],
    ['weightDate','Gewichtsdatum','date','','']
  ]) {
    const label = document.createElement('label');
    label.textContent = title;
    const input = document.createElement('input');
    input.type = type;
    input.name = key;
    if(type==='number'){input.min=min;input.max=max;input.step='0.1';}
    else input.max=localDate;
    input.value = data[key] ?? (key==='weightDate' && data.weightKg!=null ? localDate : '');
    label.append(input);form.append(label);fields[key]=input;
  }
  const save=document.createElement('button');save.type='submit';save.textContent='Profil speichern';
  const status=document.createElement('p');status.setAttribute('role','status');
  form.append(save,status);target.append(form);
  form.addEventListener('submit',async event=>{
    event.preventDefault();save.disabled=true;
    try{
      const weight=fields.weightKg.value===''?null:Number(fields.weightKg.value);
      const date=weight===null?null:(fields.weightDate.value||localDate);
      const response=await fetch('/api/profile-data',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({profile:profile.profile,profileData:{heightCm:fields.heightCm.value===''?null:Number(fields.heightCm.value),weightKg:weight,weightDate:date}})});
      const result=await response.json();if(!response.ok)throw Error(result.error||'Speichern fehlgeschlagen.');
      const details=form.closest('.profile-info');
      await refresh();
      document.querySelector('#name'+profile.profile).closest('.user-card').querySelector('.profile-info').open=true;
      msg.textContent='Profil für '+profile.name+' gespeichert.';
    }catch(error){status.textContent=error.message;}finally{save.disabled=false;}
  });
}
