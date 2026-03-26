"""
app.py  —  Control Maestro de Reforma Curricular
Página principal: Resumen General
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import math
from utils.data_loader import (
    load_data, enrich_df, apply_filters, ETAPAS_MAP, PROCESOS,
    PROCESO_COLOR, STATUS_LABEL, STATUS_COLOR, color_for_pct,
)

st.set_page_config(
    page_title="Reforma Curricular · POLI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS modo claro · colores institucionales ───────────────────────────────────
st.markdown("""
<style>
/* ── Fondos generales ── */
[data-testid="stAppViewContainer"] { background: #EEF3F8; }
/* Header de Streamlit (barra superior delgada) coincide con el degradado */
[data-testid="stHeader"] {
    background: linear-gradient(135deg, #0F385A 0%, #1A5276 50%, #1FB2DE 100%) !important;
    border-bottom: 3px solid #42F2F2 !important;
}
h1,h2,h3,h4,h5                     { font-family: 'Segoe UI', sans-serif; color: #0F385A !important; }
p, li, label, caption               { color: #2a4a5e; }
[data-testid="stCaption"]           { color: #6a8a9e !important; }
/* ── Block container ── */
.block-container { padding-top: 3.5rem !important; padding-bottom: 2rem; }
/* ── Selectbox — fondo diferenciado azul muy claro ── */
div[data-baseweb="select"] > div {
    background: #E3F4FB !important;
    border-color: rgba(31,178,222,0.45) !important;
    color: #0F385A !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] span    { color: #0F385A !important; }
[data-testid="stSelectbox"] label  { font-size: 12px; color: #4a6a7e; }
/* ── Dropdown list (options) ── */
ul[data-baseweb="menu"]            { background: #FFFFFF !important; border: 1px solid rgba(31,178,222,0.30) !important; box-shadow: 0 6px 20px rgba(15,56,90,0.14) !important; border-radius: 8px !important; }
ul[data-baseweb="menu"] li         { color: #0F385A !important; background: #FFFFFF !important; }
ul[data-baseweb="menu"] li:hover   { background: #E3F4FB !important; }
li[aria-selected="true"]           { background: #d0ecf8 !important; font-weight: 600 !important; }
/* ── Tabs ── */
button[data-baseweb="tab"]         { color: #6a8a9e !important; background: transparent !important; font-size: 13px !important; font-weight: 500 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #0F385A !important; border-bottom-color: #1FB2DE !important; font-weight: 700 !important; }
[data-testid="stDataFrame"]        { border-radius: 10px; overflow: hidden; box-shadow: 0 1px 6px rgba(15,56,90,0.08); }
hr                                  { border-color: rgba(15,56,90,0.10) !important; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
[data-testid="stExpander"]         { background: #FFFFFF; border: 1px solid rgba(15,56,90,0.10); border-radius: 10px; }
/* Info box */
[data-testid="stNotification"]     { background: #e8f6fc !important; color: #0F385A !important; border-color: #1FB2DE !important; }
/* ── Sidebar con degradado ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F385A 0%, #1A5276 45%, #1FB2DE 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebarNav"] { display: none !important; }
/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label  { color: rgba(255,255,255,0.80) !important; }
[data-testid="stSidebar"] hr     { border-color: rgba(255,255,255,0.20) !important; }
/* Page link buttons en sidebar */
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    color: rgba(255,255,255,0.82) !important;
    background: rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    padding: 8px 12px 8px 10px !important;
    margin-bottom: 3px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: background .15s;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(255,255,255,0.18) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: rgba(255,255,255,0.22) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border-left: 3px solid #42F2F2 !important;
}
/* Download button */
[data-testid="stDownloadButton"] > button {
    background: #1FB2DE !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #0F385A !important;
}
/* ── Pills / botones de filtro ── */
[data-testid="stPills"] button,
[data-testid="stSegmentedControl"] button {
    border: 2px solid #1A5276 !important;
    color: #1A5276 !important;
    background: #FFFFFF !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    transition: all .15s !important;
    box-shadow: 0 1px 3px rgba(15,56,90,0.12) !important;
}
[data-testid="stPills"] button:hover,
[data-testid="stSegmentedControl"] button:hover {
    border-color: #1FB2DE !important;
    background: #1FB2DE !important;
    color: #FFFFFF !important;
}
[data-testid="stPills"] button[aria-checked="true"],
[data-testid="stPills"] button[aria-pressed="true"],
[data-testid="stPills"] button[data-active="true"],
[data-testid="stSegmentedControl"] button[aria-selected="true"] {
    background: #0F385A !important;
    color: #FFFFFF !important;
    border-color: #0F385A !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 6px rgba(15,56,90,0.30) !important;
}
/* LIMPIAR button */
[data-testid="stBaseButton-primary"] {
    background: #0F385A !important; border-color: #0F385A !important;
    color: #FFFFFF !important; font-size: 12px !important; font-weight: 700 !important;
    border-radius: 8px !important;
}
[data-testid="stBaseButton-primary"]:hover {
    background: #1A5276 !important; border-color: #1A5276 !important;
}
/* ── Compact filter bar: collapse gap between pill rows ── */
.stVerticalBlock:has([data-testid="stPills"]) {
    gap: 0.1rem !important;
    row-gap: 0.1rem !important;
}
[data-testid="stPills"] {
    padding-bottom: 0 !important;
    margin-bottom: 0 !important;
    min-height: unset !important;
}
[data-testid="stHorizontalBlock"]:has([data-testid="stPills"]) {
    align-items: center !important;
    padding-bottom: 0 !important;
    margin-bottom: 0 !important;
}
/* Remove excess space below filter block and before tabs */
.stVerticalBlock:has([data-testid="stPills"]) + .stVerticalBlock {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
.stMainBlockContainer [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPills"]) {
    margin-bottom: 2px !important;
    padding-bottom: 2px !important;
}
/* Tighten gap between top-level page blocks (header → filters → tabs) */
.stMainBlockContainer > div > div > .stVerticalBlock { gap: 0.4rem !important; }
/* Remove top margin on tabs bar */
[data-testid="stTabs"] { margin-top: 0 !important; padding-top: 0 !important; }
[data-baseweb="tab-list"] { margin-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Datos ──────────────────────────────────────────────────────────────────────
df_raw = enrich_df(load_data())

fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}
fac_abrev = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación":    "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
}
fac_inv       = {v: k for k, v in fac_labels.items()}
fac_abrev_inv = {v: k for k, v in fac_abrev.items()}
FAC_LIST  = list(fac_labels.values())
FAC_PALETTE = {
    "Sociedad, Cultura y Creatividad":   "#EC0677",
    "Ingeniería, Diseño e Innovación":   "#1FB2DE",
    "Negocios, Gestión y Sostenibilidad":"#A6CE38",
}

# ── Sidebar personalizado ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:18px 6px 6px;text-align:center">'
        '<div style="font-size:16px;font-weight:700;color:#FFFFFF;line-height:1.3">'
        'Reforma Curricular</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:10px 0'>", unsafe_allow_html=True)
    st.page_link("app.py",                              label="Resumen General",      icon="📊")
    st.page_link("pages/1_Detalle_por_Etapa.py",        label="Detalle por Etapa",    icon="📋")
    st.page_link("pages/2_Programa.py",                 label="Ficha de Programa",    icon="🔍")
    st.page_link("pages/4_Gestion_Academica.py",        label="Gestión Académica",    icon="📑")
    st.page_link("pages/5_Periodo_Propuesto.py",        label="Periodo Propuesto",    icon="📅")
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="padding:12px 6px;font-size:10px;color:rgba(255,255,255,0.40);text-align:center">'
        'POLI · 2025–2026</div>',
        unsafe_allow_html=True,
    )

# ── Header banner ───────────────────────────────────────────────────────────────
# El stHeader (barra de Streamlit) ya tiene el degradado y cubre todo el ancho.
# Este banner es la continuación dentro del contenido principal.
st.markdown(
    '<div style="'
    'background:linear-gradient(135deg,#0F385A 0%,#1A5276 50%,#1FB2DE 100%);'
    'padding:18px 24px 14px;'
    'margin:0 0 0 0;'
    'border-radius:0 0 12px 12px;'
    'border-bottom:3px solid #42F2F2;">'
    '<div style="font-size:21px;font-weight:700;color:#FFFFFF;letter-spacing:-.3px">'
    'Reforma Curricular de Programas Académicos Poli</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    'Seguimiento de avance por proceso y etapa</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Opciones y helpers de filtro (reutilizados en tabs) ─────────────────────────
_use_pills = hasattr(st, "pills")
_mods_ops  = sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
fac_ops    = sorted([fac_abrev.get(f, f) for f in df_raw["FACULTAD"].dropna().unique()])
_pers_ops  = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())

def _clear_app():
    st.session_state["flt_mod"] = []
    st.session_state["flt_fac"] = []
    st.session_state["flt_per"] = []

_LBL = ('style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;'
        'letter-spacing:.4px;white-space:nowrap"')

# ── Filtrar datos usando session_state (widgets se renderizan dentro de cada tab) ──
_sel_mod = list(st.session_state.get("flt_mod") or [])
_sel_fac = list(st.session_state.get("flt_fac") or [])
_sel_per = list(st.session_state.get("flt_per") or [])
modalidad_f = _sel_mod
facultad_f  = [fac_abrev_inv.get(f, f) for f in _sel_fac]
periodo_f   = _sel_per
df = apply_filters(df_raw.copy(), modalidad_f, facultad_f, periodo_f)
n  = len(df)

# ── Cálculos previos (no rendering) ────────────────────────────────────────────
all_cl   = []
for i in range(len(ETAPAS_MAP)):
    all_cl.extend(df[f"cl_{i}"].tolist())
avg_av   = int(df["avance_general"].mean()) if n > 0 else 0
cnt_adv  = int((df["avance_general"] >= 70).sum())

def clasificar_programa(avance, periodo):
    """Clasificación combinada A+C por avance y periodo de implementación."""
    periodo = str(periodo) if pd.notna(periodo) else ""
    es_2026_o_oferta = "2026" in periodo or "oferta" in periodo.lower() or "Ya en oferta" in periodo
    es_2027_1 = "2027-1" in periodo
    if es_2026_o_oferta and avance < 70:
        return "Urgente"
    if es_2027_1 and avance < 40:
        return "Prioritario"
    if avance < 70:
        return "En seguimiento"
    return "En curso"

if n > 0:
    df["_clasif"] = df.apply(
        lambda r: clasificar_programa(r["avance_general"], r["PERIODO DE IMPLEMENTACIÓN"]), axis=1
    )
    cnt_urgente    = int((df["_clasif"] == "Urgente").sum())
    cnt_prioritario = int((df["_clasif"] == "Prioritario").sum())
    cnt_crit       = cnt_urgente + cnt_prioritario   # para compatibilidad
else:
    df["_clasif"] = "En curso"
    cnt_urgente = cnt_prioritario = cnt_crit = 0
cnt_2026   = int(df["PERIODO DE IMPLEMENTACIÓN"].str.contains("2026",   na=False).sum())
cnt_2027_1 = int(df["PERIODO DE IMPLEMENTACIÓN"].str.contains("2027-1", na=False).sum())
proc_avgs  = {p: (df[f"proc_{p}"].dropna().mean() if df[f"proc_{p}"].dropna().shape[0] > 0 else 0)
              for p in PROCESOS}
proc_min     = min(proc_avgs, key=proc_avgs.get)
proc_max     = max(proc_avgs, key=proc_avgs.get)
proc_min_pct = int(proc_avgs[proc_min])
proc_max_pct = int(proc_avgs[proc_max])

proc_short_map = {
    "Gestión Académica": "Gest. Académica",
    "Gestión Financiera": "Gest. Financiera",
    "Aseguramiento de la Calidad": "Aseg. Calidad",
    "Ger. Planeación y Gestión Institucional": "Ger. Planeación",
    "Producción de Contenidos": "Prod. Contenidos",
    "Convenios Institucionales": "Convenios",
    "Parametrizar Reforma en Banner": "Banner",
    "Publicación en Página Web": "Pág. Web",
}

pct_avgs, done_l, inp_l, nst_l, na_l = [], [], [], [], []
for proc in PROCESOS:
    p_vals = df[f"proc_{proc}"]
    pct_avgs.append(int(p_vals.dropna().mean()) if p_vals.dropna().any() else 0)
    done_l.append(int((p_vals == 100).sum()))
    inp_l .append(int(((p_vals > 0) & (p_vals < 100)).sum()))
    nst_l .append(int((p_vals == 0).sum()))
    na_l  .append(int(p_vals.isna().sum()))

# ── Helper functions ────────────────────────────────────────────────────────────
def _arc(pct, color, r=22, sz=56):
    circ = 2 * math.pi * r
    dash = circ * min(pct, 100) / 100
    gap  = circ - dash
    c    = sz // 2
    return (
        f'<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">'
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="rgba(15,56,90,0.10)" stroke-width="5"/>'
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{color}" stroke-width="5"'
        f' stroke-dasharray="{dash:.2f} {gap:.2f}" stroke-linecap="round"'
        f' transform="rotate(-90 {c} {c})"/>'
        f'</svg>'
    )

def _kpi(label, val, sub, color, pct=None, icon="◈", tooltip=""):
    arc = _arc(pct, color) if pct is not None else (
        f'<div style="width:56px;height:56px;display:flex;align-items:center;'
        f'justify-content:center;font-size:28px">{icon}</div>'
    )
    tip = f' title="{tooltip}"' if tooltip else ""
    return (
        f'<div{tip} style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);'
        f'border-left:4px solid {color};border-radius:12px;'
        f'padding:14px 16px;display:flex;align-items:center;gap:12px;min-height:84px;'
        f'box-shadow:0 2px 8px rgba(15,56,90,0.07);cursor:help">'
        f'<div style="flex-shrink:0">{arc}</div>'
        f'<div style="flex:1;min-width:0">'
        f'<div style="font-size:10px;color:#6a8a9e;text-transform:uppercase;'
        f'letter-spacing:.5px;margin-bottom:3px">{label}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{color};line-height:1.1">{val}</div>'
        f'<div style="font-size:10px;color:#8aabb0;margin-top:2px">{sub}</div>'
        f'</div></div>'
    )

# ── Helper: tarjeta SVG donut + stats integrados ──────────────────────────────
def _donut_card(proc, pct, done, inp, nst, na_val, color, size=128, r=44, sw=13):
    circ  = 2 * math.pi * r
    cx    = size // 2
    total = max(done + inp + nst + na_val, 1)
    _tip  = (f"Proceso: {proc} · Avance promedio: {pct}% | "
             f"De {done+inp+nst+na_val} programas: "
             f"{done} Finalizados · {inp} En Proceso · {nst} Sin iniciar · {na_val} N/A. "
             f"El % es el promedio del avance de este proceso en todos los programas filtrados.")
    segs  = [(done, "#A6CE38"), (inp, "#1FB2DE"), (nst, "#EC0677"), (na_val, "#c8d8e0")]
    arcs  = f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="#edf1f5" stroke-width="{sw}"/>'
    off   = 0.0
    for cnt, sc in segs:
        if cnt == 0:
            continue
        dash = circ * cnt / total
        arcs += (
            f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="{sc}" '
            f'stroke-width="{sw}" stroke-dasharray="{dash:.3f} {circ:.3f}" '
            f'stroke-dashoffset="-{off:.3f}" transform="rotate(-90 {cx} {cx})"/>'
        )
        off += dash
    arcs += (
        f'<text x="{cx}" y="{cx}" text-anchor="middle" dominant-baseline="central" '
        f'font-size="17" font-weight="bold" font-family="Segoe UI,sans-serif" fill="{color}">{pct}%</text>'
    )
    svg   = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">{arcs}</svg>'
    label = proc_short_map.get(proc, proc)
    return (
        f'<div title="{_tip}" style="background:#FFFFFF;border:1px solid rgba(15,56,90,.10);'
        f'border-top:3px solid {color};border-radius:10px;'
        f'padding:10px 8px 8px;box-shadow:0 2px 8px rgba(15,56,90,.06);text-align:center;cursor:help">'
        f'<div style="font-size:10px;font-weight:700;color:{color};text-transform:uppercase;'
        f'letter-spacing:.4px;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;'
        f'white-space:nowrap" title="{proc}">{label}</div>'
        f'<div style="display:flex;justify-content:center;margin:0">{svg}</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:3px;margin-top:5px">'
        f'<div style="font-size:9px;color:#5a7a2e;background:#f0f8e8;padding:2px 4px;border-radius:3px;text-align:center"><b>{done}</b> Fin.</div>'
        f'<div style="font-size:9px;color:#0a6a8e;background:#e8f6fc;padding:2px 4px;border-radius:3px;text-align:center"><b>{inp}</b> Proc.</div>'
        f'<div style="font-size:9px;color:#9a0050;background:#fce8f2;padding:2px 4px;border-radius:3px;text-align:center"><b>{nst}</b> Sin ini.</div>'
        f'<div style="font-size:9px;color:#6a8a9e;background:#f0f4f8;padding:2px 4px;border-radius:3px;text-align:center"><b>{na_val}</b> N/A</div>'
        f'</div></div>'
    )

# ── Colores de clasificación ────────────────────────────────────────────────────
CLASIF_COLORS = {
    "Urgente":        ("#EC0677", "#fce8f2"),
    "Prioritario":    ("#FBAF17", "#fdf8e8"),
    "En seguimiento": ("#2980B9", "#EBF5FB"),
    "En curso":       ("#A6CE38", "#f0f8e8"),
}

# ── Ventana emergente: definición de estados ────────────────────────────────────
_dialog_deco = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)

@_dialog_deco("Clasificación de programas · Criterios de prioridad", width="large")
def _dialog_estados():
    st.markdown(
        "Los programas se clasifican automáticamente en **4 niveles de prioridad** "
        "combinando el **periodo de implementación** y el **% de avance general**. "
        "Esta clasificación determina el nivel de atención requerido."
    )
    clasificaciones = [
        ("Urgente",        "#EC0677", "#fce8f2",
         "Periodo 2026-2 o ya en oferta", "Avance general < 70 %",
         "El programa debe implementarse en el próximo semestre (2026-2) pero "
         "aún no alcanza el avance mínimo requerido. Requiere intervención inmediata "
         "de todas las áreas involucradas para evitar incumplimiento."),
        ("Prioritario",    "#FBAF17", "#fdf8e8",
         "Periodo 2027-1", "Avance general < 40 %",
         "El programa implementa en 2027-1 pero registra un avance muy bajo. "
         "Necesita un plan de aceleración antes de que cierre el semestre actual "
         "para no pasar a estado Urgente."),
        ("En seguimiento", "#2980B9", "#EBF5FB",
         "Cualquier periodo", "Avance general < 70 %",
         "El avance es insuficiente para garantizar la implementación a tiempo, "
         "pero el plazo aún permite corrección. Requiere monitoreo activo y reporte "
         "periódico de avance."),
        ("En curso",       "#A6CE38", "#f0f8e8",
         "Cualquier periodo", "Avance general ≥ 70 %",
         "El programa registra un avance sólido en todos los procesos. Se considera "
         "que avanza al ritmo esperado y no presenta riesgo de incumplimiento en "
         "el corto plazo."),
    ]
    for nombre, fg, bg, periodo, avance, desc in clasificaciones:
        st.markdown(
            f'<div style="background:{bg};border-left:5px solid {fg};border-radius:8px;'
            f'padding:12px 16px;margin-bottom:10px">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
            f'<span style="background:{fg};color:white;font-weight:700;font-size:12px;'
            f'padding:3px 12px;border-radius:12px">{nombre}</span>'
            f'<span style="font-size:11px;color:#4a6a7e">📅 {periodo} &nbsp;·&nbsp; 📊 {avance}</span>'
            f'</div>'
            f'<div style="font-size:12px;color:#2a4a5e;line-height:1.5">{desc}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div style="background:#f0f4f8;border-radius:8px;padding:10px 14px;margin-top:4px">'
        '<span style="font-size:11px;color:#4a6a7e">ℹ️ La clasificación se recalcula '
        'automáticamente al aplicar los filtros de modalidad, facultad o periodo.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Cerrar", use_container_width=True, type="secondary"):
        st.rerun()

def _style_clasif_cell(val):
    """CSS para celda de clasificación."""
    if val in CLASIF_COLORS:
        fg, bg = CLASIF_COLORS[val]
        return f"background-color:{bg};color:{fg};font-weight:700;text-align:center"
    return ""

def _style_avance_cell(val):
    """CSS para celda de avance %."""
    try:
        pct = int(str(val).replace("%", "").strip())
    except Exception:
        return ""
    if pct >= 70:
        return "background-color:#f0f8e8;color:#5a7a2e;font-weight:700;text-align:center"
    if pct >= 40:
        return "background-color:#fef9e8;color:#8a6000;font-weight:700;text-align:center"
    return "background-color:#fce8f2;color:#9a0050;font-weight:700;text-align:center"

def _excel_bytes(df_export):
    """Genera Excel formateado con openpyxl."""
    import io
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment
    from openpyxl.utils import get_column_letter

    clasif_hex = {
        "Urgente":        ("EC0677", "FFFFFF"),
        "Prioritario":    ("FBAF17", "FFFFFF"),
        "En seguimiento": ("2980B9", "FFFFFF"),
        "En curso":       ("A6CE38", "FFFFFF"),
    }

    def _fill(hex6):
        return PatternFill(start_color=hex6, end_color=hex6, fill_type="solid")

    wb = Workbook()
    ws = wb.active
    ws.title = "Resumen"

    headers = list(df_export.columns)
    for ci, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=ci, value=h)
        cell.font = Font(bold=True, color="FFFFFF", size=10)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        if h in PROCESO_COLOR:
            cell.fill = _fill(PROCESO_COLOR[h].lstrip("#"))
        elif h == "Prioridad":
            cell.fill = _fill("0F385A")
        elif h == "Avance %":
            cell.fill = _fill("1FB2DE")
        else:
            cell.fill = _fill("0F385A")
    ws.row_dimensions[1].height = 36

    for ri, row in enumerate(df_export.itertuples(index=False), 2):
        for ci, (h, val) in enumerate(zip(headers, row), 1):
            cell = ws.cell(row=ri, column=ci, value=val)
            cell.alignment = Alignment(horizontal="left" if ci <= 4 else "center", vertical="center")
            if h == "Prioridad" and str(val) in clasif_hex:
                bg, fg = clasif_hex[str(val)]
                cell.fill = _fill(bg)
                cell.font = Font(bold=True, color=fg, size=10)
                cell.alignment = Alignment(horizontal="center")
            elif h == "Avance %":
                try:
                    pct = int(str(val).replace("%", ""))
                    bg = "A6CE38" if pct >= 70 else ("2980B9" if pct >= 40 else "EC0677")
                    fg = "FFFFFF"
                    cell.fill = _fill(bg)
                    cell.font = Font(bold=True, color=fg, size=10)
                    cell.alignment = Alignment(horizontal="center")
                except Exception:
                    pass
            elif h in PROCESO_COLOR:
                hex6 = PROCESO_COLOR[h].lstrip("#")
                r2, g2, b2 = int(hex6[:2], 16), int(hex6[2:4], 16), int(hex6[4:], 16)
                light = f"{min(r2+190,255):02X}{min(g2+190,255):02X}{min(b2+190,255):02X}"
                cell.fill = _fill(light)
                cell.font = Font(color=hex6, bold=True, size=10)
                cell.alignment = Alignment(horizontal="center")

    for ci, h in enumerate(headers, 1):
        col_vals = [ws.cell(r, ci).value or "" for r in range(1, ws.max_row + 1)]
        max_w = max(len(str(v)) for v in col_vals) if col_vals else 10
        ws.column_dimensions[get_column_letter(ci)].width = min(max_w + 3, 35)

    ws.freeze_panes = "A2"
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()

# ── Tabs principales ────────────────────────────────────────────────────────────
tab0, tab_prio, tab2 = st.tabs(["🏆 Resumen Ejecutivo", "🎯 Priorización", "🏛️ Por Facultad y Programa"])

# ── Tab 0: Resumen Ejecutivo ───────────────────────────────────────────────────
with tab0:
    # ── Filtro dentro del tab ──────────────────────────────────────────────────
    with st.container():
        st.markdown('<div style="background:#FFFFFF;border-radius:10px;padding:6px 10px 4px;'
                    'border:1px solid rgba(15,56,90,0.10);box-shadow:0 1px 4px rgba(15,56,90,0.04);'
                    'margin-bottom:6px">', unsafe_allow_html=True)
        _lb1, _in1, _sp0, _lb2, _in2 = st.columns([0.55, 2.2, 0.05, 0.65, 2.2])
        with _lb1: st.markdown(f'<div {_LBL}>📋 MODALIDAD</div>', unsafe_allow_html=True)
        with _in1:
            if _use_pills: st.pills("mod", _mods_ops, selection_mode="multi", key="flt_mod", label_visibility="collapsed")
            else: st.multiselect("mod", _mods_ops, key="flt_mod", label_visibility="collapsed", placeholder="Todas")
        with _lb2: st.markdown(f'<div {_LBL}>🏛️ FACULTAD</div>', unsafe_allow_html=True)
        with _in2:
            if _use_pills: st.pills("fac", fac_ops, selection_mode="multi", key="flt_fac", label_visibility="collapsed")
            else: st.multiselect("fac", fac_ops, key="flt_fac", label_visibility="collapsed", placeholder="Todas")
        _lb3, _in3, _sp0b, _btn0, _cnt0 = st.columns([0.55, 2.2, 0.05, 0.65, 2.2])
        with _lb3: st.markdown(f'<div {_LBL}>📅 PERÍODO</div>', unsafe_allow_html=True)
        with _in3:
            if _use_pills: st.pills("per", _pers_ops, selection_mode="multi", key="flt_per", label_visibility="collapsed")
            else: st.multiselect("per", _pers_ops, key="flt_per", label_visibility="collapsed", placeholder="Todos")
        with _btn0: st.button("✕ LIMPIAR", on_click=_clear_app, use_container_width=True, type="primary", key="app_clear")
        with _cnt0:
            st.markdown(f'<div style="padding-top:9px;font-size:12px;color:#6a8a9e;text-align:right">'
                        f'Mostrando <b style="color:#0F385A">{n}</b> de '
                        f'<b style="color:#0F385A">{len(df_raw)}</b></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── CSS propio del Resumen Ejecutivo (estilos del HTML de referencia) ──────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700;800&family=Barlow+Condensed:wght@600;700;800&display=swap');
    .re-scard{background:#fff;border-radius:10px;padding:14px 16px;border-left:4px solid;
      box-shadow:0 1px 4px rgba(0,0,0,.07);margin-bottom:4px;}
    .re-snum{font-family:'Barlow Condensed',sans-serif;font-size:2.2rem;font-weight:800;
      line-height:1;color:#0F385A;}
    .re-slbl{font-size:.71rem;color:#475569;font-weight:700;text-transform:uppercase;
      letter-spacing:.06em;margin-top:3px;}
    .re-sec{font-family:'Barlow Condensed',sans-serif;font-size:1rem;font-weight:800;
      text-transform:uppercase;letter-spacing:.06em;display:flex;align-items:center;
      gap:8px;margin:18px 0 10px;color:#0F385A;border-bottom:2px solid #e2e8f0;padding-bottom:6px;}
    .re-rcard{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.08);
      overflow:hidden;margin-bottom:8px;display:flex;flex-direction:column;height:100%;}
    .re-rcard-hdr{padding:9px 12px 7px;display:flex;align-items:flex-start;gap:8px;}
    .re-rtbl{width:100%;border-collapse:collapse;font-size:.74rem;}
    .re-rtbl thead th{background:#f1f5f9;padding:5px 8px;text-align:left;font-weight:700;
      font-size:.63rem;text-transform:uppercase;letter-spacing:.05em;color:#475569;
      border-bottom:1px solid #e2e8f0;position:sticky;top:0;z-index:1;}
    .re-rtbl tbody tr:nth-child(even){background:#f8fafc;}
    .re-rtbl tbody tr:hover{background:#e0f4fb;}
    .re-rtbl td{padding:5px 8px;border-bottom:1px solid #f1f5f9;vertical-align:middle;}
    .re-rtbl-wrap{flex:1;overflow-x:auto;overflow-y:auto;max-height:320px;}
    .re-pbar{display:inline-flex;align-items:center;gap:4px;}
    .re-pbar-w{width:50px;height:5px;background:#e2e8f0;border-radius:99px;overflow:hidden;display:inline-block;vertical-align:middle;}
    .re-pbar-f{height:100%;border-radius:99px;}
    .re-ecard{background:#fff;border-radius:10px;padding:14px 16px;
      box-shadow:0 1px 4px rgba(0,0,0,.07);border-left:4px solid;}
    .re-estats{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:9px;}
    .re-estat{display:flex;flex-direction:column;align-items:center;padding:6px 4px;border-radius:7px;}
    .re-estat-num{font-family:'Barlow Condensed',sans-serif;font-size:1.5rem;font-weight:800;line-height:1;}
    .re-estat-lbl{font-size:.59rem;font-weight:700;text-transform:uppercase;letter-spacing:.03em;margin-top:2px;}
    .re-ef{background:#dcfce7;}.re-ef .re-estat-num,.re-ef .re-estat-lbl{color:#15803d;}
    .re-ep{background:#dbeafe;}.re-ep .re-estat-num,.re-ep .re-estat-lbl{color:#1d4ed8;}
    .re-es{background:#fee2e2;}.re-es .re-estat-num,.re-es .re-estat-lbl{color:#dc2626;}
    .re-ena{background:#f1f5f9;}.re-ena .re-estat-num,.re-ena .re-estat-lbl{color:#64748b;}
    .re-ebar-row{display:flex;align-items:center;gap:8px;}
    .re-ebar-w{flex:1;height:6px;background:#e2e8f0;border-radius:99px;overflow:hidden;}
    .re-ebar-f{height:100%;border-radius:99px;}
    .re-ebar-pct{font-family:'Barlow Condensed',sans-serif;font-size:.95rem;font-weight:800;
      color:#0F385A;min-width:34px;text-align:right;}
    .re-ok{padding:10px 14px;font-size:.78rem;color:#15803d;font-weight:600;background:#f0fdf4;
      border-radius:0 0 10px 10px;}
    </style>
    """, unsafe_allow_html=True)

    # ── SECCIÓN 1: Distribución por modalidad y período ────────────────────────
    _cnt_2027_2 = int(df["PERIODO DE IMPLEMENTACIÓN"].str.contains("2027-2", na=False).sum())
    _cnt_oferta = int(df["PERIODO DE IMPLEMENTACIÓN"].str.contains("oferta", case=False, na=False).sum())
    _mod_lower  = df["MODALIDAD"].str.lower().str.strip()
    _cnt_virt   = int((_mod_lower == "virtual").sum())
    _cnt_pres   = int((_mod_lower == "presencial").sum())
    _cnt_hibr   = int((_mod_lower.isin(["híbrido", "hibrido"])).sum())

    def _re_scard(num, lbl, border_color, lbl_color=None):
        lc = lbl_color or border_color
        return (
            f'<div class="re-scard" style="border-color:{border_color}">'
            f'<div class="re-snum">{num}</div>'
            f'<div class="re-slbl" style="color:{lc}">{lbl}</div></div>'
        )

    def _re_sec_lbl(txt):
        return (f'<div style="font-size:9px;font-weight:700;letter-spacing:.08em;color:#94a3b8;'
                f'text-transform:uppercase;margin:6px 0 3px;padding-left:2px">{txt}</div>')

    st.markdown(_re_sec_lbl("DISTRIBUCIÓN POR MODALIDAD"), unsafe_allow_html=True)
    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.markdown(_re_scard(n,          "TOTAL",      "#0F385A", "#0F385A"), unsafe_allow_html=True)
    sm2.markdown(_re_scard(_cnt_virt,  "VIRTUAL",    "#1FB2DE", "#1FB2DE"), unsafe_allow_html=True)
    sm3.markdown(_re_scard(_cnt_pres,  "PRESENCIAL", "#A6CE38", "#A6CE38"), unsafe_allow_html=True)
    sm4.markdown(_re_scard(_cnt_hibr,  "HÍBRIDO",    "#FBAF17", "#FBAF17"), unsafe_allow_html=True)

    st.markdown(_re_sec_lbl("DISTRIBUCIÓN POR PERÍODO"), unsafe_allow_html=True)
    sp1, sp2, sp3, sp4 = st.columns(4)
    sp1.markdown(_re_scard(cnt_2026,    "2026-2",       "#7c3aed", "#7c3aed"), unsafe_allow_html=True)
    sp2.markdown(_re_scard(cnt_2027_1,  "2027-1",       "#EC0677", "#EC0677"), unsafe_allow_html=True)
    sp3.markdown(_re_scard(_cnt_2027_2, "2027-2",       "#0891b2", "#0891b2"), unsafe_allow_html=True)
    sp4.markdown(_re_scard(_cnt_oferta, "YA EN OFERTA", "#A6CE38", "#A6CE38"), unsafe_allow_html=True)

    # ── SECCIÓN 2: Riesgos ────────────────────────────────────────────────────
    st.markdown('<div class="re-sec">⚠️ Riesgos Activos</div>', unsafe_allow_html=True)

    # ── Helpers de riesgo ───────────────────────────────────────────────────────
    _PER_STYLE = {
        "2026-2": ("#dc2626", "#fef2f2"),
        "2027-1": ("#d97706", "#fffbeb"),
        "2027-2": ("#2563eb", "#eff6ff"),
    }

    def _per_badge(per_val):
        clr, bg = _PER_STYLE.get(str(per_val), ("#64748b", "#f1f5f9"))
        return (f'<span style="background:{bg};color:{clr};border:1px solid {clr};'
                f'border-radius:12px;padding:2px 9px;font-size:11px;font-weight:700;'
                f'white-space:nowrap">{per_val}</span>')

    def _av_badge(av):
        clr = "#15803d" if av >= 70 else ("#d97706" if av >= 30 else "#dc2626")
        return f'<span style="font-weight:700;color:{clr};font-size:13px">{av}%</span>'

    def _mod_badge(mod):
        return (f'<span style="background:#e0f2fe;color:#0369a1;border-radius:10px;'
                f'padding:2px 8px;font-size:11px;font-weight:600">{mod}</span>')

    def _pbar_html(pct, color):
        pct = min(max(float(pct or 0), 0), 100)
        clr = "#A6CE38" if pct >= 70 else ("#FBAF17" if pct >= 30 else "#EC0677")
        return (f'<div class="re-pbar">'
                f'<span style="font-weight:700;color:{clr};min-width:30px">{int(pct)}%</span>'
                f'<div class="re-pbar-w"><div class="re-pbar-f" style="width:{pct}%;background:{clr}"></div></div>'
                f'</div>')

    _FAC_CLR = {"FSCC": "#EC0677", "FIDI": "#1FB2DE", "FNGS": "#A6CE38"}

    def _r_rows(mask_df, extra):
        rows = []
        for _, r in mask_df.iterrows():
            fac_s = fac_abrev.get(r.get("FACULTAD", ""), "")
            fac_clr = _FAC_CLR.get(fac_s, "#6a8a9e")
            prog = r["NOMBRE DEL PROGRAMA"]
            prog_html = (
                f'<span style="font-weight:600;color:#0F385A;font-size:12px">{prog}</span>'
                + (f'<br><span style="font-size:10px;font-weight:700;color:{fac_clr}">{fac_s}</span>' if fac_s else "")
            )
            per = str(r.get("periodo_propuesto", r.get("PERIODO DE IMPLEMENTACIÓN", "—")))
            row_data = {
                "Programa":  prog_html,
                "Modalidad": _mod_badge(r.get("MODALIDAD", "—")),
                "Período":   _per_badge(per),
            }
            for k, fn in extra.items():
                row_data[k] = fn(r)
            rows.append(row_data)
        return rows

    def _rpct(pct):
        """Porcentaje coloreado compacto para tablas de riesgo."""
        v = min(max(float(pct or 0), 0), 100)
        clr = "#15803d" if v >= 70 else ("#d97706" if v >= 30 else "#dc2626")
        disp = f"{v:.1f}%" if v % 1 != 0 else f"{int(v)}%"
        return f'<span style="font-weight:700;color:{clr};font-size:12px">{disp}</span>'

    def _render_rcard(title, desc, color, rows, show_cols, icon="⚠️"):
        """Renderiza un risk-card compacto con cabecera visual y tabla scrollable."""
        n_r = len(rows)
        badge_color = color if n_r > 0 else "#15803d"
        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        hdr_bg = f"rgba({r},{g},{b},0.06)"
        hdr_bd = f"rgba({r},{g},{b},0.18)"
        hdr = (
            f'<div class="re-rcard" style="border-top:3px solid {badge_color}">'
            f'<div style="background:{hdr_bg};padding:9px 12px 7px;'
            f'border-bottom:1px solid {hdr_bd}">'
            f'<div style="display:flex;align-items:flex-start;'
            f'justify-content:space-between;gap:6px">'
            f'<div style="flex:1">'
            f'<div style="font-size:10px;font-weight:800;color:{badge_color};'
            f'text-transform:uppercase;letter-spacing:.04em;line-height:1.3">'
            f'{icon}&nbsp;{title}</div>'
            f'<div style="font-size:8.5px;color:#64748b;margin-top:2px;line-height:1.4">'
            f'{desc}</div></div>'
            f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.8rem;'
            f'font-weight:800;color:{badge_color};line-height:1;flex-shrink:0;'
            f'padding-left:8px">{n_r}</div>'
            f'</div></div>'
        )
        if n_r == 0:
            return hdr + '<div class="re-ok">✅ Sin programas en este riesgo</div></div>'
        thead = '<div class="re-rtbl-wrap"><table class="re-rtbl"><thead><tr>'
        for c in show_cols:
            align = "left" if c == "Programa" else "center"
            thead += f'<th style="text-align:{align}">{c}</th>'
        thead += '</tr></thead><tbody>'
        tbody = ""
        for row in rows:
            tbody += "<tr>"
            for c in show_cols:
                align = "left" if c == "Programa" else "center"
                tbody += f'<td style="text-align:{align}">{row.get(c, "—")}</td>'
            tbody += "</tr>"
        return hdr + f'{thead}{tbody}</tbody></table></div></div>'

    PERIODO_ORDER = {"2026-2": 0, "2027-1": 1, "2027-2": 2}

    # Excluir programas con aprobación ministerial requerida de los riesgos
    _req_col = "Req. Ministerial"
    if _req_col in df.columns:
        _no_min = ~df[_req_col].astype(str).str.strip().str.lower().str.startswith("si")
    else:
        _no_min = pd.Series([True]*len(df), index=df.index)
    df_risk = df[_no_min].copy()

    _pc  = df_risk["pc_pct"]  if "pc_pct"  in df_risk.columns else pd.Series([0.0]*len(df_risk), index=df_risk.index)
    _cf  = df_risk["cf_st"]   if "cf_st"   in df_risk.columns else pd.Series(["nostart"]*len(df_risk), index=df_risk.index)
    _pcs = df_risk["pc_st"]   if "pc_st"   in df_risk.columns else pd.Series(["nostart"]*len(df_risk), index=df_risk.index)
    _ban = df_risk["ban_pct"] if "ban_pct" in df_risk.columns else pd.Series([0.0]*len(df_risk), index=df_risk.index)
    _con = df_risk["conv_pct"]if "conv_pct"in df_risk.columns else pd.Series([0.0]*len(df_risk), index=df_risk.index)
    _syl = df_risk["syl_val"] if "syl_val" in df_risk.columns else pd.Series(["Si"]*len(df_risk), index=df_risk.index)
    _pp  = df_risk["periodo_propuesto"] if "periodo_propuesto" in df_risk.columns else pd.Series([""]*len(df_risk), index=df_risk.index)

    def _sort_risk(risk_df):
        if "periodo_propuesto" in risk_df.columns:
            tmp = risk_df.copy()
            tmp["_por"] = tmp["periodo_propuesto"].map(PERIODO_ORDER).fillna(99)
            return tmp.sort_values(["_por", "avance_general"], ascending=[True, False]).drop(columns=["_por"])
        return risk_df.sort_values("avance_general", ascending=False)

    # R1 — Producción virtual sin aval financiero
    r1_df   = _sort_risk(df_risk[(_pc > 0) & (_cf.isin(["nostart", "na"]))])
    r1_rows = _r_rows(r1_df, {
        "% Contenidos": lambda r: _rpct(r.get("pc_pct", 0)),
    })

    # R2 — Lanzamiento 2026-2 con contenidos incompletos
    r2_df   = _sort_risk(df_risk[(_pp == "2026-2") & (_pcs != "na") & (_pc < 100)])
    r2_rows = _r_rows(r2_df, {
        "% Contenidos": lambda r: _rpct(r.get("pc_pct", 0)),
    })

    # R3 — Parametrización en Banner sin producción de contenidos
    r3_df   = _sort_risk(df_risk[(_ban > 0) & (_pc < 100)])
    r3_rows = _r_rows(r3_df, {
        "% Banner": lambda r: _rpct(r.get("ban_pct", 0)),
    })

    # R4 — Avance en producción — Syllabus incompleto
    r4_df   = _sort_risk(df_risk[
        (df_risk["MODALIDAD"].str.lower().str.strip().isin(["virtual", "híbrido", "hibrido"])) &
        (_syl == "NO")
    ])
    r4_rows = _r_rows(r4_df, {
        "Syllabus":     lambda r: ('<span style="background:#fee2e2;color:#dc2626;font-size:10px;'
                                   'font-weight:700;padding:2px 7px;border-radius:8px">NO</span>'),
        "% Contenidos": lambda r: _rpct(r.get("pc_pct", 0)),
    })

    # R5 — Parametrización en Banner en proceso con trámite de convenios pendiente
    r5_df   = _sort_risk(df_risk[(_ban > 0) & (_con < 100)])
    r5_rows = _r_rows(r5_df, {
        "% Convenios": lambda r: _rpct(r.get("conv_pct", 0)),
        "% Banner":    lambda r: _rpct(r.get("ban_pct", 0)),
    })

    rr1, rr2, rr3 = st.columns(3)
    with rr1:
        st.markdown(_render_rcard(
            "R1 · Producción virtual sin aval financiero",
            "Virtual · % contenidos > 0 y sin concepto financiero",
            "#dc2626", r1_rows,
            ["Programa", "Período", "% Contenidos"], "⚠️"), unsafe_allow_html=True)
    with rr2:
        st.markdown(_render_rcard(
            "R2 · Lanzamiento 2026-2 con contenidos incompletos",
            "Período 2026-2 · Producción < 100% · Menor avance primero",
            "#d97706", r2_rows,
            ["Programa", "Modalidad", "% Contenidos"], "🔔"), unsafe_allow_html=True)
    with rr3:
        st.markdown(_render_rcard(
            "R3 · Parametrización en Banner sin producción de contenidos",
            "Banner > 0% y Contenidos < 100%",
            "#7c3aed", r3_rows,
            ["Programa", "Período", "% Banner"], "⚙️"), unsafe_allow_html=True)
    rr4, rr5, rr6 = st.columns(3)
    with rr4:
        st.markdown(_render_rcard(
            "R4 · Avance en producción — Syllabus incompleto",
            "Virtual/Híbrido · Avance en contenidos y Syllabus = NO",
            "#0d9488", r4_rows,
            ["Programa", "Syllabus", "% Contenidos", "Período"], "📋"), unsafe_allow_html=True)
    with rr5:
        st.markdown(_render_rcard(
            "R5 · Banner con avance sin trámite de convenios",
            "Banner > 0% y Convenios < 100%",
            "#2563eb", r5_rows,
            ["Programa", "% Convenios", "% Banner"], "🤝"), unsafe_allow_html=True)

    # ── SECCIÓN 3: Resumen por Etapa ──────────────────────────────────────────
    st.markdown('<div class="re-sec">📋 Estado por Etapa</div>', unsafe_allow_html=True)

    ETAPA_INFO = [
        ("Gestión Académica",                       "#0F385A"),
        ("Gestión Financiera",                      "#FBAF17"),
        ("Aseguramiento de la Calidad",             "#EC0677"),
        ("Ger. Planeación y Gestión Institucional", "#1FB2DE"),
        ("Producción de Contenidos",                "#A6CE38"),
        ("Convenios Institucionales",               "#42B0B5"),
        ("Parametrizar Reforma en Banner",          "#5C89B5"),
        ("Publicación en Página Web",               "#F47B20"),
    ]

    SHORT_NAME = {
        "Gestión Académica":                       "Gestión Académica",
        "Gestión Financiera":                      "Concepto Financiero",
        "Aseguramiento de la Calidad":             "Aseguramiento Calidad",
        "Ger. Planeación y Gestión Institucional": "Ger. Planeación",
        "Producción de Contenidos":                "Producción Contenidos",
        "Convenios Institucionales":               "Convenios",
        "Parametrizar Reforma en Banner":          "Banner",
        "Publicación en Página Web":               "Publicación Web",
    }

    etapa_cols_row1 = st.columns(4)
    etapa_cols_row2 = st.columns(4)
    all_etapa_cols = etapa_cols_row1 + etapa_cols_row2

    for ei, (proc, color) in enumerate(ETAPA_INFO):
        p_vals  = df[f"proc_{proc}"]
        done_e  = int((p_vals == 100).sum())
        inp_e   = int(((p_vals > 0) & (p_vals < 100)).sum())
        nst_e   = int((p_vals == 0).sum())
        na_e    = int(p_vals.isna().sum())
        total_e = max(done_e + inp_e + nst_e, 1)
        pct_e   = round(done_e / total_e * 100)
        short  = SHORT_NAME.get(proc, proc)

        card_html = (
            f'<div class="re-ecard" style="border-color:{color}">'
            f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:.82rem;'
            f'font-weight:800;color:#0F385A;text-transform:uppercase;letter-spacing:.04em;'
            f'margin-bottom:10px">{short}</div>'
            f'<div class="re-estats">'
            f'<div class="re-estat re-ef"><div class="re-estat-num">{done_e}</div>'
            f'<div class="re-estat-lbl">Final.</div></div>'
            f'<div class="re-estat re-ep"><div class="re-estat-num">{inp_e}</div>'
            f'<div class="re-estat-lbl">Proceso</div></div>'
            f'<div class="re-estat re-es"><div class="re-estat-num">{nst_e}</div>'
            f'<div class="re-estat-lbl">Sin ini.</div></div>'
            f'<div class="re-estat re-ena"><div class="re-estat-num">{na_e}</div>'
            f'<div class="re-estat-lbl">N/A</div></div>'
            f'</div>'
            f'<div class="re-ebar-row">'
            f'<div class="re-ebar-w"><div class="re-ebar-f" style="width:{pct_e}%;background:{color}"></div></div>'
            f'<div class="re-ebar-pct">{pct_e}%</div>'
            f'</div></div>'
        )
        all_etapa_cols[ei].markdown(card_html, unsafe_allow_html=True)

# ── Tab 2: Por facultad ────────────────────────────────────────────────────────
with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(
            '##### Programas por nivel de prioridad y facultad '
            '<span title="Cantidad de programas por facultad clasificados por nivel de prioridad. '
            'Urgente=periodo 2026 con avance &lt;70%; Prioritario=2027-1 con avance &lt;40%; '
            'En seguimiento=avance &lt;70%; En curso=avance ≥70%. '
            'Haga clic en una barra para ver el detalle de programas." '
            'style="cursor:help;color:#6a8a9e;font-size:13px">ⓘ</span>',
            unsafe_allow_html=True,
        )
        df_fac = df[["FACULTAD", "avance_general", "PERIODO DE IMPLEMENTACIÓN", "_clasif"]].copy()
        df_fac["Facultad"] = df_fac["FACULTAD"].map(fac_labels).fillna(df_fac["FACULTAD"])
        df_fac["Rango"]    = df_fac["_clasif"]
        fac_rango  = df_fac.groupby(["Facultad", "Rango"], observed=True).size().reset_index(name="n")
        faculties  = sorted(df_fac["Facultad"].unique())
        rangos       = ["Urgente", "Prioritario", "En seguimiento", "En curso"]
        rango_colors = ["#EC0677", "#FBAF17", "#2980B9", "#A6CE38"]

        fig_fac = go.Figure()
        # Fondo de color suave por facultad para diferenciarlas visualmente
        for fi, fac in enumerate(faculties):
            fc = FAC_PALETTE.get(fac, "#1FB2DE")
            fig_fac.add_shape(
                type="rect", layer="below",
                x0=0, x1=1, xref="paper",
                y0=fac, y1=fac, yref="y",
                fillcolor=fc, opacity=0.07,
                line_color=fc, line_width=1.5,
            )
        for rng, clr in zip(rangos, rango_colors):
            sub    = fac_rango[fac_rango["Rango"] == rng]
            counts = [int(sub[sub["Facultad"] == f]["n"].sum()) for f in faculties]
            fig_fac.add_trace(go.Bar(
                name=rng, y=faculties, x=counts, orientation="h",
                marker_color=clr, marker_line_width=0,
                text=[str(c) if c > 0 else "" for c in counts],
                textposition="inside", insidetextanchor="middle",
                textangle=0, textfont=dict(size=11, color="white", family="Segoe UI"),
            ))
        # Punto de color por facultad en el eje Y
        tick_labels = [
            f'<span style="color:{FAC_PALETTE.get(f,"#0F385A")};font-weight:700">◆</span> {f}'
            for f in faculties
        ]
        fig_fac.update_layout(
            barmode="stack", height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                        font=dict(size=10, color="#4a6a7e"), bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(showgrid=True, gridcolor="rgba(15,56,90,.07)",
                       color="#6a8a9e", tickfont=dict(size=10), dtick=5),
            yaxis=dict(color="#0F385A", tickfont=dict(size=10), autorange="reversed",
                       automargin=True),
            font=dict(family="Segoe UI"),
            bargap=0.35,
        )
        sel_fac = st.plotly_chart(
            fig_fac, use_container_width=True,
            on_select="rerun", key="sel_fac",
            config={"displayModeBar": False},
        )

        # Avance promedio por facultad — color propio de cada facultad
        st.markdown(
            '##### Avance promedio por facultad '
            '<span title="Promedio del avance general de todos los programas de cada facultad. '
            'El avance general de un programa es la media de sus avances por proceso. '
            'El color de cada barra identifica la facultad según la paleta institucional." '
            'style="cursor:help;color:#6a8a9e;font-size:13px">ⓘ</span>',
            unsafe_allow_html=True,
        )
        fac_avg = df_fac.groupby("Facultad")["avance_general"].agg(["mean", "count"]).reset_index()
        fac_avg.columns = ["Facultad", "avance", "total"]
        fac_avg = fac_avg.sort_values("avance")
        fac_avg_colors = [FAC_PALETTE.get(f, "#1FB2DE") for f in fac_avg["Facultad"]]
        hover_avg = [
            f"<b>{row.Facultad}</b><br>Avance: {int(row.avance)}%<br>Programas: {int(row.total)}"
            for row in fac_avg.itertuples()
        ]
        fig_favg = go.Figure(go.Bar(
            x=fac_avg["avance"].tolist(),
            y=fac_avg["Facultad"].tolist(),
            orientation="h",
            marker_color=fac_avg_colors,
            marker_line_color=[FAC_PALETTE.get(f, "#1FB2DE") for f in fac_avg["Facultad"]],
            marker_line_width=2,
            text=[f"  {int(v)}%  ({int(t)} prog.)" for v, t in zip(fac_avg["avance"], fac_avg["total"])],
            textposition="outside",
            textfont=dict(size=10, color="#4a6a7e"),
            hovertext=hover_avg, hoverinfo="text",
        ))
        fig_favg.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=6, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0, 128], showgrid=True, gridcolor="rgba(15,56,90,.07)",
                       color="#6a8a9e", tickfont=dict(size=10)),
            yaxis=dict(color="#0F385A", tickfont=dict(size=10, color="#0F385A"),
                       autorange="reversed", automargin=True),
            font=dict(family="Segoe UI"),
            showlegend=False,
            bargap=0.45,
        )
        st.plotly_chart(fig_favg, use_container_width=True, config={"displayModeBar": False})

    with col_r:
        st.markdown(
            '##### Ranking de programas por avance '
            '<span title="Programas ordenados por avance general (menor a mayor). '
            'El color de cada barra identifica la facultad a la que pertenece el programa. '
            'Use el filtro para ver los 15 más rezagados, los 15 más avanzados o todos. '
            'Haga clic en una barra para ver el detalle del programa por proceso." '
            'style="cursor:help;color:#6a8a9e;font-size:13px">ⓘ</span>',
            unsafe_allow_html=True,
        )
        df_s = df[["NOMBRE DEL PROGRAMA", "avance_general", "FACULTAD", "_clasif",
                   "PERIODO DE IMPLEMENTACIÓN"]].copy()
        df_s["FacCorta"] = df_s["FACULTAD"].map(fac_labels).fillna(df_s["FACULTAD"])
        df_s["label"]    = df_s["NOMBRE DEL PROGRAMA"].apply(lambda x: x[:32] + ("…" if len(x) > 32 else ""))
        df_s = df_s.sort_values("avance_general").reset_index(drop=True)

        # Control: mostrar top N o todos
        rk_opts = st.radio(
            "Mostrar", ["15 más rezagados", "15 más avanzados", "Todos"],
            horizontal=True, key="rk_filter", label_visibility="collapsed",
        )
        if rk_opts == "15 más rezagados":
            df_plot = df_s.head(15)
        elif rk_opts == "15 más avanzados":
            df_plot = df_s.tail(15)
        else:
            df_plot = df_s

        # Color por facultad + indicador visual
        bar_colors = [FAC_PALETTE.get(f, "#1FB2DE") for f in df_plot["FacCorta"]]
        hover_prg  = [
            f"<b>{row['NOMBRE DEL PROGRAMA']}</b><br>"
            f"Facultad: {row['FacCorta']}<br>"
            f"Avance: {int(row['avance_general'])}%<br>"
            f"Prioridad: {row['_clasif']}<br>"
            f"Periodo: {row['PERIODO DE IMPLEMENTACIÓN']}"
            for _, row in df_plot.iterrows()
        ]
        fig_prg = go.Figure(go.Bar(
            x=df_plot["avance_general"].tolist(),
            y=df_plot["label"].tolist(),
            orientation="h",
            marker_color=bar_colors,
            marker_line_color=[FAC_PALETTE.get(f, "#1FB2DE") for f in df_plot["FacCorta"]],
            marker_line_width=1,
            text=[f"{int(v)}%" for v in df_plot["avance_general"]],
            textposition="outside",
            textfont=dict(size=9, color="#4a6a7e"),
            hovertext=hover_prg, hoverinfo="text",
            showlegend=False,
        ))
        # Leyenda de facultades
        for fac_name, fac_color in FAC_PALETTE.items():
            fig_prg.add_trace(go.Bar(
                x=[None], y=[None], name=fac_name[:22] + ("…" if len(fac_name) > 22 else ""),
                marker_color=fac_color, showlegend=True,
            ))
        chart_h = max(320, len(df_plot) * 26 + 70)
        fig_prg.update_layout(
            height=chart_h,
            margin=dict(l=0, r=55, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0, 118], showgrid=True, gridcolor="rgba(15,56,90,.07)",
                       color="#6a8a9e", tickfont=dict(size=9)),
            yaxis=dict(color="#4a6a7e", tickfont=dict(size=9), autorange="reversed"),
            font=dict(family="Segoe UI"),
            legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="left", x=0,
                        font=dict(size=9, color="#4a6a7e"), bgcolor="rgba(0,0,0,0)"),
            barmode="overlay",
        )
        sel_prg = st.plotly_chart(
            fig_prg, use_container_width=True,
            on_select="rerun", key="sel_prg",
        )
        # Detalle al hacer clic en un programa del ranking
        if sel_prg.selection and sel_prg.selection.points:
            pt_p   = sel_prg.selection.points[0]
            y_prog = pt_p.get("y", "")
            match  = df_plot[df_plot["label"] == y_prog]
            if not match.empty:
                row      = match.iloc[0]
                clasif   = row["_clasif"]
                fg_c, bg_c = CLASIF_COLORS.get(clasif, ("#0F385A", "#f0f4f8"))
                av_pct   = int(row["avance_general"])
                fac_label = fac_labels.get(row["FACULTAD"], row["FACULTAD"])
                periodo  = row["PERIODO DE IMPLEMENTACIÓN"]
                prog_name = row["NOMBRE DEL PROGRAMA"]
                # buscar detalle por proceso
                proc_rows = ""
                for pi, proc in enumerate(PROCESOS):
                    pv = df.loc[df["NOMBRE DEL PROGRAMA"] == prog_name, f"proc_{proc}"]
                    pval = f"{int(pv.values[0])}%" if not pv.empty and pd.notna(pv.values[0]) else "N/A"
                    pc   = PROCESO_COLOR[proc]
                    proc_rows += (
                        f'<div style="display:flex;justify-content:space-between;'
                        f'padding:3px 0;border-bottom:1px solid #f0f4f8">'
                        f'<span style="font-size:10px;color:#4a6a7e">{proc_short_map.get(proc,proc)}</span>'
                        f'<span style="font-size:10px;font-weight:700;color:{pc}">{pval}</span></div>'
                    )
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid {fg_c};'
                    f'border-left:4px solid {fg_c};border-radius:8px;padding:12px 14px;margin-top:6px">'
                    f'<div style="font-size:12px;font-weight:700;color:#0F385A;margin-bottom:6px">{prog_name}</div>'
                    f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">'
                    f'<span style="font-size:10px;background:#f0f4f8;color:#4a6a7e;padding:2px 8px;border-radius:4px">{fac_label}</span>'
                    f'<span style="font-size:10px;background:{bg_c};color:{fg_c};padding:2px 8px;border-radius:4px;font-weight:700">{clasif}</span>'
                    f'<span style="font-size:10px;background:#e8f6fc;color:#0a6a8e;padding:2px 8px;border-radius:4px">Avance: {av_pct}%</span>'
                    f'<span style="font-size:10px;background:#f8f4e8;color:#6a4e00;padding:2px 8px;border-radius:4px">{periodo}</span>'
                    f'</div>'
                    f'<div>{proc_rows}</div></div>',
                    unsafe_allow_html=True,
                )

    # ── Panel de detalle al hacer clic en gráfica de facultad ────────────────
    if sel_fac.selection and sel_fac.selection.points:
        pt_f   = sel_fac.selection.points[0]
        fac_y  = pt_f.get("y", "")
        rng_n  = pt_f.get("curve_number", 0)
        if fac_y and rng_n < len(rangos):
            rng_sel = rangos[rng_n]
            clr_sel = rango_colors[rng_n]
            fac_full = fac_inv.get(fac_y, fac_y)
            mask_f   = (df["FACULTAD"] == fac_full) & (df["_clasif"] == rng_sel)
            df_fd    = df[mask_f][["NOMBRE DEL PROGRAMA", "avance_general",
                                   "_clasif", "PERIODO DE IMPLEMENTACIÓN"]].copy()
            df_fd["Avance %"] = df_fd["avance_general"].apply(lambda x: f"{int(x)}%")
            df_fd = df_fd.rename(columns={
                "NOMBRE DEL PROGRAMA": "Programa",
                "_clasif": "Prioridad",
                "PERIODO DE IMPLEMENTACIÓN": "Periodo",
            })[["Programa", "Avance %", "Prioridad", "Periodo"]]
            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid {clr_sel};'
                f'border-left:4px solid {clr_sel};border-radius:8px;'
                f'padding:10px 14px;margin-top:6px">'
                f'<span style="font-size:12px;font-weight:700;color:{clr_sel}">'
                f'📋 {len(df_fd)} programas</span>'
                f'<span style="font-size:11px;color:#6a8a9e"> — {fac_y} · {rng_sel}</span></div>',
                unsafe_allow_html=True,
            )
            fd_styled = df_fd.style\
                .map(_style_clasif_cell, subset=["Prioridad"])\
                .map(_style_avance_cell, subset=["Avance %"])
            st.dataframe(fd_styled, use_container_width=True, hide_index=True,
                         height=min(300, len(df_fd) * 38 + 40))

# ── Tab Priorización ──────────────────────────────────────────────────────────
with tab_prio:
    # ── helpers ────────────────────────────────────────────────────────────────
    _P_FAC_CLR = {"FSCC": "#EC0677", "FIDI": "#1FB2DE", "FNGS": "#A6CE38"}
    _P_MOD_CLR = {"Virtual": "#1FB2DE", "Presencial": "#A6CE38", "Híbrido": "#FBAF17"}
    _P_PER_CLR = {"2026-2": "#EC0677", "2027-1": "#FBAF17", "2027-2": "#2563eb", "Ya está en oferta": "#1FB2DE"}

    def _p_esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

    def _p_icon(val):
        try: v = float(val)
        except Exception: return '<span style="color:#b0bec5;font-size:13px">—</span>'
        import math as _m
        if _m.isnan(v): return '<span style="color:#b0bec5;font-size:11px;font-weight:600">N/A</span>'
        if v >= 100: return ('<span style="display:inline-flex;align-items:center;justify-content:center;'
                             'width:24px;height:24px;background:#dcfce7;color:#16a34a;border-radius:50%;'
                             'font-size:14px;box-shadow:0 1px 3px rgba(22,163,74,.25)">✅</span>')
        if v > 0:    return ('<span style="display:inline-flex;align-items:center;justify-content:center;'
                             'width:24px;height:24px;background:#fef3c7;color:#d97706;border-radius:50%;'
                             'font-size:13px;box-shadow:0 1px 3px rgba(217,119,6,.25)">⚠️</span>')
        return              ('<span style="display:inline-flex;align-items:center;justify-content:center;'
                             'width:24px;height:24px;background:#ffe4e6;color:#e11d48;border-radius:50%;'
                             'font-size:13px;box-shadow:0 1px 3px rgba(225,29,72,.25)">🔴</span>')

    def _p_syl(s):
        if s == "Si":  return ('<span style="display:inline-flex;align-items:center;justify-content:center;'
                               'width:24px;height:24px;background:#dcfce7;color:#16a34a;border-radius:50%;'
                               'font-size:14px;box-shadow:0 1px 3px rgba(22,163,74,.25)">✅</span>')
        if s == "NO":  return ('<span style="display:inline-flex;align-items:center;justify-content:center;'
                               'width:24px;height:24px;background:#ffe4e6;color:#e11d48;border-radius:50%;'
                               'font-size:13px;box-shadow:0 1px 3px rgba(225,29,72,.25)">🔴</span>')
        return '<span style="color:#b0bec5;font-size:11px;font-weight:600">N/A</span>'

    def _p_bar(pct):
        pct = float(pct or 0)
        clr = "#15803d" if pct >= 70 else ("#d97706" if pct >= 40 else "#dc2626")
        bar = "#22c55e" if pct >= 70 else ("#f59e0b" if pct >= 40 else "#ef4444")
        return (f'<div style="min-width:70px;text-align:center">'
                f'<div style="font-size:12px;font-weight:700;color:{clr};margin-bottom:3px">{int(pct)}%</div>'
                f'<div style="height:6px;background:#e2e8f0;border-radius:4px;overflow:hidden">'
                f'<div style="width:{min(pct,100):.0f}%;height:100%;background:{bar};border-radius:4px;'
                f'box-shadow:0 1px 2px rgba(0,0,0,.15)"></div>'
                f'</div></div>')

    def _p_badge(txt, clr):
        r,g,b = int(clr[1:3],16), int(clr[3:5],16), int(clr[5:7],16)
        return (f'<span style="background:rgba({r},{g},{b},0.12);color:{clr};font-size:10px;'
                f'font-weight:700;padding:3px 9px;border-radius:12px;white-space:nowrap">{_p_esc(txt)}</span>')

    def _p_star(av, per):
        if "2026" not in str(per) and "oferta" not in str(per).lower():
            return '<span style="color:#FBAF17;font-size:14px">★</span>'
        if av >= 70: return '<span style="color:#A6CE38;font-size:14px" title="Puede implementarse en 2026-2">★</span>'
        if av >= 40: return '<span style="color:#FBAF17;font-size:14px" title="Con esfuerzo podría implementarse">★</span>'
        return         '<span style="color:#EC0677;font-size:14px" title="No se podría implementar en 2026-2">★</span>'

    # ── Filtro propio del tab ───────────────────────────────────────────────────
    if "prio_mod" not in st.session_state: st.session_state["prio_mod"] = []
    if "prio_per" not in st.session_state: st.session_state["prio_per"] = ["2026-2"]
    if "prio_fac" not in st.session_state: st.session_state["prio_fac"] = []

    def _clear_prio():
        st.session_state["prio_mod"] = []
        st.session_state["prio_per"] = ["2026-2"]
        st.session_state["prio_fac"] = []

    _LBL_P = ('style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;'
               'letter-spacing:.4px;white-space:nowrap"')
    with st.container():
        st.markdown('<div style="background:#FFFFFF;border-radius:10px;padding:8px 12px 6px;'
                    'border:1px solid rgba(15,56,90,0.10);box-shadow:0 1px 4px rgba(15,56,90,0.04);'
                    'margin-bottom:6px">', unsafe_allow_html=True)
        _lp1, _ip1, _sp_p, _lp2, _ip2 = st.columns([0.55, 2.2, 0.05, 0.65, 2.2])
        with _lp1: st.markdown(f'<div {_LBL_P}>📋 MODALIDAD</div>', unsafe_allow_html=True)
        with _ip1: sel_pmod = st.pills("pmod", sorted(df_raw["MODALIDAD"].dropna().unique().tolist()),
                                       selection_mode="multi", key="prio_mod", label_visibility="collapsed")
        with _lp2: st.markdown(f'<div {_LBL_P}>🏛️ FACULTAD</div>', unsafe_allow_html=True)
        with _ip2: sel_pfac = st.pills("pfac", sorted([fac_abrev.get(f,f) for f in df_raw["FACULTAD"].dropna().unique()]),
                                       selection_mode="multi", key="prio_fac", label_visibility="collapsed")
        _lp3, _ip3, _sp_p2, _btn_p, _cnt_p = st.columns([0.55, 2.2, 0.05, 0.65, 2.2])
        with _lp3: st.markdown(f'<div {_LBL_P}>📅 PERÍODO</div>', unsafe_allow_html=True)
        with _ip3: sel_pper = st.pills("pper", sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist()),
                                       selection_mode="multi", key="prio_per", label_visibility="collapsed")
        with _btn_p: st.button("✕ LIMPIAR", on_click=_clear_prio, use_container_width=True, type="primary", key="prio_clear")
        with _cnt_p: _prio_cnt = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Filtrar datos ───────────────────────────────────────────────────────────
    df_p = df_raw.copy()
    if sel_pmod:  df_p = df_p[df_p["MODALIDAD"].isin(sel_pmod)]
    if sel_pfac:  df_p = df_p[df_p["FACULTAD"].isin([fac_abrev_inv.get(f,f) for f in sel_pfac])]
    if sel_pper:  df_p = df_p[df_p["PERIODO DE IMPLEMENTACIÓN"].isin(sel_pper)]
    df_p = enrich_df(df_p) if "pc_pct" not in df_p.columns else df_p

    # clasificar
    if len(df_p) > 0:
        df_p["_clasif"] = df_p.apply(
            lambda r: clasificar_programa(r["avance_general"], r["PERIODO DE IMPLEMENTACIÓN"]), axis=1)
        _pord = {"Urgente":0,"Prioritario":1,"En seguimiento":2,"En curso":3}
        df_p["_pord"] = df_p["_clasif"].map(_pord).fillna(4)
        df_p = df_p.sort_values(["_pord","avance_general"], ascending=[True,True])

    _prio_cnt.markdown(
        f'<div style="padding-top:9px;font-size:12px;color:#6a8a9e;text-align:right">'
        f'Mostrando <b style="color:#0F385A">{len(df_p)}</b> de '
        f'<b style="color:#0F385A">{len(df_raw)}</b></div>', unsafe_allow_html=True)

    # ── Leyenda ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="display:flex;gap:16px;margin:4px 0 8px;flex-wrap:wrap">'
        '<span style="font-size:11px;color:#6a8a9e"><span style="color:#A6CE38;font-size:14px">★</span> Puede implementarse en 2026-2</span>'
        '<span style="font-size:11px;color:#6a8a9e"><span style="color:#FBAF17;font-size:14px">★</span> Con esfuerzo podría implementarse</span>'
        '<span style="font-size:11px;color:#6a8a9e"><span style="color:#EC0677;font-size:14px">★</span> No se podría implementar en 2026-2</span>'
        '</div>', unsafe_allow_html=True)

    _PRIO_ETAPAS = [
        ("G.ACADÉMICA",  "proc_Gestión Académica",                       "proc"),
        ("C.FINANCIERO", "proc_Gestión Financiera",                       "proc"),
        ("ASEGURAMIENT", "proc_Aseguramiento de la Calidad",              "proc"),
        ("PLANEACIÓN",   "proc_Ger. Planeación y Gestión Institucional",  "proc"),
        ("SYLLABUS",     "syl_val",                                        "syl"),
        ("PROD.CONT.",   "pc_pct",                                         "bar"),
        ("CONVENIOS",    "proc_Convenios Institucionales",                "proc"),
        ("BANNER",       "ban_pct",                                        "bar"),
        ("TIPO TRÁMITE", "Tipo de trámite de aseguramiento de la calidad", "text"),
        ("FECHA NOTIF.", "Fecha notif. MEN",                              "text"),
        ("REQ. MIN.",    "Req. Ministerial",                              "text"),
    ]
    _PRIO_CLR = {"Urgente":("#EC0677","#fce8f2"),"Prioritario":("#FBAF17","#fdf8e8"),
                 "En seguimiento":("#2980B9","#EBF5FB"),"En curso":("#A6CE38","#f0f8e8")}

    if len(df_p) == 0:
        st.info("Sin programas para los filtros seleccionados.")
    else:
        TH_P  = ('style="background:#0F385A;color:#FFFFFF;font-size:10px;font-weight:700;'
                 'padding:8px 6px;text-align:center;white-space:nowrap;position:sticky;top:0;z-index:2;'
                 'border-right:1px solid rgba(255,255,255,0.10)"')
        THL_P = ('style="background:#0F385A;color:#FFFFFF;font-size:10px;font-weight:700;'
                 'padding:8px 10px;text-align:left;white-space:nowrap;position:sticky;top:0;z-index:2;'
                 'border-right:1px solid rgba(255,255,255,0.10)"')
        rows_p = []
        for idx, (_, row) in enumerate(df_p.iterrows()):
            rbg = "#FFFFFF" if idx % 2 == 0 else "#f8fafc"
            TD  = (f'style="padding:6px 5px;text-align:center;vertical-align:middle;'
                   f'border-bottom:1px solid #eef3f8;background:{rbg}"')
            TDL = (f'style="padding:6px 10px;text-align:left;vertical-align:middle;'
                   f'border-bottom:1px solid #eef3f8;background:{rbg};min-width:160px;max-width:220px"')
            prog   = _p_esc(row.get("NOMBRE DEL PROGRAMA","—"))
            fac_s  = fac_abrev.get(str(row.get("FACULTAD","")), "—")
            fac_c  = _P_FAC_CLR.get(fac_s, "#9aabb5")
            mod    = str(row.get("MODALIDAD","—"))
            mod_c  = _P_MOD_CLR.get(mod, "#9aabb5")
            per    = str(row.get("periodo_propuesto","—"))
            per_c  = _P_PER_CLR.get(per, "#9aabb5")
            av     = int(float(row.get("avance_general",0) or 0))
            clasif = row.get("_clasif","En curso")
            fg_c, bg_c = _PRIO_CLR.get(clasif, ("#0F385A","#f0f4f8"))

            etapa_cells = []
            for _, col_key, typ in _PRIO_ETAPAS:
                val = row.get(col_key)
                if typ == "proc":
                    try: v = None if val in ("",None) else float(val)
                    except: v = None
                    etapa_cells.append(f'<td {TD}>{_p_icon(v)}</td>')
                elif typ == "syl":
                    etapa_cells.append(f'<td {TD}>{_p_syl(str(val or "N/A"))}</td>')
                elif typ == "bar":
                    try: pct = float(val or 0)
                    except: pct = 0.0
                    etapa_cells.append(f'<td {TD}>{_p_bar(pct)}</td>')
                else:
                    tv = val if val not in [None,"","nan"] else "—"
                    etapa_cells.append(f'<td {TD}><span style="font-size:10px;color:#0F385A">{_p_esc(str(tv))}</span></td>')

            rows_p.append(
                f'<tr>'
                f'<td {TDL}>'
                f'<span style="margin-right:3px">{_p_star(av,per)}</span>'
                f'<span style="font-size:11px;font-weight:600;color:#0F385A">{prog}</span>'
                f'<br><span style="font-size:10px;font-weight:700;color:{fac_c}">{fac_s}</span></td>'
                f'<td {TD}>{_p_badge(mod, mod_c)}</td>'
                f'<td {TD}>{_p_badge(per, per_c)}</td>'
                f'<td {TD}><span style="background:{bg_c};color:{fg_c};font-size:10px;font-weight:700;'
                f'padding:2px 7px;border-radius:10px">{clasif}</span></td>'
                f'<td {TD}>{_p_bar(av)}</td>'
                + "".join(etapa_cells) +
                f'</tr>'
            )

        hdrs = "".join(f'<th {TH_P}>{h}</th>' for h,_,_ in _PRIO_ETAPAS)
        tabla_p = (
            '<div style="overflow-x:auto;overflow-y:auto;max-height:65vh;border-radius:12px;'
            'border:1.5px solid #b5c9d8;box-shadow:0 2px 12px rgba(15,56,90,.10);background:#fafdff">'
            '<table style="width:100%;border-collapse:separate;border-spacing:0;font-family:\'Segoe UI\',sans-serif">'
            '<thead><tr>'
            f'<th {THL_P}>PROGRAMA</th>'
            f'<th {TH_P}>MODALIDAD</th>'
            f'<th {TH_P}>PERÍODO</th>'
            f'<th {TH_P}>PRIORIDAD</th>'
            f'<th {TH_P}>AVANCE</th>'
            + hdrs +
            '</tr></thead><tbody>'
            + "".join(rows_p) +
            '</tbody></table></div>'
        )
        st.markdown(tabla_p, unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:11px;color:#6a8a9e;margin-top:4px;text-align:right">'
                    f'{len(df_p)} programas · ordenados por prioridad y avance general</div>',
                    unsafe_allow_html=True)

