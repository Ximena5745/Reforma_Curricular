"""
pages/1_Detalle_por_Etapa.py
Vista consolidada de todas las etapas con conteo de programas por estado.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
from utils.data_loader import (
    load_data, apply_filters, ETAPAS_MAP, PROCESOS,
    PROCESO_COLOR, STATUS_LABEL, STATUS_COLOR, color_for_pct,
)

st.set_page_config(
    page_title="Detalle por Etapa · Reforma Curricular",
    page_icon="📋",
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
.block-container { 
    padding-top: 3.5rem !important; 
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}
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
button[data-baseweb="tab"]         { color: #6a8a9e !important; background: transparent !important; font-size: 13px !important; font-weight: 500 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #0F385A !important; border-bottom-color: #1FB2DE !important; font-weight: 700 !important; }
[data-testid="stDataFrame"]        { border-radius: 10px; overflow: hidden; box-shadow: 0 1px 6px rgba(15,56,90,0.08); }
hr                                  { border-color: rgba(15,56,90,0.10) !important; }
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
[data-testid="stExpander"]         { background: #FFFFFF; border: 1px solid rgba(15,56,90,0.10); border-radius: 10px; }
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

niveles = [n for n in ["Pregrado", "Posgrado"] if "NIVEL_HOMOLOGADO" in df_raw.columns and n in df_raw["NIVEL_HOMOLOGADO"].values]


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
    'Detalle por Etapa</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    'Estado consolidado de etapas con conteo de programas por estado</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Filtros ─────────────────────────────────────────────────────────────────────
_use_pills = hasattr(st, "pills")
_mods_ops  = sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
fac_ops    = sorted([fac_abrev.get(f, f) for f in df_raw["FACULTAD"].dropna().unique()])
_pers_ops  = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())
_proc_ops  = ["Todos los procesos"] + PROCESOS

def _clear_p1():
    st.session_state["p1_mod"]   = []
    st.session_state["p1_fac"]   = []
    st.session_state["p1_per"]   = []
    st.session_state["p1_nivel"] = []
    st.session_state["p1_proc"]  = "Todos los procesos"
    st.session_state["p1_search_table"] = ""
    # Clear table filters
    st.session_state["p1_mod_filt"] = []
    st.session_state["p1_fac_filt"] = []
    st.session_state["p1_per_filt"] = []
    st.session_state["p1_nivel_filt"] = []
    st.session_state["p1_clear_table"] = False

_LBL = ('style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;'
        'letter-spacing:.4px;white-space:nowrap"')

with st.container():
    # Fila 1: MODALIDAD · FACULTAD · LIMPIAR
    lb1, in1, _sp, lb2, in2, btn_col = st.columns([0.6, 2.5, 0.05, 0.6, 2.7, 0.5])
    with lb1:
        st.markdown(f'<div {_LBL}>📋 MODALIDAD</div>', unsafe_allow_html=True)
    with in1:
        if _use_pills:
            sel_mod = st.pills("mod", _mods_ops, selection_mode="multi",
                               key="p1_mod", label_visibility="collapsed")
        else:
            sel_mod = st.multiselect("mod", _mods_ops, key="p1_mod",
                                     label_visibility="collapsed", placeholder="Todas")
    with lb2:
        st.markdown(f'<div {_LBL}>🏛️ FACULTAD</div>', unsafe_allow_html=True)
    with in2:
        if _use_pills:
            sel_fac = st.pills("fac", fac_ops, selection_mode="multi",
                               key="p1_fac", label_visibility="collapsed")
        else:
            sel_fac = st.multiselect("fac", fac_ops, key="p1_fac",
                                     label_visibility="collapsed", placeholder="Todas")
    with btn_col:
        st.button("✕", on_click=_clear_p1, type="primary", key="p1_clear")

    # Fila 2: PERÍODO · NIVEL · PROCESO · contador
    lb3, in3, lb_nivel, in_nivel, _sp2, lb4, in4, cnt_col = st.columns([0.6, 2.3, 0.65, 2.0, 0.05, 0.85, 2.3, 1.1])
    with lb3:
        st.markdown(f'<div {_LBL}>📅 PERÍODO</div>', unsafe_allow_html=True)
    with in3:
        if _use_pills:
            sel_per = st.pills("per", _pers_ops, selection_mode="multi",
                               key="p1_per", label_visibility="collapsed")
        else:
            sel_per = st.multiselect("per", _pers_ops, key="p1_per",
                                     label_visibility="collapsed", placeholder="Todos")
    with lb_nivel:
        st.markdown(f'<div {_LBL}>🎓 NIVEL</div>', unsafe_allow_html=True)
    with in_nivel:
        if _use_pills:
            sel_nivel = st.pills("nivel", niveles, selection_mode="multi", key="p1_nivel", label_visibility="collapsed")
        else:
            sel_nivel = st.multiselect("nivel", niveles, key="p1_nivel", label_visibility="collapsed", placeholder="Todos")
    with lb4:
        st.markdown(f'<div {_LBL}>⚙️ PROCESO</div>', unsafe_allow_html=True)
    with in4:
        sel_proc = st.selectbox("proc", _proc_ops, key="p1_proc",
                                label_visibility="collapsed")
    with cnt_col:
        _p1_counter = st.empty()


# Aplicar filtros
modalidad_f = list(sel_mod) if sel_mod else []
facultad_f  = [fac_abrev_inv.get(f, f) for f in sel_fac] if sel_fac else []
periodo_f   = list(sel_per) if sel_per else []
nivel_f     = list(sel_nivel) if sel_nivel else []
df_filt = df_raw.copy()
if nivel_f:
    df_filt = df_filt[df_filt["NIVEL_HOMOLOGADO"].isin(nivel_f)]
df = apply_filters(df_filt, modalidad_f, facultad_f, periodo_f)
n  = len(df)

_p1_counter.markdown(
    f'<div style="padding-top:9px;font-size:12px;color:#6a8a9e;text-align:right;white-space:nowrap">'
    f'<b style="color:#0F385A">{n}</b> de <b style="color:#0F385A">{len(df_raw)}</b></div>',
    unsafe_allow_html=True,
)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — Consolidado por etapa: barra mini + conteos
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"### Consolidado por Etapa &nbsp;"
    f"<span style='font-size:14px;color:#1FB2DE;font-weight:500'>"
    f"{n} programas seleccionados</span>",
    unsafe_allow_html=True,
)

# Cabecera de columnas
st.markdown(
    '<div style="display:flex;align-items:center;gap:8px;padding:4px 12px;'
    'border-bottom:1px solid rgba(15,56,90,0.12);margin-bottom:2px">'
    '<div style="width:220px;font-size:12px;font-weight:700;color:#4a6a7e;text-transform:uppercase;letter-spacing:.5px">Etapa</div>'
    '<div style="width:54px;font-size:12px;font-weight:700;color:#4a6a7e;text-align:center">Avance</div>'
    '<div style="flex:1;font-size:12px;font-weight:700;color:#4a6a7e">Distribución</div>'
    '<div style="width:48px;font-size:12px;font-weight:700;color:#A6CE38;text-align:center">✓ Final</div>'
    '<div style="width:48px;font-size:12px;font-weight:700;color:#1FB2DE;text-align:center">◎ Proc.</div>'
    '<div style="width:48px;font-size:12px;font-weight:700;color:#EC0677;text-align:center">✗ Sin ini.</div>'
    '<div style="width:48px;font-size:12px;font-weight:700;color:#9aabb5;text-align:center">N/A</div>'
    '</div>',
    unsafe_allow_html=True,
)

for proc in PROCESOS:
    if sel_proc != "Todos los procesos" and proc != sel_proc:
        continue

    color     = PROCESO_COLOR[proc]
    proc_idxs = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]

    # Título de proceso
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin:10px 0 3px;padding:0 12px">'
        f'<div style="width:3px;height:14px;background:{color};border-radius:2px;flex-shrink:0"></div>'
        f'<span style="font-size:11px;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:.5px">{proc}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    for i in proc_idxs:
        _, etapa_name, _, tipo = ETAPAS_MAP[i]
        done = int(df[f"cl_{i}"].eq("done").sum())
        inp  = int(df[f"cl_{i}"].eq("inprog").sum())
        nst  = int(df[f"cl_{i}"].eq("nostart").sum())
        dev  = int(df[f"cl_{i}"].eq("devuelto").sum())
        na   = int(df[f"cl_{i}"].eq("na").sum())
        inf_ = int(df[f"cl_{i}"].eq("info").sum())
        na_t = na + inf_

        applicable = max(n - na_t, 1)
        pct = round((done * 100 + inp * 50 + dev * 50) / applicable)
        total_s = max(done + inp + nst + dev + na_t, 1)

        w_done = done / total_s * 100
        w_inp  = inp  / total_s * 100
        w_nst  = nst  / total_s * 100
        w_dev  = dev  / total_s * 100
        w_na   = na_t / total_s * 100

        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'background:#FFFFFF;border:1px solid rgba(15,56,90,0.08);'
            f'border-left:2px solid {color};border-radius:8px;'
            f'padding:5px 12px;margin-bottom:2px">'
            f'<div style="width:220px;flex-shrink:0;font-size:10px;color:#4a6a7e;'
            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="{etapa_name}">{etapa_name}</div>'
            f'<div style="width:54px;flex-shrink:0;text-align:center">'
            f'<span style="font-size:12px;font-weight:700;color:{color}">{pct}%</span>'
            f'</div>'
            f'<div style="flex:1;height:6px;background:rgba(15,56,90,0.07);border-radius:3px;overflow:hidden">'
            f'<div style="display:flex;height:100%">'
            f'<div style="width:{w_done:.1f}%;background:#A6CE38"></div>'
            f'<div style="width:{w_inp:.1f}%;background:#1FB2DE"></div>'
            f'<div style="width:{w_dev:.1f}%;background:#FBAF17"></div>'
            f'<div style="width:{w_nst:.1f}%;background:#EC0677"></div>'
            f'<div style="width:{w_na:.1f}%;background:#ccd5dc"></div>'
            f'</div></div>'
            f'<div style="width:48px;text-align:center;font-size:13px;font-weight:600;color:#A6CE38">{done}</div>'
            f'<div style="width:48px;text-align:center;font-size:13px;font-weight:600;color:#1FB2DE">{inp}</div>'
            f'<div style="width:48px;text-align:center;font-size:13px;font-weight:600;color:#FBAF17">{dev}</div>'
            f'<div style="width:48px;text-align:center;font-size:13px;font-weight:600;color:#EC0677">{nst}</div>'
            f'<div style="width:48px;text-align:center;font-size:13px;color:#9aabb5">{na_t}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — Gráfico de barras apiladas por proceso (conteo total)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Vista Gráfica por Proceso")

proc_names_f = []
p_done_f, p_inp_f, p_nst_f, p_dev_f, p_na_f, p_pct_f = [], [], [], [], [], []

for proc in PROCESOS:
    if sel_proc != "Todos los procesos" and proc != sel_proc:
        continue
    proc_idxs = [i for i,(p,_,_,_) in enumerate(ETAPAS_MAP) if p==proc]
    d  = sum(int(df[f"cl_{i}"].eq("done").sum())   for i in proc_idxs)
    i_ = sum(int(df[f"cl_{i}"].eq("inprog").sum()) for i in proc_idxs)
    ns = sum(int(df[f"cl_{i}"].eq("nostart").sum())for i in proc_idxs)
    dv = sum(int(df[f"cl_{i}"].eq("devuelto").sum()) for i in proc_idxs)
    na = sum(int(df[f"cl_{i}"].eq("na").sum()) + int(df[f"cl_{i}"].eq("info").sum()) for i in proc_idxs)
    vals = df[f"proc_{proc}"].dropna()
    pct  = int(vals.mean()) if len(vals) > 0 else 0

    proc_names_f.append(proc)
    p_done_f.append(d); p_inp_f.append(i_); p_nst_f.append(ns); p_dev_f.append(dv)
    p_na_f.append(na);  p_pct_f.append(pct)

col_g1, col_g2 = st.columns([2, 2])

with col_g1:
    st.markdown("##### Distribución de estados por proceso (etapas × programas)")
    fig_sp = go.Figure()
    all_data = [
        (p_done_f, "Finalizado",  "#A6CE38"),
        (p_inp_f,  "En proceso",  "#1FB2DE"),
        (p_dev_f,  "Devuelto",    "#FBAF17"),
        (p_nst_f,  "Sin iniciar", "#EC0677"),
        (p_na_f,   "No aplica",   "#ccd5dc"),
    ]
    proc_totals = [sum(lst[k] for lst, _, _ in all_data) for k in range(len(proc_names_f))]
    for vals_lst, lbl, clr in all_data:
        pcts = [round(vals_lst[k] / max(proc_totals[k], 1) * 100, 1) for k in range(len(proc_names_f))]
        htxt = [f"<b>{proc_names_f[k]}</b><br>{lbl}: {vals_lst[k]} ({pcts[k]}%)" for k in range(len(proc_names_f))]
        txt  = [str(vals_lst[k]) if pcts[k] >= 9 else "" for k in range(len(proc_names_f))]
        fig_sp.add_trace(go.Bar(
            name=lbl, y=proc_names_f, x=pcts, orientation="h",
            marker_color=clr, marker_line_width=0,
            text=txt, textposition="inside", insidetextanchor="middle",
            constraintext="none", textangle=0,
            textfont=dict(size=10, color="white", family="Segoe UI"),
            hovertext=htxt, hoverinfo="text",
        ))
    # max label length to set left margin
    max_lbl = max((len(p) for p in proc_names_f), default=10)
    fig_sp.update_layout(
        barmode="stack", height=max(200, len(proc_names_f) * 38 + 60),
        margin=dict(l=max_lbl * 6, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        uniformtext=dict(minsize=8, mode="hide"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=10, color="#4a6a7e"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(range=[0, 100], ticksuffix="%", showgrid=True,
                   gridcolor="rgba(15,56,90,0.07)", color="#4a6a7e", tickfont=dict(size=10)),
        yaxis=dict(color="#0F385A", tickfont=dict(size=10), autorange="reversed",
                   side="left", automargin=False, ticklabelposition="outside left", ticklen=0),
        font=dict(family="Segoe UI"),
        bargap=0.28,
    )
    st.plotly_chart(fig_sp, use_container_width=True, config={"displayModeBar": False})

with col_g2:
    st.markdown("##### Avance promedio por proceso (%)")
    colors_p = [PROCESO_COLOR[p] for p in proc_names_f]
    fig_pct = go.Figure(go.Bar(
        x=p_pct_f, y=proc_names_f, orientation="h",
        marker_color=colors_p,
        text=[f"{v}%" for v in p_pct_f],
        textposition="outside",
        textfont=dict(size=10, color="#4a6a7e"),
    ))
    fig_pct.update_layout(
        height=max(250, len(proc_names_f) * 52 + 60),
        margin=dict(l=0, r=50, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 118], showgrid=True, gridcolor="rgba(15,56,90,0.07)",
                   color="#4a6a7e", tickfont=dict(size=10)),
        yaxis=dict(color="#0F385A", tickfont=dict(size=10), autorange="reversed"),
        font=dict(family="Segoe UI"),
        showlegend=False,
    )
    st.plotly_chart(fig_pct, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — Tabla detalle programa × etapa
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Tabla Detalle por Programa")

FAC_PALETTE = {
    "FSCC": "#EC0677",
    "FIDI": "#1FB2DE",
    "FNGS": "#A6CE38",
}

etapas_show = [(i, em) for i, em in enumerate(ETAPAS_MAP)
               if sel_proc == "Todos los procesos" or em[0] == sel_proc]

# Build base dataframe with columns we know exist
base_cols_existing = {
    "NOMBRE DEL PROGRAMA":       "Programa",
    "FACULTAD":                  "Facultad",
    "MODALIDAD":                 "Modal.",
    "PERIODO DE IMPLEMENTACIÓN": "Periodo",
    "avance_general":            "Avance %",
}

# Find actual column names for extra fields
tipo_tramite_col = None
fecha_notif_col = None
req_min_col = None

# Check for Tipo de trámite (various possible names)
for col in df.columns:
    if "tipo de trámite" in col.lower():
        tipo_tramite_col = col
        break
    elif "tipo de tramite" in col.lower():
        tipo_tramite_col = col
        break

# Check for Estado Radicación Reforma
for col in df.columns:
    if "estado radicación" in col.lower():
        fecha_notif_col = col
        break

# Check for Requiere aprobación ministerial
for col in df.columns:
    if "requiere" in col.lower() and "aprobaci" in col.lower():
        req_min_col = col
        break

# Build base dataframe with existing columns
base_cols = base_cols_existing.copy()
tipo_tramite_label = "Tipo Trámite"
fecha_notif_label = "Estado Radicación"
req_min_label = "Req. Ministerio"

if tipo_tramite_col:
    base_cols[tipo_tramite_col] = tipo_tramite_label
else:
    tipo_tramite_label = None
    
if fecha_notif_col:
    base_cols[fecha_notif_col] = fecha_notif_label
else:
    fecha_notif_label = None
    
if req_min_col:
    base_cols[req_min_col] = req_min_label
else:
    req_min_label = None

df_base = df[list(base_cols.keys())].copy().reset_index(drop=True)
df_det  = df_base.rename(columns=base_cols)
df_det["Facultad"] = df["FACULTAD"].map(fac_abrev).fillna("—").reset_index(drop=True)
df_det["Avance %"] = df_det["Avance %"].apply(lambda x: f"{int(float(x))}%" if pd.notna(x) and str(x).strip() != "" else "—")

# Add original columns for filtering
if "NIVEL_HOMOLOGADO" in df.columns:
    df_det["NIVEL_HOMOLOGADO"] = df["NIVEL_HOMOLOGADO"].reset_index(drop=True)
if "FACULTAD" in df.columns:
    df_det["FACULTAD_ORI"] = df["FACULTAD"].reset_index(drop=True)

# For missing columns, add empty columns
if not tipo_tramite_col:
    df_det["Tipo Trámite"] = "—"
if not fecha_notif_col:
    df_det["Estado Radicación"] = "—"

# Save the actual column names for later use
_extra_cols = {
    "tipo_tramite": tipo_tramite_col,
    "fecha_notif": fecha_notif_col,
    "req_min": req_min_col,
}

# Guardar cl_ para cada etapa (alineado con df_det tras reset_index)
df_cl = df.reset_index(drop=True)

import math as _m

def _p_icon(val):
    """Icono según avance: ✅ (100%), ⚠️ (>0%), 🔴 (0%)"""
    try:
        v = float(val) if val is not None else None
    except:
        v = None
    if v is None:
        return '<span style="color:#b0bec5;font-size:16px">—</span>'
    if _m.isnan(v):
        return '<span style="color:#b0bec5;font-size:16px">—</span>'
    if v >= 100:
        return '<span style="font-size:16px">✅</span>'
    if v > 0:
        return '<span style="font-size:16px">⚠️</span>'
    return '<span style="font-size:16px">🔴</span>'

def _p_syl(s):
    """Icono para Syllabus: ✅ (Si), 🔴 (NO), — (otros)"""
    s = str(s).strip()
    if s == "Si":
        return '<span style="font-size:16px">✅</span>'
    if s == "NO":
        return '<span style="font-size:16px">🔴</span>'
    return '<span style="color:#b0bec5;font-size:16px">—</span>'

def _p_bar(pct):
    """Barra de progreso con porcentaje."""
    try:
        pct = float(pct if pct is not None else 0)
    except:
        pct = 0.0
    if _m.isnan(pct):
        pct = 0.0
    clr = "#15803d" if pct >= 70 else ("#d97706" if pct >= 40 else "#dc2626")
    bar = "#22c55e" if pct >= 70 else ("#f59e0b" if pct >= 40 else "#ef4444")
    return (f'<div style="min-width:60px;text-align:center">'
            f'<div style="font-size:11px;font-weight:700;color:{clr};margin-bottom:2px">{int(pct)}%</div>'
            f'<div style="height:5px;background:#e2e8f0;border-radius:3px;overflow:hidden">'
            f'<div style="width:{min(pct,100):.0f}%;height:100%;background:{bar};border-radius:3px"></div>'
            f'</div></div>')

def _bar_html(pct):
    """Render a percentage value as an HTML progress bar."""
    try:
        p = float(str(pct).replace('%', '').strip())
    except Exception:
        p = 0.0
    p = max(0.0, min(100.0, p))
    # Color scheme: green >=70, orange >=40, red <40
    color = "#22c55e" if p >= 70 else ("#f59e0b" if p >= 40 else "#ef4444")
    return (
        f'<div style="min-width:60px;text-align:center">'
        f'<div style="font-size:12px;font-weight:700;color:#0F385A">{int(p)}%</div>'
        f'<div style="height:6px;background:#e2e8f0;border-radius:4px">'
        f'<div style="width:{p:.0f}%;height:100%;background:{color};border-radius:4px"></div>'
        f'</div></div>'
    )

_CL_STYLE = {
    "done":    "background-color:#edf7e1;color:#2d6a00;font-weight:600",
    "inprog":  "background-color:#e3f4fb;color:#0a5e80;font-weight:600",
    "nostart": "background-color:#fce8f2;color:#9a003e;font-weight:600",
    "na":      "color:#9aabb5;font-style:italic",
    "info":    "color:#9aabb5;font-style:italic",
}

_CL_ICON = {
    "done":    "✓",
    "inprog":  "◉",
    "nostart": "✗",
    "na":      "—",
    "info":    "i",
}

def _fmt_status_with_icon(cl, v):
    """Retorna solo icono para estados."""
    if cl in _CL_ICON:
        icon = _CL_ICON[cl]
        if cl in ("na", "info"):
            return str(v) if v and str(v) not in ("—","nan","None","") else "—"
        return icon
    return str(v) if v and str(v) not in ("—","nan","None","") else "—"

def _fmt_pct(val):
    """Convierte valor decimal (0-1) o entero a texto porcentaje."""
    try:
        v = float(val)
        pct = v * 100 if v <= 1.0 else v
        return f"{int(pct)}%" if pct == int(pct) else f"{pct:.1f}%"
    except (ValueError, TypeError):
        return str(val)

def _fmt_date(val):
    """Convierte número serial Excel a fecha dd/mm/aaaa."""
    try:
        n = int(float(str(val).strip()))
        if n <= 0:
            return "—"
        dt = datetime.date(1899, 12, 30) + datetime.timedelta(days=n)
        return dt.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return str(val) if str(val).strip() not in ("", "None", "nan", "—") else "—"

etapa_labels = []

def _p_esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

_ETAPA_ORDER = [
    "proc_Gestión Académica",
    "proc_Gestión Financiera", 
    "proc_Aseguramiento de la Calidad",
    "syl_val",
    "pc_pct",
    "conv_pct",
    "ban_pct",
]

_ETAPA_DISPLAY = {
    "proc_Gestión Académica": "G. Académica",
    "proc_Gestión Financiera": "C. Financiero",
    "proc_Aseguramiento de la Calidad": "Aseguram.",
    "syl_val": "Syllabus",
    "pc_pct": "Prod. Cont.",
    "conv_pct": "Convenios",
    "ban_pct": "Banner",
}

_ETAPA_TYPE = {
    "proc_Gestión Académica": "proc",
    "proc_Gestión Financiera": "proc",
    "proc_Aseguramiento de la Calidad": "proc",
    "syl_val": "syl",
    "pc_pct": "pct",
    "conv_pct": "pct",
    "ban_pct": "pct",
}

etapa_idx_map = {}
for i, em in enumerate(ETAPAS_MAP):
    proc_key = f"proc_{em[0]}"
    etapa_idx_map[proc_key] = i
    if em[1] == "Syllabus completos":
        etapa_idx_map["syl_val"] = i
    if em[1] == "% avance contenidos virtuales":
        etapa_idx_map["pc_pct"] = i
    if em[1] == "% avance":
        etapa_idx_map["conv_pct"] = i
    if em[1] == "% de avance":
        etapa_idx_map["ban_pct"] = i

for col_key in _ETAPA_ORDER:
    if col_key in etapa_idx_map:
        i = etapa_idx_map[col_key]
        em = ETAPAS_MAP[i]
        tipo = _ETAPA_TYPE.get(col_key, "status")
        col_label = _ETAPA_DISPLAY.get(col_key, em[1][:15])
        etapa_labels.append((i, col_label, tipo, col_key))
        
        raw = df_cl[f"val_{i}"]
        
        if tipo == "pct":
            def _make_pct_formatter(key):
                def _fmt(v):
                    if v in ("", None, "No aplica", "no aplica", "—"):
                        return '<span style="color:#b0bec5;font-size:13px">—</span>'
                    try:
                        fv = float(v)
                        pct = fv * 100 if 0 < fv <= 1 else fv
                        return _p_bar(pct)
                    except:
                        return '<span style="color:#b0bec5;font-size:13px">—</span>'
                return _fmt
            df_det[col_label] = raw.apply(_make_pct_formatter(col_key))
        elif tipo == "syl":
            df_det[col_label] = raw.apply(lambda v: _p_syl(str(v)))
        elif tipo == "proc":
            proc_val = df_cl[f"proc_{em[0]}"].tolist()
            df_det[col_label] = [_p_icon(v) for v in proc_val]
        else:
            cl_col = df_cl[f"cl_{i}"]
            df_det[col_label] = [_fmt_status_with_icon(cl, v) for cl, v in zip(cl_col, raw)]

def _av_col(s):
    out = []
    for val in s:
        try:
            p = int(str(val).replace("%", ""))
            if p >= 70:   out.append("background-color:#edf7e1;color:#2d6a00;font-weight:700")
            elif p >= 40: out.append("background-color:#EBF5FB;color:#0a5e80;font-weight:700")
            else:         out.append("background-color:#fce8f2;color:#9a003e;font-weight:700")
        except:
            out.append("")
    return out

def _fac_col(s):
    out = []
    for val in s:
        c = FAC_PALETTE.get(str(val), "#1FB2DE")
        h = c.lstrip("#")
        r2, g2, b2 = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        out.append(f"background-color:rgba({r2},{g2},{b2},0.12);"
                   f"color:{c};font-weight:700;border-left:3px solid {c}")
    return out

# Filtros antes de la tabla detallada
with st.container():
    # Fila 1: MODALIDAD · FACULTAD · PERIODO
    c1, c2, c3, c4, c5, c6 = st.columns([0.6, 1.8, 0.5, 1.8, 0.5, 2.0])
    with c1:
        st.markdown('<div style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;letter-spacing:.4px">📋 MODALIDAD</div>', unsafe_allow_html=True)
    with c2:
        sel_mod_filt = st.pills("mod_filt", _mods_ops, selection_mode="multi", key="p1_mod_filt", label_visibility="collapsed") if _use_pills else st.multiselect("mod_filt", _mods_ops, key="p1_mod_filt", label_visibility="collapsed", placeholder="Todas")
    with c3:
        st.markdown('<div style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;letter-spacing:.4px">🏛️ FACULTAD</div>', unsafe_allow_html=True)
    with c4:
        sel_fac_filt = st.pills("fac_filt", fac_ops, selection_mode="multi", key="p1_fac_filt", label_visibility="collapsed") if _use_pills else st.multiselect("fac_filt", fac_ops, key="p1_fac_filt", label_visibility="collapsed", placeholder="Todas")
    with c5:
        st.markdown('<div style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;letter-spacing:.4px">📅 PERÍODO</div>', unsafe_allow_html=True)
    with c6:
        sel_per_filt = st.pills("per_filt", _pers_ops, selection_mode="multi", key="p1_per_filt", label_visibility="collapsed") if _use_pills else st.multiselect("per_filt", _pers_ops, key="p1_per_filt", label_visibility="collapsed", placeholder="Todos")
    
    # Fila 2: NIVEL · BUSCAR · LIMPIAR
    c7, c8, c9, c10 = st.columns([0.5, 1.8, 3.5, 0.4])
    with c7:
        st.markdown('<div style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;letter-spacing:.4px">🎓 NIVEL</div>', unsafe_allow_html=True)
    with c8:
        sel_nivel_filt = st.pills("nivel_filt", niveles, selection_mode="multi", key="p1_nivel_filt", label_visibility="collapsed") if _use_pills else st.multiselect("nivel_filt", niveles, key="p1_nivel_filt", label_visibility="collapsed", placeholder="Todos")
    with c9:
        sel_search = st.text_input("search_table", key="p1_search_table", label_visibility="collapsed", placeholder="Digite nombre del programa...")
    with c10:
        st.button("✕", on_click=_clear_p1, type="primary", key="p1_clear_table")

# Apply filters to df_det
if sel_mod_filt:
    df_det = df_det[df_det["Modal."].isin(sel_mod_filt)]
if sel_fac_filt:
    # Filter using original faculty values
    if "FACULTAD_ORI" in df_det.columns:
        df_det = df_det[df_det["FACULTAD_ORI"].isin([fac_abrev_inv.get(f, f) for f in sel_fac_filt])]
    else:
        df_det = df_det[df_det["Facultad"].isin([fac_abrev_inv.get(f, f) for f in sel_fac_filt])]
if sel_per_filt:
    df_det = df_det[df_det["Periodo"].isin(sel_per_filt)]
if sel_nivel_filt and "NIVEL_HOMOLOGADO" in df_det.columns:
    df_det = df_det[df_det["NIVEL_HOMOLOGADO"].isin(sel_nivel_filt)]
if sel_search:
    df_det = df_det[df_det["Programa"].str.contains(sel_search, case=False, na=False)]

# Render detailed table as HTML to properly show icons and progress bars
# Build column headers in the same order as Prioritization tab
header_cols = ["Programa", "Modal.", "Periodo", "Avance %"] + [col_label for _, col_label, _, _ in etapa_labels] + ["Tipo Trámite", "Estado Radicación", "Req. Ministerio"]

# Build HTML header with styling similar to Prioritization tab
header_html = "".join([f'<th style="background:#0F385A;color:#FFFFFF;font-size:10px;font-weight:700;padding:6px 4px;text-align:center;white-space:nowrap;">{c}</th>' for c in header_cols])
hdr = f'<tr>{header_html}</tr>'

# Build HTML rows
rows_html = []
for idx, row in df_det.iterrows():
    rbg = "#FFFFFF" if idx % 2 == 0 else "#f8fafc"
    cells = []
    
    for col in header_cols:
        if col == "Programa":
            prog = _p_esc(row.get("Programa", "—"))
            fac = _p_esc(row.get("Facultad", "—"))
            fac_abbr = fac_abrev.get(fac, fac) if fac != "—" else "—"
            cells.append(f'<td style="padding:6px 4px;text-align:left;vertical-align:middle;border-bottom:1px solid #eef3f8;">{prog}<br><span style="font-size:10px;font-weight:700;color:#EC0677">{fac_abbr}</span></td>')
        elif col == "Facultad":
            # Skip - already shown with Programa
            cells.append(f'<td style="padding:6px 4px;text-align:left;vertical-align:middle;border-bottom:1px solid #eef3f8;"></td>')
        elif col == "Modal.":
            mod = _p_esc(row.get("Modal.", "—"))
            cells.append(f'<td style="padding:6px 4px;text-align:center;vertical-align:middle;border-bottom:1px solid #eef3f8;"><span style="font-size:10px;font-weight:600;color:#0F385A">{mod}</span></td>')
        elif col == "Periodo":
            per = _p_esc(row.get("Periodo", "—"))
            cells.append(f'<td style="padding:6px 4px;text-align:center;vertical-align:middle;border-bottom:1px solid #eef3f8;"><span style="font-size:10px;font-weight:600;color:#0F385A">{per}</span></td>')
        elif col == "Avance %":
            # Use the original value from df_det which already has the % formatted
            avance_val = row.get("Avance %", "0%")
            # Extract numeric value
            try:
                avance_pct = float(str(avance_val).replace("%", "").strip())
            except:
                avance_pct = 0.0
            cells.append(f'<td style="padding:6px 4px;text-align:center;vertical-align:middle;border-bottom:1px solid #eef3f8;">{_bar_html(avance_pct)}</td>')
        elif col == "Tipo Trámite":
            # Use the actual column name from _extra_cols
            actual_col = _extra_cols.get("tipo_tramite", "Tipo Trámite")
            val = str(row.get(actual_col, row.get("Tipo Trámite", "—")))
            cells.append(f'<td style="padding:6px 4px;text-align:center;vertical-align:middle;border-bottom:1px solid #eef3f8;">{val}</td>')
        elif col == "Estado Radicación":
            actual_col = _extra_cols.get("fecha_notif", "ESTADO RADICACIÓN REFORMA")
            val = str(row.get(actual_col, row.get("Estado Radicación", "—")))
            cells.append(f'<td style="padding:6px 4px;text-align:center;vertical-align:middle;border-bottom:1px solid #eef3f8;">{val}</td>')
        elif col == "Req. Ministerio":
            actual_col = _extra_cols.get("req_min", "¿Requiere aprobación ministerial?")
            val = str(row.get(actual_col, row.get("Req. Ministerio", "—")))
            cells.append(f'<td style="padding:6px 4px;text-align:center;vertical-align:middle;border-bottom:1px solid #eef3f8;">{val}</td>')
        else:
            # Handle etapa columns
            val = str(row.get(col, "")) if col in row else "—"
            cells.append(f'<td style="padding:6px 4px;text-align:center;vertical-align:middle;border-bottom:1px solid #eef3f8;">{val}</td>')
    
    rows_html.append(f'<tr style="background: {"#ffffff" if idx%2==0 else "#f8fafc"};">{"".join(cells)}</tr>')

# Build final HTML table
tabla_det = (
    '<div style="overflow-x:auto;border-radius:12px;'
    'border:1.5px solid #b5c9d8;box-shadow:0 2px 12px rgba(15,56,90,.10);background:#fafdff">'
    '<table style="width:100%;table-layout:auto;border-collapse:separate;border-spacing:0;font-family:\'Segoe UI\',sans-serif">'
    '<thead><tr>' + header_html + '</tr></thead><tbody>'
    + "".join(rows_html) +
    '</tbody></table></div>'
)

st.markdown(tabla_det, unsafe_allow_html=True)
st.caption(f"{len(df_det)} programas · {len(etapa_labels)} etapas mostradas")

