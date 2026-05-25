import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import mysql.connector
import warnings
from datetime import datetime, timezone, timedelta
warnings.filterwarnings('ignore')

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Capacidades — R3",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB = dict(host="186.147.60.119", port=3309, database="ofsc_cupos",
          user="ofsc_user", password="Capacidades*", connection_timeout=30)

# ── TABLAS FIJAS ──────────────────────────────────────────────────────────────
TRABAJOS = pd.DataFrame([
    ("Brownfield",              150, "FTTH", "Bronwfield"),
    ("HFC  Arreglos Pymes",     90,  "HFC",  "Arreglos"),
    ("HFC  Instalacion Pymes",  180, "HFC",  "Instalaciones"),
    ("Instalacion FTTH",        150, "FTTH", "Instalaciones"),
    ("Mantenimiento FTTH",      75,  "FTTH", "Arreglos"),
    ("Postventa  FTTH",         75,  "FTTH", "Posventas"),
    ("Traslado FTTH",           150, "FTTH", "Traslados"),
    ("HFC  Traslados pymes",    180, "HFC",  "Traslados"),
    ("Brownfield Flash",        150, "FTTH", "Bronwfield"),
    ("Instalaciones Básicas Estándar",        75,  "HFC",  "Instalaciones Básica"),
    ("Instalaciones Empaquetadas Estándar",   150, "HFC",  "Instalaciones"),
    ("Maintenance",             75,  "HFC",  "Arreglos"),
    ("Postventa Estandar",      75,  "HFC",  "Posventas"),
    ("Transfers",               150, "HFC",  "Traslados"),
    ("Disconnect",              25,  "HFC",  "Desconexiones"),
    ("HFC Postventa Pymes",     90,  "HFC",  "Posventas"),
    ("Instalacion",             150, "HFC",  "Instalaciones"),
    ("Instalación FWA",         75,  "FWA",  "Instalaciones"),
    ("Mantenimiento FWA",       75,  "FWA",  "Instalaciones"),
    ("Andamios",                150, "HFC",  "Andamios"),
    ("Technical Appt.",         75,  "HFC",  "Arreglos"),
    ("Ventas Tecnico",          75,  "HFC",  "Ventas Técnico"),
    ("Verifications",           75,  "HFC",  "Verificaciones"),
    ("Blindaje",                75,  "HFC",  "Posventas"),
    ("Instalacion Claro Box",   75,  "HFC",  "Instalaciones"),
    ("Instalaciones Alto Valor  Claro Box",   150, "HFC",  "Instalaciones"),
    ("Instalaciones FTTH Claro Box",          150, "FTTH", "Instalaciones"),
    ("Mantenimientos Moviles Especiales",     75,  "HFC",  "Arreglos"),
    ("Ordenes Moviles Especiales",            150, "FTTH", "Instalaciones"),
    ("Desconexion por Cartera", 25,  "HFC",  "Desconexiones"),
    ("Instalaciones FTTH Alto Valor",         150, "FTTH", "Instalaciones"),
    ("Mantenimientos FTTH Alto Valor",        75,  "FTTH", "Arreglos"),
    ("Reconnect",               75,  "HFC",  "Reconexiones"),
    ("Traslados FTTH Alto Valor",             150, "FTTH", "Traslados"),
    ("Instalaciones DTH Red BI",              150, "HFC",  "Instalaciones"),
    ("Postventa FTTH Alto Valor",             75,  "FTTH", "Posventas"),
    ("Brownfield PYMES",        180, "FTTH", "Bronwfield"),
    ("CAPACIDAD UNIFICADA ACOMETIDA INTERNA", 180, "HFC",  "Instalaciones"),
    ("Demostraciones",          75,  "HFC",  "Instalaciones"),
], columns=["Trabajo","Minutos","Red","Actividad"])

