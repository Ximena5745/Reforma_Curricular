"""
pages/5_Periodo_Propuesto.py
Periodo de implementación propuesto con lógica calculada + gráfico Gantt.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_data, enrich_df, STATUS_LABEL

st.set_page_config(
    page_title="Periodo Propuesto · Reforma Curricular",
    page_icon="📅",
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
[data-testid="stPills"] button {
    border: 2px solid #1A5276 !important; color: #1A5276 !important;
    background: #FFFFFF !important; border-radius: 20px !important;
    font-size: 12px !important; font-weight: 600 !important;
}
[data-testid="stPills"] button[aria-checked="true"],
[data-testid="stPills"] button[aria-pressed="true"] {
    background: #0F385A !important; color: #FFFFFF !important;
    border-color: #0F385A !important; font-weight: 700 !important;
}
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
/* LIMPIAR button */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg,#1FB2DE,#0891b2) !important;
    border-color: #1FB2DE !important;
    color: #FFFFFF !important; font-size: 11px !important; font-weight: 700 !important;
    border-radius: 8px !important; letter-spacing:.3px !important;
    box-shadow: 0 2px 8px rgba(31,178,222,0.35) !important;
}
[data-testid="stBaseButton-primary"] > button,
[data-testid="stBaseButton-primary"] button {
    height: 32px !important; min-height: 32px !important;
    padding: 0 10px !important; line-height: 1 !important; white-space: nowrap !important;
}
/* Align button vertically */
[data-testid="stColumn"]:has([data-testid="stBaseButton-primary"]) {
    display: flex !important; flex-direction: column !important; justify-content: center !important;
}
[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg,#0891b2,#0F385A) !important;
    border-color: #0891b2 !important;
}
/* Compact filter bar */
.stVerticalBlock:has([data-testid="stPills"]) { gap: 0.1rem !important; row-gap: 0.1rem !important; }
[data-testid="stPills"] { padding-bottom: 0 !important; margin-bottom: 0 !important; min-height: unset !important; }
[data-testid="stHorizontalBlock"]:has([data-testid="stPills"]) { align-items: center !important; padding-bottom: 0 !important; margin-bottom: 0 !important; min-height: unset !important; height: auto !important; padding-top: 0 !important; }
/* Sidebar toggle always visible */
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important; visibility: visible !important;
    opacity: 1 !important; position: fixed !important;
    top: 0.5rem !important; left: 0.5rem !important; z-index: 999999 !important;
}
/* Pill colors */
[data-testid="stPills"] button[aria-checked="false"]:nth-child(1),
[data-testid="stPills"] button[aria-pressed="false"]:nth-child(1) { border-color: #FBAF17 !important; color: #d97706 !important; }
[data-testid="stPills"] button[aria-checked="false"]:nth-child(2),
[data-testid="stPills"] button[aria-pressed="false"]:nth-child(2) { border-color: #A6CE38 !important; color: #5a7a2e !important; }
[data-testid="stPills"] button[aria-checked="false"]:nth-child(3),
[data-testid="stPills"] button[aria-pressed="false"]:nth-child(3) { border-color: #1FB2DE !important; color: #0891b2 !important; }
[data-testid="stPills"] button[aria-checked="false"]:nth-child(4),
[data-testid="stPills"] button[aria-pressed="false"]:nth-child(4) { border-color: #7c3aed !important; color: #7c3aed !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Datos ──────────────────────────────────────────────────────────────────────
df_raw = enrich_df(load_data())

niveles = [n for n in ["Pregrado", "Posgrado"] if "NIVEL_HOMOLOGADO" in df_raw.columns and n in df_raw["NIVEL_HOMOLOGADO"].values]

fac_abrev = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación":    "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
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
    st.page_link("pages/2_Programa.py",                 label="Resumen Programa",     icon="🔍")
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
    '📅 Periodo de Implementación Propuesto</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    'Periodo calculado automáticamente según avance de CF y PC</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Nota metodológica ──────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:#e8f6fc;border:1px solid rgba(31,178,222,0.35);border-radius:8px;'
    'padding:10px 14px;margin-bottom:12px">'
    '<span style="font-size:11px;color:#0a6a8e">'
    '<b>Lógica de cálculo:</b> Si CF (col T) está en proceso o finalizado y PC (AK) > 0 → propone <b>2026-2</b>. '
    'Si CF está avanzado pero PC = 0 → propone <b>2027-1</b>. '
    'Programas "Ya en oferta" mantienen su estado. Demás casos mantienen periodo original.</span></div>',
    unsafe_allow_html=True,
)

# ── Preparar datos ─────────────────────────────────────────────────────────────
df = df_raw[["NOMBRE DEL PROGRAMA", "MODALIDAD", "NIVEL", "NIVEL_HOMOLOGADO", "SEDE", "FACULTAD",
             "PERIODO DE IMPLEMENTACIÓN", "periodo_propuesto", "pc_pct", "cf_st",
             "avance_general"]].copy()

df["Facultad"] = df["FACULTAD"].map(fac_abrev).fillna(df["FACULTAD"])
df["Cambio"]   = df["PERIODO DE IMPLEMENTACIÓN"] != df["periodo_propuesto"]

# ── Métricas resumen ────────────────────────────────────────────────────────────
cnt_total   = len(df)
cnt_cambio  = int(df["Cambio"].sum())
cnt_2026_2  = int((df["periodo_propuesto"] == "2026-2").sum())
cnt_2027_1  = int((df["periodo_propuesto"] == "2027-1").sum())
cnt_2027_2  = int((df["periodo_propuesto"] == "2027-2").sum())
cnt_oferta  = int((df["periodo_propuesto"] == "Ya está en oferta").sum())

mc1, mc2, mc3, mc4, mc5 = st.columns(5)
for col, label, val, color in [
    (mc1, "Programas totales",    cnt_total,  "#0F385A"),
    (mc2, "Con cambio de periodo",cnt_cambio, "#EC0677"),
    (mc3, "Propuesto 2026-2",     cnt_2026_2, "#FBAF17"),
    (mc4, "Propuesto 2027-1",     cnt_2027_1, "#1FB2DE"),
    (mc5, "Propuesto 2027-2",     cnt_2027_2, "#A6CE38"),
]:
    col.markdown(
        f'<div style="background:#FFFFFF;border-left:4px solid {color};border-radius:10px;'
        f'padding:12px 14px;box-shadow:0 2px 8px rgba(15,56,90,.06);margin-bottom:6px">'
        f'<div style="font-size:9px;color:#6a8a9e;text-transform:uppercase;letter-spacing:.5px">{label}</div>'
        f'<div style="font-size:24px;font-weight:800;color:{color};line-height:1.2">{val}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)



# ── Tabla de periodo propuesto ─────────────────────────────────────────────────
st.markdown("#### Detalle por Programa")

with st.container():
    _LBL_P5 = 'style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;letter-spacing:.4px;white-space:nowrap"'
    lb_c, in_c, lb_nivel, in_nivel = st.columns([0.65, 3, 0.7, 2.5])
    with lb_c:
        st.markdown(
            f'<div {_LBL_P5}>🔀 VER SOLO CAMBIOS</div>',
            unsafe_allow_html=True,
        )
    with in_c:
        show_cambios = st.checkbox("cambios", value=False, key="p5_cambios",
                                   label_visibility="collapsed")
    with lb_nivel:
        st.markdown(f'<div {_LBL_P5}>🎓 NIVEL</div>', unsafe_allow_html=True)
    with in_nivel:
        _use_pills = hasattr(st, "pills")
        if _use_pills:
            sel_nivel = st.pills("nivel", niveles, selection_mode="multi", key="p5_nivel", label_visibility="collapsed")
        else:
            sel_nivel = st.multiselect("nivel", niveles, key="p5_nivel", label_visibility="collapsed", placeholder="Todos")

df_table = df.copy() if not show_cambios else df[df["Cambio"]].copy()
if sel_nivel:
    df_table = df_table[df_table["NIVEL_HOMOLOGADO"].isin(sel_nivel)]

rows = []
for _, row in df_table.iterrows():
    cambio = "✦ Cambio" if row["Cambio"] else "—"
    rows.append({
        "Programa": row["NOMBRE DEL PROGRAMA"],
        "Modalidad": row.get("MODALIDAD", "—"),
        "Facultad": row["Facultad"],
        "Periodo original": row["PERIODO DE IMPLEMENTACIÓN"],
        "Periodo propuesto": row["periodo_propuesto"],
        "Cambio": cambio,
        "Avance %": int(row["avance_general"]),
        "% PC": int(row.get("pc_pct", 0)),
        "CF": STATUS_LABEL.get(str(row.get("cf_st", "")), str(row.get("cf_st", "—"))),
    })

df_disp = pd.DataFrame(rows)

def _style_periodo_prop(val):
    clrs = {"2026-2": ("#EC0677", "#fce8f2"), "2027-1": ("#8a6000", "#fdf8e8"),
            "2027-2": ("#5a7a2e", "#f0f8e8"), "Ya está en oferta": ("#0a6a8e", "#e8f6fc")}
    if val in clrs:
        fg, bg = clrs[val]
        return f"background:{bg};color:{fg};font-weight:700;text-align:center"
    return ""

def _style_cambio(val):
    if val == "✦ Cambio":
        return "background:#fdf8e8;color:#8a6000;font-weight:700;text-align:center"
    return "color:#c0c0c0;text-align:center"

def _style_av(val):
    if isinstance(val, (int, float)):
        if val >= 70: return "background:#f0f8e8;color:#5a7a2e;font-weight:700;text-align:center"
        if val >= 40: return "background:#fef9e8;color:#8a6000;font-weight:700;text-align:center"
        return "background:#fce8f2;color:#9a0050;font-weight:700;text-align:center"
    return ""

styled = (
    df_disp.style
    .applymap(_style_periodo_prop, subset=["Periodo propuesto"])
    .applymap(_style_cambio, subset=["Cambio"])
    .applymap(_style_av, subset=["Avance %"])
)

st.dataframe(styled, use_container_width=True, hide_index=True,
             height=min(600, len(df_disp) * 38 + 60))

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

