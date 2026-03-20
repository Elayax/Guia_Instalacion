/**
 * LBS Monitor — Topología de Red
 * Diagrama visual + inventario editable in-place
 */

let topoData = null;
let sitesCache = [];

// === INIT ===
document.addEventListener('DOMContentLoaded', () => {
    refreshTopology();
    loadSitesForModal();
    setInterval(refreshTopology, 60000);
});

// === CLOCK ===
setInterval(() => {
    const now = new Date();
    const cl = document.getElementById('clock');
    const dt = document.getElementById('date');
    if (cl) cl.textContent = now.toLocaleTimeString('es-MX', { hour12: false });
    if (dt) dt.textContent = now.toLocaleDateString('es-MX');
}, 1000);

// === FETCH TOPOLOGY ===
async function refreshTopology() {
    try {
        const res = await fetch('/api/monitoreo/topology');
        if (!res.ok) throw new Error(res.statusText);
        topoData = await res.json();
        renderDiagram(topoData);
        renderInventory(topoData);
        updateNetworkBadge(topoData);
    } catch (e) {
        console.error('Error loading topology:', e);
    }
}

// === NETWORK STATUS BADGE ===
function updateNetworkBadge(data) {
    const el = document.getElementById('networkStatusIndicator');
    if (!el) return;
    const zt = data.servidor?.zerotier?.status || 'UNKNOWN';
    const ztOk = zt === 'ONLINE';
    const siteParts = (data.sites || []).map(s => {
        const ok = s.devices?.some(d => d.fail_count === 0);
        return `S${String(s.numero).padStart(2,'0')}: ${ok ? '\u2705' : '\u26a0\ufe0f'}`;
    });
    el.innerHTML = `ZT: ${ztOk ? '\u2705' : '\u274c'} ${siteParts.length ? '| ' + siteParts.join(' | ') : ''}`;
}

// === RENDER DIAGRAM ===
function renderDiagram(data) {
    const container = document.getElementById('topoDiagram');
    if (!container) return;

    const srv = data.servidor || {};
    const sites = data.sites || [];
    const unassigned = data.unassigned_devices || [];

    let html = '';

    // Server node
    html += `<div class="topo-server">
        <i class="bi bi-server me-1"></i> SERVIDOR
        <div style="font-size:0.7rem; color:#94a3b8;">${srv.ip || '10.216.124.126'}</div>
        <div style="font-size:0.65rem; color:${srv.zerotier?.status === 'ONLINE' ? '#22c55e' : '#ef4444'}">
            ZT: ${srv.zerotier?.status || 'UNKNOWN'} ${srv.zerotier?.node_id ? '(' + srv.zerotier.node_id + ')' : ''}
        </div>
    </div>`;

    // Vertical line
    html += '<div class="topo-line"></div>';
    html += '<div class="topo-zt-label">ZEROTIER 10.216.124.0/24</div>';
    html += '<div class="topo-line"></div>';

    // Sites row
    html += '<div class="topo-sites-row">';
    for (const site of sites) {
        const devs = site.devices || [];
        const hasOnline = devs.some(d => d.fail_count === 0);
        const allOff = devs.length > 0 && devs.every(d => d.fail_count > 0);
        const stateClass = devs.length === 0 ? '' : (hasOnline ? 'reachable' : 'unreachable');

        html += `<div class="topo-site-col">`;
        html += `<div class="topo-site-node ${stateClass}" onclick="toggleSiteBody(${site.id})">
            <div><i class="bi bi-building me-1"></i>${escHtml(site.nombre)}</div>
            <div style="font-size:0.7rem; color:#94a3b8;">${escHtml(site.ip_zt_router || '--')}</div>
        </div>`;

        // Devices under site
        for (const dev of devs) {
            const online = dev.fail_count === 0;
            html += `<div class="topo-device-node ${online ? 'online' : 'offline'}">
                <div>${escHtml(dev.nombre || 'UPS')}</div>
                <div>${escHtml(dev.ip_local || dev.ip || '--')}</div>
            </div>`;
        }
        html += '</div>';
    }

    // Unassigned devices
    if (unassigned.length > 0) {
        html += `<div class="topo-site-col">`;
        html += `<div class="topo-site-node" style="border-style:dashed;">
            <div><i class="bi bi-question-circle me-1"></i>SIN SITIO</div>
        </div>`;
        for (const dev of unassigned) {
            const online = dev.fail_count === 0;
            html += `<div class="topo-device-node ${online ? 'online' : 'offline'}">
                <div>${escHtml(dev.nombre || 'UPS')}</div>
                <div>${escHtml(dev.ip || '--')}</div>
            </div>`;
        }
        html += '</div>';
    }

    // Add site button
    html += `<div class="topo-site-col">
        <div class="topo-add-btn" data-bs-toggle="modal" data-bs-target="#addSiteModal">
            <i class="bi bi-plus-lg"></i><br>AGREGAR<br>SITIO
        </div>
    </div>`;

    html += '</div>'; // end topo-sites-row
    container.innerHTML = html;
}

