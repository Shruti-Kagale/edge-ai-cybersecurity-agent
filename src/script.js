// ---- State (mirrors dashboard.py session_state) ----
const MAX_LOGS = 25;
let logs = [];          // {Time, Type, Port, Severity} - newest first
let allLogsForExport = []; // full history for CSV export (not capped)
let portHistory = [];   // {Time, Port} - capped at 25
let attackCount = 0;
let normalCount = 0;
let running = false;

const modeSelect = document.getElementById('modeSelect');
const startBtn = document.getElementById('startBtn');
const logBody = document.getElementById('logBody');
const runToast = document.getElementById('runToast');

function pad(n){ return n.toString().padStart(2,'0'); }
function nowTime(){
  const d = new Date();
  return pad(d.getHours())+':'+pad(d.getMinutes())+':'+pad(d.getSeconds());
}

// ---- Packet generation (mirrors generate_packet / process_packet) ----
const PORTS = [22, 80, 443];
function generatePacket(){
  const attackProb = modeSelect.value === 'attack' ? 0.6 : 0.3;
  const isAttack = Math.random() < attackProb;
  return {
    type: isAttack ? 'ATTACK' : 'NORMAL',
    port: PORTS[Math.floor(Math.random()*PORTS.length)]
  };
}

function processPacket(pkt){
  const severity = pkt.type === 'ATTACK' ? 'HIGH' : 'LOW';
  if(pkt.type === 'ATTACK') attackCount++; else normalCount++;

  const entry = { Time: nowTime(), Type: pkt.type, Port: pkt.port, Severity: severity };
  logs.unshift(entry);
  if(logs.length > MAX_LOGS) logs.pop();
  allLogsForExport.push(entry);

  portHistory.push({ Time: entry.Time, Port: pkt.port });
  if(portHistory.length > MAX_LOGS) portHistory.shift();

  renderMetrics();
  renderLogTable();
  drawPie();
  drawPortChart();
}

function renderMetrics(){
  document.getElementById('attackCount').textContent = attackCount;
  document.getElementById('normalCount').textContent = normalCount;
  document.getElementById('totalCount').textContent = attackCount + normalCount;
}

function renderLogTable(){
  logBody.innerHTML = logs.map((row, i) => `
    <tr class="${i===0 ? 'new-row' : ''}">
      <td>${row.Time}</td>
      <td class="type-${row.Type}">${row.Type}</td>
      <td>${row.Port}</td>
      <td><span class="sev sev-${row.Severity}">${row.Severity}</span></td>
    </tr>
  `).join('');
}

// ---- Pie chart (Attack vs Normal) ----
function sizeCanvas(c){
  const ratio = window.devicePixelRatio || 1;
  const rect = c.getBoundingClientRect();
  c.width = rect.width * ratio;
  c.height = rect.height * ratio;
  const ctx = c.getContext('2d');
  ctx.setTransform(ratio,0,0,ratio,0,0);
  return ctx;
}

const pieCanvas = document.getElementById('pieChart');
function drawPie(){
  const ctx = sizeCanvas(pieCanvas);
  const w = pieCanvas.getBoundingClientRect().width;
  const h = pieCanvas.getBoundingClientRect().height;
  ctx.clearRect(0,0,w,h);

  const total = attackCount + normalCount;
  const cx = w/2, cy = h/2, r = Math.min(w,h)/2 - 10;

  if(total === 0){
    ctx.strokeStyle = '#1E2A42';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI*2);
    ctx.stroke();
    return;
  }

  const attackAngle = (attackCount/total) * Math.PI*2;
  let start = -Math.PI/2;

  ctx.beginPath();
  ctx.moveTo(cx,cy);
  ctx.arc(cx, cy, r, start, start+attackAngle);
  ctx.closePath();
  ctx.fillStyle = '#FF4757';
  ctx.fill();

  ctx.beginPath();
  ctx.moveTo(cx,cy);
  ctx.arc(cx, cy, r, start+attackAngle, start+Math.PI*2);
  ctx.closePath();
  ctx.fillStyle = '#33C2A0';
  ctx.fill();

  // percentage labels
  ctx.fillStyle = '#0B1120';
  ctx.font = '600 12px "IBM Plex Mono", monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const attackPct = Math.round((attackCount/total)*100);
  const normalPct = 100 - attackPct;
  const midAttack = start + attackAngle/2;
  const midNormal = start + attackAngle + (Math.PI*2-attackAngle)/2;
  if(attackCount>0) ctx.fillText(attackPct+'%', cx + Math.cos(midAttack)*r*0.55, cy + Math.sin(midAttack)*r*0.55);
  if(normalCount>0) ctx.fillText(normalPct+'%', cx + Math.cos(midNormal)*r*0.55, cy + Math.sin(midNormal)*r*0.55);
}

