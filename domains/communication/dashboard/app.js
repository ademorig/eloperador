/**
 * El Operador - Dashboard Application
 * Read-only dashboard, no actions, only observation
 */

const API_BASE = '/api';
const REFRESH_INTERVAL = 30000; // 30 seconds

// DOM Elements
const elements = {
    statusBadge: document.getElementById('status-badge'),
    statusText: document.querySelector('.status-text'),
    lastHeartbeat: document.getElementById('last-heartbeat'),
    observationsCount: document.getElementById('observations-count'),
    runsCount: document.getElementById('runs-count'),
    memoryEntries: document.getElementById('memory-entries'),
    observationsList: document.getElementById('observations-list'),
    runsList: document.getElementById('runs-list'),
    acceptanceBar: document.getElementById('acceptance-bar'),
    acceptanceRate: document.getElementById('acceptance-rate'),
    statAccepted: document.getElementById('stat-accepted'),
    statRejected: document.getElementById('stat-rejected'),
    statDeferred: document.getElementById('stat-deferred'),
    statModified: document.getElementById('stat-modified'),
    refreshTime: document.getElementById('refresh-time')
};

/**
 * Fetch data from API endpoint
 */
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

/**
 * Format relative time
 */
function formatRelativeTime(isoString) {
    if (!isoString) return '--';

    const date = new Date(isoString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return `hace ${diff}s`;
    if (diff < 3600) return `hace ${Math.floor(diff / 60)}m`;
    if (diff < 86400) return `hace ${Math.floor(diff / 3600)}h`;
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' });
}

/**
 * Format short time
 */
function formatShortTime(isoString) {
    if (!isoString) return '--';
    const date = new Date(isoString);
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
}

/**
 * Update status section
 */
async function updateStatus() {
    const data = await fetchAPI('/status');

    if (data && data.status === 'alive') {
        elements.statusBadge.className = 'status-badge alive';
        elements.statusText.textContent = 'Activo';
        elements.lastHeartbeat.textContent = formatRelativeTime(data.last_heartbeat);
    } else {
        elements.statusBadge.className = 'status-badge error';
        elements.statusText.textContent = 'Sin conexión';
        elements.lastHeartbeat.textContent = '--';
    }
}

/**
 * Update observations section
 */
async function updateObservations() {
    const data = await fetchAPI('/observations');

    if (!data) {
        elements.observationsCount.textContent = '--';
        return;
    }

    elements.observationsCount.textContent = data.count.toString();

    if (data.recent && data.recent.length > 0) {
        elements.observationsList.innerHTML = data.recent.map(obs => {
            const decisionClass =
                obs.decision_usuario === 'sí' ? 'accepted' :
                    obs.decision_usuario === 'no' ? 'rejected' : 'deferred';

            const decisionLabel =
                obs.decision_usuario === 'sí' ? '✓ Sí' :
                    obs.decision_usuario === 'no' ? '✗ No' :
                        obs.decision_usuario === 'después' ? '⏳ Después' : '✏️ Mod';

            return `
                <div class="observation-item">
                    <div class="observation-context">${escapeHtml(obs.propuesta || obs.contexto || 'Sin contexto')}</div>
                    <div class="observation-meta">
                        <span>${formatRelativeTime(obs.timestamp)}</span>
                        <span class="observation-decision ${decisionClass}">${decisionLabel}</span>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        elements.observationsList.innerHTML = '<div class="empty-state">Sin observaciones aún</div>';
    }
}

/**
 * Update runs section
 */
async function updateRuns() {
    const data = await fetchAPI('/runs');

    if (!data) {
        elements.runsCount.textContent = '--';
        return;
    }

    elements.runsCount.textContent = data.total_runs.toString();

    if (data.history && data.history.length > 0) {
        elements.runsList.innerHTML = data.history.map(run => `
            <div class="run-item">
                <div class="run-status ${run.status}"></div>
                <div class="run-info">
                    <div class="run-context">${escapeHtml(run.context || 'Ejecución')}</div>
                    <div class="run-time">${formatShortTime(run.timestamp)}</div>
                </div>
            </div>
        `).join('');
    } else {
        elements.runsList.innerHTML = '<div class="empty-state">Sin ejecuciones aún</div>';
    }
}

/**
 * Update memory section
 */
async function updateMemory() {
    const data = await fetchAPI('/memory');

    if (!data) {
        elements.memoryEntries.textContent = '--';
        return;
    }

    elements.memoryEntries.textContent = data.total_entries.toString();

    // Update acceptance rate
    const rate = data.acceptance_rate || 0;
    elements.acceptanceBar.style.width = `${rate}%`;
    elements.acceptanceRate.textContent = `${rate}%`;

    // Update stats
    const stats = data.statistics || {};
    elements.statAccepted.textContent = stats.accepted || 0;
    elements.statRejected.textContent = stats.rejected || 0;
    elements.statDeferred.textContent = stats.deferred || 0;
    elements.statModified.textContent = stats.modified || 0;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Update refresh timestamp
 */
function updateRefreshTime() {
    const now = new Date();
    elements.refreshTime.textContent = `Actualizado: ${now.toLocaleTimeString('es-ES')}`;
}

/**
 * Refresh all dashboard data
 */
async function refreshDashboard() {
    await Promise.all([
        updateStatus(),
        updateObservations(),
        updateRuns(),
        updateMemory()
    ]);
    updateRefreshTime();
}

/**
 * Initialize dashboard
 */
async function init() {
    console.log('⚙️ El Operador Dashboard - Initializing...');

    // Initial load
    await refreshDashboard();

    // Set up auto-refresh
    setInterval(refreshDashboard, REFRESH_INTERVAL);

    console.log('✓ Dashboard ready');
}

// Start when DOM is ready
document.addEventListener('DOMContentLoaded', init);
