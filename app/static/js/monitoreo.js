/**
 * LBS Monitor — SCADA Frontend
 * Monitoreo en tiempo real de UPS via WebSocket (SNMP/Modbus)
 * Features: dual-method ZT connection, recording, persistent alerts, history
 */

const socket = io();

// === STATE ===
let devices = {};
let currentDevId = null;
let chartVIn = null, chartVOut = null, chartB = null, chartFreq = null, chartTemp = null;
let pollTimer = null;
let statusLogMessages = [];
let lastDeviceStatus = {};
const MAX_LOG_MESSAGES = 50;

const PHASE_COLORS = { l1: '#ff453a', l2: '#ff9f0a', l3: '#0a84ff' };

// === HELPERS ===
function getTimeString() {
    const now = new Date();
    return `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
}

function setTxt(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = (val !== undefined && val !== null) ? val : '--';
}

// === PROTOCOL TOGGLE IN MODAL ===
document.querySelectorAll('input[name="protocolo"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        const isModbus = e.target.value === 'modbus';
        document.getElementById('modbusFields').style.display = isModbus ? 'flex' : 'none';
        document.getElementById('snmpFields').style.display = isModbus ? 'none' : 'flex';
    });
});

// === CHART CONFIG ===
function lineChartConfig(datasets) {
    return {
        type: 'line',
        data: { labels: [], datasets: datasets },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            interaction: { intersect: false, mode: 'index' },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: 'rgba(255,255,255,0.5)', font: { size: 9, family: 'JetBrains Mono' } },
                    border: { display: false }
                },
                x: { display: true, grid: { display: false }, ticks: { display: false } }
            },
            plugins: {
                legend: { labels: { color: '#bbb', usePointStyle: true, boxWidth: 6, font: { size: 10, family: 'Rajdhani' } } },
                tooltip: {
                    backgroundColor: 'rgba(28,28,30,0.9)', titleFont: { family: 'Rajdhani' },
                    bodyFont: { family: 'JetBrains Mono' }, borderColor: '#ff453a', borderWidth: 1
                }
            },
            elements: { line: { tension: 0.4 }, point: { radius: 0, hoverRadius: 4 } }
        }
    };
}

function initCharts() {
    const vConfig = () => lineChartConfig([
        { label: 'L1', borderColor: PHASE_COLORS.l1, data: [], borderWidth: 2 },
        { label: 'L2', borderColor: PHASE_COLORS.l2, data: [], borderWidth: 2 },
        { label: 'L3', borderColor: PHASE_COLORS.l3, data: [], borderWidth: 2 }
    ]);
    chartVIn = new Chart(document.getElementById('chartVoltajeIn').getContext('2d'), vConfig());
    chartVOut = new Chart(document.getElementById('chartVoltajeOut').getContext('2d'), vConfig());
    chartFreq = new Chart(document.getElementById('chartFrequency').getContext('2d'), lineChartConfig([
        { label: 'IN', borderColor: '#bf5af2', data: [], borderWidth: 2, borderDash: [5, 5] },
        { label: 'OUT', borderColor: '#32d74b', data: [], borderWidth: 2 }
    ]));
    chartTemp = new Chart(document.getElementById('chartTemp').getContext('2d'), lineChartConfig([
        { label: 'BATT', borderColor: '#ff9f0a', data: [], borderWidth: 2, fill: { target: 'origin', below: 'rgba(255,159,10,0.1)' } },
        { label: 'ENV', borderColor: '#30d158', data: [], borderWidth: 1 }
    ]));
    chartB = new Chart(document.getElementById('chartBateria').getContext('2d'), {
        type: 'doughnut', data: { datasets: [{ data: [1, 1] }] }
    });
}

function pushChartData(chart, label, values) {
    const maxPoints = 50;
    if (chart.data.labels.length >= maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(ds => ds.data.shift());
    }
    chart.data.labels.push(label);
    values.forEach((v, i) => { if (chart.data.datasets[i]) chart.data.datasets[i].data.push(v); });
    chart.update('none');
}

// === DEVICE LIST ===
function loadDeviceList() {
    fetch('/api/monitoreo/list')
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('deviceList');
            container.innerHTML = '';
            data.forEach(dev => {
                devices[dev.id] = dev;
                renderDeviceCard(dev);
            });
        });
}

function renderDeviceCard(dev) {
    const container = document.getElementById('deviceList');
    let card = document.getElementById(`card-${dev.id}`);
    if (!card) {
        card = document.createElement('div');
        card.id = `card-${dev.id}`;
        card.className = 'device-list-item';
        card.onclick = () => selectDevice(dev.id);
        container.appendChild(card);
    }
    card.classList.remove('status-online', 'status-offline');
    card.classList.add(dev.status === 'online' ? 'status-online' : 'status-offline');

    const proto = (dev.protocolo || 'modbus').toUpperCase();
    const recBadge = dev.recording ? '<span class="badge bg-danger ms-1" style="font-size:0.55rem;">REC</span>' : '';
    const connIcon = dev.connection_method === 'port_forward' ? 'bi-hdd-network' : 'bi-ethernet';

    card.innerHTML = `
        <div class="d-flex justify-content-between">
            <div>
                <div class="fw-bold text-white mb-1 font-mono" style="font-size:0.8rem;">${dev.nombre || dev.name}${recBadge}</div>
                <div class="small text-muted" style="font-size:0.7rem;">
                    ${dev.ip} | ${proto}
                    <i class="bi ${connIcon} ms-1" title="${dev.connection_method || 'direct'}"></i>
                </div>
            </div>
            <div class="text-end">
                <i class="bi bi-trash text-dark" style="opacity:0.3; cursor:pointer;" onclick="deleteDevice(${dev.id}, event)" title="Eliminar"></i>
            </div>
        </div>
    `;
    if (currentDevId === dev.id) card.classList.add('active');
}

// === TELEMETRY POLLING ===
function startTelemetry() {
    if (pollTimer) clearInterval(pollTimer);
    let pollInterval = 500;
    pollTimer = setInterval(() => {
        if (currentDevId) socket.emit('request_update', { device_id: currentDevId });
    }, pollInterval);
    setTimeout(() => {
        clearInterval(pollTimer);
        pollTimer = setInterval(() => {
            if (currentDevId) socket.emit('request_update', { device_id: currentDevId });
        }, 2000);
    }, 10000);
}

// === SELECT DEVICE ===
function selectDevice(id) {
    currentDevId = id;
    document.getElementById('dashboardView').style.display = 'none';
    document.getElementById('monitorPanel').style.display = 'block';

    document.querySelectorAll('.device-list-item').forEach(c => c.classList.remove('active'));
    const activeCard = document.getElementById(`card-${id}`);
    if (activeCard) activeCard.classList.add('active');

    const dev = devices[id];
    if (!dev) return;

    document.getElementById('currentDevName').textContent = dev.nombre || dev.name;
    document.getElementById('currentDevIp').textContent = dev.ip;
    document.getElementById('currentDevProtocol').textContent = (dev.protocolo || 'modbus').toUpperCase();

    // Connection method badge
    const connBadge = document.getElementById('currentConnMethod');
    if (connBadge) {
        const method = dev.connection_method || 'direct';
        connBadge.textContent = method === 'port_forward' ? 'ZT-PORTFWD' : 'DIRECTO';
        connBadge.className = `eng-badge badge-${method === 'port_forward' ? 'info' : 'warn'}`;
    }

    // Recording button state
    updateRecordingUI(dev);

    // Phase detection
    const phases = dev.phases || dev.fases || (dev.ups_type === 'invt_minimal' || dev.ups_type === 'megatec_snmp' ? 1 : 3);
    const isMono = (phases === 1);

    document.querySelectorAll('.text-l2, .text-l3').forEach(el => {
        if (isMono) el.style.setProperty('display', 'none', 'important');
        else el.style.display = el.classList.contains('mimic-value-row') ? 'flex' : '';
    });

    // Recreate voltage charts for phase count
    if (chartVIn) chartVIn.destroy();
    if (chartVOut) chartVOut.destroy();
    const datasetsV = [{ label: 'L1', borderColor: PHASE_COLORS.l1, data: [], borderWidth: 2 }];
    if (!isMono) {
        datasetsV.push({ label: 'L2', borderColor: PHASE_COLORS.l2, data: [], borderWidth: 2 });
        datasetsV.push({ label: 'L3', borderColor: PHASE_COLORS.l3, data: [], borderWidth: 2 });
    }
    chartVIn = new Chart(document.getElementById('chartVoltajeIn').getContext('2d'), lineChartConfig(JSON.parse(JSON.stringify(datasetsV))));
    chartVOut = new Chart(document.getElementById('chartVoltajeOut').getContext('2d'), lineChartConfig(JSON.parse(JSON.stringify(datasetsV))));

    [chartFreq, chartTemp].forEach(c => {
        if (c) { c.data.labels = []; c.data.datasets.forEach(ds => ds.data = []); c.update(); }
    });

    // Restore history from session if available
    if (dev.history) {
        const h = dev.history;
        const restoreData = (chart, dataArrs) => {
            if (!chart) return;
            chart.data.labels = [...h.labels];
            dataArrs.forEach((arr, idx) => { if (chart.data.datasets[idx]) chart.data.datasets[idx].data = [...arr]; });
            chart.update();
        };
        restoreData(chartVIn, [h.vInL1, h.vInL2, h.vInL3]);
        restoreData(chartVOut, [h.vOutL1, h.vOutL2, h.vOutL3]);
        restoreData(chartFreq, [h.freqIn, h.freqOut]);
        restoreData(chartTemp, [h.temp, h.envTemp]);
    }

    // Load persistent alerts for this device
    loadAlerts(id);

    startTelemetry();
}

// === RECORDING ===
function updateRecordingUI(dev) {
    const btn = document.getElementById('btnToggleRecording');
    if (!btn) return;
    if (dev.recording) {
        btn.innerHTML = '<i class="bi bi-stop-circle"></i> STOP';
        btn.classList.remove('btn-outline-danger');
        btn.classList.add('btn-danger');
    } else {
        btn.innerHTML = '<i class="bi bi-record-circle"></i> REC';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-outline-danger');
    }
}

function toggleRecording() {
    if (!currentDevId) return;
    const dev = devices[currentDevId];
    const newState = !dev.recording;
    const interval = parseInt(document.getElementById('recInterval')?.value || '30');

    fetch(`/api/monitoreo/${currentDevId}/recording`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recording: newState, interval: interval })
    }).then(r => r.json()).then(() => {
        dev.recording = newState;
        dev.recording_interval = interval;
        updateRecordingUI(dev);
        renderDeviceCard(dev);
        addStatusLog(newState ? `Grabación iniciada (${interval}s)` : 'Grabación detenida', newState ? 'success' : 'info');
    });
}

// === PERSISTENT ALERTS ===
function loadAlerts(deviceId) {
    fetch(`/api/monitoreo/alerts?device_id=${deviceId}&active_only=false&limit=50`)
        .then(r => r.json())
        .then(alerts => renderPersistentAlerts(alerts));
}

function renderPersistentAlerts(alerts) {
    const panel = document.getElementById('persistentAlertPanel');
    if (!panel) return;

    if (!alerts || alerts.length === 0) {
        panel.innerHTML = '<div class="text-muted small p-2">Sin alertas registradas.</div>';
        return;
    }

    let html = '<table class="alarm-table w-100"><thead><tr><th>HORA</th><th>NIVEL</th><th>MENSAJE</th><th>ESTADO</th></tr></thead><tbody>';
    alerts.forEach(a => {
        const time = a.timestamp ? new Date(a.timestamp).toLocaleTimeString('es-MX', { hour12: false }) : '--';
        const levelBadge = `<span class="badge bg-${a.level === 'critical' ? 'danger' : a.level === 'warning' ? 'warning' : 'info'}">${a.level}</span>`;
        const statusBadge = a.resolved
            ? '<span class="badge bg-secondary">Resuelta</span>'
            : `<button class="btn btn-sm btn-outline-success py-0 px-1" onclick="resolveAlert(${a.id})" style="font-size:0.65rem;">Resolver</button>`;
        html += `<tr${a.resolved ? '' : ' style="background:rgba(255,69,58,0.05);"'}><td class="font-mono text-muted">${time}</td><td>${levelBadge}</td><td class="small">${a.message}</td><td>${statusBadge}</td></tr>`;
    });
    html += '</tbody></table>';
    panel.innerHTML = html;
}

function resolveAlert(alertId) {
    fetch(`/api/monitoreo/alerts/${alertId}/resolve`, { method: 'POST' })
        .then(() => { if (currentDevId) loadAlerts(currentDevId); });
}

// === HISTORY PANEL ===
let historyChart = null;

function loadHistory() {
    if (!currentDevId) return;
    const desde = document.getElementById('histDesde')?.value;
    const hasta = document.getElementById('histHasta')?.value;
    let url = `/api/monitoreo/${currentDevId}/history?limit=2000`;
    if (desde) url += `&desde=${desde}`;
    if (hasta) url += `&hasta=${hasta}`;

    fetch(url).then(r => r.json()).then(readings => {
        if (!readings || readings.length === 0) {
            addStatusLog('Sin datos históricos para el rango seleccionado', 'warning');
            return;
        }
        readings.reverse(); // Oldest first for chart
        renderHistoryChart(readings);
    });
}

function renderHistoryChart(readings) {
    const canvas = document.getElementById('chartHistory');
    if (!canvas) return;
    if (historyChart) historyChart.destroy();

    const field = document.getElementById('histField')?.value || 'voltaje_in_l1';
    const labels = readings.map(r => {
        const d = new Date(r.timestamp);
        return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
    });
    const data = readings.map(r => r[field]);

    historyChart = new Chart(canvas.getContext('2d'), lineChartConfig([
        { label: field.replace(/_/g, ' ').toUpperCase(), borderColor: '#3b82f6', data: data, borderWidth: 2 }
    ]));
    historyChart.data.labels = labels;
    historyChart.update();
}

function exportCSV() {
    if (!currentDevId) return;
    const desde = document.getElementById('histDesde')?.value;
    const hasta = document.getElementById('histHasta')?.value;
    let url = `/api/monitoreo/${currentDevId}/history/csv?limit=50000`;
    if (desde) url += `&desde=${desde}`;
    if (hasta) url += `&hasta=${hasta}`;
    window.open(url, '_blank');
}

// === ADD DEVICE ===
function addDevice() {
    const protocolo = document.querySelector('input[name="protocolo"]:checked').value;
    const data = {
        nombre: document.getElementById('devName').value,
        ip: document.getElementById('devIp').value,
        protocolo: protocolo,
        port: protocolo === 'modbus' ? document.getElementById('devPort').value : 161,
        slave_id: protocolo === 'modbus' ? document.getElementById('devSlave').value : 1,
        snmp_port: protocolo === 'snmp' ? document.getElementById('devSnmpPort').value : 161,
        snmp_community: protocolo === 'snmp' ? document.getElementById('devCommunity').value : 'public',
        snmp_version: protocolo === 'snmp' ? parseInt(document.getElementById('devSnmpVersion').value) : 1,
        ups_type: protocolo === 'snmp' ? document.getElementById('devUpsType').value : 'invt_enterprise',
    };

    // ZeroTier fields
    const ipZt = document.getElementById('devIpZt')?.value;
    const portZt = document.getElementById('devSnmpPortZt')?.value;
    const ipLocal = document.getElementById('devIpLocal')?.value;
    const siteId = document.getElementById('devSiteId')?.value;
    if (ipZt) data.ip_zt = ipZt;
    if (portZt) data.snmp_port_zt = parseInt(portZt);
    if (ipLocal) data.ip_local = ipLocal;
    if (siteId) data.site_id = parseInt(siteId);

    fetch('/api/monitoreo/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(r => {
        if (r.ok) location.reload();
        else alert('Error: Verifique parámetros de conexión.');
    });
}

function deleteDevice(id, e) {
    e.stopPropagation();
    if (confirm('¿Eliminar esta configuración de dispositivo?')) {
        fetch(`/api/monitoreo/delete/${id}`, { method: 'DELETE' }).then(() => location.reload());
    }
}

// Auto-fill IP local when site changes
function onSiteChange() {
    const siteSelect = document.getElementById('devSiteId');
    const ipLocalField = document.getElementById('devIpLocal');
    if (!siteSelect || !ipLocalField) return;
    const siteNum = siteSelect.selectedOptions[0]?.getAttribute('data-numero');
    if (siteNum) {
        ipLocalField.value = `192.168.${siteNum}.10`;
    }
}

// Load sites into the dropdown
function loadSitesDropdown() {
    fetch('/api/monitoreo/sites').then(r => r.json()).then(sites => {
        const select = document.getElementById('devSiteId');
        if (!select) return;
        select.innerHTML = '<option value="">-- Sin sitio --</option>';
        sites.forEach(s => {
            select.innerHTML += `<option value="${s.id}" data-numero="${s.numero}">${s.nombre} (${s.numero})</option>`;
        });
    });
}

// === ALARMS (in-memory from WebSocket) ===
function renderAlarms(alarms) {
    const container = document.getElementById('alarmContainer');
    const panel = document.getElementById('alarmPanel');
    const count = document.getElementById('alarmCount');

    if (!alarms || alarms.length === 0) {
        if (container) container.style.display = 'none';
        if (count) count.textContent = '0';
        return;
    }
    if (container) container.style.display = 'block';
    if (count) count.textContent = alarms.length;
    if (panel) {
        panel.innerHTML = '<table class="alarm-table"><thead><tr><th>HORA</th><th>MENSAJE</th><th>NIVEL</th></tr></thead><tbody>';
        alarms.forEach(a => {
            panel.innerHTML += `<tr><td class="font-mono text-muted">${getTimeString()}</td><td>${a.msg}</td><td><span class="badge bg-${a.level === 'critical' ? 'danger' : 'warning'}">${a.level}</span></td></tr>`;
        });
        panel.innerHTML += '</tbody></table>';
    }
}

function renderModules(modules) {
    const container = document.getElementById('modulesContainer');
    const section = document.getElementById('modulesSection');
    if (!modules || modules.length === 0) { if (section) section.style.display = 'none'; return; }
    if (section) section.style.display = 'block';
    if (container) {
        container.innerHTML = '';
        modules.forEach(m => {
            container.innerHTML += `<div class="col-md-6"><div class="eng-panel p-2 mb-0"><div class="d-flex justify-content-between border-bottom border-secondary mb-1"><span class="small text-info">MOD ${m.module_number}</span><span class="small text-muted">${(m.mod_output_voltage_a||0).toFixed(1)}V</span></div></div></div>`;
        });
    }
}

// === STATUS LOG ===
function addStatusLog(message, type = 'info') {
    const timestamp = getTimeString();
    const color = type === 'error' ? '#ff4444' : type === 'warning' ? '#ffaa00' : type === 'success' ? '#00ff88' : '#88aaff';
    const icon = type === 'error' ? '❌' : type === 'warning' ? '⚠️' : type === 'success' ? '✅' : 'ℹ️';
    statusLogMessages.unshift({ time: timestamp, message, type, color, icon });
    if (statusLogMessages.length > MAX_LOG_MESSAGES) statusLogMessages.pop();
    renderStatusLog();
}

function renderStatusLog() {
    const panel = document.getElementById('statusLogPanel');
    if (!panel) return;
    if (statusLogMessages.length === 0) {
        panel.innerHTML = '<div class="text-muted small">Esperando eventos...</div>';
        return;
    }
    panel.innerHTML = statusLogMessages.map(log =>
        `<div style="margin-bottom:0.3rem;color:${log.color};"><span class="text-muted">[${log.time}]</span> ${log.icon} ${log.message}</div>`
    ).join('');
    panel.scrollTop = 0;
}

function clearStatusLog() { statusLogMessages = []; renderStatusLog(); }

function logConnectionStatus(devId, status, data) {
    if (!devId) return;
    const prevStatus = lastDeviceStatus[devId];
    if (prevStatus !== status) {
        if (status === 'online') {
            addStatusLog(`UPS ${devId} ONLINE`, 'success');
        } else {
            addStatusLog(`UPS ${devId} DESCONECTADO`, 'error');
        }
        lastDeviceStatus[devId] = status;
    }
}

// === NETWORK STATUS INDICATOR ===
function updateNetworkStatus() {
    fetch('/api/monitoreo/network-status')
        .then(r => r.json())
        .then(data => {
            const indicator = document.getElementById('networkStatusIndicator');
            if (!indicator) return;
            let html = `ZT: ${data.zerotier?.status === 'ONLINE' ? '✅' : '❌'}`;
            (data.sites || []).forEach(s => {
                html += ` | S${String(s.numero).padStart(2,'0')}: ${s.reachable ? '✅' : '⚠️'}`;
            });
            indicator.textContent = html;
        })
        .catch(() => {});
}

// === WEBSOCKET HANDLER ===
socket.on('ups_update', (data) => {
    // Update device status in sidebar
    const card = document.getElementById(`card-${data.id}`);
    if (card) {
        card.classList.remove('status-online', 'status-offline');
        card.classList.add(data.status === 'online' ? 'status-online' : 'status-offline');
    }

    devices[data.id] = { ...devices[data.id], ...data };
    logConnectionStatus(data.id, data.status, data.data);

    if (currentDevId === data.id && data.data) {
        const d = data.data;

        // Badges
        document.getElementById('currentDevStatus').textContent = data.status === 'online' ? 'EN LINEA' : 'ERROR';
        document.getElementById('currentDevStatus').className = `eng-badge badge-${data.status === 'online' ? 'ok' : 'err'}`;

        // Connection method
        const connBadge = document.getElementById('currentConnMethod');
        if (connBadge) {
            const method = data.connection_method || 'direct';
            connBadge.textContent = method === 'port_forward' ? 'ZT-PORTFWD' : 'DIRECTO';
            connBadge.className = `eng-badge badge-${method === 'port_forward' ? 'info' : 'warn'}`;
        }

        // Phase handling
        const devConfig = devices[data.id];
        const isConfigMono = (devConfig && (devConfig.ups_type === 'invt_minimal' || devConfig.ups_type === 'megatec_snmp'));
        const phases = isConfigMono ? 1 : (d._phases || d.phases || 3);
        const isMono = (phases === 1);

        document.querySelectorAll('.text-l2, .text-l3').forEach(el => {
            if (isMono) el.style.setProperty('display', 'none', 'important');
            else el.style.display = el.classList.contains('mimic-value-row') ? 'flex' : '';
        });

        if (chartVIn && chartVIn.data.datasets.length >= 3) {
            chartVIn.data.datasets[1].hidden = isMono;
            chartVIn.data.datasets[2].hidden = isMono;
            chartVIn.update('none');
        }
        if (chartVOut && chartVOut.data.datasets.length >= 3) {
            chartVOut.data.datasets[1].hidden = isMono;
            chartVOut.data.datasets[2].hidden = isMono;
            chartVOut.update('none');
        }

        // Data mapping
        setTxt('val_vin_l1', d.voltaje_in_l1); setTxt('val_vin_l2', d.voltaje_in_l2); setTxt('val_vin_l3', d.voltaje_in_l3);
        setTxt('val_freq_in', d.frecuencia_in);
        setTxt('val_vout_l1', d.voltaje_out_l1); setTxt('val_vout_l2', d.voltaje_out_l2); setTxt('val_vout_l3', d.voltaje_out_l3);
        setTxt('val_iout_l1', d.corriente_out_l1); setTxt('val_iout_l2', d.corriente_out_l2); setTxt('val_iout_l3', d.corriente_out_l3);
        setTxt('val_pf', d.power_factor); setTxt('val_pwr_active', d.active_power); setTxt('val_pwr_apparent', d.apparent_power);
        setTxt('val_remain_time', d.battery_remain_time);

        const bPct = d.bateria_pct || 0;
        setTxt('val_bat', bPct); setTxt('val_vbat', d.voltaje_bateria); setTxt('val_ibat', d.corriente_bateria); setTxt('val_temp', d.temperatura);

        const progBat = document.getElementById('prog_bat');
        if (progBat) {
            progBat.style.width = `${bPct}%`;
            progBat.className = `progress-bar bg-${bPct < 30 ? 'danger' : (bPct < 70 ? 'warning' : 'success')}`;
        }

        setTxt('val_load', d.carga_pct || 0);

        // Environment
        if (d.env_temperature || d.env_humidity) {
            const envSec = document.getElementById('envSection');
            if (envSec) envSec.style.display = 'block';
            setTxt('val_env_temp', d.env_temperature); setTxt('val_env_hum', d.env_humidity);
            const wlEl = document.getElementById('val_water_leak');
            if (wlEl) {
                const wl = d.water_leak || 0;
                wlEl.textContent = wl > 0 ? 'FUGA DETECTADA' : 'SECO';
                wlEl.style.color = wl > 0 ? 'var(--status-err)' : 'var(--status-ok)';
            }
        }

        if (d.modules) renderModules(d.modules);
        renderAlarms(data.alarms || []);

        // In-memory history for charts
        if (!devices[data.id].history) {
            try { const saved = sessionStorage.getItem(`ups_hist_${data.id}`); if (saved) devices[data.id].history = JSON.parse(saved); } catch(e) {}
            if (!devices[data.id].history) {
                devices[data.id].history = { labels: [], vInL1: [], vInL2: [], vInL3: [], vOutL1: [], vOutL2: [], vOutL3: [], freqIn: [], freqOut: [], temp: [], envTemp: [] };
            }
        }
        const hist = devices[data.id].history;
        const timeStr = getTimeString();
        const MAX_POINTS = 50;
        const addPoint = (arr, val) => { arr.push(val); if (arr.length > MAX_POINTS) arr.shift(); };
        addPoint(hist.labels, timeStr);
        addPoint(hist.vInL1, d.voltaje_in_l1); addPoint(hist.vInL2, d.voltaje_in_l2); addPoint(hist.vInL3, d.voltaje_in_l3);
        addPoint(hist.vOutL1, d.voltaje_out_l1); addPoint(hist.vOutL2, d.voltaje_out_l2); addPoint(hist.vOutL3, d.voltaje_out_l3);
        addPoint(hist.freqIn, d.frecuencia_in); addPoint(hist.freqOut, d.frecuencia_out);
        addPoint(hist.temp, d.temperatura); addPoint(hist.envTemp, d.env_temperature || 0);

        if (currentDevId === data.id) {
            if (chartVIn) pushChartData(chartVIn, timeStr, [d.voltaje_in_l1, d.voltaje_in_l2, d.voltaje_in_l3]);
            if (chartVOut) pushChartData(chartVOut, timeStr, [d.voltaje_out_l1, d.voltaje_out_l2, d.voltaje_out_l3]);
            if (chartFreq) pushChartData(chartFreq, timeStr, [d.frecuencia_in, d.frecuencia_out]);
            if (chartTemp) pushChartData(chartTemp, timeStr, [d.temperatura, d.env_temperature || 0]);
        }
    }
});

// === MARQUEE ===
const statusMessages = [
    "SISTEMA NOMINAL", "ENLACE DE DATOS ESTABLE", "ENCRIPTACIÓN: AES-256",
    "ESPERANDO HEARTBEAT...", "VERIFICANDO REDUNDANCIA...", "SALUD DE BATERÍA: OK",
    "FRECUENCIA DE RED ESTABLE", "SISTEMA DE ENFRIAMIENTO ACTIVO"
];
setInterval(() => {
    const marquee = document.getElementById('sys-status-marquee');
    if (marquee) {
        const msg = statusMessages[Math.floor(Math.random() * statusMessages.length)];
        const time = getTimeString();
        const linkStatus = currentDevId ? (devices[currentDevId]?.status === 'online' ? 'CONECTADO' : 'SIN CONEXIÓN') : 'ESPERA';
        marquee.textContent = `HORA DEL SISTEMA: ${time} | ESTADO: ${msg} | MONITOREO ACTIVO | ENLACE UPS: ${linkStatus}`;
    }
}, 5000);

// === CLOCK ===
setInterval(() => {
    const el = document.getElementById('clock');
    if (el) {
        const now = new Date();
        el.textContent = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
    }
    const dateEl = document.getElementById('date');
    if (dateEl) {
        const now = new Date();
        dateEl.textContent = now.toISOString().slice(0, 10);
    }
}, 1000);

// === SESSION PERSISTENCE ===
window.addEventListener('beforeunload', () => {
    Object.keys(devices).forEach(id => {
        if (devices[id].history) {
            try { sessionStorage.setItem(`ups_hist_${id}`, JSON.stringify(devices[id].history)); } catch(e) {}
        }
    });
});

// === INIT ===
initCharts();
loadDeviceList();
loadSitesDropdown();
updateNetworkStatus();
setInterval(updateNetworkStatus, 60000);