// === RENDER INVENTORY ===
function renderInventory(data) {
    const panel = document.getElementById('inventoryPanel');
    if (!panel) return;

    const sites = data.sites || [];
    const unassigned = data.unassigned_devices || [];
    let html = '';

    for (const site of sites) {
        html += renderSiteAccordion(site);
    }

    if (unassigned.length > 0) {
        html += renderSiteAccordion({
            id: null, nombre: 'Sin Sitio Asignado', numero: '--',
            ip_zt_router: '--', subnet: '--', gateway: '--',
            devices: unassigned
        });
    }

    if (sites.length === 0 && unassigned.length === 0) {
        html = '<div class="text-muted text-center py-4">No hay sitios ni dispositivos registrados.</div>';
    }

    panel.innerHTML = html;
}

function renderSiteAccordion(site) {
    const devs = site.devices || [];
    const siteId = site.id;
    const editable = siteId !== null;

    let html = `<div class="mb-2">`;

    // Site header
    html += `<div class="site-header" onclick="this.nextElementSibling.classList.toggle('open')">
        <div>
            <span class="site-name"><i class="bi bi-building me-2"></i>${escHtml(site.nombre)}</span>
            <span class="site-meta ms-3">
                #${site.numero} | Router: ${escHtml(site.ip_zt_router || '--')} | Subnet: ${escHtml(site.subnet || '--')} | GW: ${escHtml(site.gateway || '--')}
            </span>
        </div>
        <div class="d-flex align-items-center gap-2">
            <span class="badge bg-secondary">${devs.length} UPS</span>
            ${editable ? `<button class="btn btn-sm btn-outline-danger" style="font-size:0.6rem;" onclick="event.stopPropagation(); deleteSite(${siteId})"><i class="bi bi-trash"></i></button>` : ''}
            <i class="bi bi-chevron-down"></i>
        </div>
    </div>`;

    // Site body
    html += `<div class="site-body">`;

    // Site details (editable row)
    if (editable) {
        html += `<div class="mb-2 px-2" style="font-size:0.7rem;">
            <span class="text-muted">DATOS DEL SITIO:</span>
            <table class="topo-table mt-1"><thead><tr>
                <th>NOMBRE</th><th>NÚMERO</th><th>IP ZT ROUTER</th><th>SUBNET</th><th>GATEWAY</th><th>ROUTER NODE ID</th>
            </tr></thead><tbody><tr>
                <td class="editable" onclick="editCell(this,'site',${siteId},'nombre')">${escHtml(site.nombre)}</td>
                <td class="editable" onclick="editCell(this,'site',${siteId},'numero')">${site.numero}</td>
                <td class="editable" onclick="editCell(this,'site',${siteId},'ip_zt_router')">${escHtml(site.ip_zt_router || '')}</td>
                <td class="editable" onclick="editCell(this,'site',${siteId},'subnet')">${escHtml(site.subnet || '')}</td>
                <td class="editable" onclick="editCell(this,'site',${siteId},'gateway')">${escHtml(site.gateway || '')}</td>
                <td class="editable" onclick="editCell(this,'site',${siteId},'router_node_id')">${escHtml(site.router_node_id || '')}</td>
            </tr></tbody></table>
        </div>`;
    }

    // Devices table
    if (devs.length > 0) {
        html += `<table class="topo-table"><thead><tr>
            <th>NOMBRE</th><th>IP</th><th>IP ZT</th><th>IP LOCAL</th><th>PTO ZT</th>
            <th>PROTOCOLO</th><th>COMMUNITY</th><th>TIPO UPS</th><th>SNMP VER</th>
            <th>MAC</th><th>MARCA</th><th>ESTADO</th><th>MÉTODO</th><th>ÚLTIMA VEZ</th><th>ACCIONES</th>
        </tr></thead><tbody>`;

        for (const dev of devs) {
            const online = dev.fail_count === 0;
            const statusBadge = online
                ? '<span class="badge bg-success">ONLINE</span>'
                : '<span class="badge bg-danger">OFFLINE</span>';

            html += `<tr>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'nombre')">${escHtml(dev.nombre || '')}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'ip')">${escHtml(dev.ip || '')}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'ip_zt')">${escHtml(dev.ip_zt || '')}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'ip_local')">${escHtml(dev.ip_local || '')}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'snmp_port_zt')">${dev.snmp_port_zt || ''}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'protocolo')">${escHtml(dev.protocolo || '')}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'snmp_community')">${escHtml(dev.snmp_community || '')}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'ups_type')">${escHtml(dev.ups_type || '')}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'snmp_version')">${dev.snmp_version ?? ''}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'mac_address')">${escHtml(dev.mac_address || '')}</td>
                <td class="editable" onclick="editCell(this,'device',${dev.id},'brand')">${escHtml(dev.brand || '')}</td>
                <td>${statusBadge}</td>
                <td>${escHtml(dev.connection_method || '--')}</td>
                <td style="font-size:0.65rem;">${dev.last_seen ? new Date(dev.last_seen).toLocaleString('es-MX') : '--'}</td>
                <td>
                    <div class="d-flex gap-1">
                        <button class="btn btn-outline-info btn-sm" style="font-size:0.55rem; padding:1px 4px;" onclick="testDevConnection(${dev.id},'${escAttr(dev.ip || '')}')">PING</button>
                        <button class="btn btn-outline-warning btn-sm" style="font-size:0.55rem; padding:1px 4px;" onclick="discoverOids(${dev.id},'${escAttr(dev.ip || '')}')">OID</button>
                        <button class="btn btn-outline-danger btn-sm" style="font-size:0.55rem; padding:1px 4px;" onclick="deleteDevice(${dev.id})"><i class="bi bi-trash"></i></button>
                    </div>
                </td>
            </tr>`;
        }
        html += '</tbody></table>';
    } else {
        html += '<div class="text-muted text-center py-2" style="font-size:0.75rem;">Sin dispositivos en este sitio.</div>';
    }

    html += '</div></div>';
    return html;
}

