from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import mysql.connector
import re, io
from datetime import datetime

app = Flask(__name__)

DB_HOST = "186.147.60.119"
DB_PORT = 3309
DB_NAME = "ofsc_cupos"
DB_USER = "ofsc_user"
DB_PASS = "Capacidades*"

TIMESLOT_RE = re.compile(r"^\d{2}[:\-]\d{2}")

HTML = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OFSC ETL — Carga de Cuotas</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --red:#da291c; --red-dark:#a81f14;
  --bg:#f5f4f0; --surface:#fff; --surface2:#f0eeea;
  --text:#1a1816; --muted:#7a7670; --border:#e0ddd8;
  --green:#1a7a4a; --green-bg:#eaf5ef;
  --orange:#c25a00; --orange-bg:#fff3e8;
  --mono:'DM Mono',monospace; --sans:'DM Sans',sans-serif;
}
body { font-family:var(--sans); background:var(--bg); color:var(--text); min-height:100vh; }

header {
  background:var(--red); color:white; padding:0 2rem;
  height:56px; display:flex; align-items:center; gap:1rem;
}
.logo { font-size:1.1rem; font-weight:600; letter-spacing:-0.02em; }
.sub  { font-size:0.8rem; opacity:0.7; font-weight:300; }
.badge {
  margin-left:auto; background:rgba(255,255,255,0.15);
  border:1px solid rgba(255,255,255,0.25); border-radius:4px;
  padding:2px 10px; font-family:var(--mono); font-size:0.72rem;
}

main { max-width:960px; margin:0 auto; padding:2.5rem 1.5rem; }
h2 { font-size:1.4rem; font-weight:600; letter-spacing:-0.02em; margin-bottom:0.3rem; }
.page-desc { color:var(--muted); font-size:0.9rem; margin-bottom:2rem; }

.layout { display:grid; grid-template-columns:1fr 1fr; gap:2rem; align-items:start; }
@media(max-width:700px){ .layout { grid-template-columns:1fr; } }

/* Upload panel */
.upload-panel { display:flex; flex-direction:column; gap:1rem; }

