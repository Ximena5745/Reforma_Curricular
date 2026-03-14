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
    load_data, apply_filters, ETAPAS_MAP, PROCESOS,
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
</style>
""", unsafe_allow_html=True)

# ── Datos ──────────────────────────────────────────────────────────────────────
df_raw = load_data()

fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}
fac_inv  = {v: k for k, v in fac_labels.items()}
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
    st.page_link("app.py",                          label="Resumen General",     icon="📊")
    st.page_link("pages/1_Detalle_por_Etapa.py",    label="Detalle por Etapa",   icon="📋")
    st.page_link("pages/2_Programa.py",             label="Ficha de Programa",   icon="🔍")
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

# ── Filtros inline ─────────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:#FFFFFF;border-radius:10px;'
    'margin:8px 0 10px;padding:12px 16px 10px;'
    'border:1px solid rgba(15,56,90,0.10);'
    'box-shadow:0 2px 8px rgba(15,56,90,0.06)">',
    unsafe_allow_html=True,
)
f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
with f1:
    modalidades = ["Todas las modalidades"] + sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
    sel_mod = st.selectbox("Modalidad", modalidades, help="Filtra los programas por su modalidad de oferta (presencial, virtual, distancia, etc.)")
with f2:
    fac_ops = [fac_labels.get(f, f) for f in sorted(df_raw["FACULTAD"].dropna().unique())]
    sel_fac = st.selectbox("Facultad", ["Todas las facultades"] + fac_ops, help="Filtra los programas por facultad. Hay tres facultades: Sociedad Cultura y Creatividad, Ingeniería Diseño e Innovación, y Negocios Gestión y Sostenibilidad.")
with f3:
    periodos = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())
    sel_per  = st.selectbox("Periodo de implementación", ["Todos los periodos"] + periodos, help="Filtra por el semestre objetivo de implementación del programa. Los periodos 2026 son los más urgentes.")
with f4:
    st.caption(f"📊 Total: **{len(df_raw)}** programas")
    st.caption("📂 Excel · Hoja: Maestro")

st.markdown("</div>", unsafe_allow_html=True)   # cierre wrapper filtros

modalidad_f = "" if sel_mod == "Todas las modalidades" else sel_mod
facultad_f  = "" if sel_fac == "Todas las facultades" else fac_inv.get(sel_fac, sel_fac)
periodo_f   = "" if sel_per == "Todos los periodos"   else sel_per
df = apply_filters(df_raw.copy(), modalidad_f, facultad_f, periodo_f)
n  = len(df)

st.divider()

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
    vals = df[f"proc_{proc}"].dropna()
    pct_avgs.append(int(vals.mean()) if len(vals) > 0 else 0)
    idxs = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]
    done_l.append(sum(int(df[f"cl_{i}"].eq("done").sum())    for i in idxs))
    inp_l .append(sum(int(df[f"cl_{i}"].eq("inprog").sum())  for i in idxs))
    nst_l .append(sum(int(df[f"cl_{i}"].eq("nostart").sum()) for i in idxs))
    na_l  .append(sum(int(df[f"cl_{i}"].eq("na").sum()) + int(df[f"cl_{i}"].eq("info").sum()) for i in idxs))

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
             f"De {done+inp+nst+na_val} registros de etapas: "
             f"{done} Finalizadas · {inp} En Proceso · {nst} Sin iniciar · {na_val} N/A. "
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
    "Prioritario":    ("#F47B20", "#fdf0e8"),
    "En seguimiento": ("#FBAF17", "#fef9e8"),
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
        ("Prioritario",    "#F47B20", "#fdf0e8",
         "Periodo 2027-1", "Avance general < 40 %",
         "El programa implementa en 2027-1 pero registra un avance muy bajo. "
         "Necesita un plan de aceleración antes de que cierre el semestre actual "
         "para no pasar a estado Urgente."),
        ("En seguimiento", "#FBAF17", "#fef9e8",
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
        "Prioritario":    ("F47B20", "FFFFFF"),
        "En seguimiento": ("FBAF17", "333333"),
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
                    bg = "A6CE38" if pct >= 70 else ("FBAF17" if pct >= 40 else "EC0677")
                    fg = "FFFFFF" if pct < 40 or pct >= 70 else "333333"
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
tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen General", "🏛️ Por Facultad y Programa", "📋 Tabla Resumen", "📖 Metodología"])

# ── Tab 1: Resumen General ─────────────────────────────────────────────────────
with tab1:
    # KPI fila 1
    _cap_col, _btn_col = st.columns([5, 1])
    _cap_col.caption(f"Mostrando **{n}** de {len(df_raw)} programas")
    with _btn_col:
        if st.button("📋 Ver estados", use_container_width=True, help="Consulta los criterios de clasificación de prioridad de los programas"):
            _dialog_estados()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_kpi("Programas en reforma",  n,          f"de {len(df_raw)} en total",                    "#0F385A", None, "📚",
        tooltip="Total de programas académicos que están dentro del proceso de reforma curricular, aplicando los filtros activos."), unsafe_allow_html=True)
    c2.markdown(_kpi("Avance promedio",        f"{avg_av}%", "sobre todos los procesos",                   "#A6CE38", avg_av,
        tooltip=f"Promedio del avance general de los {n} programas filtrados. Se calcula como la media de todos los procesos de reforma de cada programa."), unsafe_allow_html=True)
    c3.markdown(_kpi("Avanzados ≥ 70%",        cnt_adv,    f"de {n} programas",                            "#1FB2DE", round(cnt_adv/n*100) if n else 0,
        tooltip="Programas cuyo avance general supera el 70% en todos los procesos. Se consideran 'En curso' y con menor riesgo de incumplimiento."), unsafe_allow_html=True)
    c4.markdown(_kpi("Urgentes / Prioritarios",  cnt_crit,   f"{cnt_urgente} urgentes · {cnt_prioritario} prioritarios", "#EC0677", round(cnt_crit/n*100) if n else 0,
        tooltip="Urgente: periodo 2026 con avance <70%. Prioritario: periodo 2027-1 con avance <40%. Estos programas requieren atención inmediata para cumplir los plazos de implementación."), unsafe_allow_html=True)

    st.markdown("<div style='margin:6px 0'></div>", unsafe_allow_html=True)

    # KPI fila 2
    c5, c6, c7, c8 = st.columns(4)
    c5.markdown(_kpi("Periodo 2026-2",       cnt_2026,       "programas más urgentes",       "#F47B20", round(cnt_2026/n*100)   if n else 0,
        tooltip="Programas cuyo periodo de implementación es 2026-2. Son los de mayor urgencia porque su fecha límite es el próximo semestre."), unsafe_allow_html=True)
    c6.markdown(_kpi("Periodo 2027-1",       cnt_2027_1,     "programas próximo semestre",   "#FBAF17", round(cnt_2027_1/n*100) if n else 0,
        tooltip="Programas con periodo de implementación 2027-1. Deben completar al menos el 40% del proceso para no considerarse prioritarios."), unsafe_allow_html=True)
    c7.markdown(_kpi("Proceso rezagado",     f"{proc_min_pct}%", proc_short_map.get(proc_min, proc_min), "#EC0677", proc_min_pct,
        tooltip=f"Proceso con el avance promedio más bajo entre todos los programas filtrados. Proceso: {proc_min} ({proc_min_pct}%). Indica el cuello de botella global de la reforma."), unsafe_allow_html=True)
    c8.markdown(_kpi("Proceso más avanzado", f"{proc_max_pct}%", proc_short_map.get(proc_max, proc_max), "#A6CE38", proc_max_pct,
        tooltip=f"Proceso con el avance promedio más alto entre todos los programas filtrados. Proceso: {proc_max} ({proc_max_pct}%)."), unsafe_allow_html=True)

    st.markdown(
        '#### Avance Consolidado por Proceso '
        '<span title="Cada donut muestra el avance promedio de un proceso en todos los programas filtrados. '
        'Los segmentos representan: verde=Finalizado, azul=En Proceso, rosa=Sin iniciar, gris=N/A. '
        'El % central es el promedio ponderado del proceso." '
        'style="cursor:help;color:#6a8a9e;font-size:14px">ⓘ</span>',
        unsafe_allow_html=True,
    )

    # Donuts — 2 filas de 4
    row1_cols = st.columns(4)
    row2_cols = st.columns(4)
    for idx, proc in enumerate(PROCESOS):
        col = (row1_cols + row2_cols)[idx]
        with col:
            st.markdown(
                _donut_card(proc, pct_avgs[idx], done_l[idx], inp_l[idx], nst_l[idx], na_l[idx], PROCESO_COLOR[proc]),
                unsafe_allow_html=True,
            )

    st.markdown(
        '#### Estado por Etapa '
        '<span title="Gráfica de barras apiladas al 100%. Cada barra es una etapa del proceso de reforma. '
        'Muestra qué proporción de programas está Finalizada, En Proceso, Sin iniciar o No aplica en esa etapa. '
        'Haga clic en una barra para ver el listado de programas en ese estado." '
        'style="cursor:help;color:#6a8a9e;font-size:14px">ⓘ</span>',
        unsafe_allow_html=True,
    )

    cats       = ["done", "inprog", "nostart", "na"]
    cat_labels = ["Finalizado", "En proceso", "Sin iniciar", "No aplica"]
    cat_colors = ["#A6CE38", "#1FB2DE", "#EC0677", "#c8d8e0"]

    # Construir lista de etapas agrupadas por proceso, con spacers entre grupos
    # Solo incluir etapas con al menos un programa con datos
    def _etapa_has_data(j):
        # Solo mostrar etapas con al menos un programa en done/inprog/nostart
        return sum(int(df[f"cl_{j}"].eq(c).sum()) for c in ["done", "inprog", "nostart"]) > 0

    etapa_names, etapa_idxs, etapa_proc = [], [], []
    for proc in PROCESOS:
        items = [(i, em[1]) for i, em in enumerate(ETAPAS_MAP)
                 if em[0] == proc and _etapa_has_data(i)]
        if not items:
            continue
        # Spacer SIEMPRE antes de cada grupo → sirve como fila de encabezado del proceso
        sp_key = f"__sp_{proc}__"
        etapa_names.append(sp_key)
        etapa_idxs.append(None)
        etapa_proc.append(None)
        for i, name in items:
            etapa_names.append(name)
            etapa_idxs.append(i)
            etapa_proc.append(proc)

    N = len(etapa_names)
    totals = [
        max(sum(int(df[f"cl_{j}"].eq(c).sum()) for c in cats) if j is not None else 1, 1)
        for j in etapa_idxs
    ]

    col_chart, col_legend = st.columns([3, 2])
    with col_chart:
        fig_bar = go.Figure()
        for cat, lbl, clr in zip(cats, cat_labels, cat_colors):
            cnts = [int(df[f"cl_{j}"].eq(cat).sum()) if j is not None else 0 for j in etapa_idxs]
            pcts = [round(cnts[k] / totals[k] * 100, 1) for k in range(N)]
            htxt = [
                f"<b>{etapa_names[k]}</b><br>{lbl}: {cnts[k]} ({pcts[k]}%)"
                if etapa_idxs[k] is not None else ""
                for k in range(N)
            ]
            txt = [str(cnts[k]) if pcts[k] >= 9 and etapa_idxs[k] is not None else "" for k in range(N)]
            fig_bar.add_trace(go.Bar(
                name=lbl, y=etapa_names, x=pcts, orientation="h",
                marker_color=clr, marker_line_width=0,
                text=txt, textposition="inside", insidetextanchor="middle",
                constraintext="none", textangle=0,
                textfont=dict(size=10, color="white", family="Segoe UI"),
                hovertext=htxt, hoverinfo="text",
                showlegend=False,
            ))

        # Fondo de color suave + etiqueta en la parte superior del grupo (sin superposición)
        for proc in PROCESOS:
            color     = PROCESO_COLOR[proc]
            grp_idxs  = [k for k, p in enumerate(etapa_proc) if p == proc]
            if not grp_idxs:
                continue
            fig_bar.add_shape(
                type="rect", layer="below",
                x0=0, x1=100,
                y0=etapa_names[grp_idxs[0]], y1=etapa_names[grp_idxs[-1]],
                yref="y", xref="x",
                fillcolor=color, opacity=0.06,
                line_color=color, line_width=0.8,
            )
            # Etiqueta centrada en el spacer que precede al grupo (nunca superpuesto a las barras)
            sp_idx = grp_idxs[0] - 1  # el spacer siempre está justo antes del grupo
            fig_bar.add_annotation(
                x=2, y=sp_idx,
                xref="x", yref="y",
                text=f"<b>{proc_short_map.get(proc, proc)}</b>",
                showarrow=False,
                font=dict(size=9, color=color, family="Segoe UI"),
                xanchor="left", yanchor="middle",
                bgcolor="rgba(255,255,255,0.0)",
            )

        tick_text = ["" if nm.startswith("__sp") else nm for nm in etapa_names]
        fig_bar.update_layout(
            barmode="stack", height=520,
            margin=dict(l=190, r=10, t=6, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            uniformtext=dict(minsize=8, mode="hide"),
            xaxis=dict(range=[0, 100], ticksuffix="%", showgrid=True,
                       gridcolor="rgba(15,56,90,.07)", color="#6a8a9e", tickfont=dict(size=10)),
            yaxis=dict(
                color="#4a6a7e", tickfont=dict(size=9.5), autorange="reversed",
                tickvals=etapa_names, ticktext=tick_text,
                side="left", automargin=False, ticklabelposition="outside left",
                ticklen=0,
            ),
            font=dict(family="Segoe UI"),
            bargap=0.28,
        )
        sel_etapa = st.plotly_chart(
            fig_bar, use_container_width=True,
            on_select="rerun", key="sel_etapa",
            config={"displayModeBar": False},
        )

    with col_legend:
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
        for lbl, clr in zip(cat_labels, cat_colors):
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">'
                f'<div style="width:12px;height:12px;border-radius:3px;background:{clr};flex-shrink:0"></div>'
                f'<span style="font-size:11px;color:#4a6a7e">{lbl}</span></div>',
                unsafe_allow_html=True,
            )

    # ── Panel de detalle al hacer clic en una barra ──────────────────────────
    if sel_etapa.selection and sel_etapa.selection.points:
        pt         = sel_etapa.selection.points[0]
        y_name     = pt.get("y", "")
        curve_n    = pt.get("curve_number", 0)
        if y_name and not str(y_name).startswith("__sp") and curve_n < len(cats):
            cat_sel   = cats[curve_n]
            lbl_sel   = cat_labels[curve_n]
            clr_sel   = cat_colors[curve_n]
            try:
                ej = etapa_idxs[etapa_names.index(y_name)]
            except (ValueError, IndexError):
                ej = None
            if ej is not None:
                mask   = df[f"cl_{ej}"].eq(cat_sel)
                df_det = df[mask][["NOMBRE DEL PROGRAMA", "FACULTAD", "avance_general",
                                   "_clasif", "PERIODO DE IMPLEMENTACIÓN"]].copy()
                df_det["Facultad"] = df_det["FACULTAD"].map(fac_labels).fillna(df_det["FACULTAD"])
                df_det["Avance %"] = df_det["avance_general"].apply(lambda x: f"{int(x)}%")
                df_det = df_det.rename(columns={
                    "NOMBRE DEL PROGRAMA": "Programa",
                    "_clasif": "Prioridad",
                    "PERIODO DE IMPLEMENTACIÓN": "Periodo",
                })[["Programa", "Facultad", "Avance %", "Prioridad", "Periodo"]]
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid {clr_sel};'
                    f'border-left:4px solid {clr_sel};border-radius:8px;'
                    f'padding:10px 14px;margin-top:6px">'
                    f'<span style="font-size:12px;font-weight:700;color:{clr_sel}">'
                    f'📋 {len(df_det)} programas</span>'
                    f'<span style="font-size:11px;color:#6a8a9e"> — {y_name} · {lbl_sel}</span></div>',
                    unsafe_allow_html=True,
                )
                det_styled = df_det.style\
                    .map(_style_clasif_cell, subset=["Prioridad"])\
                    .map(_style_avance_cell, subset=["Avance %"])
                st.dataframe(det_styled, use_container_width=True, hide_index=True,
                             height=min(300, len(df_det) * 38 + 40))

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
        rango_colors = ["#EC0677", "#F47B20", "#FBAF17", "#A6CE38"]

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

# ── Tab 3: Tabla resumen ───────────────────────────────────────────────────────
with tab3:
    hdr_l, hdr_r = st.columns([3, 1])
    hdr_l.caption(f"{n} programas · avance por proceso")

    display_cols = {
        "NOMBRE DEL PROGRAMA":       "Programa",
        "FACULTAD":                  "Facultad",
        "MODALIDAD":                 "Modalidad",
        "NIVEL":                     "Nivel académico",
        "PERIODO DE IMPLEMENTACIÓN": "Periodo",
        "avance_general":            "Avance %",
        "_clasif":                   "Prioridad",
    }
    for proc in PROCESOS:
        display_cols[f"proc_{proc}"] = proc

    df_show = df[list(display_cols.keys())].copy().rename(columns=display_cols)
    df_show["Facultad"] = df_show["Facultad"].map(fac_labels).fillna(df_show["Facultad"])
    df_show["Avance %"] = df_show["Avance %"].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "—")
    for proc in PROCESOS:
        df_show[proc] = df_show[proc].apply(
            lambda x: f"{int(x)}%" if pd.notna(x) and x == x else "N/A"
        )

    # Colorear columnas: proceso + Prioridad + Avance % + Facultad
    def _style_proc(df_s):
        result = pd.DataFrame("", index=df_s.index, columns=df_s.columns)
        # Procesos
        for proc in PROCESOS:
            if proc not in df_s.columns:
                continue
            color = PROCESO_COLOR[proc]
            r2, g2, b2 = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            result[proc] = (
                f"background-color: rgba({r2},{g2},{b2},0.10); "
                f"color: {color}; font-weight: 600; text-align: center"
            )
        # Prioridad semáforo
        if "Prioridad" in df_s.columns:
            result["Prioridad"] = df_s["Prioridad"].apply(_style_clasif_cell)
        # Avance % semáforo
        if "Avance %" in df_s.columns:
            result["Avance %"] = df_s["Avance %"].apply(_style_avance_cell)
        # Facultad con color distintivo por facultad
        if "Facultad" in df_s.columns:
            def _fac_style(val):
                color = FAC_PALETTE.get(str(val), "#1FB2DE")
                r2, g2, b2 = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                return (f"background-color: rgba({r2},{g2},{b2},0.10); "
                        f"color: {color}; font-weight: 700; border-left: 3px solid {color}")
            result["Facultad"] = df_s["Facultad"].apply(_fac_style)
        return result

    cols_list = list(df_show.columns)
    header_styles = [
        {"selector": "th", "props": [
            ("background-color", "#0F385A"), ("color", "white"),
            ("font-weight", "bold"), ("font-size", "11px"), ("text-align", "center"),
        ]},
    ]
    for proc in PROCESOS:
        if proc in df_show.columns:
            col_idx = cols_list.index(proc)
            color   = PROCESO_COLOR[proc]
            header_styles.append({
                "selector": f"th.col_heading.col{col_idx}",
                "props": [("background-color", color), ("color", "white"),
                          ("font-weight", "bold"), ("font-size", "11px"), ("text-align", "center")],
            })
    for fac_short, fac_color in FAC_PALETTE.items():
        pass  # handled in cell style
    if "Prioridad" in df_show.columns:
        header_styles.append({
            "selector": f"th.col_heading.col{cols_list.index('Prioridad')}",
            "props": [("background-color", "#EC0677"), ("color", "white"),
                      ("font-weight", "bold"), ("font-size", "11px"), ("text-align", "center")],
        })
    if "Facultad" in df_show.columns:
        header_styles.append({
            "selector": f"th.col_heading.col{cols_list.index('Facultad')}",
            "props": [("background-color", "#1FB2DE"), ("color", "white"),
                      ("font-weight", "bold"), ("font-size", "11px")],
        })

    styled = df_show.style.apply(_style_proc, axis=None).set_table_styles(
        header_styles, overwrite=False
    )

    # Columnas con anchos específicos en píxeles (auto-ajuste por contenido)
    max_prog_len = df_show["Programa"].apply(len).max() if "Programa" in df_show.columns else 30
    col_cfg = {
        "Programa":        st.column_config.TextColumn(width=min(max(max_prog_len * 7, 220), 380)),
        "Facultad":        st.column_config.TextColumn(width=200),
        "Avance %":        st.column_config.TextColumn(width=85),
        "Prioridad":       st.column_config.TextColumn(width=120),
        "Modalidad":       st.column_config.TextColumn(width=90),
        "Nivel académico": st.column_config.TextColumn(width=90),
        "Periodo":         st.column_config.TextColumn(width=90),
    }
    for proc in PROCESOS:
        if proc in df_show.columns:
            col_cfg[proc] = st.column_config.TextColumn(width=90)

    st.dataframe(
        styled,
        use_container_width=True,
        height=460,
        hide_index=True,
        column_config=col_cfg,
    )

    # ── Descarga Excel ─────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    with hdr_r:
        st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)
        excel_data = _excel_bytes(df_show)
        st.download_button(
            label="⬇️ Descargar Excel",
            data=excel_data,
            file_name="reforma_curricular.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ── Tab 4: Metodología ─────────────────────────────────────────────────────────
with tab4:
    def _card(title, color, body_html):
        return (
            f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);'
            f'border-top:4px solid {color};border-radius:10px;padding:16px 20px 14px;'
            f'box-shadow:0 2px 8px rgba(15,56,90,0.06);margin-bottom:14px">'
            f'<div style="font-size:13px;font-weight:700;color:{color};'
            f'text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px">{title}</div>'
            f'{body_html}</div>'
        )

    def _row(label, value, desc, color="#0F385A"):
        return (
            f'<div style="display:grid;grid-template-columns:140px 80px 1fr;'
            f'gap:8px;align-items:start;padding:6px 0;border-bottom:1px solid #f0f4f8">'
            f'<span style="font-size:12px;font-weight:600;color:{color}">{label}</span>'
            f'<span style="font-size:12px;font-weight:700;color:{color};'
            f'background:rgba(15,56,90,0.07);border-radius:4px;padding:1px 6px;text-align:center">{value}</span>'
            f'<span style="font-size:11px;color:#4a6a7e">{desc}</span></div>'
        )

    st.markdown(
        '<div style="background:linear-gradient(135deg,#0F385A 0%,#1A5276 60%,#1FB2DE 100%);'
        'border-radius:10px;padding:18px 22px;margin-bottom:18px">'
        '<div style="font-size:16px;font-weight:700;color:#FFFFFF">Nota metodológica</div>'
        '<div style="font-size:12px;color:rgba(255,255,255,0.75);margin-top:4px;line-height:1.6">'
        'Este tablero consolida el seguimiento de la Reforma Curricular de Programas Académicos de POLI. '
        'El avance se calcula a partir del estado registrado en cada etapa del proceso, '
        'agrupado por proceso y luego promediado para obtener el avance general de cada programa.</div></div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        # ── Bloque 1: Estado de etapa ──────────────────────────────────────────
        body1 = (
            '<div style="font-size:11px;color:#4a6a7e;margin-bottom:8px">'
            'Cada etapa se clasifica según el tipo de dato que registra en el archivo Excel:</div>'
            + _row("Finalizado",  "100 pts", "La actividad está completada (estado=Finalizado, valor=Sí, % = 100, número > 0).", "#A6CE38")
            + _row("En proceso",  " 50 pts", "La actividad está iniciada pero no concluida (estado=En proceso, pendiente, elaboración…, 0 % < % < 100 %).", "#1FB2DE")
            + _row("Sin iniciar", "  0 pts", "No se ha registrado avance (estado=Sin iniciar / No, % = 0).", "#EC0677")
            + _row("No aplica",   "Excluido", "El campo No aplica o está vacío para ese programa — no entra al cálculo.", "#9aabb5")
            + _row("Informativo", "Excluido", "Campos de tipo informativo (Tipo de trámite, Periodo, Fecha) — sólo para contexto, sin peso en el avance.", "#FBAF17")
        )
        st.markdown(_card("1 · Estado de cada etapa", "#1FB2DE", body1), unsafe_allow_html=True)

        # ── Bloque 2: Avance por proceso ──────────────────────────────────────
        body2 = (
            '<div style="font-size:11px;color:#4a6a7e;margin-bottom:8px">'
            'Se promedian los puntos de todas las etapas <b>aplicables</b> del proceso '
            '(excluyendo No aplica e Informativos):</div>'
            '<div style="background:#f8fafc;border-radius:8px;padding:10px 14px;'
            'font-family:monospace;font-size:12px;color:#0F385A;margin-bottom:8px">'
            'Avance<sub>proceso</sub> =<br>'
            '&nbsp;&nbsp;Σ(puntos de etapas aplicables)<br>'
            '&nbsp;&nbsp;─────────────────────────────<br>'
            '&nbsp;&nbsp;N° etapas aplicables</div>'
            '<div style="font-size:11px;color:#4a6a7e">'
            '<b>Ejemplo:</b> un proceso con 3 etapas: Finalizado (100), En proceso (50), No aplica (excluida) '
            '→ avance = (100 + 50) / 2 = <b>75 %</b></div>'
        )
        st.markdown(_card("2 · Avance por proceso", "#0F385A", body2), unsafe_allow_html=True)

    with col_b:
        # ── Bloque 3: Avance general ───────────────────────────────────────────
        body3 = (
            '<div style="font-size:11px;color:#4a6a7e;margin-bottom:8px">'
            'El avance general del programa es el promedio de los avances de cada proceso, '
            'considerando solo los procesos que tienen al menos una etapa aplicable:</div>'
            '<div style="background:#f8fafc;border-radius:8px;padding:10px 14px;'
            'font-family:monospace;font-size:12px;color:#0F385A;margin-bottom:8px">'
            'Avance<sub>general</sub> =<br>'
            '&nbsp;&nbsp;Σ(Avance<sub>proceso i</sub>)<br>'
            '&nbsp;&nbsp;───────────────────────<br>'
            '&nbsp;&nbsp;N° procesos con datos</div>'
            '<div style="font-size:11px;color:#4a6a7e;line-height:1.6">'
            f'Hay <b>{len(PROCESOS)} procesos</b> definidos: '
            + ", ".join(f"<span style='color:{PROCESO_COLOR[p]};font-weight:600'>{p}</span>" for p in PROCESOS)
            + '.</div>'
        )
        st.markdown(_card("3 · Avance general del programa", "#A6CE38", body3), unsafe_allow_html=True)

        # ── Bloque 4: Clasificación de prioridad ──────────────────────────────
        body4 = (
            '<div style="font-size:11px;color:#4a6a7e;margin-bottom:8px">'
            'Con el avance general y el periodo de implementación se asigna un nivel de prioridad:</div>'
        )
        clasif_rows = [
            ("Urgente",        "#EC0677", "#fce8f2", "2026-2 o ya en oferta", "< 70 %"),
            ("Prioritario",    "#F47B20", "#fdf0e8", "2027-1",               "< 40 %"),
            ("En seguimiento", "#FBAF17", "#fef9e8", "Cualquier periodo",     "< 70 %"),
            ("En curso",       "#A6CE38", "#f0f8e8", "Cualquier periodo",     "≥ 70 %"),
        ]
        for nombre, fg, bg, periodo, avance in clasif_rows:
            body4 += (
                f'<div style="display:flex;align-items:center;gap:10px;'
                f'padding:5px 8px;background:{bg};border-radius:6px;margin-bottom:5px">'
                f'<span style="background:{fg};color:white;font-size:11px;font-weight:700;'
                f'padding:2px 10px;border-radius:10px;white-space:nowrap">{nombre}</span>'
                f'<span style="font-size:11px;color:#4a6a7e">Periodo: <b>{periodo}</b></span>'
                f'<span style="font-size:11px;color:{fg};font-weight:700;margin-left:auto">{avance}</span>'
                f'</div>'
            )
        st.markdown(_card("4 · Clasificación de prioridad", "#EC0677", body4), unsafe_allow_html=True)

    # ── Bloque 5: Procesos y etapas ─────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:14px;font-weight:700;color:#0F385A;margin:4px 0 10px">',
        unsafe_allow_html=True,
    )
    st.markdown("##### Detalle de procesos y etapas")
    proc_cols = st.columns(4)
    for pi, proc in enumerate(PROCESOS):
        col = proc_cols[pi % 4]
        etapas_proc = [(em[1], em[3]) for em in ETAPAS_MAP if em[0] == proc]
        color = PROCESO_COLOR[proc]
        tipo_icon = {"status": "🔘", "pct": "📊", "num": "🔢", "info": "ℹ️", "date": "📅", "estado_tramite": "🔘"}
        etapa_html = "".join(
            f'<div style="display:flex;align-items:center;gap:6px;padding:3px 0;'
            f'border-bottom:1px solid rgba(15,56,90,0.06)">'
            f'<span style="font-size:11px">{tipo_icon.get(tipo, "·")}</span>'
            f'<span style="font-size:11px;color:#2a4a5e">{etapa}</span></div>'
            for etapa, tipo in etapas_proc
        )
        col.markdown(
            f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);'
            f'border-top:3px solid {color};border-radius:8px;padding:10px 12px;'
            f'box-shadow:0 1px 4px rgba(15,56,90,0.06)">'
            f'<div style="font-size:11px;font-weight:700;color:{color};'
            f'text-transform:uppercase;letter-spacing:.4px;margin-bottom:6px">{proc}</div>'
            f'{etapa_html}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="background:#f0f4f8;border-radius:8px;padding:10px 16px;margin-top:14px">'
        '<span style="font-size:11px;color:#4a6a7e">'
        '🔘 Estado (Sí/No/Finalizado/En proceso) &nbsp;·&nbsp; '
        '📊 Porcentaje (0–100%) &nbsp;·&nbsp; '
        '🔢 Numérico (> 0 = Finalizado) &nbsp;·&nbsp; '
        'ℹ️ Informativo (contexto, no suma al avance) &nbsp;·&nbsp; '
        '📅 Fecha (informativo)</span></div>',
        unsafe_allow_html=True,
    )