// === IN-PLACE EDITING ===
function editCell(td, type, id, field) {
    if (td.querySelector('input')) return; // already editing

    const original = td.textContent.trim();
    const input = document.createElement('input');
    input.type = 'text';
    input.value = original;
    td.textContent = '';
    td.appendChild(input);
    input.focus();
    input.select();

    const save = async () => {
        const newVal = input.value.trim();
        td.textContent = newVal || original;

        if (newVal === original) return;

        const url = type === 'site'
            ? `/api/monitoreo/sites/${id}`
            : `/api/monitoreo/${id}`;

        try {
            const body = {};
            // Convert numeric fields
            if (['numero', 'snmp_port_zt', 'snmp_version', 'snmp_port', 'modbus_port'].includes(field)) {
                body[field] = parseInt(newVal) || 0;
            } else {
                body[field] = newVal;
            }

            const res = await fetch(url, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            if (res.ok) {
                td.classList.add('edit-ok');
                setTimeout(() => td.classList.remove('edit-ok'), 600);
            } else {
                td.textContent = original;
                td.classList.add('edit-err');
                setTimeout(() => td.classList.remove('edit-err'), 600);
            }
        } catch {
            td.textContent = original;
            td.classList.add('edit-err');
            setTimeout(() => td.classList.remove('edit-err'), 600);
        }
    };

    input.addEventListener('blur', save);
    input.addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); input.blur(); }
        if (e.key === 'Escape') { td.textContent = original; }
    });
}