.drop-zone {
  border:2px dashed var(--border); border-radius:12px;
  background:var(--surface); padding:2.5rem 1.5rem;
  text-align:center; cursor:pointer; transition:all 0.2s; position:relative;
}
.drop-zone:hover, .drop-zone.dragover { border-color:var(--red); background:#fff5f5; }
.drop-zone input { position:absolute; inset:0; opacity:0; cursor:pointer; width:100%; height:100%; }
.drop-icon { font-size:2.2rem; margin-bottom:0.6rem; }
.drop-title { font-size:0.95rem; font-weight:500; margin-bottom:0.25rem; }
.drop-hint  { font-size:0.8rem; color:var(--muted); }

.file-info {
  display:none; align-items:center; gap:0.6rem;
  background:var(--green-bg); border:1px solid #a8d5be;
  border-radius:8px; padding:0.75rem 1rem; font-size:0.85rem;
}
.file-info.show { display:flex; }
.fname { font-family:var(--mono); font-weight:500; color:var(--green); }

.dup-alert { display:none; border-radius:8px; padding:0.85rem 1rem; font-size:0.84rem; line-height:1.6; }
.dup-alert.show { display:block; }
.dup-alert.warn { background:var(--orange-bg); border:1px solid #f5c49a; color:var(--orange); }
.dup-alert.ok   { background:var(--green-bg);  border:1px solid #a8d5be; color:var(--green); }
.dup-alert strong { display:block; margin-bottom:0.3rem; font-weight:600; }
.date-chip {
  display:inline-block; margin:2px 3px; padding:1px 8px;
  border-radius:4px; font-family:var(--mono); font-size:0.78rem;
}
.chip-dup  { background:#f5c49a; color:var(--orange); }
.chip-new  { background:#c3e8d3; color:var(--green); }

.btn {
  padding:0.85rem; border:none; border-radius:8px; font-family:var(--sans);
  font-size:0.9rem; font-weight:600; cursor:pointer; transition:all 0.15s;
  display:flex; align-items:center; justify-content:center; gap:0.5rem; width:100%;
}
.btn-primary { background:var(--red);    color:white; }
.btn-primary:hover { background:var(--red-dark); }
.btn-warn    { background:var(--orange); color:white; }
.btn-warn:hover    { background:#a04800; }
.btn:disabled { background:#ccc; cursor:not-allowed; }

.log-wrap { display:none; border-radius:10px; overflow:hidden; border:1px solid var(--border); }
.log-wrap.show { display:block; }
.log-header {
  padding:0.75rem 1rem; font-size:0.82rem; font-weight:500; color:var(--muted);
  border-bottom:1px solid var(--border); display:flex; align-items:center; gap:0.5rem;
  background:var(--surface2);
}
.spinner {
  width:13px; height:13px; border:2px solid var(--border);
  border-top-color:var(--red); border-radius:50%; animation:spin 0.7s linear infinite;
}
.spinner.done { animation:none; border-color:var(--green); border-top-color:var(--green); }
@keyframes spin { to { transform:rotate(360deg); } }
.log-body {
  padding:0.85rem 1rem; font-family:var(--mono); font-size:0.76rem;
  line-height:1.75; max-height:180px; overflow-y:auto;
  background:#1a1816; color:#c8c4bc;
}
.log-body .ok   { color:#6bcf8f; }
.log-body .err  { color:#ff6b6b; }
.log-body .info { color:#7eb8f7; }
.log-body .warn { color:#ffd080; }

.result-card { display:none; border-radius:10px; overflow:hidden; border:1px solid var(--border); }
.result-card.show { display:block; }
.result-card.success { border-color:#a8d5be; }
.result-card.error   { border-color:#ffb3ae; }
.result-header { padding:0.85rem 1rem; font-weight:600; font-size:0.9rem; display:flex; align-items:center; gap:0.5rem; }
.result-card.success .result-header { background:var(--green-bg); color:var(--green); }
.result-card.error   .result-header { background:#fff0ef; color:#c0392b; }
.result-stats { display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--border); }
.stat { background:var(--surface); padding:0.85rem 0.4rem; text-align:center; }
.stat-val { font-size:1.35rem; font-weight:600; font-family:var(--mono); letter-spacing:-0.03em; }
.stat-lbl { font-size:0.67rem; color:var(--muted); margin-top:0.15rem; text-transform:uppercase; letter-spacing:0.05em; }

/* Dates panel */
.panel-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem; }
.panel-title  { font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:var(--muted); }
.total-badge  {
  background:var(--surface2); border:1px solid var(--border);
  border-radius:20px; padding:2px 10px; font-family:var(--mono);
  font-size:0.72rem; color:var(--muted);
}

.dates-box {
  background:var(--surface); border-radius:10px;
  border:1px solid var(--border); overflow:hidden;
}
.dates-scroll { max-height:460px; overflow-y:auto; }
table { width:100%; border-collapse:collapse; font-size:0.82rem; }
thead th {
  background:var(--surface2); padding:0.55rem 0.9rem; text-align:left;
  font-size:0.67rem; font-weight:600; text-transform:uppercase;
  letter-spacing:0.06em; color:var(--muted); border-bottom:1px solid var(--border);
  position:sticky; top:0;
}
tbody td { padding:0.55rem 0.9rem; border-bottom:1px solid var(--border); font-family:var(--mono); font-size:0.8rem; }
tbody tr:last-child td { border-bottom:none; }
tbody tr:hover td { background:var(--surface2); }
.tag { display:inline-block; padding:1px 7px; border-radius:4px; font-size:0.7rem; font-weight:500; }
.tag-new { background:var(--green-bg); color:var(--green); }
.tag-ago { color:var(--muted); font-family:var(--sans); font-size:0.75rem; }
.empty { text-align:center; color:var(--muted); padding:2rem; font-size:0.85rem; }
</style>
</head>
<body>

<header>
  <div class="logo">🔴 OFSC ETL</div>
  <div class="sub">Región Occidente · Claro Colombia</div>
  <div class="badge">186.147.60.119:3309</div>
</header>

<main>
  <h2>Carga de Cuotas</h2>
  <p class="page-desc">Sube el Excel exportado desde OFSC. El sistema detecta automáticamente si las fechas ya fueron cargadas.</p>

  <div class="layout">

    <!-- IZQUIERDA: CARGA -->
    <div class="upload-panel">

      <div class="drop-zone" id="dropZone">
        <input type="file" id="fileInput" accept=".xlsx,.xls">
        <div class="drop-icon">📊</div>
        <div class="drop-title">Arrastra el archivo Excel aquí</div>
        <div class="drop-hint">o haz clic para seleccionar · Solo .xlsx</div>
      </div>

      <div class="file-info" id="fileInfo">
        <span>📄</span>
        <span class="fname" id="fileName"></span>
        <span style="color:var(--muted);margin-left:auto;font-family:var(--mono);font-size:0.78rem" id="fileSize"></span>
      </div>

      <div class="dup-alert" id="dupAlert">
        <strong id="dupTitle"></strong>
        <div id="dupBody"></div>
      </div>

      <button class="btn btn-primary" id="btnUpload" disabled onclick="uploadFile()">
        ▶ Procesar y guardar en BD
      </button>

      <div class="log-wrap" id="logWrap">
        <div class="log-header">
          <div class="spinner" id="spinner"></div>
          <span id="logLabel">Procesando...</span>
        </div>
        <div class="log-body" id="logBody"></div>
      </div>

      <div class="result-card" id="resultCard">
        <div class="result-header" id="resultHeader"></div>
        <div class="result-stats" id="resultStats"></div>
      </div>

    </div>

    <!-- DERECHA: FECHAS EN BD -->
    <div>
      <div class="panel-header">
        <div class="panel-title">Fechas cargadas en BD</div>
        <div class="total-badge" id="totalBadge">— días</div>
      </div>
      <div class="dates-box">
        <div class="dates-scroll">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Día</th>
                <th>Registros</th>
                <th>Cargado</th>
              </tr>
            </thead>
            <tbody id="datesBody">
              <tr><td colspan="4" class="empty">Cargando...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</main>

<script>
const DIAS = ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'];
let fechasEnBD = new Set();
let selectedFile = null;

// Drag & drop
const dropZone  = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

dropZone.addEventListener('dragover',  e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('dragover');
  if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', () => { if (fileInput.files[0]) setFile(fileInput.files[0]); });

function setFile(f) {
  selectedFile = f;
  document.getElementById('fileName').textContent = f.name;
  document.getElementById('fileSize').textContent = (f.size/1024).toFixed(0) + ' KB';
  document.getElementById('fileInfo').classList.add('show');
  document.getElementById('resultCard').classList.remove('show');
  document.getElementById('logWrap').classList.remove('show');
  document.getElementById('dupAlert').classList.remove('show');
  document.getElementById('btnUpload').disabled = false;
  previewFechas(f);
}

async function previewFechas(f) {
  const form = new FormData();
  form.append('file', f);
  try {
    const res  = await fetch('/preview', { method:'POST', body:form });
    const data = await res.json();
    if (!data.ok) return;

    const dups  = data.fechas.filter(x => fechasEnBD.has(x));
    const news  = data.fechas.filter(x => !fechasEnBD.has(x));
    const alert = document.getElementById('dupAlert');
    const btn   = document.getElementById('btnUpload');

    let chips = '';
    if (dups.length) {
      chips += '<div style="margin-top:4px">';
      dups.forEach(f => { chips += `<span class="date-chip chip-dup">${f} ${DIAS[new Date(f+'T12:00:00').getDay()]}</span>`; });
      chips += '</div>';
    }
    if (news.length) {
      chips += '<div style="margin-top:4px">';
      news.forEach(f => { chips += `<span class="date-chip chip-new">${f} ${DIAS[new Date(f+'T12:00:00').getDay()]}</span>`; });
      chips += '</div>';
    }

    if (dups.length > 0 && news.length === 0) {
      alert.className = 'dup-alert show warn';
      document.getElementById('dupTitle').textContent = '⚠️ Todas las fechas ya están cargadas — se sobreescribirán';
      btn.className = 'btn btn-warn';
      btn.innerHTML = '⚠️ Fechas duplicadas — subir igualmente';
    } else if (dups.length > 0) {
      alert.className = 'dup-alert show warn';
      document.getElementById('dupTitle').textContent = `⚠️ ${dups.length} fecha(s) duplicada(s) · ${news.length} nueva(s)`;
      btn.className = 'btn btn-warn';
      btn.innerHTML = '⚠️ Hay duplicados — subir igualmente';
    } else {
      alert.className = 'dup-alert show ok';
      document.getElementById('dupTitle').textContent = `✅ ${news.length} fecha(s) nueva(s) — ninguna duplicada`;
      btn.className = 'btn btn-primary';
      btn.innerHTML = '▶ Procesar y guardar en BD';
    }
    document.getElementById('dupBody').innerHTML = chips;
  } catch(e) { console.error(e); }
}

function addLog(msg, cls='') {
  const el   = document.getElementById('logBody');
  const line = document.createElement('div');
  if (cls) line.className = cls;
  line.textContent = msg;
  el.appendChild(line);
  el.scrollTop = el.scrollHeight;
}

async function uploadFile() {
  if (!selectedFile) return;
  document.getElementById('btnUpload').disabled = true;
  document.getElementById('logWrap').classList.add('show');
  document.getElementById('logBody').innerHTML = '';
  document.getElementById('resultCard').classList.remove('show');
  document.getElementById('logLabel').textContent = 'Procesando...';
  document.getElementById('spinner').className = 'spinner';

  addLog('Subiendo archivo...', 'info');
  const form = new FormData();
  form.append('file', selectedFile);

  try {
    const res  = await fetch('/upload', { method:'POST', body:form });
    const data = await res.json();
    document.getElementById('spinner').className = 'spinner done';

    if (data.ok) {
      document.getElementById('logLabel').textContent = '✓ Completado';
      data.logs.forEach(l => addLog(l.msg, l.type));
      const card = document.getElementById('resultCard');
      card.className = 'result-card show success';
      document.getElementById('resultHeader').innerHTML = '✅ Datos guardados correctamente';
      document.getElementById('resultStats').innerHTML = `
        <div class="stat"><div class="stat-val">${data.stats.fechas}</div><div class="stat-lbl">Fechas</div></div>
        <div class="stat"><div class="stat-val">${data.stats.registros.toLocaleString()}</div><div class="stat-lbl">Registros</div></div>
        <div class="stat"><div class="stat-val">${data.stats.insertados.toLocaleString()}</div><div class="stat-lbl">Nuevos</div></div>
        <div class="stat"><div class="stat-val">${data.stats.actualizados.toLocaleString()}</div><div class="stat-lbl">Actualizados</div></div>
      `;
      cargarFechas();
    } else {
      document.getElementById('logLabel').textContent = '✗ Error';
      addLog('ERROR: ' + data.error, 'err');
      document.getElementById('resultCard').className = 'result-card show error';
      document.getElementById('resultHeader').innerHTML = '❌ ' + data.error;
      document.getElementById('resultStats').innerHTML = '';
    }
  } catch(e) { addLog('Error: ' + e.message, 'err'); }

  document.getElementById('btnUpload').disabled = false;
  document.getElementById('btnUpload').className = 'btn btn-primary';
  document.getElementById('btnUpload').innerHTML = '▶ Procesar y guardar en BD';
}

function tiempoRelativo(horas) {
  if (horas < 1)  return '<span class="tag tag-new">hace menos de 1h</span>';
  if (horas < 24) return `<span class="tag-ago">hace ${horas}h</span>`;
  const dias = Math.floor(horas / 24);
  return `<span class="tag-ago">hace ${dias}d</span>`;
}

async function cargarFechas() {
  try {
    const res  = await fetch('/fechas');
    const data = await res.json();
    fechasEnBD = new Set(data.rows.map(r => r.fecha));
    document.getElementById('totalBadge').textContent = data.rows.length + ' días';
    const tbody = document.getElementById('datesBody');
    if (!data.rows.length) {
      tbody.innerHTML = '<tr><td colspan="4" class="empty">Sin datos aún</td></tr>';
      return;
    }
    tbody.innerHTML = data.rows.map(r => {
      const d   = new Date(r.fecha + 'T12:00:00');
      const dia = DIAS[d.getDay()];
      return `<tr>
        <td style="font-weight:500">${r.fecha}</td>
        <td style="color:var(--muted);font-family:var(--sans);font-size:0.8rem">${dia}</td>
        <td>${r.registros.toLocaleString()}</td>
        <td>${tiempoRelativo(r.horas)}</td>
      </tr>`;
    }).join('');
  } catch(e) { console.error(e); }
}

cargarFechas();
</script>
</body>
</html>'''


def get_conn():
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASS, connection_timeout=30)


def transformar_excel(content):
    df_raw = pd.read_excel(io.BytesIO(content), sheet_name="Quota Data", header=None)
    date_blocks = [(i, v) for i, v in enumerate(df_raw.iloc[0, :])
                   if pd.notna(v) and v != "Time slot\nCapacity categories"]
    if not date_blocks:
        raise ValueError("No se encontraron bloques de fecha en el archivo")

    rows = []
    for block_start, date_val in date_blocks:
        zone = timeslot = None
        for idx, row in df_raw.iterrows():
            if idx <= 1:
                continue
            v0, v1 = row[0], row[1]
            if pd.notna(v0) and v0 != "Time slot\nCapacity categories":
                zone = str(v0).strip()
                timeslot = str(v1).strip() if pd.notna(v1) else None
                continue
            if pd.notna(v1):
                s = str(v1).strip()
                if TIMESLOT_RE.match(s):
                    timeslot = s
                else:
                    rows.append({
                        "fecha": date_val, "zona": zone,
                        "franja_horaria": timeslot, "categoria": s,
                        "quota_pct":           row[block_start + 0],
                        "min_quota":           row[block_start + 1],
                        "used_quota_pct":      row[block_start + 2],
                        "weight":              row[block_start + 3],
                        "estimated_quota_pct": row[block_start + 4],
                        "stop_booking_pct":    row[block_start + 5],
                        "status":              row[block_start + 6],
                        "close_time":          row[block_start + 7],
                        "max_available":       row[block_start + 8],
                        "other_activities":    row[block_start + 9],
                        "quota_mins":          row[block_start + 10],
                        "plan":                row[block_start + 11],
                        "booked_activities":   row[block_start + 12],
                        "used":                row[block_start + 13],
                    })

    df = pd.DataFrame(rows)
    df["fecha"]      = pd.to_datetime(df["fecha"], errors="coerce").dt.date
    df["close_time"] = pd.to_datetime(df["close_time"], errors="coerce")
    fechas = sorted([str(f) for f in df["fecha"].dropna().unique()])
    return df, fechas


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/preview', methods=['POST'])
def preview():
    """Detecta las fechas del Excel sin guardar nada."""
    try:
        f = request.files.get('file')
        if not f:
            return jsonify({"ok": False})
        content = f.read()
        df_raw = pd.read_excel(io.BytesIO(content), sheet_name="Quota Data", header=None)
        date_blocks = [(i, v) for i, v in enumerate(df_raw.iloc[0, :])
                       if pd.notna(v) and v != "Time slot\nCapacity categories"]
        fechas = sorted([str(v) for _, v in date_blocks])
        return jsonify({"ok": True, "fechas": fechas})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route('/upload', methods=['POST'])
def upload():
    logs  = []
    stats = {"fechas": 0, "registros": 0, "insertados": 0, "actualizados": 0, "omitidos": 0}

    def log(msg, t=''):
        logs.append({"msg": msg, "type": t})

    try:
        f = request.files.get('file')
        if not f:
            return jsonify({"ok": False, "error": "No se recibió archivo"})
        if not f.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({"ok": False, "error": "Solo se aceptan archivos .xlsx"})

        log(f"Leyendo: {f.filename}", "info")
        content    = f.read()
        df, fechas = transformar_excel(content)

        log(f"Fechas: {', '.join(fechas)}")
        stats["fechas"]    = len(fechas)
        stats["registros"] = len(df)
        log(f"Transformacion OK: {len(df):,} registros · {df['zona'].nunique()} zonas", "ok")

        # ── Lógica: DELETE por fecha → INSERT limpio ─────────────────────────
        # Garantiza que si el nuevo Excel tiene más o menos filas que el anterior,
        # la BD queda exactamente igual al archivo subido.
        conn = get_conn()
        cur  = conn.cursor()

        # Clasificar fechas
        ph       = ','.join(['%s'] * len(fechas))
        cur.execute(f"SELECT DISTINCT fecha, COUNT(*) FROM uso_cupos WHERE fecha IN ({ph}) GROUP BY fecha", fechas)
        en_bd    = {str(r[0]): int(r[1]) for r in cur.fetchall()}
        nuevas   = [f for f in fechas if f not in en_bd]
        dups     = [f for f in fechas if f in en_bd]

        if dups:
            for f in dups:
                log(f"Fecha {f}: borrando {en_bd[f]:,} registros existentes → reemplazando", "warn")
        if nuevas:
            log(f"Fechas nuevas (se INSERTAN): {', '.join(nuevas)}", "info")

        # PASO 1: DELETE de todas las fechas duplicadas de una vez
        if dups:
            ph_dups = ','.join(['%s'] * len(dups))
            cur.execute(f"DELETE FROM uso_cupos WHERE fecha IN ({ph_dups})", dups)
            borrados = cur.rowcount
            log(f"Borrados {borrados:,} registros antiguos", "info")

        # PASO 2: INSERT limpio de todos los registros del Excel
        SQL_INSERT = """INSERT INTO uso_cupos (
            fecha, zona, franja_horaria, categoria,
            quota_pct, min_quota, used_quota_pct, weight,
            estimated_quota_pct, stop_booking_pct,
            status, close_time, max_available, other_activities,
            quota_mins, plan, booked_activities, used
        ) VALUES (
            %(fecha)s, %(zona)s, %(franja_horaria)s, %(categoria)s,
            %(quota_pct)s, %(min_quota)s, %(used_quota_pct)s, %(weight)s,
            %(estimated_quota_pct)s, %(stop_booking_pct)s,
            %(status)s, %(close_time)s, %(max_available)s, %(other_activities)s,
            %(quota_mins)s, %(plan)s, %(booked_activities)s, %(used)s
        )"""

        ins = err = 0
        for rec in df.where(pd.notna(df), other=None).to_dict("records"):
            clean = {k: (None if v is not None and str(v) == 'nan' else v) for k, v in rec.items()}
            try:
                cur.execute(SQL_INSERT, clean)
                ins += 1
            except Exception as e:
                err += 1

        conn.commit()
        cur.close()
        conn.close()

        stats["insertados"]   = ins
        stats["actualizados"] = len(dups)  # fechas que se reemplazaron
        stats["omitidos"]     = 0
        log(f"MySQL: {ins:,} insertados · {len(dups)} fechas reemplazadas · {err} errores", "ok")

        return jsonify({"ok": True, "logs": logs, "stats": stats})

    except Exception as e:
        log(str(e), "err")
        return jsonify({"ok": False, "error": str(e), "logs": logs})


@app.route('/fechas')
def fechas():
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT
                fecha,
                COUNT(*) AS registros,
                MAX(fecha_carga) AS ultima_carga,
                TIMESTAMPDIFF(HOUR, MAX(fecha_carga), NOW()) AS horas
            FROM uso_cupos
            GROUP BY fecha
            ORDER BY fecha DESC
        """)
        rows = [{"fecha": str(r[0]), "registros": int(r[1]),
                 "ultima_carga": r[2].strftime("%Y-%m-%d %H:%M") if r[2] else "",
                 "horas": int(r[3]) if r[3] is not None else 9999}
                for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({"rows": rows})
    except Exception as e:
        return jsonify({"rows": [], "error": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=False)