# Solo nombres exactos como están en MySQL campo zona (sin duplicados)
TABLA_FTTH = pd.DataFrame([
    ("Andalucia CONECTAR",           "VACANA",  "No","Si"),
    ("Buga CONECTAR",                "VACANA",  "No","Si"),
    ("Caicedonia CONECTAR",          "VACANA",  "No","Si"),
    ("CALI NORTE CONECTAR",          "CALI",    "Si","Si"),
    ("CALI SUR CICSA",               "CALI",    "Si","Si"),
    ("Candelaria CONECTAR",          "VACANA",  "No","Si"),
    ("Cartago CONECTAR",             "VACANA",  "No","Si"),
    ("Cerrito CONECTAR",             "VACANA",  "No","No"),
    ("Chicoral CONECTAR",            "TOLHUCA", "No","No"),
    ("Ciudad del Campo CONECTAR",    "VACANA",  "No","No"),
    ("Espinal CONECTAR",             "TOLHUCA", "No","No"),
    ("Flandes CONECTAR",             "TOLHUCA", "No","No"),
    ("Florencia CONECTAR",           "TOLHUCA", "No","Si"),
    ("Florida CONECTAR",             "VACANA",  "No","No"),
    ("Garzon CICSA",                 "TOLHUCA", "No","Si"),
    ("Guamo CONECTAR",               "TOLHUCA", "No","Si"),
    ("Ibague CONECTAR",              "TOLHUCA", "Si","Si"),
    ("Ipiales CICSA",                "VACANA",  "No","Si"),
    ("Jamundi CICSA",                "CALI",    "No","Si"),
    ("La Union CONECTAR",            "VACANA",  "No","Si"),
    ("Melgar CONECTAR",              "TOLHUCA", "No","No"),
    ("Neiva CICSA",                  "TOLHUCA", "Si","Si"),
    ("Palmira CONECTAR",             "VACANA",  "Si","Si"),
    ("Pasto CICSA",                  "VACANA",  "Si","Si"),
    ("Pitalito CICSA",               "TOLHUCA", "No","Si"),
    ("Popayan CICSA",                "VACANA",  "Si","Si"),
    ("Pradera CONECTAR",             "VACANA",  "No","No"),
    ("Puerto Tejada CICSA",          "VACANA",  "No","Si"),
    ("Roldanillo CONECTAR",          "VACANA",  "No","Si"),
    ("Santander de Quilichao CICSA", "VACANA",  "No","No"),
    ("Sevilla CONECTAR",             "VACANA",  "No","Si"),
    ("Tulua CONECTAR",               "VACANA",  "No","Si"),
    ("Yumbo CONECTAR",               "CALI",    "Si","Si"),
    ("Zarzal CONECTAR",              "VACANA",  "No","Si"),
], columns=["Categoria","Territorio","Meta_Modernizacion","Ciudad_tiene_FTTH"])

FRANJAS_MAP = {
    "07-13":"AM","13-18":"PM","07-18":"ALL DAY","14-20":"PM","18:00-20:30":"PM",
    "07-10":"AM","01-06":"AM","06-10":"AM","07-09":"AM","08-10":"AM",
    "09-11":"AM","10-13":"AM","11-13":"AM","14-16":"PM","14-17":"PM",
    "16-18":"PM","17-19":"PM","18-22":"PM",
}

# ── CARGA ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_datos():
    try:
        conn = mysql.connector.connect(**DB)
        df = pd.read_sql("""
            SELECT fecha, zona, franja_horaria, categoria,
                   quota_pct, used_quota_pct, status, close_time,
                   max_available, quota_mins, booked_activities, used
            FROM uso_cupos
            ORDER BY fecha DESC, zona, franja_horaria, categoria
        """, conn)
        # Última actualización = MAX(fecha_carga) en toda la tabla
        cur = conn.cursor()
        cur.execute("SELECT MAX(fecha_carga) FROM uso_cupos")
        row = cur.fetchone()
        ultima_actualizacion = row[0] if row and row[0] else None
        cur.close()
        conn.close()
        return df, None, ultima_actualizacion
    except Exception as e:
        return pd.DataFrame(), str(e), None


