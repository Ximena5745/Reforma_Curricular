"""
pages/2_Programa.py
Vista general de programas con conteo de etapas + ficha detallada por programa.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
from utils.data_loader import (
    load_data, apply_filters, ETAPAS_MAP, PROCESOS, PROCESO_COLOR,
    STATUS_LABEL, STATUS_COLOR, color_for_pct,
)

st.set_page_config(
    page_title="Programas · Reforma Curricular",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #EEF3F8; }
[data-testid="stHeader"] {
    background: linear-gradient(135deg, #0F385A 0%, #1A5276 50%, #1FB2DE 100%) !important;
    border-bottom: 3px solid #42F2F2 !important;
}
h1,h2,h3,h4,h5                     { font-family: 'Segoe UI', sans-serif; color: #0F385A !important; }
p, li, label, caption               { color: #2a4a5e; }
[data-testid="stCaption"]           { color: #6a8a9e !important; }
.block-container { padding-top: 3.5rem !important; padding-bottom: 2rem; }
div[data-baseweb="select"] > div {
    background: #E3F4FB !important;
    border-color: rgba(31,178,222,0.45) !important;
    color: #0F385A !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] span    { color: #0F385A !important; }
[data-testid="stSelectbox"] label  { font-size: 12px; color: #4a6a7e; }
ul[data-baseweb="menu"]            { background: #FFFFFF !important; border: 1px solid rgba(31,178,222,0.30) !important; box-shadow: 0 6px 20px rgba(15,56,90,0.14) !important; border-radius: 8px !important; }
ul[data-baseweb="menu"] li         { color: #0F385A !important; background: #FFFFFF !important; }
ul[data-baseweb="menu"] li:hover   { background: #E3F4FB !important; }
li[aria-selected="true"]           { background: #d0ecf8 !important; font-weight: 600 !important; }
[data-testid="stMetric"]           { background: #FFFFFF; border: 1px solid rgba(15,56,90,0.10);
                                     border-radius: 10px; padding: 12px 14px;
                                     box-shadow: 0 2px 6px rgba(15,56,90,0.06); }
[data-testid="stMetric"] > div:first-child { color: #6a8a9e !important; font-size: 11px !important; text-transform: uppercase; }
[data-testid="stMetricValue"]      { font-size: 20px !important; font-weight: 700 !important; color: #0F385A !important; }
[data-testid="stDataFrame"]        { border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(15,56,90,0.08); }
button[data-baseweb="tab"]         { color: #6a8a9e !important; background: transparent !important; font-size: 13px !important; font-weight: 500 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #0F385A !important; border-bottom-color: #1FB2DE !important; font-weight: 700 !important; }
hr  { border-color: rgba(15,56,90,0.10) !important; }
[data-testid="stExpander"] { background: #FFFFFF; border: 1px solid rgba(15,56,90,0.10); border-radius: 10px; }
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
    padding: 0 10px !important; line-height: 1 !important;
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
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F385A 0%, #1A5276 45%, #1FB2DE 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label  { color: rgba(255,255,255,0.80) !important; }
[data-testid="stSidebar"] hr     { border-color: rgba(255,255,255,0.20) !important; }
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
</style>
""", unsafe_allow_html=True)

# ── Datos ──────────────────────────────────────────────────────────────────────
df_raw = load_data()

FAC_LABELS = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}
FAC_ABREV = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación":    "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
}
fac_inv       = {v: k for k, v in FAC_LABELS.items()}
fac_abrev_inv = {v: k for k, v in FAC_ABREV.items()}

PROC_SHORT = {
    "Gestión Académica":                       "Gest. Académica",
    "Gestión Financiera":                      "Gest. Financiera",
    "Aseguramiento de la Calidad":             "Aseg. Calidad",
    "Producción de Contenidos":                "Prod. Contenidos",
    "Convenios Institucionales":               "Convenios",
    "Parametrizar Reforma en Banner":          "Banner",
    "Publicación en Página Web":               "Pág. Web",
}

N_ETAPAS = len(ETAPAS_MAP)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
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