// === SITE CRUD ===
async function addSite() {
    const data = {
        nombre: document.getElementById('siteNombre').value.trim(),
        numero: parseInt(document.getElementById('siteNumero').value) || 0,
        ip_zt_router: document.getElementById('siteIpZt').value.trim(),
        subnet: document.getElementById('siteSubnet').value.trim(),
        gateway: document.getElementById('siteGateway').value.trim(),
        router_node_id: document.getElementById('siteNodeId').value.trim(),
    };

    if (!data.nombre || !data.numero) {
        alert('Nombre y Número son requeridos');
        return;
    }

    try {
        const res = await fetch('/api/monitoreo/sites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('addSiteModal'))?.hide();
            refreshTopology();
            loadSitesForModal();
        } else {
            const err = await res.json();
            alert(err.error || 'Error agregando sitio');
        }
    } catch (e) {
        alert('Error de red: ' + e.message);
    }
}

async function deleteSite(siteId) {
    if (!confirm('Eliminar este sitio? Los UPS se quedarán sin sitio asignado.')) return;
    try {
        await fetch(`/api/monitoreo/sites/${siteId}`, { method: 'DELETE' });
        refreshTopology();
    } catch (e) {
        alert('Error eliminando sitio');
    }
}

// === DEVICE CRUD ===
async function addDeviceFromTopology() {
    const data = {
        nombre: document.getElementById('newDevName').value.trim(),
        ip: document.getElementById('newDevIp').value.trim(),
        ip_zt: document.getElementById('newDevIpZt').value.trim(),
        ip_local: document.getElementById('newDevIpLocal').value.trim(),
        protocolo: document.getElementById('newDevProtocolo').value,
        snmp_port_zt: parseInt(document.getElementById('newDevPortZt').value) || 10161,
        snmp_community: document.getElementById('newDevCommunity').value.trim() || 'public',
        ups_type: document.getElementById('newDevUpsType').value,
        site_id: parseInt(document.getElementById('newDevSiteId').value) || null,
    };

    if (!data.ip && !data.ip_zt) {
        alert('Se requiere al menos una IP (directa o ZT)');
        return;
    }

    try {
        const res = await fetch('/api/monitoreo/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('addDeviceModal'))?.hide();
            refreshTopology();
        } else {
            const err = await res.json();
            alert(err.error || 'Error agregando UPS');
        }
    } catch (e) {
        alert('Error de red: ' + e.message);
    }
}

async function deleteDevice(devId) {
    if (!confirm('Eliminar este UPS del inventario?')) return;
    try {
        await fetch(`/api/monitoreo/delete/${devId}`, { method: 'DELETE' });
        refreshTopology();
    } catch (e) {
        alert('Error eliminando dispositivo');
    }
}

// === LOAD SITES FOR DEVICE MODAL ===
async function loadSitesForModal() {
    try {
        const res = await fetch('/api/monitoreo/sites');
        sitesCache = await res.json();
        const sel = document.getElementById('newDevSiteId');
        if (!sel) return;
        sel.innerHTML = '<option value="">-- Sin sitio --</option>';
        for (const s of sitesCache) {
            sel.innerHTML += `<option value="${s.id}">${escHtml(s.nombre)} (#${s.numero})</option>`;
        }
    } catch (e) {
        console.error('Error loading sites:', e);
    }
}

// === TEST CONNECTION ===
async function testConnection() {
    const ip = document.getElementById('newDevIp').value.trim() || document.getElementById('newDevIpZt').value.trim();
    if (!ip) { alert('Ingresa una IP primero'); return; }
    await _doDiscover(ip);
}

async function testDevConnection(devId, ip) {
    if (!ip) { alert('Dispositivo sin IP configurada'); return; }
    await _doDiscover(ip);
}

async function discoverOids(devId, ip) {
    if (!ip) { alert('Dispositivo sin IP configurada'); return; }
    await _doDiscover(ip);
}

async function _doDiscover(ip) {
    try {
        const res = await fetch('/api/monitoreo/discover', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip })
        });
        const data = await res.json();
        if (res.ok) {
            const oids = data.oids_found || [];
            const type = data.recommended_type || 'unknown';
            alert(`Resultado para ${ip}:\nTipo recomendado: ${type}\nOIDs encontrados: ${oids.length}\n\n${oids.slice(0, 10).map(o => o.oid + ' = ' + o.value).join('\n')}`);
        } else {
            alert(`Error: ${data.error || 'Sin respuesta'}`);
        }
    } catch (e) {
        alert('Error de conexión: ' + e.message);
    }
}

// === HELPERS ===
function escHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function escAttr(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function toggleSiteBody(siteId) {
    // Toggle accordion in inventory for matching site
    // This is handled by onclick on site-header in inventory
}
