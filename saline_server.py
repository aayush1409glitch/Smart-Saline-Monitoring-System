from flask import Flask, request, render_template_string
import time

app = Flask(__name__)

latest_data = {
    "weight": 0,
    "percentage": 100,
    "alert": False,
    "timestamp": time.time()
}

FULL_VOLUME_ML = 100

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Saline Monitor</title>
  <meta http-equiv="refresh" content="3">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #F0F4F8;
      min-height: 100vh;
      padding: 0;
    }

    /* ── NAV ── */
    .nav {
      background: #ffffff;
      border-bottom: 1px solid #E2E8F0;
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .nav-left { display: flex; align-items: center; gap: 10px; }
    .nav-icon {
      width: 34px; height: 34px; border-radius: 8px;
      background: #E1F5EE;
      display: flex; align-items: center; justify-content: center;
    }
    .nav-icon svg { width: 16px; height: 16px; }
    .nav-title { font-size: 15px; font-weight: 600; color: #1A202C; }
    .nav-sub   { font-size: 11px; color: #718096; margin-top: 1px; }
    .nav-right { display: flex; align-items: center; gap: 12px; }
    .live-dot  {
      display: flex; align-items: center; gap: 5px;
      font-size: 12px; color: #718096;
    }
    .dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: {{ '#E53E3E' if alert else '#1D9E75' }};
    }
    .clock-chip {
      background: #F7FAFC; border: 1px solid #E2E8F0;
      border-radius: 6px; padding: 4px 10px;
      font-size: 11px; color: #718096; font-variant-numeric: tabular-nums;
    }

    /* ── LAYOUT ── */
    .main {
      display: grid;
      grid-template-columns: 260px 1fr;
      gap: 16px;
      padding: 16px;
      max-width: 1100px;
      margin: 0 auto;
    }

    /* ── CARD ── */
    .card {
      background: #ffffff;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      overflow: hidden;
    }
    .card-body { padding: 14px 16px; }
    .sec-head {
      font-size: 10px; font-weight: 600; letter-spacing: 0.06em;
      color: #A0AEC0; text-transform: uppercase; margin-bottom: 10px;
    }
    .info-row {
      display: flex; justify-content: space-between; align-items: center;
      padding: 7px 0; border-bottom: 1px solid #F0F4F8;
      font-size: 12px;
    }
    .info-row:last-child { border-bottom: none; }
    .info-label { color: #718096; }
    .info-val   { font-weight: 500; color: #1A202C; }

    /* ── PATIENT HEADER ── */
    .patient-header {
      background: #E1F5EE;
      padding: 14px 16px;
      border-bottom: 1px solid #C6F6D5;
      display: flex; align-items: center; gap: 10px;
    }
    .avatar {
      width: 40px; height: 40px; border-radius: 50%;
      background: #0F6E56; color: #fff;
      display: flex; align-items: center; justify-content: center;
      font-size: 13px; font-weight: 600; flex-shrink: 0;
    }
    .patient-name  { font-size: 14px; font-weight: 600; color: #085041; }
    .patient-id    { font-size: 11px; color: #0F6E56; margin-top: 1px; }

    .info-grid {
      display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
      padding: 14px 16px;
    }
    .ig-item .lbl { font-size: 10px; color: #A0AEC0; margin-bottom: 2px; }
    .ig-item .v   { font-size: 13px; font-weight: 500; color: #1A202C; }

    .divider { height: 1px; background: #F0F4F8; }

    .chip {
      font-size: 10px; font-weight: 600; padding: 2px 8px;
      border-radius: 20px;
    }
    .chip-green { background: #E1F5EE; color: #085041; }
    .chip-blue  { background: #EBF8FF; color: #2C5282; }

    /* ── MONITOR PANEL ── */
    .monitor-col { display: flex; flex-direction: column; gap: 12px; }

    /* Level card */
    .level-card { padding: 20px 22px; }
    .level-top {
      display: flex; justify-content: space-between;
      align-items: flex-start; margin-bottom: 16px;
    }
    .level-label { font-size: 11px; color: #A0AEC0; margin-bottom: 4px; }
    .level-num {
      font-size: 72px; font-weight: 700; line-height: 1;
      color: {{ '#E53E3E' if alert else ('#D69E2E' if percentage < 45 else '#1D9E75') }};
    }
    .level-ml  { font-size: 16px; color: #718096; }
    .level-cap { font-size: 11px; color: #A0AEC0; margin-top: 2px; }

    .status-badge {
      display: flex; align-items: center; gap: 6px;
      padding: 6px 12px; border-radius: 20px;
      font-size: 12px; font-weight: 600;
      background: {{ '#FFF5F5' if alert else ('#FFFBEB' if percentage < 45 else '#E1F5EE') }};
      border: 1px solid {{ '#FEB2B2' if alert else ('#F6E05E' if percentage < 45 else '#9AE6B4') }};
      color: {{ '#9B2C2C' if alert else ('#744210' if percentage < 45 else '#085041') }};
    }
    .badge-dot {
      width: 7px; height: 7px; border-radius: 50%;
      background: {{ '#E53E3E' if alert else ('#D69E2E' if percentage < 45 else '#1D9E75') }};
    }

    /* progress bar */
    .bar-track {
      background: #EDF2F7; border-radius: 8px;
      height: 16px; overflow: hidden; margin-bottom: 6px;
    }
    .bar-fill {
      height: 100%; border-radius: 8px;
      width: {{ "%.1f"|format(percentage) }}%;
      background: {{ '#E53E3E' if alert else ('#D69E2E' if percentage < 45 else '#1D9E75') }};
      transition: width 1s;
    }
    .bar-labels {
      display: flex; justify-content: space-between;
      font-size: 11px; color: #A0AEC0;
    }
    .bar-labels .alert-mark { color: #E53E3E; }

    /* alert banner */
    .alert-banner {
      display: {{ 'block' if alert else 'none' }};
      margin-top: 14px;
      background: #FFF5F5; border: 1px solid #FEB2B2;
      border-radius: 10px; padding: 12px 16px;
    }
    .alert-title { font-size: 13px; font-weight: 600; color: #742A2A; margin-bottom: 3px; }
    .alert-sub   { font-size: 12px; color: #C53030; }

    /* stat cards */
    .stats-grid {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
    }
    .stat-card {
      background: #F7FAFC; border-radius: 10px; padding: 12px 14px;
    }
    .stat-lbl { font-size: 10px; color: #A0AEC0; margin-bottom: 4px; }
    .stat-val { font-size: 20px; font-weight: 600; color: #2B6CB0; }
    .stat-sub { font-size: 10px; color: #A0AEC0; margin-top: 2px; }

    /* two col bottom */
    .bottom-grid {
      display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
    }

    /* footer */
    .footer {
      background: #fff; border-top: 1px solid #E2E8F0;
      padding: 9px 24px;
      display: flex; justify-content: space-between;
      font-size: 11px; color: #A0AEC0;
      margin-top: 4px;
    }

    @media (max-width: 700px) {
      .main { grid-template-columns: 1fr; }
      .stats-grid { grid-template-columns: 1fr 1fr; }
      .bottom-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

<!-- NAV -->
<div class="nav">
  <div class="nav-left">
    <div class="nav-icon">
      <svg viewBox="0 0 16 16" fill="none">
        <rect x="7" y="2" width="2" height="12" rx="1" fill="#0F6E56"/>
        <rect x="2" y="7" width="12" height="2" rx="1" fill="#0F6E56"/>
      </svg>
    </div>
    <div>
      <div class="nav-title">Saline Monitor</div>
      <div class="nav-sub">Smart IV Tracking System</div>
    </div>
  </div>
  <div class="nav-right">
    <div class="live-dot">
      <div class="dot"></div>
      <span>{{ 'Alert' if alert else 'Live' }}</span>
    </div>
    <div class="clock-chip">{{ last_update }}</div>
  </div>
</div>

<!-- MAIN GRID -->
<div class="main">

  <!-- LEFT: Patient Panel -->
  <div style="display:flex;flex-direction:column;gap:12px;">

    <!-- Patient info card -->
    <div class="card">
      <div class="patient-header">
        <div class="avatar">RK</div>
        <div>
          <div class="patient-name">Rajesh Kumar</div>
          <div class="patient-id">ID: MH-2026-0419</div>
        </div>
      </div>
      <div class="info-grid">
        <div class="ig-item"><div class="lbl">Age</div><div class="v">54 yrs</div></div>
        <div class="ig-item"><div class="lbl">Gender</div><div class="v">Male</div></div>
        <div class="ig-item"><div class="lbl">Ward</div><div class="v">C — Bed 4</div></div>
        <div class="ig-item"><div class="lbl">Blood group</div><div class="v">B+</div></div>
      </div>
      <div class="divider"></div>
      <div class="card-body">
        <div class="info-row">
          <span class="info-label">Attending doctor</span>
          <span class="info-val">Dr. Saumya Singh</span>
        </div>
        <div class="info-row">
          <span class="info-label">Diagnosis</span>
          <span class="info-val">Post-op recovery</span>
        </div>
        <div class="info-row">
          <span class="info-label">IV solution</span>
          <span class="info-val">Normal Saline 0.9%</span>
        </div>
        <div class="info-row">
          <span class="info-label">Bag size</span>
          <span class="chip chip-green">100 ml</span>
        </div>
        <div class="info-row">
          <span class="info-label">Nurse assigned</span>
          <span class="info-val">Priya Nair</span>
        </div>
      </div>
    </div>

    <!-- Prescription card -->
    <div class="card">
      <div class="card-body">
        <div class="sec-head">Prescription</div>
        <div class="info-row">
          <span class="info-label">Ordered rate</span>
          <span class="info-val">2 ml / min</span>
        </div>
        <div class="info-row">
          <span class="info-label">Total volume</span>
          <span class="info-val">100 ml</span>
        </div>
        <div class="info-row">
          <span class="info-label">Alert threshold</span>
          <span style="font-weight:500;color:#E53E3E;">30%  (30 ml)</span>
        </div>
        <div class="info-row">
          <span class="info-label">Server refresh</span>
          <span class="chip chip-blue">Every 3s</span>
        </div>
      </div>
    </div>

  </div>

  <!-- RIGHT: Monitor Panel -->
  <div class="monitor-col">

    <!-- Level card -->
    <div class="card level-card">
      <div class="level-top">
        <div>
          <div class="level-label">Current saline level</div>
          <div style="display:flex;align-items:baseline;gap:10px;">
            <div class="level-num">{{ "%.1f"|format(percentage) }}%</div>
            <div>
              <div class="level-ml">{{ "%.1f"|format(weight) }} ml</div>
              <div class="level-cap">of 100 ml</div>
            </div>
          </div>
        </div>
        <div class="status-badge">
          <div class="badge-dot"></div>
          <span>{{ 'Alert' if alert else ('Low' if percentage < 45 else 'Normal') }}</span>
        </div>
      </div>

      <div class="bar-track">
        <div class="bar-fill"></div>
      </div>
      <div class="bar-labels">
        <span>0%</span>
        <span class="alert-mark">&#9888; alert at 30%</span>
        <span>100%</span>
      </div>

      <div class="alert-banner">
        <div class="alert-title">Replace saline bag immediately</div>
        <div class="alert-sub">Servo actuated to 90&deg; &nbsp;&middot;&nbsp; Buzzer active &nbsp;&middot;&nbsp; Nurse notified</div>
      </div>
    </div>

    <!-- Stat cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-lbl">Drip rate</div>
        <div class="stat-val">~2 ml/m</div>
        <div class="stat-sub">avg last 5 min</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Last POST</div>
        <div class="stat-val">{{ last_update }}</div>
        <div class="stat-sub">from ESP8266</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Alert status</div>
        <div class="stat-val" style="color:{{ '#E53E3E' if alert else '#1D9E75' }}">
          {{ 'Active' if alert else 'Clear' }}
        </div>
        <div class="stat-sub">threshold: 30%</div>
      </div>
    </div>

    <!-- Live readings + System health -->
    <div class="bottom-grid">
      <div class="card">
        <div class="card-body">
          <div class="sec-head">Live readings</div>
          <div class="info-row">
            <span class="info-label">Weight</span>
            <span class="info-val">{{ "%.1f"|format(weight) }} g</span>
          </div>
          <div class="info-row">
            <span class="info-label">Level</span>
            <span class="info-val" style="color:{{ '#E53E3E' if alert else ('#D69E2E' if percentage < 45 else '#1D9E75') }}">
              {{ "%.1f"|format(percentage) }}%
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">Alert</span>
            <span class="chip {{ 'chip-green' if not alert else '' }}"
              style="{{ 'background:#FFF5F5;color:#9B2C2C;' if alert else '' }}">
              {{ 'Yes' if alert else 'No' }}
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">Servo</span>
            <span class="info-val" style="color:{{ '#E53E3E' if alert else '#1A202C' }}">
              {{ '90&deg;' if alert else '0&deg;' }}
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">Buzzer</span>
            <span class="info-val" style="color:{{ '#E53E3E' if alert else '#1A202C' }}">
              {{ 'Active' if alert else 'Silent' }}
            </span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-body">
          <div class="sec-head">System health</div>
          <div class="info-row">
            <span class="info-label">ESP8266</span>
            <span class="chip chip-green">Connected</span>
          </div>
          <div class="info-row">
            <span class="info-label">HX711</span>
            <span class="chip chip-green">Ready</span>
          </div>
          <div class="info-row">
            <span class="info-label">Flask server</span>
            <span class="chip chip-green">Running</span>
          </div>
          <div class="info-row">
            <span class="info-label">WiFi signal</span>
            <span class="info-val">Strong</span>
          </div>
          <div class="info-row">
            <span class="info-label">Server IP</span>
            <span class="info-val">192.168.1.9</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>

<div class="footer">
  <span>Auto-refreshes every 3s &nbsp;&middot;&nbsp; SCOE Avishkar 2026</span>
  <span>Smart Saline Monitoring System</span>
</div>

<script>
  // ── BROWSER NOTIFICATION ──────────────────────────────────────────────────
  // alertFlag is injected by Jinja2 — true/false from ESP8266 POST
  var alertFlag = {{ 'true' if alert else 'false' }};

  function fireNotification() {
    if (!("Notification" in window)) return;

    if (Notification.permission === "granted") {
      new Notification("⚠️ Saline Level Low", {
        body: "Saline bag for Rajesh Kumar (Bed 4) is below 30%. Replace immediately.",
        icon: "",
        requireInteraction: true,   // stays until dismissed
        tag: "saline-alert"         // prevents duplicates on repeat renders
      });
    } else if (Notification.permission !== "denied") {
      Notification.requestPermission().then(function(permission) {
        if (permission === "granted") {
          new Notification("⚠️ Saline Level Low", {
            body: "Saline bag for Rajesh Kumar (Bed 4) is below 30%. Replace immediately.",
            icon: "",
            requireInteraction: true,
            tag: "saline-alert"
          });
        }
      });
    }
  }

  // Request permission on first load so it's ready when alert fires
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }

  // Fire notification if this page load has alert active
  if (alertFlag) {
    fireNotification();
  }
</script>

</body>
</html>
"""

@app.route("/update", methods=["POST"])
def update():
    latest_data["weight"]     = float(request.form.get("weight", 0))
    latest_data["percentage"] = float(request.form.get("percentage", 100))
    latest_data["alert"]      = request.form.get("alert", "0") == "1"
    latest_data["timestamp"]  = time.time()
    return "OK", 200

@app.route("/")
def dashboard():
    return render_template_string(
        HTML_PAGE,
        percentage = latest_data["percentage"],
        weight     = latest_data["weight"],
        alert      = latest_data["alert"],
        last_update = time.strftime("%H:%M:%S", time.localtime(latest_data["timestamp"]))
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)