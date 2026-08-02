// 57R337 $M4R7 NYC — Application JavaScript
(function() {
  'use strict';

  // CSRF token from the meta tag injected by base.html (API POSTs need it).
  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  // Toast notification system (appends to #toast-container from components/toast.html)
  function showToast(message, type) {
    type = type || 'info';
    var toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    var container = document.getElementById('toast-container');
    if (container) { container.appendChild(toast); }
    else { document.body.appendChild(toast); }
    setTimeout(function() { toast.remove(); }, 3000);
  }

  // Upload zone drag-and-drop. The zone targets its file input via data-input.
  function initUploadZones() {
    var zones = document.querySelectorAll('.upload-zone');
    zones.forEach(function(zone) {
      zone.addEventListener('dragover', function(e) {
        e.preventDefault();
        zone.classList.add('dragover');
      });
      zone.addEventListener('dragleave', function() {
        zone.classList.remove('dragover');
      });
      zone.addEventListener('drop', function(e) {
        e.preventDefault();
        zone.classList.remove('dragover');
        var files = e.dataTransfer.files;
        var input = zone.dataset.input
          ? document.getElementById(zone.dataset.input)
          : null;
        if (files.length > 0) {
          if (input) { input.files = files; }
          showToast('File staged: ' + files[0].name, 'info');
        }
      });
    });
  }

  // Upload forms: submit via fetch so the user stays on the flight deck
  // instead of landing on a raw JSON response. Form needs data-upload="true".
  function initUploadForms() {
    var forms = document.querySelectorAll('form[data-upload="true"]');
    forms.forEach(function(form) {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        var data = new FormData(form);
        fetch(form.action, {
          method: 'POST',
          body: data,
          headers: { 'X-CSRFToken': csrfToken() }
        })
          .then(function(resp) {
            return resp.json().then(function(json) {
              return { ok: resp.ok, json: json };
            });
          })
          .then(function(res) {
            if (res.ok) {
              showToast('Uploaded: ' + (res.json.original_name || 'file'), 'success');
              setTimeout(function() { location.reload(); }, 600);
            } else {
              showToast('Upload failed: ' + (res.json.error || 'unknown error'), 'error');
            }
          })
          .catch(function() {
            showToast('Upload failed — network error', 'error');
          });
      });
    });
  }

  // Live system telemetry: websocket first, /api/health polling as fallback.
  // Updates [data-metric-bar]/[data-metric-value] from health_panel.html.
  function updateHealthPanel(metrics) {
    Object.keys(metrics).forEach(function(key) {
      var value = metrics[key];
      var bar = document.querySelector('[data-metric-bar="' + key + '"]');
      var label = document.querySelector('[data-metric-value="' + key + '"]');
      if (bar) { bar.style.width = value + '%'; }
      if (label) { label.textContent = value + '%'; }
    });
  }

  function pollMetrics() {
    fetch('/api/health', { headers: { 'Accept': 'application/json' } })
      .then(function(resp) { return resp.json(); })
      .then(function(data) {
        if (data && data.metrics) { updateHealthPanel(data.metrics); }
      })
      .catch(function() { /* keep the last known values */ });
  }

  function initLiveMetrics() {
    var link = document.querySelector('[data-metric-link]');
    if (!link) { return; } // no health panel on this page
    if (typeof io === 'undefined') {
      link.textContent = 'polling: /api/health';
      pollMetrics();
      return;
    }
    var socket = io();
    socket.on('connect', function() { socket.emit('system:get'); });
    socket.on('system', function(data) {
      updateHealthPanel(data);
      link.textContent = 'websocket: live';
    });
    socket.on('connect_error', function() {
      link.textContent = 'polling: /api/health';
      pollMetrics();
    });
    // Safety net: if the socket never delivers, keep the panel fresh anyway.
    setInterval(pollMetrics, 10000);
  }

  // Confirm dialogs (components/modal_confirm.html): data-modal-open / -close.
  function initModals() {
    document.querySelectorAll('[data-modal-open]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var modal = document.getElementById(btn.getAttribute('data-modal-open'));
        if (modal) { modal.classList.remove('hidden'); modal.classList.add('flex'); }
      });
    });
    document.querySelectorAll('[data-modal-close]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var modal = document.getElementById(btn.getAttribute('data-modal-close'));
        if (modal) { modal.classList.add('hidden'); modal.classList.remove('flex'); }
      });
    });
  }

  // Notification rows: data-notif-read="<id>" and data-notif-read-all.
  function initNotificationActions() {
    document.querySelectorAll('[data-notif-read]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var id = btn.getAttribute('data-notif-read');
        fetch('/api/notifications/' + id + '/read', {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken() }
        }).then(function(resp) {
          if (resp.ok) { location.reload(); }
        });
      });
    });
    var readAll = document.querySelector('[data-notif-read-all]');
    if (readAll) {
      readAll.addEventListener('click', function() {
        fetch('/api/notifications/read-all', {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken() }
        }).then(function(resp) {
          if (resp.ok) { location.reload(); }
        });
      });
    }
  }

  // Status color helper (9 campaign states -> status hue key)
  function statusColor(status) {
    var colors = {
      'not_started': 'gray', 'preparing': 'blue', 'connecting': 'cyan',
      'running': 'green', 'waiting': 'yellow', 'retrying': 'orange',
      'transferring': 'purple', 'failed': 'red', 'finished': 'white'
    };
    return colors[status] || 'gray';
  }

  // Progress bar animation
  function animateProgress(bar, targetPercent) {
    bar.style.width = targetPercent + '%';
  }

  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', function() {
    initUploadZones();
    initUploadForms();
    initLiveMetrics();
    initModals();
    initNotificationActions();
    initMissionControl();
  });

  // Mission Control: listen for campaign events via WebSocket
  function initMissionControl() {
    var mcPanel = document.getElementById('mc-event-feed');
    if (!mcPanel) return;
    if (typeof io === 'undefined') return;

    var socket = io();
    socket.on('connect', function() {
      // Join the campaign room if a run_id is available
      var runId = mcPanel.getAttribute('data-run-id');
      if (runId) {
        socket.emit('join', { run_id: parseInt(runId) });
      }
    });

    socket.on('campaign_event', function(data) {
      // Add event to the feed
      var li = document.createElement('li');
      li.className = 'flex items-start gap-2 text-body-md';
      var time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      var color = data.level === 'success' ? 'green' : data.level === 'error' ? 'red' : data.level === 'warning' ? 'yellow' : 'cyan';
      var icon = data.action === 'finished' ? 'check_circle' : data.action === 'stopped' ? 'stop' : data.action === 'paused' ? 'pause' : data.action === 'launched' ? 'rocket_launch' : 'phone';
      li.innerHTML = '<span class="mt-1 w-2 h-2 rounded-full shrink-0 bg-status-' + color + '"></span>' +
        '<span class="font-mono text-label-sm text-label-sm text-outline shrink-0">' + time + '</span>' +
        '<span class="text-on-surface">' + (data.message || data.action || '') + '</span>';
      mcPanel.insertBefore(li, mcPanel.firstChild);
      while (mcPanel.children.length > 50) {
        mcPanel.removeChild(mcPanel.lastChild);
      }

      // Update progress pipeline if status counts provided
      if (data.action === 'tick' && data.status_counts) {
        updatePipeline(data.status_counts);
      }

      // Update call detail table
      if (data.action === 'call_stage' && data.call_id) {
        updateCallRow(data);
      }

      // Update counters on finish
      if (data.action === 'finished' && data.counters) {
        updateCounters(data.counters);
      }
    });
  }

  function updatePipeline(statusCounts) {
    var pipeline = document.getElementById('mc-pipeline');
    if (!pipeline) return;
    var bars = pipeline.querySelectorAll('[data-stage]');
    bars.forEach(function(bar) {
      var stage = bar.getAttribute('data-stage');
      var count = statusCounts[stage] || 0;
      var total = parseInt(bar.getAttribute('data-total')) || 1;
      var pct = Math.round((count / total) * 100);
      var fill = bar.querySelector('.progress-fill');
      var countEl = bar.querySelector('.progress-count');
      if (fill) fill.style.width = pct + '%';
      if (countEl) countEl.textContent = count;
    });
  }

  function updateCallRow(data) {
    var table = document.getElementById('mc-call-table');
    if (!table) return;
    var row = document.getElementById('call-row-' + data.call_id);
    if (!row) {
      row = document.createElement('tr');
      row.id = 'call-row-' + data.call_id;
      row.className = 'hover:bg-primary/5 transition-colors';
      row.innerHTML =
        '<td class="px-4 py-2 font-mono text-label-sm text-on-surface">' + (data.contact_phone || '—') + '</td>' +
        '<td class="px-4 py-2 text-center"><span class="border border-primary/40 text-primary px-2 py-0.5 rounded text-[10px] uppercase">' + (data.stage || '—') + '</span></td>' +
        '<td class="px-4 py-2 text-center text-on-surface">—</td>' +
        '<td class="px-4 py-2 text-center font-mono text-label-sm text-on-surface">—</td>';
      table.appendChild(row);
    } else {
      var cells = row.querySelectorAll('td');
      if (cells[1]) cells[1].innerHTML = '<span class="border border-primary/40 text-primary px-2 py-0.5 rounded text-[10px] uppercase">' + (data.stage || '—') + '</span>';
      if (cells[2] && data.outcome) cells[2].innerHTML = '<span class="text-on-surface">' + data.outcome + '</span>';
    }
  }

  function updateCounters(counters) {
    var countEl = document.getElementById('mc-call-count');
    if (countEl) countEl.textContent = counters.total + ' calls';
  }

  // Export for global use
  window.StreetSmart = {
    showToast: showToast,
    statusColor: statusColor,
    animateProgress: animateProgress
  };
})();
