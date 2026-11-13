// Measurement script used for the experiments. Run in the browser console on a page of the API's own origin
// (https://ypq1jax2t5.execute-api.ap-south-1.amazonaws.com/) right after changing the Lambda configuration,
// which forces new (cold) execution environments. Usage: await runTest('128MB')
window.__runs = window.__runs || {};
window.runTest = async (label) => {
  const base = location.origin, rows = [];
  const call = async (phase, seq) => {
    const t0 = performance.now();
    const r = await fetch(base + '/interest', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({from: 'loadtest', to: 'user_' + seq, message: label + ' ' + phase + ' ' + seq}), cache: 'no-store'});
    const j = await r.json();
    rows.push({config: label, phase, seq, status: r.status, coldStart: j.coldStart,
               latencyMs: +(performance.now() - t0).toFixed(1), at: new Date().toISOString()});
  };
  await call('first', 1);                                   // request 1: cold start
  for (let i = 2; i <= 101; i++) await call('sequential', i); // requests 2-101: warm, one after another
  await Promise.all(Array.from({length: 10}, (_, k) => call('burst', 200 + k))); // 10 at once: extra environments
  window.__runs[label] = rows;
  return rows;
};
