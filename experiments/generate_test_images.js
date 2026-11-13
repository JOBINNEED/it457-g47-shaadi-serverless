// Run in the browser console on the S3 console "Upload" page (prefix photos/) to create the 30 synthetic
// 640x480 test images used in the experiment and attach them to the upload form. No personal photos are used.
const input = document.querySelectorAll('input[type=file]')[0];
const dt = new DataTransfer();
for (let i = 1; i <= 30; i++) {
  const c = document.createElement('canvas'); c.width = 640; c.height = 480;
  const g = c.getContext('2d'); const h = (i * 37) % 360;
  const grad = g.createLinearGradient(0, 0, 640, 480);
  grad.addColorStop(0, `hsl(${h},60%,70%)`); grad.addColorStop(1, `hsl(${(h + 120) % 360},55%,40%)`);
  g.fillStyle = grad; g.fillRect(0, 0, 640, 480);
  for (let k = 0; k < 12; k++) { g.fillStyle = `hsla(${(h + k * 30) % 360},70%,55%,0.5)`; g.beginPath();
    g.arc((k * 97 * i) % 640, (k * 61 + i * 13) % 480, 20 + (k * 7) % 60, 0, 7); g.fill(); }
  g.fillStyle = '#fff'; g.font = 'bold 48px sans-serif'; g.fillText('IT457 G47 test photo ' + String(i).padStart(2, '0'), 30, 250);
  const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.85));
  dt.items.add(new File([blob], `photo_${String(i).padStart(2, '0')}.jpg`, { type: 'image/jpeg' }));
}
input.files = dt.files; input.dispatchEvent(new Event('change', { bubbles: true }));