def enriquecer(df):
    """
    Aplica exactamente las fórmulas DAX de Power BI:
      Min_Trabajo     = RELATED(Tabla_Trabajos[Minutos])
      Cupos_Abiertos  = IFERROR(quota_mins / Min_Trabajo, 0)
      Cupos_Usados    = IF(ISBLANK(booked_activities), 0, booked_activities)
      Cupos_Libres    = Cupos_Abiertos - Cupos_Usados
    """
    if df.empty:
        return df

    df = df.copy()
    df["zona"]           = df["zona"].str.strip()
    df["categoria"]      = df["categoria"].str.strip()
    df["franja_horaria"] = df["franja_horaria"].str.strip()

    # Lookup dicts (evita merge duplicador)
    min_d  = dict(zip(TRABAJOS["Trabajo"].str.strip(), TRABAJOS["Minutos"]))
    red_d  = dict(zip(TRABAJOS["Trabajo"].str.strip(), TRABAJOS["Red"]))
    act_d  = dict(zip(TRABAJOS["Trabajo"].str.strip(), TRABAJOS["Actividad"]))
    ter_d  = dict(zip(TABLA_FTTH["Categoria"].str.strip(), TABLA_FTTH["Territorio"]))
    meta_d = dict(zip(TABLA_FTTH["Categoria"].str.strip(), TABLA_FTTH["Meta_Modernizacion"]))
    ftth_d = dict(zip(TABLA_FTTH["Categoria"].str.strip(), TABLA_FTTH["Ciudad_tiene_FTTH"]))

    df["Min_Trabajo"]        = df["categoria"].map(min_d).fillna(0).astype(float)
    df["Red"]                = df["categoria"].map(red_d).fillna("HFC")
    df["Tipo_Orden"]         = df["categoria"].map(act_d).fillna("")
    df["Gerencia"]           = df["zona"].map(ter_d).fillna("")
    df["Meta_Modernizacion"] = df["zona"].map(meta_d).fillna("No")
    df["Ciudad_tiene_FTTH"]  = df["zona"].map(ftth_d).fillna("No")
    df["Franja_H"]           = df["franja_horaria"].map(FRANJAS_MAP).fillna("")
    df["Aliado_Final"]       = df["zona"].apply(lambda z:
        "CONECTAR TV" if "CONECTAR" in str(z).upper()
        else ("TABASCO" if "CICSA" in str(z).upper() else ""))

    # DAX exacto
    qm = pd.to_numeric(df["quota_mins"], errors="coerce")
    mt = df["Min_Trabajo"]
    df["Cupos_Abiertos"] = np.where((mt > 0) & qm.notna(), qm / mt, 0)
    df["Cupos_Usados"]   = pd.to_numeric(df["booked_activities"], errors="coerce").fillna(0)
    df["Cupos_Libres"]   = df["Cupos_Abiertos"] - df["Cupos_Usados"]
    df["Uso_Cap"]        = np.where(df["Cupos_Abiertos"]>0,
                                     df["Cupos_Usados"]/df["Cupos_Abiertos"], 0)
    df["fecha"]          = pd.to_datetime(df["fecha"])
    return df


# ── ESTILOS GLOBALES ──────────────────────────────────────────────────────────
st.markdown("""
<style>
html,body,[class*="css"]{font-family:'Segoe UI',Arial,sans-serif!important}
.stApp{background:#f4f6f9 !important;color:#1a1816 !important}
[data-testid="stAppViewContainer"]{background:#f4f6f9 !important}
[data-testid="block-container"]{background:#f4f6f9 !important;padding-top:1rem!important}
section[data-testid="stSidebar"]{background:#ffffff !important;border-right:1px solid #dde3ec !important}
section[data-testid="stSidebar"] *{color:#1a1816 !important;font-family:'Segoe UI',Arial,sans-serif!important}
.stTabs [data-baseweb="tab-list"]{background:#ffffff !important;border-bottom:2px solid #dde3ec !important}
.stTabs [data-baseweb="tab"]{color:#555 !important;font-family:'Segoe UI',Arial,sans-serif!important}
.stTabs [aria-selected="true"]{color:#c00 !important;border-bottom-color:#c00 !important;font-weight:600!important}
.page-header{margin-bottom:.5rem}
.page-sub{font-size:.78rem;color:#7a7670;margin-top:.1rem}
</style>
""", unsafe_allow_html=True)

# ── INICIALIZAR ───────────────────────────────────────────────────────────────
raw, error, ultima_actualizacion = cargar_datos()
if error:
    st.error(f"❌ Error BD: {error}")
    st.stop()

df = enriquecer(raw)
if df.empty:
    st.warning("Sin datos en la BD.")
    st.stop()

fechas_disp = sorted(df["fecha"].dt.date.unique(), reverse=True)

# Meses y años disponibles
MESES_NUM = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
             7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

