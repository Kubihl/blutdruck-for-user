async function showLastPhone() {
  const area = document.querySelector('#handy-status');
  if (!area) return;
  try {
    const response = await fetch('/api/sync-status', {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok) throw Error();
    const time = data.time && !Number.isNaN(Date.parse(data.time)) ? new Date(data.time).toLocaleString('de-DE') : '';
    area.textContent = data.device && time
      ? `Zuletzt abgeglichenes Handy: ${data.device} · ${time}`
      : 'Noch kein erfolgreicher Handy-Abgleich gespeichert.';
  } catch (_) { area.textContent = 'Handy-Abgleichstatus momentan nicht verfügbar.'; }
}
showLastPhone();
setInterval(showLastPhone, 15000);
