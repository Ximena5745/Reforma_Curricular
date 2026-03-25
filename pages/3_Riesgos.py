"""
pages/3_Riesgos.py
Análisis de riesgos: 5 secciones con criterios específicos de filtrado.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_data, PROCESO_COLOR, STATUS_LABEL, STATUS_COLOR

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
def _status_badge(st_val, pct=None):
    """Retorna HTML de badge para un estado."""
    labels = {"done": "Finalizado", "inprog": "En proceso",
              "nostart": "Sin iniciar", "na": "No aplica", "info": "Info"}
    colors = {"done": ("#f0f8e8", "#5a7a2e"), "inprog": ("#e8f6fc", "#0a6a8e"),
              "nostart": ("#fce8f2", "#9a0050"), "na": ("#f0f4f8", "#6a8a9e"),
              "info": ("#fdf8e8", "#8a6000")}
    bg, fg = colors.get(st_val, ("#f0f4f8", "#6a8a9e"))
    lbl = labels.get(st_val, st_val)
    if pct is not None and pct > 0:
        lbl = f"{lbl} ({int(pct)}%)"
    return (f'<span style="background:{bg};color:{fg};font-weight:700;font-size:10px;'
            f'padding:2px 8px;border-radius:12px;white-space:nowrap">{lbl}</span>')

def _pct_bar(pct, color="#1FB2DE", width=80):
    pct = min(max(float(pct or 0), 0), 100)
    clr = "#A6CE38" if pct >= 70 else ("#FBAF17" if pct >= 30 else "#EC0677")
    return (
        f'<div style="display:flex;align-items:center;gap:6px">'
        f'<div style="width:{width}px;height:6px;background:#e2e8f0;border-radius:4px;overflow:hidden">'
        f'<div style="width:{pct}%;height:100%;background:{clr};border-radius:4px"></div></div>'
        f'<span style="font-size:11px;font-weight:700;color:{clr}">{int(pct)}%</span></div>'
    )

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

PERIODO_ORDER = {"2026-2": 0, "2027-1": 1, "2027-2": 2}

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 1: PC > 0 y CF sin iniciar → ordenar por periodo (2026-2 primero)
# ═══════════════════════════════════════════════════════════════════════════════
r1 = df_raw[
    (df_raw["pc_pct"] > 0) &
    (df_raw["cf_st"].isin(["nostart", "na"]) | df_raw["cf_st"].isna())
].copy()
r1["_ord"] = r1["PERIODO DE IMPLEMENTACIÓN"].map(PERIODO_ORDER).fillna(99)
r1 = r1.sort_values("_ord")

st.markdown(
    _risk_header(
        "Riesgo 1 — Producción de Contenidos sin Concepto Financiero",
        "Programas con avance en Producción de Contenidos (AK > 0%) pero sin Concepto Financiero aprobado (col T sin iniciar)",
        "#EC0677", len(r1),
    ),
    unsafe_allow_html=True,
)

if len(r1) == 0:
    st.markdown(
        '<div style="background:#f0f8e8;border:1px solid #A6CE38;border-radius:8px;'
        'padding:10px 14px;color:#5a7a2e;font-size:12px">✅ Sin programas en este riesgo</div>',
        unsafe_allow_html=True,
    )
else:
    rows_r1 = []
    for _, row in r1.iterrows():
        rows_r1.append({
            "Programa": row["NOMBRE DEL PROGRAMA"],
            "Modalidad": row.get("MODALIDAD", "—"),
            "Sede": row.get("SEDE", "—"),
            "Facultad": fac_abrev.get(row.get("FACULTAD", ""), row.get("FACULTAD", "—")),
            "Periodo": row.get("PERIODO DE IMPLEMENTACIÓN", "—"),
            "% PC (AK)": int(row["pc_pct"]),
            "CF (T)": STATUS_LABEL.get(row["cf_st"], row["cf_st"]),
        })
    df_r1 = pd.DataFrame(rows_r1)
    st.dataframe(
        df_r1.style.applymap(
            lambda v: "background:#fce8f2;color:#9a0050;font-weight:700" if v == "Sin iniciar" else "",
            subset=["CF (T)"]
        ).background_gradient(subset=["% PC (AK)"], cmap="Reds"),
        use_container_width=True, hide_index=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 2: Periodo 2026-2 con PC < 100% (excluye No aplica) → ordenar asc por PC
# ═══════════════════════════════════════════════════════════════════════════════
r2 = df_raw[
    (df_raw["PERIODO DE IMPLEMENTACIÓN"].str.contains("2026-2", na=False)) &
    (df_raw["pc_st"] != "na") &
    (df_raw["pc_pct"] < 100)
].copy()
r2 = r2.sort_values("pc_pct", ascending=True)

st.markdown(
    _risk_header(
        "Riesgo 2 — Periodo 2026-2 con Producción de Contenidos incompleta",
        "Programas para 2026-2 con % de PC (AK) < 100% — excluye modalidad Presencial (No aplica)",
        "#FBAF17", len(r2),
    ),
    unsafe_allow_html=True,
)

if len(r2) == 0:
    st.markdown(
        '<div style="background:#f0f8e8;border:1px solid #A6CE38;border-radius:8px;'
        'padding:10px 14px;color:#5a7a2e;font-size:12px">✅ Sin programas en este riesgo</div>',
        unsafe_allow_html=True,
    )
else:
    rows_r2 = []
    for _, row in r2.iterrows():
        rows_r2.append({
            "Programa": row["NOMBRE DEL PROGRAMA"],
            "Modalidad": row.get("MODALIDAD", "—"),
            "Facultad": fac_abrev.get(row.get("FACULTAD", ""), row.get("FACULTAD", "—")),
            "Periodo": row.get("PERIODO DE IMPLEMENTACIÓN", "—"),
            "% PC (AK)": int(row["pc_pct"]),
            "Estado PC": STATUS_LABEL.get(row["pc_st"], row["pc_st"]),
        })
    df_r2 = pd.DataFrame(rows_r2)

    def _style_r2_pct(val):
        if isinstance(val, (int, float)):
            if val == 0:
                return "background:#fce8f2;color:#9a0050;font-weight:700"
            if val < 50:
                return "background:#fdf8e8;color:#8a6000;font-weight:700"
        return ""

    st.dataframe(
        df_r2.style.applymap(_style_r2_pct, subset=["% PC (AK)"]),
        use_container_width=True, hide_index=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 3: Banner > 0 y PC = 0 → ordenar desc por Banner
# ═══════════════════════════════════════════════════════════════════════════════
r3 = df_raw[
    (df_raw["ban_pct"] > 0) &
    (df_raw["pc_pct"] == 0) &
    (df_raw["pc_st"] != "na")
].copy()
r3 = r3.sort_values("ban_pct", ascending=False)

st.markdown(
    _risk_header(
        "Riesgo 3 — Banner avanzado sin Producción de Contenidos iniciada",
        "Programas con avance en Parametrizar Banner (BB > 0%) pero sin contenidos producidos (AK = 0%)",
        "#0F385A", len(r3),
    ),
    unsafe_allow_html=True,
)

if len(r3) == 0:
    st.markdown(
        '<div style="background:#f0f8e8;border:1px solid #A6CE38;border-radius:8px;'
        'padding:10px 14px;color:#5a7a2e;font-size:12px">✅ Sin programas en este riesgo</div>',
        unsafe_allow_html=True,
    )
else:
    rows_r3 = []
    for _, row in r3.iterrows():
        rows_r3.append({
            "Programa": row["NOMBRE DEL PROGRAMA"],
            "Modalidad": row.get("MODALIDAD", "—"),
            "Facultad": fac_abrev.get(row.get("FACULTAD", ""), row.get("FACULTAD", "—")),
            "Periodo": row.get("PERIODO DE IMPLEMENTACIÓN", "—"),
            "% Banner (BB)": int(row["ban_pct"]),
            "% PC (AK)": int(row["pc_pct"]),
        })
    st.dataframe(pd.DataFrame(rows_r3), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 4: Virtual/Híbrido con PC > 0 y Syllabus sin completar
# ═══════════════════════════════════════════════════════════════════════════════
r4 = df_raw[
    (df_raw["MODALIDAD"].isin(["Virtual", "Híbrido"])) &
    (df_raw["pc_pct"] > 0) &
    (df_raw["syl_val"] == "NO")
].copy()
r4 = r4.sort_values("pc_pct", ascending=False)

st.markdown(
    _risk_header(
        "Riesgo 4 — Contenidos producidos sin Syllabus completado (Virtual/Híbrido)",
        "Programas Virtual/Híbrido con producción de contenidos iniciada (AK > 0%) pero Syllabus incompleto",
        "#A6CE38", len(r4),
    ),
    unsafe_allow_html=True,
)

if len(r4) == 0:
    st.markdown(
        '<div style="background:#f0f8e8;border:1px solid #A6CE38;border-radius:8px;'
        'padding:10px 14px;color:#5a7a2e;font-size:12px">✅ Sin programas en este riesgo</div>',
        unsafe_allow_html=True,
    )
else:
    rows_r4 = []
    for _, row in r4.iterrows():
        rows_r4.append({
            "Programa": row["NOMBRE DEL PROGRAMA"],
            "Modalidad": row.get("MODALIDAD", "—"),
            "Facultad": fac_abrev.get(row.get("FACULTAD", ""), row.get("FACULTAD", "—")),
            "Periodo": row.get("PERIODO DE IMPLEMENTACIÓN", "—"),
            "% PC (AK)": int(row["pc_pct"]),
            "Syllabus": row.get("syl_val", "—"),
        })
    st.dataframe(pd.DataFrame(rows_r4), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RIESGO 5: Banner > 0 y Convenios < 100% → ordenar asc por Convenios
# ═══════════════════════════════════════════════════════════════════════════════
r5 = df_raw[
    (df_raw["ban_pct"] > 0) &
    (df_raw["conv_pct"] < 100)
].copy()
r5 = r5.sort_values("conv_pct", ascending=True)

st.markdown(
    _risk_header(
        "Riesgo 5 — Banner configurado con Convenios pendientes",
        "Programas con Banner avanzado (BB > 0%) pero Convenios Institucionales sin completar (AS < 100%)",
        "#1FB2DE", len(r5),
    ),
    unsafe_allow_html=True,
)

if len(r5) == 0:
    st.markdown(
        '<div style="background:#f0f8e8;border:1px solid #A6CE38;border-radius:8px;'
        'padding:10px 14px;color:#5a7a2e;font-size:12px">✅ Sin programas en este riesgo</div>',
        unsafe_allow_html=True,
    )
else:
    rows_r5 = []
    for _, row in r5.iterrows():
        rows_r5.append({
            "Programa": row["NOMBRE DEL PROGRAMA"],
            "Modalidad": row.get("MODALIDAD", "—"),
            "Facultad": fac_abrev.get(row.get("FACULTAD", ""), row.get("FACULTAD", "—")),
            "Periodo": row.get("PERIODO DE IMPLEMENTACIÓN", "—"),
            "% Banner (BB)": int(row["ban_pct"]),
            "% Convenios (AS)": int(row["conv_pct"]),
        })
    df_r5 = pd.DataFrame(rows_r5)

    def _style_r5_conv(val):
        if isinstance(val, (int, float)):
            if val == 0:
                return "background:#fce8f2;color:#9a0050;font-weight:700"
            if val < 50:
                return "background:#fdf8e8;color:#8a6000;font-weight:700"
        return ""

    st.dataframe(
        df_r5.style.applymap(_style_r5_conv, subset=["% Convenios (AS)"]),
        use_container_width=True, hide_index=True,
    )

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
