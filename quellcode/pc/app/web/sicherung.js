const file = document.querySelector('#backup-file');
const check = document.querySelector('#check');
const status = document.querySelector('#status');
const preview = document.querySelector('#preview');
const summary = document.querySelector('#summary');
const confirm = document.querySelector('#confirm');
const restore = document.querySelector('#restore');
let token = null;
function reset() { token = null; preview.hidden = true; confirm.checked = false; restore.disabled = true; }
file.addEventListener('change', reset);
confirm.addEventListener('change', () => { restore.disabled = !token || !confirm.checked; });
async function request(payload) {
  const response = await fetch('/api/backup-restore', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Vorgang fehlgeschlagen.');
  return data;
}
check.addEventListener('click', async () => {
  reset(); status.textContent = ''; check.disabled = true;
  try {
    const selected = file.files[0];
    if (!selected) throw Error('Bitte eine JSON-Sicherung auswählen.');
    if (selected.size > 39 * 1024 * 1024) throw Error('Datei zu groß (maximal 39 MB).');
    const data = await request({action:'preview', data:JSON.parse(await selected.text())});
    token = data.token;
    summary.textContent = `Sicherung: ${data.count} Messungen, davon ${data.hidden} ausgeblendet; ${data.files} Monatsdateien. Benutzer: ${data.profiles.join(', ')}. Bisher im Tagebuch: ${data.current} Messungen.`;
    preview.hidden = false;
    status.textContent = 'Datei geprüft. Noch keine Daten geändert.';
  } catch (error) { status.textContent = error.message; }
  finally { check.disabled = false; }
});
restore.addEventListener('click', async () => {
  if (!token || !confirm.checked) return;
  restore.disabled = true; check.disabled = true; file.disabled = true; confirm.disabled = true;
  try {
    const data = await request({action:'restore', token, confirmed:true});
    reset();
    status.textContent = `${data.count} Messungen wiederhergestellt. Der vorherige Stand ist gesichert unter: ${data.backup}. Über „Zurück zum Tagebuch“ die Messwerte öffnen.`;
  } catch (error) { reset(); status.textContent = error.message + ' Bitte erneut Datei prüfen.'; }
  finally { check.disabled = false; file.disabled = false; confirm.disabled = false; }
});
