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
  });

  // Export for global use
  window.StreetSmart = {
    showToast: showToast,
    statusColor: statusColor,
    animateProgress: animateProgress
  };
})();
