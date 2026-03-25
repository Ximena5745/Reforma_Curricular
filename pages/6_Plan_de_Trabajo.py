"""
pages/6_Plan_de_Trabajo.py
Plan de trabajo sugerido con fechas de inicio y cierre por periodo propuesto.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_data, enrich_df, STATUS_LABEL

st.set_page_config(
    page_title="Plan de Trabajo · Reforma Curricular",
    page_icon="🗓️",
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
[data-testid="stDataFrame"]        { border-radius: 10px; overflow: hidden; }
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
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Datos ──────────────────────────────────────────────────────────────────────
df_raw = enrich_df(load_data())

fac_abrev = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación":    "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
}

WORK_DATES = {
    "2026-2":            {"inicio": "Enero 2026",   "cierre": "Junio 2026"},
    "2027-1":            {"inicio": "Julio 2026",   "cierre": "Diciembre 2026"},
    "2027-2":            {"inicio": "Enero 2027",   "cierre": "Junio 2027"},
    "Ya está en oferta": {"inicio": "Ya implementado", "cierre": "—"},
}

PERIOD_COLORS = {
    "2026-2":            "#EC0677",
    "2027-1":            "#FBAF17",
    "2027-2":            "#A6CE38",
    "Ya está en oferta": "#1FB2DE",
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
    '🗓️ Plan de Trabajo Sugerido</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    'Fechas de inicio y cierre sugeridas según periodo de implementación propuesto</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Tabla de fechas por periodo ────────────────────────────────────────────────
for periodo, dates in WORK_DATES.items():
    sub = df_raw[df_raw["periodo_propuesto"] == periodo].copy()
    if sub.empty:
        continue
    color = PERIOD_COLORS.get(periodo, "#1FB2DE")
    n     = len(sub)

    st.markdown(
        f'<div style="background:white;border-left:5px solid {color};border-radius:10px;'
        f'padding:12px 16px;margin:12px 0 6px;box-shadow:0 2px 8px rgba(15,56,90,.06)">'
        f'<div style="display:flex;align-items:center;justify-content:space-between">'
        f'<div>'
        f'<div style="font-size:15px;font-weight:700;color:#0F385A">Periodo {periodo}</div>'
        f'<div style="font-size:11px;color:#6a8a9e;margin-top:2px">'
        f'📅 Inicio sugerido: <b>{dates["inicio"]}</b> &nbsp;·&nbsp; '
        f'🏁 Cierre sugerido: <b>{dates["cierre"]}</b></div>'
        f'</div>'
        f'<div style="background:{color};color:white;font-size:18px;font-weight:800;'
        f'padding:5px 16px;border-radius:20px">{n} programas</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    rows = []
    for _, row in sub.iterrows():
        avance = int(row.get("avance_general", 0))
        cf_lbl = STATUS_LABEL.get(str(row.get("cf_st", "")), str(row.get("cf_st", "—")))
        rows.append({
            "Programa": row["NOMBRE DEL PROGRAMA"],
            "Modalidad": row.get("MODALIDAD", "—"),
            "Sede": row.get("SEDE", "—"),
            "Facultad": fac_abrev.get(row.get("FACULTAD", ""), "—"),
            "Fecha inicio sugerida": dates["inicio"],
            "Fecha cierre sugerida": dates["cierre"],
            "Avance %": avance,
            "CF": cf_lbl,
            "% PC": int(row.get("pc_pct", 0)),
        })

    df_sub = pd.DataFrame(rows)

    def _style_av(val):
        if isinstance(val, (int, float)):
            if val >= 70: return "background:#f0f8e8;color:#5a7a2e;font-weight:700;text-align:center"
            if val >= 40: return "background:#fef9e8;color:#8a6000;font-weight:700;text-align:center"
            return "background:#fce8f2;color:#9a0050;font-weight:700;text-align:center"
        return ""

    st.dataframe(
        df_sub.style.applymap(_style_av, subset=["Avance %"]),
        use_container_width=True,
        hide_index=True,
        height=min(400, n * 38 + 60),
    )

# ── Resumen visual por periodo ──────────────────────────────────────────────────
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown("#### Resumen de carga por periodo")

cols = st.columns(len(WORK_DATES))
for col, (periodo, dates) in zip(cols, WORK_DATES.items()):
    n = int((df_raw["periodo_propuesto"] == periodo).sum())
    color = PERIOD_COLORS.get(periodo, "#1FB2DE")
    col.markdown(
        f'<div style="background:white;border-top:4px solid {color};border-radius:10px;'
        f'padding:14px;text-align:center;box-shadow:0 2px 8px rgba(15,56,90,.06)">'
        f'<div style="font-size:11px;font-weight:700;color:{color};text-transform:uppercase;'
        f'letter-spacing:.5px;margin-bottom:6px">{periodo}</div>'
        f'<div style="font-size:30px;font-weight:800;color:#0F385A;line-height:1">{n}</div>'
        f'<div style="font-size:10px;color:#6a8a9e;margin-top:4px">programas</div>'
        f'<div style="margin-top:8px;font-size:10px;color:#4a6a7e">'
        f'📅 {dates["inicio"]}</div>'
        f'<div style="font-size:10px;color:#4a6a7e">🏁 {dates["cierre"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Descarga Excel ──────────────────────────────────────────────────────────────
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

all_rows = []
for periodo, dates in WORK_DATES.items():
    sub = df_raw[df_raw["periodo_propuesto"] == periodo]
    for _, row in sub.iterrows():
        all_rows.append({
            "Programa": row["NOMBRE DEL PROGRAMA"],
            "Modalidad": row.get("MODALIDAD", "—"),
            "Sede": row.get("SEDE", "—"),
            "Facultad": fac_abrev.get(row.get("FACULTAD", ""), "—"),
            "Periodo propuesto": periodo,
            "Fecha inicio sugerida": dates["inicio"],
            "Fecha cierre sugerida": dates["cierre"],
            "Avance %": int(row.get("avance_general", 0)),
            "Periodo original": row.get("PERIODO DE IMPLEMENTACIÓN", "—"),
        })

df_export = pd.DataFrame(all_rows)

import io
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

def _gen_excel_plan(df_exp):
    wb = Workbook(); ws = wb.active; ws.title = "Plan de Trabajo"
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
            cell.alignment = Alignment(horizontal="left" if ci <= 4 else "center")
    for ci, h in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(ci)].width = min(max(len(str(h)) + 2, 10), 35)
    ws.freeze_panes = "A2"
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.getvalue()

st.download_button(
    "⬇️ Descargar Plan de Trabajo (Excel)",
    data=_gen_excel_plan(df_export),
    file_name="plan_de_trabajo.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
