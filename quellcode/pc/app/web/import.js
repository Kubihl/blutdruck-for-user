const file = document.querySelector('#datei');
const profile = document.querySelector('#profil');
const preview = document.querySelector('#vorschau');
const message = document.querySelector('#meldung');
const confirmButton = document.querySelector('#importieren');
const restoreWrap = document.querySelector('#restore-wrap');
const restoreInput = document.querySelector('#restore-hidden');
let selectedPackage = null;
let checkedProfile = null;
let newCount = 0;
let hasProfileData = false;

async function loadNames() {
  try {
    const response = await fetch('/api/profiles', {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok) throw Error(data.error || 'Benutzer konnten nicht geladen werden.');
    for (const item of data.profiles || []) {
      const option = profile.querySelector(`option[value="${item.profile}"]`);
      if (option) option.textContent = item.name;
    }
  } catch (error) { message.textContent = error.message; }
}

function reset() {
  selectedPackage = null;
  checkedProfile = null;
  newCount = 0;
  hasProfileData = false;
  restoreInput.checked = false;
  restoreWrap.hidden = true;
  confirmButton.hidden = true;
  preview.textContent = '';
  message.textContent = '';
}
file.addEventListener('change', reset);
profile.addEventListener('change', reset);
restoreInput.addEventListener('change', () => {
  confirmButton.hidden = !selectedPackage || (newCount === 0 && !restoreInput.checked && !hasProfileData);
});

async function send(commit) {
  const response = await fetch('/api/measurement-import', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({package: selectedPackage, profile: profile.value, commit,
      restoreHidden: commit && restoreInput.checked})
  });
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Datei konnte nicht gelesen werden.');
  return data;
}

document.querySelector('#pruefen').addEventListener('click', async () => {
  reset();
  try {
    if (!file.files.length) throw Error('Bitte zuerst eine Datei auswählen.');
    if (file.files[0].size > 2000000) throw Error('Datei ist zu groß.');
    selectedPackage = JSON.parse(await file.files[0].text());
    const data = await send(false);
    checkedProfile = profile.value;
    newCount = data.new;
    hasProfileData = !!data.profileData;
    const hiddenCount = data.hiddenDuplicates || 0;
    preview.textContent = `Datei von ${data.sourceName}: ${data.count} Werte. Ziel im PC: ${profile.selectedOptions[0].textContent}. Neu: ${data.new}, schon vorhanden: ${data.duplicates}, davon ausgeblendet: ${hiddenCount}.`;
    if (data.profileData) {const p=data.profileData; preview.textContent += ` Profil wird mit übernommen: Größe ${p.heightCm == null ? 'nicht angegeben' : p.heightCm+' cm'}, Gewicht ${p.weightKg == null ? 'nicht angegeben' : p.weightKg+' kg'}${p.weightDate ? ' vom '+p.weightDate : ''}; ${p.weightHistory.length} Gewichtsangaben. Bestehende neuere Gewichtsangaben bleiben erhalten.`;}
    restoreWrap.hidden = hiddenCount === 0;
    confirmButton.hidden = data.new === 0 && !hasProfileData;
    if (data.new === 0 && !hasProfileData) message.textContent = hiddenCount
      ? 'Diese Werte sind vorhanden, aber ausgeblendet. Nur mit dem Haken werden sie wieder angezeigt.'
      : 'Alle Werte sind bereits vorhanden und sichtbar.';
  } catch (error) { reset(); message.textContent = error.message; }
});

confirmButton.addEventListener('click', async () => {
  if (!selectedPackage || checkedProfile !== profile.value) return reset();
  confirmButton.disabled = true;
  try {
    const data = await send(true);
    message.textContent = `${data.profileData ? 'Profil übernommen. ' : ''}${data.added} neue Werte importiert, ${data.restored || 0} ausgeblendete Werte wieder angezeigt. Im Tagebuch auf Aktualisieren drücken.`;
    confirmButton.hidden = true;
    restoreWrap.hidden = true;
  } catch (error) { message.textContent = error.message; }
  finally { confirmButton.disabled = false; }
});
loadNames();