# ── Header banner ───────────────────────────────────────────────────────────────
st.markdown(
    '<div style="'
    'background:linear-gradient(135deg,#0F385A 0%,#1A5276 50%,#1FB2DE 100%);'
    'padding:18px 24px 14px;'
    'border-radius:0 0 12px 12px;'
    'border-bottom:3px solid #42F2F2;">'
    '<div style="font-size:21px;font-weight:700;color:#FFFFFF;letter-spacing:-.3px">'
    'Resumen Programa</div>'
    f'<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    f'Vista general con conteo de etapas completadas · {len(df_raw)} programas totales</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Filtros ─────────────────────────────────────────────────────────────────────
_use_pills = hasattr(st, "pills")
fac_ops    = sorted([FAC_ABREV.get(f, f) for f in df_raw["FACULTAD"].dropna().unique()])
_mods_ops  = sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
_pers_ops  = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())

def _clear_p2():
    st.session_state["p2_mod"] = []
    st.session_state["p2_fac"] = []
    st.session_state["p2_per"] = []

_LBL = ('style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;'
        'letter-spacing:.4px;white-space:nowrap"')

with st.container():
    # Fila 1: MODALIDAD · FACULTAD · LIMPIAR
    lb1, in1, _sp, lb2, in2, btn_col = st.columns([0.6, 2.5, 0.05, 0.6, 2.7, 0.8])
    with lb1:
        st.markdown(f'<div {_LBL}>📋 MODALIDAD</div>', unsafe_allow_html=True)
    with in1:
        if _use_pills:
            sel_mod = st.pills("mod", _mods_ops, selection_mode="multi",
                               key="p2_mod", label_visibility="collapsed")
        else:
            sel_mod = st.multiselect("mod", _mods_ops, key="p2_mod",
                                     label_visibility="collapsed", placeholder="Todas")
    with lb2:
        st.markdown(f'<div {_LBL}>🏛️ FACULTAD</div>', unsafe_allow_html=True)
    with in2:
        if _use_pills:
            sel_fac = st.pills("fac", fac_ops, selection_mode="multi",
                               key="p2_fac", label_visibility="collapsed")
        else:
            sel_fac = st.multiselect("fac", fac_ops, key="p2_fac",
                                     label_visibility="collapsed", placeholder="Todas")
    with btn_col:
        st.button("✕ LIMPIAR", on_click=_clear_p2,
                  type="primary", key="p2_clear")

    # Fila 2: PERÍODO · contador
    lb3, in3, cnt_col = st.columns([0.6, 5.15, 1.65])
    with lb3:
        st.markdown(f'<div {_LBL}>📅 PERÍODO</div>', unsafe_allow_html=True)
    with in3:
        if _use_pills:
            sel_per = st.pills("per", _pers_ops, selection_mode="multi",
                               key="p2_per", label_visibility="collapsed")
        else:
            sel_per = st.multiselect("per", _pers_ops, key="p2_per",
                                     label_visibility="collapsed", placeholder="Todos")
    with cnt_col:
        _p2_counter = st.empty()

# Aplicar filtros
modalidad_f = list(sel_mod) if sel_mod else []
facultad_f  = [fac_abrev_inv.get(f, f) for f in sel_fac] if sel_fac else []
periodo_f   = list(sel_per) if sel_per else []
df = apply_filters(df_raw.copy(), modalidad_f, facultad_f, periodo_f)

_p2_counter.markdown(
    f'<div style="padding-top:9px;font-size:12px;color:#6a8a9e;text-align:right;white-space:nowrap">'
    f'Mostrando <b style="color:#0F385A">{len(df)}</b> de '
    f'<b style="color:#0F385A">{len(df_raw)}</b></div>',
    unsafe_allow_html=True,
)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — Tabla general de programas con conteo de etapas
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"### Resumen General &nbsp;<span style='font-size:14px;color:#1FB2DE;font-weight:500'>"
    f"{len(df)} programas</span>",
    unsafe_allow_html=True,
)
st.caption("Selecciona un programa en la tabla para ver su ficha detallada")

# Construir tabla de overview con conteo de etapas
overview_rows = []
for idx_r, (_, row) in enumerate(df.iterrows()):
    done = sum(1 for i in range(N_ETAPAS) if row[f"cl_{i}"] == "done")
    inp  = sum(1 for i in range(N_ETAPAS) if row[f"cl_{i}"] == "inprog")
    nst  = sum(1 for i in range(N_ETAPAS) if row[f"cl_{i}"] == "nostart")
    na   = sum(1 for i in range(N_ETAPAS) if row[f"cl_{i}"] in ("na", "info"))
    overview_rows.append({
        "_row_idx":        idx_r,
        "Programa":        row["NOMBRE DEL PROGRAMA"],
        "Facultad":        FAC_ABREV.get(row["FACULTAD"], row["FACULTAD"]),
        "Modalidad":       row["MODALIDAD"],
        "Nivel":           row["NIVEL"],
        "Periodo":         row["PERIODO DE IMPLEMENTACIÓN"],
        "Avance %":        int(row["avance_general"]),
        f"✓ Finalizadas":  done,
        f"◎ En proceso":   inp,
        f"✗ Sin iniciar":  nst,
        f"N/A":            na,
    })

