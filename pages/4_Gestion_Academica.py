"""
pages/4_Gestion_Academica.py
Tabla principal de Gestión Académica con estado de todas las etapas por programa.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import (
    load_data, apply_filters, ETAPAS_MAP, PROCESOS,
    PROCESO_COLOR, STATUS_LABEL, STATUS_COLOR, color_for_pct,
)

st.set_page_config(
    page_title="Gestión Académica · Reforma Curricular",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
[data-testid="stAppViewContainer"] { background: #EEF3F8; }
[data-testid="stHeader"] {
    background: linear-gradient(135deg, #0F385A 0%, #1A5276 50%, #1FB2DE 100%) !important;
    border-bottom: 3px solid #42F2F2 !important;
}
h1,h2,h3,h4,h5  { font-family: 'Segoe UI', sans-serif; color: #0F385A !important; }
p, li, label, caption { color: #2a4a5e; }
.block-container { padding-top: 3.5rem !important; padding-bottom: 2rem; }
div[data-baseweb="select"] > div {
    background: #E3F4FB !important; border-color: rgba(31,178,222,0.45) !important;
    color: #0F385A !important; border-radius: 8px !important;
}
div[data-baseweb="select"] span    { color: #0F385A !important; }
ul[data-baseweb="menu"]            { background: #FFFFFF !important; border-radius: 8px !important; }
ul[data-baseweb="menu"] li         { color: #0F385A !important; background: #FFFFFF !important; }
ul[data-baseweb="menu"] li:hover   { background: #E3F4FB !important; }
li[aria-selected="true"]           { background: #d0ecf8 !important; font-weight: 600 !important; }
[data-testid="stDataFrame"]        { border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(15,56,90,.08); }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F385A 0%, #1A5276 45%, #1FB2DE 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label  { color: rgba(255,255,255,0.80) !important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    color: rgba(255,255,255,0.82) !important; background: rgba(255,255,255,0.08) !important;
    border-radius: 8px !important; padding: 8px 12px 8px 10px !important;
    margin-bottom: 3px !important; font-size: 13px !important; font-weight: 500 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(255,255,255,0.18) !important; color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: rgba(255,255,255,0.22) !important; color: #FFFFFF !important;
    font-weight: 700 !important; border-left: 3px solid #42F2F2 !important;
}
[data-testid="stPills"] button { border: 2px solid #1A5276 !important; color: #1A5276 !important;
    background: #FFFFFF !important; border-radius: 20px !important; font-size: 12px !important;
    font-weight: 600 !important; }
[data-testid="stPills"] button[aria-checked="true"],
[data-testid="stPills"] button[aria-pressed="true"] {
    background: #0F385A !important; color: #FFFFFF !important;
    border-color: #0F385A !important; font-weight: 700 !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Datos ─────────────────────────────────────────────────────────────────────
df_raw = load_data()

fac_abrev = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación":    "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
}
fac_full = {v: k for k, v in fac_abrev.items()}
fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
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
    st.page_link("pages/3_Riesgos.py",                  label="Riesgos",              icon="⚠️")
    st.page_link("pages/4_Gestion_Academica.py",        label="Gestión Académica",    icon="📑")
    st.page_link("pages/5_Periodo_Propuesto.py",        label="Periodo Propuesto",    icon="📅")
    st.page_link("pages/6_Plan_de_Trabajo.py",          label="Plan de Trabajo",      icon="🗓️")
    st.markdown(
        '<div style="padding:12px 6px;font-size:10px;color:rgba(255,255,255,0.40);text-align:center">'
        'POLI · 2025–2026</div>',
        unsafe_allow_html=True,
    )

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:linear-gradient(135deg,#0F385A 0%,#1A5276 50%,#1FB2DE 100%);'
    'padding:18px 24px 14px;border-radius:0 0 12px 12px;border-bottom:3px solid #42F2F2;">'
    '<div style="font-size:21px;font-weight:700;color:#FFFFFF;letter-spacing:-.3px">'
    '📑 Gestión Académica</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    'Estado de etapas por programa · Avance general calculado</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Filtros ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:#FFFFFF;border-radius:10px;padding:14px 16px 12px;'
    'border:1px solid rgba(15,56,90,0.10);box-shadow:0 2px 8px rgba(15,56,90,0.06);'
    'margin-bottom:12px">',
    unsafe_allow_html=True,
)

_use_pills = hasattr(st, "pills")

_mods_ops = sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
_fac_ops  = [fac_abrev.get(f, f) for f in sorted(df_raw["FACULTAD"].dropna().unique())]
_per_ops  = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())
_sede_ops = sorted(df_raw["SEDE"].dropna().unique().tolist()) if "SEDE" in df_raw.columns else []

def _pill_or_multi(label, options, key):
    if _use_pills:
        return st.pills(label, options, selection_mode="multi", key=key)
    return st.multiselect(label, options, key=key, placeholder="Todas")

fc1, fc2, fc3, fc4 = st.columns(4)
with fc1:
    sel_mod = _pill_or_multi("Modalidad", _mods_ops, "ga_mod")
with fc2:
    sel_fac = _pill_or_multi("Facultad", _fac_ops, "ga_fac")
with fc3:
    sel_per = _pill_or_multi("Periodo", _per_ops, "ga_per")
with fc4:
    if _sede_ops:
        sel_sed = _pill_or_multi("Sede", _sede_ops, "ga_sed")
    else:
        sel_sed = []

st.markdown("</div>", unsafe_allow_html=True)

# Aplicar filtros
modalidad_f = list(sel_mod) if sel_mod else []
facultad_f  = [fac_full.get(f, f) for f in sel_fac] if sel_fac else []
periodo_f   = list(sel_per) if sel_per else []
df = apply_filters(df_raw.copy(), modalidad_f, facultad_f, periodo_f)

if sel_sed and "SEDE" in df.columns:
    df = df[df["SEDE"].isin(list(sel_sed))]

n = len(df)
st.caption(f"📊 **{n}** programas mostrados")

# ── Columnas de estado por etapa agrupadas por proceso ────────────────────────
# Para cada proceso, tomamos el primer campo de tipo status/pct como el estado representativo
PROC_KEY = {
    "Gestión Académica":                       "GA",
    "Gestión Financiera":                      "CF",
    "Aseguramiento de la Calidad":             "Aseg",
    "Ger. Planeación y Gestión Institucional": "GP",
    "Producción de Contenidos":                "PC",
    "Convenios Institucionales":               "Conv",
    "Parametrizar Reforma en Banner":          "Banner",
    "Publicación en Página Web":               "Pub",
}

# Índice del campo representativo por proceso (preferir pct > status)
PROC_REP_IDX = {}
for proc in PROCESOS:
    idxs = [i for i, (p, _, _, t) in enumerate(ETAPAS_MAP) if p == proc]
    # Preferir pct, luego status
    pct_idxs = [i for i in idxs if ETAPAS_MAP[i][3] == "pct"]
    st_idxs  = [i for i in idxs if ETAPAS_MAP[i][3] in ("status", "estado_tramite")]
    PROC_REP_IDX[proc] = pct_idxs[0] if pct_idxs else (st_idxs[0] if st_idxs else idxs[0])

def _st_html(cl, pct_val=None):
    bg = {"done":"#f0f8e8","inprog":"#e8f6fc","nostart":"#fce8f2","na":"#f0f4f8","info":"#fdf8e8"}
    fg = {"done":"#5a7a2e","inprog":"#0a6a8e","nostart":"#9a0050","na":"#6a8a9e","info":"#8a6000"}
    lbl = {"done":"✓ Finalizado","inprog":"⟳ En proceso","nostart":"✗ Sin iniciar",
           "na":"— N/A","info":"ℹ Info"}.get(cl, cl)
    if pct_val is not None and cl not in ("na", "info"):
        lbl = f"{lbl} {int(pct_val)}%"
    b = bg.get(cl, "#f0f4f8"); c = fg.get(cl, "#4a6a7e")
    return f'<span style="background:{b};color:{c};font-size:10px;font-weight:600;padding:2px 7px;border-radius:10px;white-space:nowrap">{lbl}</span>'

def _avance_bar_html(pct):
    pct = float(pct or 0)
    clr = "#A6CE38" if pct >= 70 else ("#FBAF17" if pct >= 40 else "#EC0677")
    return (
        f'<div style="display:flex;align-items:center;gap:5px">'
        f'<div style="flex:1;min-width:50px;height:7px;background:#e2e8f0;border-radius:4px;overflow:hidden">'
        f'<div style="width:{min(pct,100):.0f}%;height:100%;background:{clr};border-radius:4px"></div></div>'
        f'<span style="font-size:11px;font-weight:700;color:{clr};min-width:32px">{int(pct)}%</span>'
        f'</div>'
    )

# ── Construir tabla ────────────────────────────────────────────────────────────
rows = []
for _, row in df.iterrows():
    r = {
        "Programa": row["NOMBRE DEL PROGRAMA"],
        "Modalidad": row.get("MODALIDAD", "—"),
        "Nivel": row.get("NIVEL", "—"),
        "Sede": row.get("SEDE", "—"),
        "Facultad": fac_abrev.get(row.get("FACULTAD", ""), "—"),
        "Avance %": int(row["avance_general"]),
        "Periodo": row.get("PERIODO DE IMPLEMENTACIÓN", "—"),
    }
    for proc in PROCESOS:
        key = PROC_KEY[proc]
        rep_i = PROC_REP_IDX[proc]
        cl = str(row.get(f"cl_{rep_i}", "na"))
        pct = df_raw.loc[row.name, f"proc_{proc}"] if f"proc_{proc}" in df_raw.columns else None
        pct_val = round(float(pct)) if pct is not None and not np.isnan(pct) else None
        lbl = {"done": "Finalizado", "inprog": f"En proceso {pct_val}%" if pct_val else "En proceso",
               "nostart": "Sin iniciar", "na": "N/A", "info": "Info"}.get(cl, cl)
        r[key] = lbl
    rows.append(r)

df_show = pd.DataFrame(rows)

if len(df_show) == 0:
    st.info("Sin programas para los filtros seleccionados.")
else:
    # Estilo condicional
    def _style_col(val):
        if isinstance(val, str):
            if "Finalizado" in val:
                return "background:#f0f8e8;color:#5a7a2e;font-weight:600;text-align:center"
            if "En proceso" in val:
                return "background:#e8f6fc;color:#0a6a8e;font-weight:600;text-align:center"
            if "Sin iniciar" in val:
                return "background:#fce8f2;color:#9a0050;font-weight:600;text-align:center"
            if val == "N/A":
                return "background:#f0f4f8;color:#6a8a9e;text-align:center"
        return ""

    def _style_avance(val):
        if isinstance(val, (int, float)):
            if val >= 70:
                return "background:#f0f8e8;color:#5a7a2e;font-weight:700;text-align:center"
            if val >= 40:
                return "background:#fef9e8;color:#8a6000;font-weight:700;text-align:center"
            return "background:#fce8f2;color:#9a0050;font-weight:700;text-align:center"
        return ""

    etapa_cols = list(PROC_KEY.values())
    styled = df_show.style.applymap(_style_avance, subset=["Avance %"])
    for ec in etapa_cols:
        if ec in df_show.columns:
            styled = styled.applymap(_style_col, subset=[ec])

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        height=min(700, n * 38 + 60),
        column_config={
            "Avance %": st.column_config.ProgressColumn(
                "Avance %", help="Avance general calculado", min_value=0, max_value=100, format="%d%%"
            ),
        },
    )

    # ── Descarga Excel ─────────────────────────────────────────────────────────
    import io
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment
    from openpyxl.utils import get_column_letter

    def _gen_excel(df_exp):
        wb = Workbook(); ws = wb.active; ws.title = "Gestión Académica"
        headers = list(df_exp.columns)
        for ci, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=ci, value=h)
            cell.font = Font(bold=True, color="FFFFFF", size=10)
            cell.fill = PatternFill(start_color="0F385A", end_color="0F385A", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 28
        for ri, row_data in enumerate(df_exp.itertuples(index=False), 2):
            for ci, val in enumerate(row_data, 1):
                cell = ws.cell(row=ri, column=ci, value=val)
                cell.alignment = Alignment(horizontal="left" if ci <= 5 else "center")
        for ci, h in enumerate(headers, 1):
            ws.column_dimensions[get_column_letter(ci)].width = min(
                max(len(str(h)) + 2, 8), 30
            )
        ws.freeze_panes = "A2"
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
        return buf.getvalue()

    st.download_button(
        "⬇️ Descargar Excel",
        data=_gen_excel(df_show),
        file_name="gestion_academica.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