meses_anios_disp = sorted(
    df["fecha"].dt.to_period("M").unique(), reverse=True
)
meses_anios_str  = [str(m) for m in meses_anios_disp]  # "2026-03", "2026-02", ...

def fmt_mes(s):
    y,m = s.split("-")
    return f"{MESES_NUM.get(int(m),m)} {y}"

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔴 CAPACIDADES - R3")
    st.markdown("**Región Occidente · Claro**")
    st.markdown("---")

    # ── Filtro Mes/Año ─────────────────────────────────────────────────────────
    st.markdown("**📆 Mes / Año**")
    mes_sel = st.multiselect("",
        options=meses_anios_str,
        default=[meses_anios_str[0]],
        format_func=fmt_mes,
        placeholder="Todos los meses",
        label_visibility="collapsed")
    if not mes_sel:
        mes_sel = [meses_anios_str[0]]

    # Fechas disponibles dentro de los meses seleccionados
    fechas_en_mes = sorted([
        f for f in fechas_disp
        if f.strftime("%Y-%m") in mes_sel
    ], reverse=True)

    st.markdown("**📅 Días**")
    fechas_sel = st.multiselect("",
        options=fechas_en_mes,
        default=fechas_en_mes,
        format_func=lambda d: d.strftime("%d/%m/%Y (%a)"),
        placeholder="Todos los días del mes",
        label_visibility="collapsed")
    if not fechas_sel:
        fechas_sel = fechas_en_mes if fechas_en_mes else fechas_disp[:1]

    st.markdown("---")

    # ── Filtro Red ─────────────────────────────────────────────────────────────
    st.markdown("**📡 Red**")
    red_sel = st.multiselect("Red",
        options=["FTTH","HFC","FWA"],
        default=[],
        placeholder="Todas",
        label_visibility="collapsed")

    st.markdown("**🏙️ Ciudad**")
    ciudad_sel = st.multiselect("Ciudad",
        options=sorted(df["zona"].dropna().unique()),
        default=[], placeholder="Todas", label_visibility="collapsed")

    st.markdown("**⏰ Franja**")
    franja_sel = st.multiselect("Franja",
        options=["AM","PM","ALL DAY"],
        default=[], placeholder="Todas", label_visibility="collapsed")

    st.markdown("**🤝 Aliado**")
    aliado_sel = st.multiselect("Aliado", options=["CONECTAR TV","TABASCO"],
        default=[], placeholder="Todos", label_visibility="collapsed")

    st.markdown("**🗺️ Territorio**")
    territorio_sel = st.multiselect("Territorio",
        options=sorted(df["Gerencia"].dropna().unique()),
        default=[], placeholder="Todos", label_visibility="collapsed")

    st.markdown("**⚠️ Uso Capacidad**")
    uso_menor_50 = st.checkbox("Mostrar solo ciudades < 50%", value=False)

    st.markdown("---")


    with st.expander("🔧 Diagnóstico BD", expanded=False):
        cols_ok = [c for c in raw.columns if raw[c].notna().sum()>0]
        st.caption(f"Registros: {len(raw):,}")
        st.caption(f"Columnas con datos: {', '.join(cols_ok)}")
        st.dataframe(raw[cols_ok].head(5), use_container_width=True)

# ── FILTRO GLOBAL ─────────────────────────────────────────────────────────────
mask = df["fecha"].dt.date.isin(fechas_sel)
if red_sel:        mask &= df["Red"].isin(red_sel)
if ciudad_sel:     mask &= df["zona"].isin(ciudad_sel)
if franja_sel:     mask &= df["Franja_H"].isin(franja_sel)
if aliado_sel:     mask &= df["Aliado_Final"].isin(aliado_sel)
if territorio_sel: mask &= df["Gerencia"].isin(territorio_sel)
dff = df[mask].copy()