df_ov = pd.DataFrame(overview_rows)

event = st.dataframe(
    df_ov.drop(columns=["_row_idx"]),
    use_container_width=True,
    height=380,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    column_config={
        "Programa":       st.column_config.TextColumn("Programa",      width="large"),
        "Facultad":       st.column_config.TextColumn("Facultad",      width="small"),
        "Modalidad":      st.column_config.TextColumn("Modalidad",     width="small"),
        "Nivel":          st.column_config.TextColumn("Nivel",         width="small"),
        "Periodo":        st.column_config.TextColumn("Periodo",       width="small"),
        "Avance %":       st.column_config.ProgressColumn("Avance %",  min_value=0, max_value=100, format="%d%%"),
        "✓ Finalizadas":  st.column_config.NumberColumn("✓ Finalizadas", help=f"Etapas finalizadas de {N_ETAPAS} totales"),
        "◎ En proceso":   st.column_config.NumberColumn("◎ En proceso"),
        "✗ Sin iniciar":  st.column_config.NumberColumn("✗ Sin iniciar"),
        "N/A":            st.column_config.NumberColumn("N/A"),
    },
)

# ── Obtener programa seleccionado ──────────────────────────────────────────────
selected_rows = event.selection.rows if event and hasattr(event, "selection") else []

if not selected_rows:
    st.info("👆 Selecciona un programa en la tabla para ver su ficha completa.")
    st.stop()

# Fila seleccionada en df (no en df_ov porque df_ov ya está indexado de 0..n-1)
sel_ov_idx = selected_rows[0]
row = df.iloc[sel_ov_idx]

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — Ficha del programa seleccionado
# ══════════════════════════════════════════════════════════════════════════════
av        = int(row["avance_general"])
av_color  = color_for_pct(av)
fac_short = FAC_LABELS.get(row["FACULTAD"], row["FACULTAD"])

# Header de la ficha
st.markdown(
    f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,.10);'
    f'border-left:5px solid {av_color};border-radius:12px;'
    f'padding:16px 20px;margin-bottom:12px;box-shadow:0 2px 10px rgba(15,56,90,.07)">'
    f'<div style="font-size:18px;font-weight:700;color:#0F385A;margin-bottom:4px">'
    f'{row["NOMBRE DEL PROGRAMA"]}</div>'
    f'<div style="font-size:12px;color:#4a6a7e">{row.get("ESCUELA","")}</div>'
    f'<div style="font-size:11px;color:#8aabb0;margin-top:2px">{fac_short}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# Métricas de la ficha
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Modalidad", row["MODALIDAD"])
m2.metric("Nivel",     row["NIVEL"])
m3.metric("Sede",      row["SEDE"])
m4.metric("Periodo",   row["PERIODO DE IMPLEMENTACIÓN"])
m5.metric("Avance",    f"{av}%")

# Resumen visual de etapas de este programa
done_p = sum(1 for i in range(N_ETAPAS) if row[f"cl_{i}"] == "done")
inp_p  = sum(1 for i in range(N_ETAPAS) if row[f"cl_{i}"] == "inprog")
nst_p  = sum(1 for i in range(N_ETAPAS) if row[f"cl_{i}"] == "nostart")
na_p   = sum(1 for i in range(N_ETAPAS) if row[f"cl_{i}"] in ("na", "info"))

