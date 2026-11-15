"""shaadi-demo: serves the one-page presentation (GET /demo) and its helpers.

GET  /demo                    -> the HTML page (same origin as the API, so its buttons call /baseline, /interest, /moderate)
GET  /demo/photo?key=photos/x -> the test photo as JPEG (bucket stays private; read with this role)
GET  /demo/items?table=verdicts|interests -> latest items from DynamoDB
POST /demo/cold {"fn": "ping"|"interest"|"moderate"} -> sets a new RUN_NONCE env var so the next call is a cold start
"""
import base64
import json
import os
import time
import uuid
from decimal import Decimal

import boto3
from boto3.dynamodb.types import TypeDeserializer

BUCKET = os.environ["BUCKET"]
S3 = boto3.client("s3")
DDB = boto3.client("dynamodb")
LAMBDA = boto3.client("lambda")
DES = TypeDeserializer()
FUNCS = {"ping": "shaadi-ping", "interest": "shaadi-interest-api", "moderate": "shaadi-moderate"}
TABLES = {"verdicts": "verdicts", "interests": "Interests"}
HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shaadi.com Serverless PoC - IT457 G47</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1d2430;--mut:#5b6575;--line:#e2e6ec;--acc:#1f4e78;--a2:#c026d3;--ok:#2f9e44;--warn:#e8590c;--bad:#c92a2a;--ping:#6b7a8f;--mono:ui-monospace,Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header{background:var(--acc);color:#fff;padding:18px 28px}header h1{margin:0;font-size:22px}header p{margin:4px 0 0;opacity:.85;font-size:13.5px}
nav{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line);display:flex;gap:2px;padding:0 20px;overflow-x:auto}
nav a{padding:12px 14px;color:var(--mut);text-decoration:none;font-weight:600;font-size:14px;border-bottom:3px solid transparent;white-space:nowrap}
nav a.on{color:var(--acc);border-color:var(--acc)}
main{max-width:1180px;margin:0 auto;padding:22px 20px 60px}section{display:none}section.on{display:block}
h2{font-size:20px;margin:6px 0 12px}h3{font-size:16px;margin:18px 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:14px}
.grid{display:grid;gap:14px}.g2{grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}.g4{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.kpi .v{font-size:26px;font-weight:700;color:var(--acc)}.kpi .l{color:var(--mut);font-size:13px}
table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{background:#eef2f7}
button{font:inherit;font-weight:600;border:0;border-radius:7px;padding:8px 14px;background:var(--acc);color:#fff;cursor:pointer}button.sec{background:#e9edf3;color:var(--ink)}button:disabled{opacity:.5;cursor:wait}
input,select{font:inherit;padding:7px 9px;border:1px solid #c9d1db;border-radius:6px}
pre{background:#0f1720;color:#d6e2ee;border-radius:8px;padding:12px;font:12.5px/1.45 var(--mono);overflow:auto;max-height:300px;margin:8px 0 0;white-space:pre-wrap}
.badge{display:inline-block;padding:2px 9px;border-radius:99px;font-size:12px;font-weight:700}.cold{background:#ffe3e3;color:var(--bad)}.warm{background:#d3f9d8;color:#2b8a3e}.st{background:#e7f5ff;color:#1864ab}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.lr{display:flex;gap:10px;align-items:center;margin:3px 0}.lr .bar{flex:none}.mut{color:var(--mut);font-size:13px}a{color:var(--acc)}
.bar{height:12px;border-radius:3px;background:var(--acc)}.photo{width:180px;height:135px;object-fit:cover;border-radius:8px;border:1px solid var(--line);background:#eee}
.links a{display:block;padding:3px 0}.verdict{font-size:22px;font-weight:800;text-transform:uppercase}
.talk{border-left:4px solid #f0b429;background:#fff9e6;padding:8px 12px;border-radius:6px;font-size:13.5px;margin:8px 0}
svg text{font-family:system-ui,sans-serif}
</style></head><body>
<header><h1>Shaadi.com on AWS: serverless proof of concept</h1>
<p>IT-457 Cloud Computing, Group 47 (Theme 4: Serverless and Startups) &middot; Sri Sai Madhava Teja Yanduri 202301138 &middot; Kavya Chauhan 202301116 &middot; Venkata L Subramanyam 202301280 &middot; live in ap-south-1 (Mumbai)</p></header>
<nav id="nav"></nav>
<main>

<section id="overview"><h2>1. Overview</h2>
<div class="card"><b>What we did.</b> Analysed how Shaadi.com uses AWS, then rebuilt the serverless part of it (photo moderation with S3, Lambda and Amazon Rekognition) in the same region, Mumbai, and measured cold starts, memory sizing, concurrency and cost per 1,000 requests.
<div class="talk">Say: "Our case is Shaadi.com. We analysed why they moved to AWS and then rebuilt their serverless photo moderation ourselves, and measured what serverless really costs and where it breaks."</div></div>
<div class="grid g4">
<div class="card kpi"><div class="v">10-60x</div><div class="l">cold call vs warm call latency</div></div>
<div class="card kpi"><div class="v">18 ms</div><div class="l">warm floor (API Gateway + Lambda, in-region)</div></div>
<div class="card kpi"><div class="v">$0.0012</div><div class="l">per 1,000 baseline requests</div></div>
<div class="card kpi"><div class="v">$1.0038</div><div class="l">per 1,000 moderations (99.6% Rekognition)</div></div>
<div class="card kpi"><div class="v">100 req/s</div><div class="l">ceiling = 10 x account quota of 10</div></div>
<div class="card kpi"><div class="v">59-63%</div><div class="l">requests throttled (HTTP 503) at 9 and 50 users</div></div>
<div class="card kpi"><div class="v">INIT billed</div><div class="l">cold Billed = Init + handler time</div></div>
<div class="card kpi"><div class="v">~$0.30</div><div class="l">total experiment cost (list price)</div></div></div>
<div class="card"><b>Presentation order:</b> 1 Overview &rarr; 2 Case &rarr; 3 Architecture &rarr; 4 Live demo &rarr; 5 Results &rarr; 6 Cost &rarr; 7 Links (fallback). Each tab has a yellow "Say" note.</div>
</section>

<section id="case"><h2>2. The case: Shaadi.com</h2>
<div class="card">Founded 1996 by Anupam Mittal (People Interactive, Mumbai). 35M+ users (2016), 3M+ active profiles (2021), 2.5M interest requests/day at the April 2020 peak. Moved from a hosted private cloud to AWS in 2016.</div>
<div class="card"><table><tr><th>#</th><th>Problem</th><th>Root cause</th><th>AWS fix</th></tr>
<tr><td>P1</td><td>Slow delivery, 1-2 algorithms per cycle</td><td>Hosted private cloud, capacity bought per project</td><td>Full migration (DMS), Redshift, Auto Scaling, ELB per service</td></tr>
<tr><td>P2</td><td>Lockdown 2020: chats delayed 10-500 s</td><td>DB3 MySQL IOPS tied to disk size on gp2</td><td>EBS gp3: IOPS independent of size, changed live</td></tr>
<tr><td>P3</td><td>Messaging costly to scale</td><td>Relational DB for a key-value pattern</td><td>DynamoDB via strangler-fig migration (60% cheaper)</td></tr>
<tr><td>P4</td><td>Photos waited for manual review</td><td>Humans checked every upload</td><td><b>S3 &rarr; Lambda &rarr; Rekognition (what we rebuilt)</b></td></tr></table>
<h3>DB3 cost per 1,000 interest requests (our calculation)</h3>
<table><tr><th>Stage</th><th>Setup</th><th>Requests/day</th><th>Cost/month</th><th>Per 1,000</th></tr>
<tr><td>Before lockdown</td><td>6 x r5.8xlarge, gp2</td><td>1.8 M</td><td>$9,730</td><td>$0.180</td></tr>
<tr><td>Scaled on gp2</td><td>8 x r5.8xlarge</td><td>2.5 M</td><td>$13,373</td><td>$0.178</td></tr>
<tr><td>After gp3</td><td>6 x r5.8xlarge, gp3</td><td>2.5 M</td><td>$9,963</td><td>$0.133 (-26%)</td></tr></table>
<div class="talk">Say: "Every change broke one coupling: compute to procurement, IOPS to disk size, access pattern to a relational engine, moderation to people. We tested the serverless one, P4."</div></div>
</section>

<section id="arch"><h2>3. Architecture we built</h2>
<div class="card"><div id="svgArch"></div>
<p class="mut">Click a box to open it in the AWS console (log in first). Python 3.15; one least-privilege IAM role per function; tag project=it457-g47; $5 budget alert.</p>
<table><tr><th>Route</th><th>Function</th><th>What it does</th></tr>
<tr><td>GET /baseline</td><td>shaadi-ping (A)</td><td>Returns pong; no AWS calls. Measures Lambda + API Gateway alone. (/ping is reserved by API Gateway.)</td></tr>
<tr><td>POST /interest</td><td>shaadi-interest-api</td><td>Writes an interest (UUID key) to DynamoDB Interests, like Shaadi.com's "send interest".</td></tr>
<tr><td>POST /moderate</td><td>shaadi-moderate (B)</td><td>Rekognition DetectModerationLabels on an S3 photo; verdict (&ge;80% rejected, 60-80% review, else approved) saved to DynamoDB verdicts.</td></tr>
<tr><td>console test</td><td>shaadi-loadgen</td><td>Harness: forces cold starts, fires bursts and load, queries Logs Insights, writes CSVs to S3.</td></tr>
<tr><td>GET /demo</td><td>shaadi-demo</td><td>This page and its helpers (photo preview, latest items, force a cold start).</td></tr></table>
<div class="talk">Say: "Client, HTTP API, three functions. Rekognition reads the photo straight from S3, so the image never passes through Lambda."</div></div>
</section>

<section id="demo"><h2>4. Live demo</h2>
<p class="mut">Latencies here include the network from this browser to Mumbai, so they are higher than the in-region numbers in Results.</p>
<div class="grid g2">
<div class="card"><h3>A. Baseline &nbsp;<code>GET /baseline</code></h3>
<div class="row"><button onclick="callBaseline()">Call once</button><button class="sec" onclick="callBaseline(5)">Call 5 times</button></div><div id="outBase"></div>
<div class="talk">First call after a cold start shows <b>cold</b>; then <b>warm</b> at tens of ms.</div></div>
<div class="card"><h3>B. Send interest &nbsp;<code>POST /interest</code></h3>
<div class="row"><input id="iFrom" value="demo_user" size="10"><input id="iTo" value="user_42" size="8"><input id="iMsg" value="Hello from the IT457 demo!" size="22"></div>
<div class="row" style="margin-top:8px"><button onclick="callInterest()">Send</button><button class="sec" onclick="loadItems('interests')">Show latest in DynamoDB</button></div><div id="outInt"></div></div>
<div class="card"><h3>C. Photo moderation &nbsp;<code>POST /moderate</code></h3>
<div class="row"><select id="photoSel" onchange="showPhoto()"></select><button onclick="callModerate()">Moderate</button><button class="sec" onclick="loadItems('verdicts')">Latest verdicts</button></div>
<div class="row" style="margin-top:10px;align-items:flex-start"><img id="photo" class="photo" alt="photo"><div id="verdictBox"></div></div><div id="outMod"></div>
<div class="talk">Say: "Rekognition fetched the photo from S3 itself; the function decided the verdict and stored it with the Rekognition time."</div></div>
<div class="card" style="grid-column:1/-1"><h3>D. Cold start lab</h3>
<p class="mut">Changes an environment variable on the chosen function. Any configuration change retires its execution environments, so the next calls are cold. This is how our harness forced cold starts.</p>
<div class="row"><select id="coldFn"><option value="ping">shaadi-ping (baseline)</option><option value="interest">shaadi-interest-api</option><option value="moderate">shaadi-moderate</option></select>
<button onclick="coldLab()">Force cold start, then call 1 + 5</button><button class="sec" onclick="burst()">Burst 5 in parallel</button></div><div id="outCold"></div>
<div class="talk">Say: "The first call pays the INIT phase (start the runtime, import boto3), and that INIT time is now billed. The rest reuse the warm environment."</div></div>
</div>
<div class="card"><h3>Session log</h3><table id="log"><tr><th>#</th><th>Call</th><th>HTTP</th><th>Start</th><th>Latency (browser)</th><th></th></tr></table>
<div class="row" style="margin-top:8px"><button class="sec" onclick="document.querySelectorAll('#log tr.r').forEach(e=>e.remove());n=0">Clear</button></div></div>
</section>

<section id="results"><h2>5. Results (measured 12-13 Nov 2026, in-region harness)</h2>
<div class="card"><h3>E1/E2: cold vs warm latency by memory (client p50, ms)</h3><div id="chartCW"></div>
<table id="tblCW"></table>
<div class="talk">Say: "Memory buys CPU. It shortened the interest API's cold start from 1,950 to 699 ms, but moderation barely moved because it waits for Rekognition."</div></div>
<div class="card"><h3>Inside a cold start (CloudWatch REPORT lines)</h3>
<table><tr><th>Function</th><th>Memory</th><th>Init p50</th><th>Cold handler p50</th><th>Cold billed p50</th><th>Warm billed mean</th><th>Max mem</th></tr>
<tr><td>Baseline</td><td>128 / 1024</td><td>116 / 115 ms</td><td>1.8 / 1.7 ms</td><td>118 / 117 ms</td><td>2.1 / 2.0 ms</td><td>35 MB</td></tr>
<tr><td>Interest API</td><td>128 / 1024</td><td>1,242 / 502 ms</td><td>552 / 65 ms</td><td>1,831 / 569 ms</td><td>38.0 / 7.4 ms</td><td>95 MB</td></tr>
<tr><td>Moderation</td><td>128 / 1024</td><td>1,320 / 1,207 ms</td><td>649 / 239 ms</td><td>1,954 / 1,447 ms</td><td>237.8 / 214.7 ms</td><td>~100 MB</td></tr></table>
<p class="mut">Cold Billed Duration = Init + handler: INIT is billed (Aug 2025 change). 10,954 REPORT lines.</p></div>
<div class="card"><h3>E3: concurrency (GET /baseline, 512 MB, 60 s per level)</h3><div id="chartConc"></div>
<table><tr><th>Users</th><th>Requests</th><th>200 OK</th><th>503 throttled</th><th>Served/s</th><th>p50 / p95 / p99</th></tr>
<tr><td>1</td><td>3,969</td><td>3,969</td><td>0</td><td>66.2</td><td>14.7 / 17.7 / 20.7 ms</td></tr>
<tr><td>9</td><td>15,983</td><td>5,936</td><td>10,047 (63%)</td><td>98.9</td><td>38.3 / 50.9 / 56.2 ms</td></tr>
<tr><td>50</td><td>14,823</td><td>6,044</td><td>8,779 (59%)</td><td>100.7</td><td>197.5 / 315.7 / 380.9 ms</td></tr></table>
<div class="talk">Say: "Lambda allows requests per second up to 10 x the concurrency quota. Our new account's quota is 10, so 100 req/s, exactly where it flattened. Concurrency itself was only about 0.15 on average because the function runs in 1.5 ms."</div></div>
</section>

<section id="cost"><h2>6. Cost per 1,000 requests</h2>
<div class="card"><table><tr><th>Per 1,000 warm requests</th><th>Baseline 128 MB</th><th>Interest 512 MB</th><th>Moderation 512 MB</th></tr>
<tr><td>Billed ms (mean)</td><td>2.06</td><td>6.94</td><td>188.72</td></tr>
<tr><td>Lambda compute</td><td>$0.0000043</td><td>$0.0000578</td><td>$0.0015727</td></tr>
<tr><td>Lambda requests + API Gateway</td><td>$0.0012</td><td>$0.0012</td><td>$0.0012</td></tr>
<tr><td>DynamoDB write</td><td>-</td><td>$0.000625</td><td>$0.000625</td></tr>
<tr><td>Rekognition + S3 GET</td><td>-</td><td>-</td><td>$1.0004</td></tr>
<tr><th>Total measured</th><th>$0.0012</th><th>$0.0019</th><th>$1.0038</th></tr>
<tr><td>Week 2 model</td><td>$0.0012</td><td>-</td><td>$1.007</td></tr></table>
<p class="mut">Prices: Lambda $0.20/M + $0.0000166667/GB-s; HTTP API $1.00/M; DynamoDB $0.625/M writes; Rekognition $0.001/image.</p></div>
<div class="card"><h3>Calculator</h3><div class="row">Requests per month <input id="calcN" type="number" value="1000000" style="width:140px">
Memory <select id="calcM"><option>128</option><option>256</option><option selected>512</option><option>1024</option></select><button onclick="calc()">Calculate</button></div><div id="calcOut"></div>
<div class="talk">Say: "Lambda is almost free here. For moderation the bill is the ML call, so savings come from calling Rekognition less, not from tuning Lambda."</div></div>
</section>

<section id="links"><h2>7. Links and fallbacks</h2>
<div class="card"><b>Log in first</b> (IAM users): <a href="https://705029438856.signin.aws.amazon.com/console" target="_blank">https://705029438856.signin.aws.amazon.com/console</a>, then set region to <b>Asia Pacific (Mumbai)</b>. If a live call fails during the presentation, open the matching console page below or show the screenshots in the report (Appendix C).</div>
<div class="grid g2"><div class="card links" id="links1"></div><div class="card links" id="links2"></div></div>
</section>
</main>
<script>
const R='ap-south-1',C='https://ap-south-1.console.aws.amazon.com',B='it457-g47-shaadi-705029438856';
const L={lambda:C+'/lambda/home?region='+R+'#/functions',fn:f=>C+'/lambda/home?region='+R+'#/functions/'+f+'?tab=code',mon:f=>C+'/lambda/home?region='+R+'#/functions/'+f+'?tab=monitoring',
api:C+'/apigateway/main/develop/routes?api=ypq1jax2t5&region='+R,integ:C+'/apigateway/main/develop/integrations/manage?api=ypq1jax2t5&region='+R,
ddb:t=>C+'/dynamodbv2/home?region='+R+'#item-explorer?table='+t,s3:p=>C+'/s3/buckets/'+B+'?region='+R+'&prefix='+p,
logs:C+'/cloudwatch/home?region='+R+'#logsV2:log-groups$3FlogGroupNameFilter$3Dshaadi',insights:C+'/cloudwatch/home?region='+R+'#logsV2:logs-insights',
iam:'https://us-east-1.console.aws.amazon.com/iam/home#/roles?search=shaadi',budget:'https://us-east-1.console.aws.amazon.com/billing/home#/budgets',
quota:C+'/servicequotas/home/services/lambda/quotas',rg:C+'/resource-groups/group/it457-g47-shaadi-project?region='+R};
const tabs=[['overview','1 Overview'],['case','2 Case'],['arch','3 Architecture'],['demo','4 Live demo'],['results','5 Results'],['cost','6 Cost'],['links','7 Links']];
const nav=document.getElementById('nav');tabs.forEach(([id,t])=>{const a=document.createElement('a');a.href='#'+id;a.textContent=t;a.onclick=e=>{e.preventDefault();show(id)};nav.appendChild(a)});
function show(id){document.querySelectorAll('section').forEach(s=>s.classList.toggle('on',s.id===id));nav.querySelectorAll('a').forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+id));history.replaceState(null,'','#'+id)}
show((location.hash||'#overview').slice(1));
document.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT')return;const i=tabs.findIndex(t=>document.getElementById(t[0]).classList.contains('on'));if(e.key==='ArrowRight'&&i<tabs.length-1)show(tabs[i+1][0]);if(e.key==='ArrowLeft'&&i>0)show(tabs[i-1][0])});
let n=0;const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
function badge(c){return c===true?'<span class="badge cold">COLD</span>':c===false?'<span class="badge warm">WARM</span>':''}
async function api(label,method,path,body){const t=performance.now();let st=0,j=null,txt='';try{const r=await fetch(path,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined,cache:'no-store'});st=r.status;txt=await r.text();try{j=JSON.parse(txt)}catch(e){}}catch(e){txt=String(e)}
const ms=Math.round(performance.now()-t);n++;const tr=document.createElement('tr');tr.className='r';tr.innerHTML=`<td>${n}</td><td>${esc(label)}</td><td><span class="badge st">${st}</span></td><td>${badge(j&&j.coldStart)}</td><td>${ms} ms</td><td style="width:35%"><div class="bar" style="width:${Math.min(100,ms/25)}%;background:${j&&j.coldStart?'var(--bad)':'var(--acc)'}"></div></td>`;
document.querySelector('#log tbody').appendChild(tr);return{st,j,txt,ms}}
function out(id,r,extra=''){document.getElementById(id).innerHTML=`<div class="row" style="margin-top:8px"><span class="badge st">HTTP ${r.st}</span>${badge(r.j&&r.j.coldStart)}<b>${r.ms} ms</b>${extra}</div><pre>${esc(r.j?JSON.stringify(r.j,null,2):r.txt)}</pre>`}
async function callBaseline(k=1){let r,s=[];for(let i=0;i<k;i++){r=await api('GET /baseline','GET','/baseline');s.push(r.ms+(r.j&&r.j.coldStart?' (cold)':''))}out('outBase',r,k>1?'<span class="mut">&nbsp;all: '+s.join(', ')+' ms</span>':'')}
async function callInterest(){const r=await api('POST /interest','POST','/interest',{from:iFrom.value,to:iTo.value,message:iMsg.value});out('outInt',r)}
const sel=document.getElementById('photoSel');for(let i=1;i<=30;i++){const o=document.createElement('option');o.value=`photos/photo_${String(i).padStart(2,'0')}.jpg`;o.textContent=`photo_${String(i).padStart(2,'0')}.jpg`;sel.appendChild(o)}sel.value='photos/photo_07.jpg';
function showPhoto(){document.getElementById('photo').src='/demo/photo?key='+encodeURIComponent(sel.value)}showPhoto();
async function callModerate(){const r=await api('POST /moderate','POST','/moderate',{imageKey:sel.value});const v=r.j&&r.j.verdict;const col=v==='approved'?'var(--ok)':v==='review'?'var(--warn)':'var(--bad)';
document.getElementById('verdictBox').innerHTML=v?`<div class="verdict" style="color:${col}">${v}</div><div>Rekognition: <b>${r.j.rekognitionMs} ms</b></div><div>Labels: ${r.j.labels.length?r.j.labels.map(l=>esc(l.name)+' '+l.confidence+'%').join(', '):'none'}</div>`:'';out('outMod',r)}
async function loadItems(t){const id=t==='verdicts'?'outMod':'outInt';const r=await fetch('/demo/items?table='+t,{cache:'no-store'});const j=await r.json();
const cols=t==='verdicts'?['createdAt','imageKey','verdict','rekognitionMs','coldStart']:['createdAt','fromUser','toUser','message'];
document.getElementById(id).innerHTML=`<p class="mut" style="margin:8px 0 4px">Latest 8 of ${j.count} items in DynamoDB table <b>${t==='verdicts'?'verdicts':'Interests'}</b></p><div style="overflow-x:auto"><table style="font-size:12px"><tr>${cols.map(c=>'<th>'+c+'</th>').join('')}</tr>${j.items.slice(0,8).map(it=>'<tr>'+cols.map(c=>'<td>'+esc(c==='createdAt'?new Date(+it[c]).toLocaleTimeString():it[c])+'</td>').join('')+'</tr>').join('')}</table></div>`}
const P={ping:['GET','/baseline'],interest:['POST','/interest',{from:'coldlab',to:'u',message:'cold lab'}],moderate:['POST','/moderate',{imageKey:'photos/photo_05.jpg'}]};
async function coldLab(){const f=coldFn.value;const o=document.getElementById('outCold');o.innerHTML='<p class="mut">Updating configuration of '+f+' and waiting until it is ready...</p>';
const t=performance.now();const r=await fetch('/demo/cold',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({fn:f})});const j=await r.json();
let rows=[];for(let i=0;i<6;i++){const x=await api(f+(i?' warm?':' first'),...P[f]);rows.push(x)}
const mx=Math.max(...rows.map(x=>x.ms));o.innerHTML=`<p class="mut">Configuration updated in ${((performance.now()-t)/1000).toFixed(1)} s (nonce ${esc(j.nonce||j.error)}).</p>`+rows.map((x,i)=>`<div class="lr"><span style="width:60px">call ${i+1}</span>${badge(x.j&&x.j.coldStart)}<div class="bar" style="width:${Math.max(4,x.ms/mx*420)}px;background:${x.j&&x.j.coldStart?'var(--bad)':'var(--acc)'}"></div><b>${x.ms} ms</b></div>`).join('')}
async function burst(){const f=coldFn.value;const rs=await Promise.all(Array.from({length:5},(_,i)=>api(f+' burst','GET'===P[f][0]?'GET':P[f][0],P[f][1],P[f][2])));
document.getElementById('outCold').innerHTML='<p class="mut">5 parallel calls: each needs its own execution environment, so new environments start cold.</p>'+rs.map((x,i)=>`<div class="row" style="margin:3px 0"><span style="width:60px">call ${i+1}</span>${badge(x.j&&x.j.coldStart)}<b>${x.ms} ms</b></div>`).join('')}
// ---------- static data and charts
const CW=[['ping',128,7,492.69,18.58,22.06],['ping',256,8,216.92,18.08,21.3],['ping',512,8,230.84,18.69,22.86],['ping',1024,8,309.84,18.46,21.32],
['interest',128,8,1950.17,31.59,60.16],['interest',256,8,1540.5,24.87,34.34],['interest',512,8,876.45,24.05,30.01],['interest',1024,8,698.52,24.54,26.36],
['moderate',128,8,2070.92,201.54,242.46],['moderate',256,8,999.73,185.67,256.23],['moderate',512,8,1071.62,179.36,206.91],['moderate',1024,8,1608.07,173.07,268.03]];
const COL={ping:'#6b7a8f',interest:'#c026d3',moderate:'#2f9e44'},NM={ping:'A: baseline',interest:'Interest API',moderate:'B: moderation'};
document.getElementById('tblCW').innerHTML='<tr><th>Function</th><th>Memory</th><th>Cold starts</th><th>Cold p50</th><th>Warm p50</th><th>Warm p95</th><th>Cold/warm</th></tr>'+CW.map(r=>`<tr><td>${NM[r[0]]}</td><td>${r[1]} MB</td><td>${r[2]}/8</td><td>${Math.round(r[3]).toLocaleString()} ms</td><td>${r[4]} ms</td><td>${r[5]} ms</td><td>${Math.round(r[3]/r[4])}x</td></tr>`).join('');
(function(){const W=1080,H=280,pl=50,pb=40,gw=(W-pl-20)/12,lg=v=>Math.log10(v),y=v=>H-pb-(lg(v)-1)/(lg(3000)-1)*(H-pb-20);let s=`<svg viewBox="0 0 ${W} ${H}" width="100%">`;
[10,30,100,300,1000,3000].forEach(v=>{s+=`<line x1="${pl}" x2="${W-10}" y1="${y(v)}" y2="${y(v)}" stroke="#e6e6e6"/><text x="${pl-6}" y="${y(v)+4}" font-size="11" text-anchor="end" fill="#666">${v}</text>`});
CW.forEach((r,i)=>{const x=pl+i*gw+8,c=COL[r[0]];s+=`<rect x="${x}" y="${y(r[3])}" width="${gw/2-6}" height="${H-pb-y(r[3])}" fill="${c}"/><rect x="${x+gw/2-4}" y="${y(r[4])}" width="${gw/2-6}" height="${H-pb-y(r[4])}" fill="${c}" opacity=".35"/>
<text x="${x+gw/4-3}" y="${y(r[3])-4}" font-size="10" text-anchor="middle">${Math.round(r[3])}</text><text x="${x+3*gw/4-7}" y="${y(r[4])-4}" font-size="10" text-anchor="middle">${Math.round(r[4])}</text><text x="${x+gw/2-6}" y="${H-pb+14}" font-size="11" text-anchor="middle">${r[1]}</text>`});
['ping','interest','moderate'].forEach((k,i)=>{s+=`<text x="${pl+(i*4+2)*gw}" y="${H-6}" font-size="12" font-weight="700" text-anchor="middle" fill="${COL[k]}">${NM[k]} (MB)</text>`});
s+=`<text x="${W-14}" y="18" font-size="11" text-anchor="end" fill="#444">solid = cold p50, light = warm p50, log scale (ms)</text></svg>`;document.getElementById('chartCW').innerHTML=s})();
(function(){const d=[[1,66.2,0],[9,98.9,167.5],[50,100.7,146.3]],W=700,H=230,pb=30,mx=300,y=v=>H-pb-v/mx*(H-pb-10);let s=`<svg viewBox="0 0 ${W} ${H}" width="70%">`;
[0,100,200,300].forEach(v=>{s+=`<line x1="40" x2="${W-10}" y1="${y(v)}" y2="${y(v)}" stroke="#e6e6e6"/><text x="34" y="${y(v)+4}" font-size="11" text-anchor="end" fill="#666">${v}</text>`});
d.forEach((r,i)=>{const x=90+i*200;s+=`<rect x="${x}" y="${y(r[1])}" width="110" height="${H-pb-y(r[1])}" fill="#6b7a8f"/><rect x="${x}" y="${y(r[1]+r[2])}" width="110" height="${H-pb-y(r[2])}" fill="#e8590c"/>
<text x="${x+55}" y="${y(r[1])+16}" fill="#fff" font-size="12" text-anchor="middle">${r[1]}/s OK</text>${r[2]?`<text x="${x+55}" y="${y(r[1]+r[2])+16}" fill="#fff" font-size="12" text-anchor="middle">${r[2]}/s 503</text>`:''}<text x="${x+55}" y="${H-10}" font-size="12" text-anchor="middle">${r[0]} user${r[0]>1?'s':''}</text>`});
s+=`<line x1="40" x2="${W-10}" y1="${y(100)}" y2="${y(100)}" stroke="#111" stroke-dasharray="5 4"/><text x="${W-12}" y="${y(100)-5}" font-size="11" text-anchor="end">100 req/s = 10 x quota 10</text></svg>`;document.getElementById('chartConc').innerHTML=s})();
function calc(){const N=+calcN.value,M=+calcM.value,ms={ping:{128:2.06,256:2.3,512:2.12,1024:2.02},interest:{128:38.04,256:13.62,512:6.94,1024:7.38},moderate:{128:237.78,256:209.16,512:188.72,1024:214.68}};
const f=(k,ddb,rek)=>N*(ms[k][M]/1000*M/1024*0.0000166667+0.2e-6+1e-6+(ddb?0.625e-6:0)+(rek?0.001+0.0004e-3:0));
calcOut.innerHTML=`<table style="margin-top:10px"><tr><th>Function at ${M} MB</th><th>Monthly cost for ${N.toLocaleString()} requests</th></tr><tr><td>Baseline</td><td>$${f('ping').toFixed(2)}</td></tr><tr><td>Interest API</td><td>$${f('interest',1).toFixed(2)}</td></tr><tr><td>Moderation</td><td>$${f('moderate',1,1).toFixed(2)} (Rekognition $${(N*0.001).toFixed(2)})</td></tr></table>`}calc();
// ---------- architecture svg
(function(){const b=(x,y,w,h,t,s,c,href)=>`<a href="${href}" target="_blank"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="#fff" stroke="${c}" stroke-width="2"/><text x="${x+w/2}" y="${y+h/2-3}" text-anchor="middle" font-size="13" font-weight="700">${t}</text><text x="${x+w/2}" y="${y+h/2+14}" text-anchor="middle" font-size="10.5" fill="#555">${s}</text></a>`;
const ar=(x1,y1,x2,y2,t='')=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#444" stroke-width="1.5" marker-end="url(#m)"/>`+(t?`<text x="${(x1+x2)/2}" y="${(y1+y2)/2-5}" font-size="10.5" text-anchor="middle" fill="#444">${t}</text>`:'');
let s=`<svg viewBox="0 0 1100 420" width="100%"><defs><marker id="m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#444"/></marker></defs>
<rect x="150" y="10" width="940" height="400" rx="14" fill="#fafbfc" stroke="#222"/><text x="168" y="34" font-size="13" font-weight="700">AWS account 705029438856, ap-south-1 (Mumbai)</text>`;
s+=b(10,170,120,60,'Client','browser / curl','#222','#demo');s+=b(175,160,150,80,'API Gateway','HTTP API ypq1jax2t5','#c026d3',L.api);
s+=b(380,55,190,62,'shaadi-ping (A)','GET /baseline','#6b7a8f',L.fn('shaadi-ping'));s+=b(380,169,190,62,'shaadi-interest-api','POST /interest','#c026d3',L.fn('shaadi-interest-api'));
s+=b(380,283,190,62,'shaadi-moderate (B)','POST /moderate','#2f9e44',L.fn('shaadi-moderate'));s+=b(640,169,170,62,'DynamoDB','Interests','#1971c2',L.ddb('Interests'));
s+=b(640,283,170,62,'Rekognition','DetectModerationLabels','#2f9e44',L.lambda);s+=b(880,283,190,62,'S3 bucket','photos/ and results/','#e8590c',L.s3('photos/'));
s+=b(640,355,170,46,'DynamoDB','verdicts','#1971c2',L.ddb('verdicts'));s+=b(880,55,190,62,'CloudWatch Logs','REPORT: Init, Billed','#495057',L.logs);s+=b(880,169,190,62,'shaadi-loadgen','experiment harness','#495057',L.fn('shaadi-loadgen'));
s+=ar(130,200,175,200,'HTTPS')+ar(325,180,380,90)+ar(325,200,380,200)+ar(325,220,380,312)+ar(570,200,640,200,'PutItem')+ar(570,312,640,312,'1 detect')+ar(810,312,880,312,'2 read image')+ar(475,345,640,375,'3 save verdict')+ar(570,86,880,86,'logs');
s+='</svg>';document.getElementById('svgArch').innerHTML=s})();
// ---------- links
const lk=(t,u)=>`<a href="${u}" target="_blank">${t}</a>`;
document.getElementById('links1').innerHTML='<b>Compute and API</b>'+[['All Lambda functions',L.lambda],['shaadi-ping code',L.fn('shaadi-ping')],['shaadi-interest-api code',L.fn('shaadi-interest-api')],['shaadi-moderate code',L.fn('shaadi-moderate')],['shaadi-loadgen (harness)',L.fn('shaadi-loadgen')],['shaadi-ping metrics (throttles, concurrency)',L.mon('shaadi-ping')],['API Gateway routes',L.api],['API Gateway integrations',L.integ],['Live: GET /baseline','/baseline']].map(x=>lk(...x)).join('');
document.getElementById('links2').innerHTML='<b>Data, logs, security, cost</b>'+[['DynamoDB verdicts',L.ddb('verdicts')],['DynamoDB Interests',L.ddb('Interests')],['S3 test photos',L.s3('photos/')],['S3 experiment results (CSV)',L.s3('results/')],['CloudWatch log groups',L.logs],['Logs Insights',L.insights],['IAM roles (shaadi-*)',L.iam],['AWS Budgets ($5 alert)',L.budget],['Lambda quotas (concurrency 10)',L.quota],['Resource group: whole project',L.rg]].map(x=>lk(...x)).join('');
</script></body></html>
"""


def resp(code, body, ctype="application/json", b64=False):
    if not isinstance(body, str):
        body = json.dumps(body, default=lambda o: float(o) if isinstance(o, Decimal) else str(o))
    return {"statusCode": code, "headers": {"Content-Type": ctype, "Cache-Control": "no-store"},
            "body": body, "isBase64Encoded": b64}


def lambda_handler(event, context):
    path = event.get("rawPath", "/demo")
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    qs = event.get("queryStringParameters") or {}

    if path in ("/demo", "/demo/"):
        return resp(200, HTML, "text/html; charset=utf-8")

    if path == "/demo/photo":
        key = qs.get("key", "photos/photo_01.jpg")
        if not key.startswith("photos/") or ".." in key:
            return resp(400, {"error": "key must be under photos/"})
        data = S3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
        return resp(200, base64.b64encode(data).decode(), "image/jpeg", True)

    if path == "/demo/items":
        table = TABLES.get(qs.get("table", "verdicts"))
        if not table:
            return resp(400, {"error": "unknown table"})
        items, kw = [], {"TableName": table}
        while True:
            page = DDB.scan(**kw)
            items += [{k: DES.deserialize(v) for k, v in it.items()} for it in page["Items"]]
            if "LastEvaluatedKey" not in page:
                break
            kw["ExclusiveStartKey"] = page["LastEvaluatedKey"]
        items.sort(key=lambda i: i.get("createdAt", 0), reverse=True)
        return resp(200, {"count": len(items), "items": items[:20]})

    if path == "/demo/cold" and method == "POST":
        fn = FUNCS.get(json.loads(event.get("body") or "{}").get("fn", "ping"))
        if not fn:
            return resp(400, {"error": "unknown function"})
        t0 = time.time()
        env = LAMBDA.get_function_configuration(FunctionName=fn).get("Environment", {}).get("Variables", {})
        env["RUN_NONCE"] = uuid.uuid4().hex[:8]
        LAMBDA.update_function_configuration(FunctionName=fn, Environment={"Variables": env})
        LAMBDA.get_waiter("function_updated").wait(FunctionName=fn, WaiterConfig={"Delay": 1, "MaxAttempts": 25})
        time.sleep(2)
        return resp(200, {"function": fn, "nonce": env["RUN_NONCE"], "seconds": round(time.time() - t0, 1)})

    return resp(404, {"error": "not found", "path": path})