# ── FILTROS POR PÁGINA (del PBIX) ────────────────────────────────────────────
FILTROS_PAGINA = {
    "Meta Modernización": {
        "Tipo_Orden":         ["Bronwfield"],
        "Meta_Modernizacion": ["Si"],
    },
    "Instalaciones FTTH": {
        "Tipo_Orden":        ["Instalaciones"],
        "Ciudad_tiene_FTTH": ["Si"],
        "Red":               ["FTTH"],
    },
    "Instalaciones HFC": {
        "Tipo_Orden": ["Instalaciones","Instalaciones Básica"],
        "Red":        ["HFC"],
        "_excluir_zona": [
            "Andalucia CONECTAR","Caicedonia CONECTAR","Cartago CONECTAR",
            "Guamo CONECTAR","Ipiales CICSA","La Union CONECTAR","Pitalito CICSA",
            "Roldanillo CONECTAR","Sevilla CONECTAR","Zarzal CONECTAR","Garzon CICSA",
        ],
    },
    "Arreglos":       {"Tipo_Orden": ["Arreglos"]},
    "Posventas":      {"Tipo_Orden": ["Posventas"]},
    "General FTTH": {
        "Red":               ["FTTH"],
        "Ciudad_tiene_FTTH": ["Si"],
    },
    "Total Trabajos": {},  # filtro dinámico por categoría — se aplica dentro del tab
    "Pymes": {
        "categoria": ["Brownfield PYMES","HFC  Arreglos Pymes","HFC  Instalacion Pymes",
                      "HFC Postventa Pymes","HFC  Traslados pymes"],
    },
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
DIAS_ES  = {"Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
            "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"}
MESES_ES = {"January":"enero","February":"febrero","March":"marzo","April":"abril",
            "May":"mayo","June":"junio","July":"julio","August":"agosto",
            "September":"septiembre","October":"octubre","November":"noviembre",
            "December":"diciembre"}

def fmt_fecha(d):
    return f"{DIAS_ES.get(d.strftime('%A'),'')} {d.day:02d} de {MESES_ES.get(d.strftime('%B'),'')} de {d.year}"

def uso_bg(u):
    """Colores de fondo/texto para columna Uso Capacidad (igual Power BI)"""
    if u >= 0.9:   return "#c6efce","#276221"   # verde: >= 90%
    elif u >= 0.5: return "#ffeb9c","#9c6500"   # amarillo: 50-89%
    else:          return "#ffc7ce","#9c0006"   # rojo: < 50%

def uso_icon(u):
    """Icono de estado al final de fila según uso"""
    if u >= 0.9:   return '<span style="color:#276221;font-size:1rem">✅</span>'
    elif u >= 0.5: return '<span style="color:#9c6500;font-size:1rem">⚠️</span>'
    else:          return '<span style="color:#9c0006;font-size:1rem">❌</span>'

def barra_uso(u):
    """Barra de progreso horizontal dentro de la celda"""
    pct = min(u * 100, 100)
    if u >= 0.9:   bar_color = "#70ad47"
    elif u >= 0.5: bar_color = "#ffc000"
    else:          bar_color = "#ff0000"
    bg,fg = uso_bg(u)
    return (f'<div style="display:flex;align-items:center;gap:5px;justify-content:flex-end">'
            f'<div style="width:50px;height:10px;background:#e0e0e0;border-radius:3px;overflow:hidden;flex-shrink:0">'
            f'<div style="width:{pct:.0f}%;height:100%;background:{bar_color};border-radius:3px"></div></div>'
            f'<span style="font-weight:700;color:{fg};min-width:38px;text-align:right">{u:.0%}</span>'
            f'</div>')

# ── RENDER ────────────────────────────────────────────────────────────────────
def render_pagina(df_full, titulo, filtro_extra=None, aplicar_filtro_uso=False):
    d = df_full.copy()

    if filtro_extra:
        for col, val in filtro_extra.items():
            if col == "_excluir_zona":
                d = d[~d["zona"].isin(val)]
            elif isinstance(val, list):
                d = d[d[col].isin(val)]
            else:
                d = d[d[col] == val]

    if aplicar_filtro_uso:
        uso_ciudad = d.groupby("zona")[["Cupos_Usados", "Cupos_Abiertos"]].sum()
        uso_ciudad["Uso"] = np.where(uso_ciudad["Cupos_Abiertos"] > 0,
                                     uso_ciudad["Cupos_Usados"] / uso_ciudad["Cupos_Abiertos"], 0)
        ciudades_filtradas = uso_ciudad[uso_ciudad["Uso"] < 0.5].index
        d = d[d["zona"].isin(ciudades_filtradas)]

    fechas = sorted(d["fecha"].dt.date.unique())

    if d.empty:
        st.info("Sin datos con los filtros aplicados.")
        return

    agg = d.groupby(["Gerencia","zona","fecha"], as_index=False).agg(
        Ab=("Cupos_Abiertos","sum"),
        Us=("Cupos_Usados","sum"),
        Li=("Cupos_Libres","sum"),
    )
    agg["fd"] = agg["fecha"].dt.date

    ger_agg = agg.groupby(["Gerencia","fd"], as_index=False).agg(
        Ab=("Ab","sum"), Us=("Us","sum"), Li=("Li","sum"))
    ciu_agg = agg.groupby(["Gerencia","zona","fd"], as_index=False).agg(
        Ab=("Ab","sum"), Us=("Us","sum"), Li=("Li","sum"))
    tot_agg = agg.groupby("fd", as_index=False).agg(
        Ab=("Ab","sum"), Us=("Us","sum"), Li=("Li","sum"))

    def get_met(src, keys):
        data = []; ta=tu=tl=0
        for f in fechas:
            s = src.copy()
            for k,v in keys.items(): s = s[s[k]==v]
            s = s[s["fd"]==f]
            if s.empty: data.append((0,0,0,0))
            else:
                a=s["Ab"].sum(); u=s["Us"].sum(); l=s["Li"].sum()
                data.append((a,u,l, u/a if a>0 else 0))
                ta+=a; tu+=u; tl+=l
        data.append((ta,tu,tl, tu/ta if ta>0 else 0))
        return data

    def libres_icon(l):
        li = int(round(l))
        if li <= 0:  return '<span style="font-size:.95rem">🔴</span>'
        elif li < 4: return '<span style="font-size:.95rem">🟡</span>'
        else:        return '<span style="font-size:.95rem">🟢</span>'

    def cells_html(mets, bold=False, is_total=False):
        h = ""
        total_uso = mets[-1][3] if mets else 0
        for i,(a,u,l,uso) in enumerate(mets):
            last = (i == len(mets)-1)
            # Separador visual entre bloques de fecha y bloque total
            bl_style = "border-left:2px solid #a0c4e8;" if not last else "border-left:3px solid #6aab8e;"
            bg_uso, fg_uso = uso_bg(uso)
            fw = "font-weight:700;" if bold or is_total else ""
            bg_row = ""
            icon = libres_icon(l)
            h += (
                f'<td style="{bl_style}{fw}text-align:right;padding:5px 10px;{bg_row}">{a:,.0f}</td>'
                f'<td style="{fw}text-align:right;padding:5px 10px;{bg_row}">{u:,.0f}</td>'
                f'<td style="{fw}text-align:right;padding:5px 10px;{bg_row}white-space:nowrap">{icon}&nbsp;{l:,.0f}</td>'
                f'<td style="padding:5px 8px;{bg_row}min-width:130px">{barra_uso(uso)}</td>'
            )
        # Icono de estado al final (basado en uso total de la fila = último período Total)
        h += f'<td style="text-align:center;padding:5px 8px;border-left:1px solid #dde3ec">{uso_icon(total_uso)}</td>'
        return h

    nf = len(fechas)

    # ── ENCABEZADO PRINCIPAL ────────────────────────────────────────────────
    # Fila 1: título + fechas + total
    h_titulo = f'''<th colspan="{1 + (nf+1)*4 + 1}"
        style="background:#000000;color:#ffffff;text-align:center;
               padding:10px;font-size:.95rem;font-weight:700;
               letter-spacing:.05em;border:1px solid #333">
        {titulo.upper()}
    </th>'''

    # Fila 2: Fecha/Gerencia + bloques de fechas + Total
    h_sub = '''<th rowspan="2" style="background:#E0F7FF;color:#1a3a6f;text-align:center;
                  vertical-align:bottom;min-width:210px;padding:7px 10px;
                  border:1px solid #b8d4e8;font-size:.72rem;font-weight:700">
        Fecha<br>Gerencia
    </th>'''
    for f in fechas:
        h_sub += (f'<th colspan="4" style="text-align:center;background:#E0F7FF;color:#1a3a6f;'
                  f'border-left:2px solid #a0c4e8;border-bottom:1px solid #b8d4e8;'
                  f'padding:7px 4px;font-size:.72rem;font-weight:700;white-space:nowrap">'
                  f'{fmt_fecha(f)}</th>')
    h_sub += ('<th colspan="4" style="text-align:center;background:#d4edda;color:#1a5030;'
              'border-left:3px solid #6aab8e;border-bottom:1px solid #a8d5be;'
              'padding:7px 4px;font-size:.72rem;font-weight:700">Total</th>'
              '<th style="background:#E0F7FF;border:1px solid #b8d4e8;padding:7px 4px;font-size:.72rem;font-weight:700;color:#1a3a6f;text-align:center">Estado</th>')

    # Fila 3: sub-métricas
    h_met = ""
    for _ in range(nf + 1):
        for m,w in [("Abiertos","65px"),("Usados","65px"),("Libres","80px"),("Uso Capacidad","130px")]:
            bl = "border-left:2px solid #a0c4e8;" if _ < nf else "border-left:3px solid #6aab8e;"
            h_met += (f'<th style="min-width:{w};text-align:right;background:#E0F7FF;color:#1a3a6f;'
                      f'{bl}padding:5px 8px;font-size:.65rem;font-weight:700;white-space:nowrap;border-bottom:1px solid #b8d4e8">'
                      f'{m}</th>')
    h_met += '<th style="background:#E0F7FF;border-left:1px solid #dde3ec;padding:5px 8px;font-size:.65rem;font-weight:700;color:#1a3a6f;text-align:center">KPI</th>'

    # ── FILAS GERENCIA + CIUDADES ───────────────────────────────────────────
    gerencias = sorted(d["Gerencia"].dropna().unique())
    # Colores lila para gerencias (alternado)
    GER_COLORS = ["#e8e4f3","#ddd7f0","#d2cbed"]
    body = ""
    for gi, ger in enumerate(gerencias):
        gid    = f"g{gi}"
        gc     = GER_COLORS[gi % len(GER_COLORS)]
        gm     = cells_html(get_met(ger_agg,{"Gerencia":ger}), bold=True)
        body  += (f'<tr style="background:{gc};cursor:pointer;border-top:1px solid #c8c0e0" onclick="tog(\'{gid}\')">' 
                  f'<td style="font-weight:700;color:#2d1f6e;padding:7px 10px;white-space:nowrap;font-size:.78rem">'
                  f'<span id="ic_{gid}" style="display:inline-block;width:16px;font-size:.65rem;color:#6a5acd">⊟</span>'
                  f'&nbsp;{ger}</td>{gm}</tr>')
        ciudades = sorted(d[d["Gerencia"]==ger]["zona"].dropna().unique())
        for ci, ciu in enumerate(ciudades):
            cm    = cells_html(get_met(ciu_agg,{"Gerencia":ger,"zona":ciu}))
            bg_ciu = "#ffffff" if ci % 2 == 0 else "#f7f7fb"
            body += (f'<tr class="c_{gid}" style="background:{bg_ciu};border-top:1px solid #ece9f0">'
                     f'<td style="padding:5px 10px 5px 30px;color:#444;font-size:.74rem;white-space:nowrap">'
                     f'<span style="color:#9090b0;margin-right:4px">⊞</span>{ciu}</td>{cm}</tr>')

    # ── FILA TOTAL ──────────────────────────────────────────────────────────
    tm=[]; ta=tu=tl=0
    for f in fechas:
        fr=tot_agg[tot_agg["fd"]==f]
        if fr.empty: tm.append((0,0,0,0))
        else:
            a=fr["Ab"].sum(); u=fr["Us"].sum(); l=fr["Li"].sum()
            tm.append((a,u,l, u/a if a>0 else 0)); ta+=a; tu+=u; tl+=l
    tm.append((ta,tu,tl, tu/ta if ta>0 else 0))

    body += (f'<tr style="background:#cce5ff;border-top:2px solid #7aa8d4">'
             f'<td style="font-weight:700;color:#003366;padding:7px 10px;font-size:.8rem">Total</td>'
             f'{cells_html(tm, bold=True, is_total=True)}</tr>')

    # ── ALTURA DINÁMICA ─────────────────────────────────────────────────────
    n_tot = len(gerencias) + sum(
        len(d[d["Gerencia"]==g]["zona"].dropna().unique()) for g in gerencias) + 3
    altura = max(180, min(n_tot * 34 + 120, 900))

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box}}
body{{margin:0;padding:0;background:#ffffff;color:#1a1816;
     font-family:'Segoe UI',Arial,sans-serif;font-size:.78rem}}