st.markdown(
    f'<div style="display:flex;gap:10px;margin:10px 0;flex-wrap:wrap">'
    f'<div style="background:#f0f8e8;border:1px solid #A6CE38;border-radius:8px;padding:8px 16px;text-align:center">'
    f'<div style="font-size:20px;font-weight:700;color:#5a8a10">{done_p}</div>'
    f'<div style="font-size:10px;color:#5a8a10;text-transform:uppercase;letter-spacing:.5px">Finalizadas</div></div>'
    f'<div style="background:#e8f6fc;border:1px solid #1FB2DE;border-radius:8px;padding:8px 16px;text-align:center">'
    f'<div style="font-size:20px;font-weight:700;color:#0a6a8e">{inp_p}</div>'
    f'<div style="font-size:10px;color:#0a6a8e;text-transform:uppercase;letter-spacing:.5px">En proceso</div></div>'
    f'<div style="background:#fce8f2;border:1px solid #EC0677;border-radius:8px;padding:8px 16px;text-align:center">'
    f'<div style="font-size:20px;font-weight:700;color:#9a0050">{nst_p}</div>'
    f'<div style="font-size:10px;color:#9a0050;text-transform:uppercase;letter-spacing:.5px">Sin iniciar</div></div>'
    f'<div style="background:#f0f4f8;border:1px solid #c8d8e0;border-radius:8px;padding:8px 16px;text-align:center">'
    f'<div style="font-size:20px;font-weight:700;color:#6a8a9e">{na_p}</div>'
    f'<div style="font-size:10px;color:#6a8a9e;text-transform:uppercase;letter-spacing:.5px">N/A / Info</div></div>'
    f'<div style="flex:1;min-width:200px;background:#FFFFFF;border:1px solid rgba(15,56,90,.10);'
    f'border-radius:8px;padding:8px 14px;display:flex;align-items:center;gap:10px">'
    f'<div style="flex:1;height:8px;background:#f0f4f8;border-radius:4px;overflow:hidden">'
    f'<div style="display:flex;height:100%">'
    f'<div style="width:{done_p/N_ETAPAS*100:.1f}%;background:#A6CE38"></div>'
    f'<div style="width:{inp_p/N_ETAPAS*100:.1f}%;background:#1FB2DE"></div>'
    f'<div style="width:{nst_p/N_ETAPAS*100:.1f}%;background:#EC0677"></div>'
    f'<div style="width:{na_p/N_ETAPAS*100:.1f}%;background:#c8d8e0"></div>'
    f'</div></div>'
    f'<div style="font-size:14px;font-weight:700;color:{av_color};width:40px;text-align:right">{av}%</div>'
    f'<div style="font-size:10px;color:#8aabb0">de {N_ETAPAS} etapas</div>'
    f'</div></div>',
    unsafe_allow_html=True,
)

st.divider()

# ── Tabs por proceso ───────────────────────────────────────────────────────────
st.markdown("### Detalle por Proceso y Etapa")

CL_ICON = {"done": "✅", "inprog": "🔵", "nostart": "🔴", "info": "ℹ️", "na": "⬜"}
def _fmt_val(val, tipo):
    """Formatea el valor según el tipo de campo."""
    s = str(val).strip()
    if s in ("—", "No aplica", "no aplica", "None", "nan", ""):
        return s
    if tipo in ("pct", "pct_nostart"):
        try:
            v = float(s)
            pct = v * 100 if v <= 1.0 else v
            return f"{int(pct)}%" if pct == int(pct) else f"{pct:.1f}%"
        except (ValueError, TypeError):
            return s
    if tipo == "date":
        try:
            n = int(float(s))
            if n <= 0:
                return "—"
            dt = datetime.date(1899, 12, 30) + datetime.timedelta(days=n)
            return dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return s
    return s
tabs = st.tabs([PROC_SHORT.get(p, p) for p in PROCESOS])