// ---- Port activity line chart ----
const portCanvas = document.getElementById('portChart');
function drawPortChart(){
  const ctx = sizeCanvas(portCanvas);
  const w = portCanvas.getBoundingClientRect().width;
  const h = portCanvas.getBoundingClientRect().height;
  ctx.clearRect(0,0,w,h);

  ctx.strokeStyle = '#1E2A42';
  ctx.lineWidth = 1;
  for(let i=1;i<3;i++){
    const y = (h/3)*i;
    ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke();
  }

  if(portHistory.length < 2) return;

  const portVals = [22,80,443];
  const stepX = w / (portHistory.length - 1);
  const padTop = 16, padBottom = 16;
  const plotH = h - padTop - padBottom;

  ctx.beginPath();
  portHistory.forEach((pt, i) => {
    const x = i * stepX;
    const idx = portVals.indexOf(pt.Port);
    const y = padTop + (plotH - (idx/(portVals.length-1))*plotH);
    if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.strokeStyle = '#33C2A0';
  ctx.lineWidth = 2;
  ctx.stroke();

  portHistory.forEach((pt, i) => {
    const x = i * stepX;
    const idx = portVals.indexOf(pt.Port);
    const y = padTop + (plotH - (idx/(portVals.length-1))*plotH);
    ctx.beginPath();
    ctx.arc(x, y, 2.5, 0, Math.PI*2);
    ctx.fillStyle = '#33C2A0';
    ctx.fill();
  });

  ctx.fillStyle = '#7C8798';
  ctx.font = '11px "IBM Plex Mono", monospace';
  ctx.textAlign = 'left';
  portVals.forEach((p, idx) => {
    const y = padTop + (plotH - (idx/(portVals.length-1))*plotH);
    ctx.fillText(p, 4, y - 4);
  });
}

// ---- Start SOC Monitoring (mirrors the 40-iteration Streamlit loop) ----
startBtn.addEventListener('click', () => {
  if(running) return;
  running = true;
  startBtn.disabled = true;
  startBtn.textContent = 'Monitoring…';

  let i = 0;
  const interval = setInterval(() => {
    processPacket(generatePacket());
    i++;
    if(i >= 40){
      clearInterval(interval);
      running = false;
      startBtn.disabled = false;
      startBtn.textContent = 'Start SOC Monitoring';
    }
  }, 400);
});

// ---- Save Log / Download Log (CSV: Time, Type, Port, Severity) ----
function buildCsv(){
  const header = 'Time,Classification,Port,Severity\n';
  const rows = allLogsForExport.map(r => `${r.Time},${r.Type},${r.Port},${r.Severity}`).join('\n');
  return header + rows;
}

function showToast(msg){
  runToast.textContent = msg;
  runToast.classList.add('show');
  setTimeout(() => runToast.classList.remove('show'), 2200);
}

document.getElementById('saveLogBtn').addEventListener('click', () => {
  if(allLogsForExport.length === 0){
    showToast('No log entries yet');
    return;
  }
  showToast(`Log saved — ${allLogsForExport.length} entries`);
});

document.getElementById('downloadLogBtn').addEventListener('click', () => {
  if(allLogsForExport.length === 0){
    showToast('No log entries yet');
    return;
  }
  const csv = buildCsv();
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const stamp = new Date().toISOString().replace(/[:.]/g,'-');
  a.href = url;
  a.download = `soc_log_${stamp}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('CSV downloaded');
});

window.addEventListener('resize', () => { drawPie(); drawPortChart(); });

// initial paint
renderMetrics();
drawPie();
drawPortChart();