.wrap{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;border:1px solid #ccd6e0}}
thead th{{border:1px solid #b8d4e8}}
tbody td{{border-bottom:1px solid #e8e4f0;border-right:1px solid #f0eef8}}
tbody tr:hover td{{filter:brightness(.96)}}
</style></head><body>
<div class="wrap"><table>
<thead>
  <tr>{h_titulo}</tr>
  <tr>{h_sub}</tr>
  <tr>{h_met}</tr>
</thead>
<tbody>{body}</tbody>
</table></div>
<script>
function tog(id){{
  var rows=document.querySelectorAll('.c_'+id);
  var ic=document.getElementById('ic_'+id);
  var open=ic.textContent==='⊟';
  rows.forEach(function(r){{r.style.display=open?'none':'table-row'}});
  ic.textContent=open?'⊞':'⊟';
}}
</script>
</body></html>"""

    components.html(html, height=altura, scrolling=True)


# ── ENCABEZADO ESTÉTICO (MAIN AREA) ───────────────────────────────────────────
ua_cot_str = "N/A"
if ultima_actualizacion:
    COT = timezone(timedelta(hours=-5))
    ua_cot = ultima_actualizacion.replace(tzinfo=timezone.utc).astimezone(COT)
    ua_cot_str = ua_cot.strftime('%Y-%m-%d %H:%M')

ultima_carga_str = df['fecha'].max().strftime('%Y-%m-%d') if not df.empty else "N/A"

header_html = f"""
<div style="
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #ffffff;
    padding: 18px 25px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    border: 1px solid #eaeaea;
    border-left: 6px solid #e61c24;
    margin-bottom: 20px;
">
    <h1 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #1a1816; letter-spacing: -0.5px;">
        USO DE LA CAPACIDAD EN CUPOS <span style="color: #e61c24;">- R3</span>
    </h1>
    <div style="display: flex; align-items: center; gap: 12px; background: #f8f9fa; padding: 10px 18px; border-radius: 8px; border: 1px solid #e9ecef;">
        <span style="font-size: 1.4rem;">⏱️</span>
        <div style="color: #495057; font-size: 0.85rem; line-height: 1.3;">
            <div style="font-weight: 600;">Actualizado: <span style="font-weight: 400;">{ua_cot_str} (COT)</span></div>
            <div style="font-weight: 600;">Última carga: <span style="font-weight: 400; color: #6c757d;">{ultima_carga_str}</span></div>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
paginas = ["Meta Modernización","Instalaciones FTTH","Instalaciones HFC",
           "Arreglos","Posventas","General FTTH","Total Trabajos","Pymes"]

tabs = st.tabs(paginas)
for tab, pag in zip(tabs, paginas):
    with tab:
        if pag == "Total Trabajos":
            # ── Filtro de categoría dentro del tab ────────────────────────────
            cats_disponibles = sorted(dff["categoria"].dropna().unique())

            st.markdown(
                '<p style="font-weight:600;font-size:.85rem;margin-bottom:4px">'
                '🔧 Filtrar por Categoría / Trabajo</p>',
                unsafe_allow_html=True
            )
            col1, col2 = st.columns([5, 1])
            with col1:
                cats_sel = st.multiselect(
                    "Categoría",
                    options=cats_disponibles,
                    default=[],
                    placeholder=f"Todas las categorías ({len(cats_disponibles)} disponibles)",
                    label_visibility="collapsed",
                    key="cats_total_trabajos"
                )
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Limpiar", key="limpiar_cats"):
                    cats_sel = []

            # Mostrar cuántas categorías están activas
            if cats_sel:
                st.caption(f"Mostrando {len(cats_sel)} de {len(cats_disponibles)} categorías")
            else:
                st.caption(f"Mostrando todas las categorías ({len(cats_disponibles)})")

            # Aplicar filtro
            dff_tt = dff[dff["categoria"].isin(cats_sel)].copy() if cats_sel else dff.copy()
            render_pagina(dff_tt, "Total Trabajos", None, aplicar_filtro_uso=uso_menor_50)
        else:
            filtro = FILTROS_PAGINA.get(pag, {})
            render_pagina(dff, pag, filtro or None, aplicar_filtro_uso=uso_menor_50)