for tab, proc in zip(tabs, PROCESOS):
    with tab:
        color      = PROCESO_COLOR[proc]
        proc_idxs  = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]
        proc_pct   = row.get(f"proc_{proc}")
        pct_disp   = f"{int(proc_pct)}%" if pd.notna(proc_pct) and proc_pct == proc_pct else "N/A"

        # Encabezado del proceso
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;'
            f'padding:10px 14px;background:#FFFFFF;border:1px solid rgba(15,56,90,.10);'
            f'border-left:4px solid {color};border-radius:10px;'
            f'box-shadow:0 1px 4px rgba(15,56,90,.06)">'
            f'<div style="font-size:14px;font-weight:700;color:{color};flex:1">{proc}</div>'
            f'<div style="font-size:22px;font-weight:800;color:{color}">{pct_disp}</div>'
            f'<div style="font-size:10px;color:#8aabb0">avance</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Tarjetas de etapas
        ncols = min(len(proc_idxs), 4)
        ecols = st.columns(ncols)
        for col_i, i in enumerate(proc_idxs):
            _, etapa_name, _, tipo = ETAPAS_MAP[i]
            cl         = row[f"cl_{i}"]
            val        = _fmt_val(row[f"val_{i}"], tipo)
            status_lbl = STATUS_LABEL.get(cl, "—")
            status_clr = STATUS_COLOR.get(cl, "#9aabb5")
            icon       = CL_ICON.get(cl, "")

            # Background de la tarjeta según estado
            bg_map = {
                "done":    "#f6fbee",
                "inprog":  "#e8f6fc",
                "nostart": "#fef0f7",
                "info":    "#fffbeb",
                "na":      "#f8f9fa",
            }
            bg = bg_map.get(cl, "#FFFFFF")

            with ecols[col_i % ncols]:
                st.markdown(
                    f'<div style="background:{bg};border:1px solid rgba(15,56,90,.10);'
                    f'border-left:3px solid {status_clr};border-radius:10px;'
                    f'padding:12px 14px;margin-bottom:8px;'
                    f'box-shadow:0 1px 4px rgba(15,56,90,.05)">'
                    f'<div style="font-size:10px;color:#6a8a9e;margin-bottom:6px;'
                    f'line-height:1.3;font-weight:500">{etapa_name}</div>'
                    f'<div style="font-size:12px;font-weight:600;color:#0F385A;'
                    f'word-break:break-word;margin-bottom:8px;'
                    f'border-bottom:1px solid rgba(15,56,90,.08);padding-bottom:6px">{val}</div>'
                    f'<div style="font-size:11px;font-weight:700;color:{status_clr}">'
                    f'{icon} {status_lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

# ── Tabla valores completa ────────────────────────────────────────────────────
st.divider()

FAC_PALETTE = {
    "FSCC": "#EC0677",
    "FIDI": "#1FB2DE",
    "FNGS": "#A6CE38",
}

# Estilos por estado (cl_)
_CL_BG = {
    "done":    "background-color:#edf7e1;color:#2d6a00;font-weight:600",
    "inprog":  "background-color:#e3f4fb;color:#0a5e80;font-weight:600",
    "nostart": "background-color:#fce8f2;color:#9a003e;font-weight:600",
    "na":      "color:#9aabb5;font-style:italic",
    "info":    "color:#9aabb5;font-style:italic",
}

with st.expander("Ver tabla completa de valores para este programa"):
    rows_data = []
    cl_list   = []
    proc_list = []
    tipo_list = []

    for i, (proc, etapa, col_excel, tipo) in enumerate(ETAPAS_MAP):
        cl  = row[f"cl_{i}"]
        val = _fmt_val(row[f"val_{i}"], tipo)
        rows_data.append({
            "Proceso": proc,
            "Etapa":   etapa,
            "Valor":   val,
            "Estado":  STATUS_LABEL.get(cl, "—"),
        })
        cl_list.append(cl)
        proc_list.append(proc)
        tipo_list.append(tipo)

    df_tbl = pd.DataFrame(rows_data)

    # ── Styler columna por columna ──
    def _proc_col(s):
        return [
            f"background-color:rgba({int(PROCESO_COLOR[p][1:3],16)},"
            f"{int(PROCESO_COLOR[p][3:5],16)},"
            f"{int(PROCESO_COLOR[p][5:7],16)},0.12);"
            f"color:{PROCESO_COLOR[p]};font-weight:700"
            if p in PROCESO_COLOR else ""
            for p in proc_list
        ]

    def _estado_col(s):
        return [_CL_BG.get(cl, "") for cl in cl_list]

    def _valor_col(s):
        styles = []
        for cl, tp in zip(cl_list, tipo_list):
            base = _CL_BG.get(cl, "")
            if tp == "pct" and cl not in ("na", "info"):
                base += ";font-weight:700"
            styles.append(base)
        return styles

    styled_tbl = (
        df_tbl.style
        .apply(_proc_col,   subset=["Proceso"])
        .apply(_valor_col,  subset=["Valor"])
        .apply(_estado_col, subset=["Estado"])
    )

    st.dataframe(
        styled_tbl,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            "Proceso": st.column_config.TextColumn("Proceso", width="medium"),
            "Etapa":   st.column_config.TextColumn("Etapa",   width="large"),
            "Valor":   st.column_config.TextColumn("Valor",   width="medium"),
            "Estado":  st.column_config.TextColumn("Estado",  width="small"),
        },
    )
