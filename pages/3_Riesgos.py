"""
pages/3_Riesgos.py
Análisis de riesgos: 5 secciones con criterios específicos de filtrado.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_data, enrich_df, STATUS_LABEL

st.set_page_config(
    page_title="Riesgos · Reforma Curricular",
    page_icon="⚠️",
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
h1,h2,h3,h4,h5                     { font-family: 'Segoe UI', sans-serif; color: #0F385A !important; }
p, li, label, caption               { color: #2a4a5e; }
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
    transition: background .15s;
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
[data-testid="stBaseButton-primary"] > button {
    height: 32px !important; min-height: 32px !important;
    padding: 0 10px !important; line-height: 1 !important;
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

# ── Datos ─────────────────────────────────────────────────────────────────────
df_raw = enrich_df(load_data())

fac_abrev = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación":    "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
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

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:linear-gradient(135deg,#0F385A 0%,#1A5276 50%,#1FB2DE 100%);'
    'padding:18px 24px 14px;border-radius:0 0 12px 12px;border-bottom:3px solid #42F2F2;">'
    '<div style="font-size:21px;font-weight:700;color:#FFFFFF;letter-spacing:-.3px">'
    '⚠️ Análisis de Riesgos</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    'Programas que requieren atención prioritaria según criterios de riesgo</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ─── helpers ──────────────────────────────────────────────────────────────────
def _risk_header(title, desc, color, n):
    return (
        f'<div style="background:white;border-left:5px solid {color};border-radius:10px;'
        f'padding:12px 16px;margin:16px 0 8px;box-shadow:0 2px 8px rgba(15,56,90,.07)">'
        f'<div style="display:flex;align-items:center;justify-content:space-between">'
        f'<div>'
        f'<div style="font-size:14px;font-weight:700;color:#0F385A">{title}</div>'
        f'<div style="font-size:11px;color:#6a8a9e;margin-top:3px">{desc}</div></div>'
        f'<div style="background:{color};color:white;font-size:22px;font-weight:800;'
        f'padding:6px 18px;border-radius:20px;min-width:52px;text-align:center">{n}</div>'
        f'</div></div>'
    )

def _empty_risk():
    st.markdown(
        '<div style="background:#f0f8e8;border:1px solid #A6CE38;border-radius:8px;'
        'padding:10px 14px;color:#5a7a2e;font-size:12px">✅ Sin programas en este riesgo</div>',
        unsafe_allow_html=True,
    )

def _av(row):
    """Retorna avance_general como int de forma segura."""
    import math
    v = row.get("avance_general", 0)
    try:
        f = float(v)
        return 0 if math.isnan(f) else int(f)
    except Exception:
        return 0

def _style_avance(val):
    if isinstance(val, (int, float)):
        if val >= 70: return "background:#f0f8e8;color:#5a7a2e;font-weight:700;text-align:center"
        if val >= 40: return "background:#fef9e8;color:#8a6000;font-weight:700;text-align:center"
        return "background:#fce8f2;color:#9a0050;font-weight:700;text-align:center"
    return ""

def _style_pc(val):
    if isinstance(val, (int, float)):
        if val >= 100: return "background:#f0f8e8;color:#5a7a2e;font-weight:700;text-align:center"
        if val >= 50:  return "background:#fef9e8;color:#8a6000;font-weight:700;text-align:center"
        if val > 0:    return "background:#fde8f4;color:#7a0050;font-weight:700;text-align:center"
        return "background:#fce8f2;color:#9a0050;font-weight:700;text-align:center"
    return ""

def _style_ban(val):
    if isinstance(val, (int, float)):
        if val >= 100: return "background:#f0f0fa;color:#3a1a9e;font-weight:700;text-align:center"
        if val >= 50:  return "background:#ece8fc;color:#5a3aae;font-weight:700;text-align:center"
        return "background:#f5f0fe;color:#7c3aed;font-weight:700;text-align:center"
    return ""

PERIODO_ORDER = {"2026-2": 0, "2027-1": 1, "2027-2": 2, "Ya está en oferta": 3}

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 1: Producción virtual sin aval financiero
# PC (AK) > 0 Y CF (T) sin iniciar / vacío
# Tabla: Programa | Periodo | % AK | % Avance  — ordenar 2026-2 → 2027-1 → 2027-2
# ═══════════════════════════════════════════════════════════════════════════════
r1 = df_raw[
    (df_raw["pc_pct"] > 0) &
    (df_raw["cf_st"].isin(["nostart", "na"]) | df_raw["cf_st"].isna())
].copy()
r1["_ord"] = r1["periodo_propuesto"].map(PERIODO_ORDER).fillna(99)
r1 = r1.sort_values("_ord")

st.markdown(
    _risk_header(
        "Riesgo 1 — Producción virtual sin aval financiero",
        "Programas con avance en Producción de Contenidos (AK > 0%) pero sin Concepto Financiero aprobado (col T sin iniciar o vacío)",
        "#dc2626", len(r1),
    ),
    unsafe_allow_html=True,
)

if len(r1) == 0:
    _empty_risk()
else:
    rows_r1 = []
    for _, row in r1.iterrows():
        rows_r1.append({
            "Programa":   row["NOMBRE DEL PROGRAMA"],
            "Periodo":    row.get("periodo_propuesto", row.get("PERIODO DE IMPLEMENTACIÓN", "—")),
            "% PC (AK)":  int(float(row["pc_pct"])),
            "% Avance":   _av(row),
        })
    df_r1 = pd.DataFrame(rows_r1)
    st.dataframe(
        df_r1.style
            .applymap(_style_pc,     subset=["% PC (AK)"])
            .applymap(_style_avance, subset=["% Avance"]),
        use_container_width=True, hide_index=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 2: Lanzamiento en 2026-2 con Contenidos incompletos
# periodo_propuesto = 2026-2  Y  pc_pct < 100  (excluye No aplica)
# Tabla: Programa | % AK (asc, excluye 100%) | % Avance
# ═══════════════════════════════════════════════════════════════════════════════
r2 = df_raw[
    (df_raw["periodo_propuesto"] == "2026-2") &
    (df_raw["pc_st"] != "na") &
    (df_raw["pc_pct"] < 100)
].copy()
r2 = r2.sort_values("pc_pct", ascending=True)

st.markdown(
    _risk_header(
        "Riesgo 2 — Lanzamiento en 2026-2 con Contenidos incompletos",
        "Programas propuestos para 2026-2 con % de Producción de Contenidos (AK) < 100% — excluye No aplica",
        "#d97706", len(r2),
    ),
    unsafe_allow_html=True,
)

if len(r2) == 0:
    _empty_risk()
else:
    rows_r2 = []
    for _, row in r2.iterrows():
        rows_r2.append({
            "Programa":   row["NOMBRE DEL PROGRAMA"],
            "% PC (AK)":  int(float(row["pc_pct"])),
            "% Avance":   _av(row),
        })
    df_r2 = pd.DataFrame(rows_r2)

    def _style_pc(val):
        if isinstance(val, (int, float)):
            if val == 0:   return "background:#fce8f2;color:#9a0050;font-weight:700;text-align:center"
            if val < 50:   return "background:#fdf8e8;color:#8a6000;font-weight:700;text-align:center"
            return "text-align:center"
        return ""

    st.dataframe(
        df_r2.style
            .applymap(_style_pc,    subset=["% PC (AK)"])
            .applymap(_style_avance, subset=["% Avance"]),
        use_container_width=True, hide_index=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 3: Avance en Banner con producción de contenidos incompleta
# ban_pct (BB) > 0  Y  pc_pct (AK) < 100
# Tabla: Programa | % Banner (BB) | % PC (AK) | % Avance  — desc por BB
# ═══════════════════════════════════════════════════════════════════════════════
r3 = df_raw[
    (df_raw["ban_pct"] > 0) &
    (df_raw["pc_pct"] < 100)
].copy()
r3 = r3.sort_values("ban_pct", ascending=False)

st.markdown(
    _risk_header(
        "Riesgo 3 — Avance en parametrización en Banner sin producción de contenidos virtuales",
        "Programas con avance en Parametrizar Banner (BB > 0%) pero con producción de contenidos incompleta (AK < 100%)",
        "#7c3aed", len(r3),
    ),
    unsafe_allow_html=True,
)

if len(r3) == 0:
    _empty_risk()
else:
    rows_r3 = []
    for _, row in r3.iterrows():
        rows_r3.append({
            "Programa":      row["NOMBRE DEL PROGRAMA"],
            "% Banner (BB)": int(float(row["ban_pct"])),
            "% PC (AK)":     int(float(row["pc_pct"])),
            "% Avance":      _av(row),
        })
    df_r3 = pd.DataFrame(rows_r3)
    st.dataframe(
        df_r3.style
            .applymap(_style_ban,    subset=["% Banner (BB)"])
            .applymap(_style_pc,     subset=["% PC (AK)"])
            .applymap(_style_avance, subset=["% Avance"]),
        use_container_width=True, hide_index=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 4: Syllabus incompleto en programas Virtual/Híbrido
# Modalidad Virtual/Híbrido  Y  syl_val (AD) = "NO"
# Tabla: Programa | Estado Syllabus (AD) | % AK | % Avance  — desc por AK
# ═══════════════════════════════════════════════════════════════════════════════
r4 = df_raw[
    (df_raw["MODALIDAD"].str.lower().str.strip().isin(["virtual", "híbrido", "hibrido"])) &
    (df_raw["syl_val"] == "NO")
].copy()
r4 = r4.sort_values("pc_pct", ascending=False)

st.markdown(
    _risk_header(
        "Riesgo 4 — Avance en producción de contenidos virtuales y Syllabus incompleto",
        "Programas Virtual/Híbrido con producción de contenidos iniciada (AK > 0%) pero Syllabus sin completar (AD = NO)",
        "#0d9488", len(r4),
    ),
    unsafe_allow_html=True,
)

if len(r4) == 0:
    _empty_risk()
else:
    rows_r4 = []
    for _, row in r4.iterrows():
        rows_r4.append({
            "Programa":             row["NOMBRE DEL PROGRAMA"],
            "Estado Syllabus (AD)": row.get("syl_val", "—"),
            "% PC (AK)":            int(float(row["pc_pct"])),
            "% Avance":             _av(row),
        })
    df_r4 = pd.DataFrame(rows_r4)

    def _style_syl(val):
        if val == "NO": return "background:#fce8f2;color:#9a0050;font-weight:700;text-align:center"
        if val == "Si": return "background:#f0f8e8;color:#5a7a2e;font-weight:700;text-align:center"
        return "text-align:center"

    st.dataframe(
        df_r4.style
            .applymap(_style_syl,    subset=["Estado Syllabus (AD)"])
            .applymap(_style_pc,     subset=["% PC (AK)"])
            .applymap(_style_avance, subset=["% Avance"]),
        use_container_width=True, hide_index=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 5: Parametrización en Banner sin trámite de convenios
# ban_pct (BB) > 0  Y  conv_pct (AS) < 100
# Tabla: Programa | % Convenios (AS) | % Banner (BB) | % Avance  — asc por AS
# ═══════════════════════════════════════════════════════════════════════════════
r5 = df_raw[
    (df_raw["ban_pct"] > 0) &
    (df_raw["conv_pct"] < 100)
].copy()
r5 = r5.sort_values("conv_pct", ascending=True)

st.markdown(
    _risk_header(
        "Riesgo 5 — Parametrización en Banner sin trámite de convenios",
        "Programas con Banner avanzado (BB > 0%) pero Convenios Institucionales sin completar (AS < 100%)",
        "#2563eb", len(r5),
    ),
    unsafe_allow_html=True,
)

if len(r5) == 0:
    _empty_risk()
else:
    rows_r5 = []
    for _, row in r5.iterrows():
        rows_r5.append({
            "Programa":         row["NOMBRE DEL PROGRAMA"],
            "% Convenios (AS)": int(float(row["conv_pct"])),
            "% Banner (BB)":    int(float(row["ban_pct"])),
            "% Avance":         _av(row),
        })
    df_r5 = pd.DataFrame(rows_r5)

    def _style_conv(val):
        if isinstance(val, (int, float)):
            if val == 0:  return "background:#fce8f2;color:#9a0050;font-weight:700;text-align:center"
            if val < 50:  return "background:#fdf8e8;color:#8a6000;font-weight:700;text-align:center"
            return "text-align:center"
        return ""

    st.dataframe(
        df_r5.style
            .applymap(_style_conv,   subset=["% Convenios (AS)"])
            .applymap(_style_ban,    subset=["% Banner (BB)"])
            .applymap(_style_avance, subset=["% Avance"]),
        use_container_width=True, hide_index=True,
    )

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
