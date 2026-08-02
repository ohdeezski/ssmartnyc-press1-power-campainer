"""SocketIO event handlers — live host telemetry for the Mission Control shell.

The dashboard health panel subscribes to the ``system`` event (sent on
connect and on request). Metrics are collected with the standard library only
— no extra runtime dependencies.
"""

import os
import shutil

from app.extensions import socketio


def collect_system_metrics():
    """Best-effort host telemetry, clamped to 0-100.

    Values are honest samples, not fabricated numbers: when a source is
    unavailable the metric stays 0 and the UI renders it as unknown.
    """
    metrics = {"cpu": 0, "ram": 0, "disk": 0}

    # CPU: 1-minute load average relative to core count.
    try:
        load = os.getloadavg()
        cpus = os.cpu_count() or 1
        metrics["cpu"] = max(0, min(100, int(round(load[0] / cpus * 100))))
    except (OSError, AttributeError, ValueError):
        pass

    # RAM: /proc/meminfo (Linux). MemAvailable is in kB.
    try:
        with open("/proc/meminfo") as fh:
            meminfo = {}
            for line in fh:
                parts = line.split(":")
                if len(parts) == 2 and parts[0] in ("MemTotal", "MemAvailable"):
                    meminfo[parts[0]] = int(parts[1].strip().split()[0])
        total = meminfo.get("MemTotal")
        if total:
            available = meminfo.get("MemAvailable", total)
            metrics["ram"] = max(0, min(100, int(round((1 - available / total) * 100))))
    except (OSError, ValueError, KeyError):
        pass

    # Disk: root partition usage.
    try:
        usage = shutil.disk_usage("/")
        metrics["disk"] = max(0, min(100, int(round(usage.used / usage.total * 100))))
    except (OSError, ValueError):
        pass

    return metrics


@socketio.on("connect")
def on_connect():
    socketio.emit("system", collect_system_metrics())


@socketio.on("system:get")
def on_system_get():
    socketio.emit("system", collect_system_metrics())
