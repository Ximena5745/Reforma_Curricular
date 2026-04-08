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
    page_title="Detalle por Etapa ?? Reforma Curricular",
    page_icon="????",
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

# ?????? Datos ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
df_raw = load_data()

niveles = [n for n in ["Pregrado", "Posgrado"] if "NIVEL_HOMOLOGADO" in df_raw.columns and n in df_raw["NIVEL_HOMOLOGADO"].values]


fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingenier??a, Dise??o e Innovaci??n":    "Ingenier??a, Dise??o e Innovaci??n",
    "Facultad de Negocios, Gesti??n y Sostenibilidad": "Negocios, Gesti??n y Sostenibilidad",
}
fac_abrev = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingenier??a, Dise??o e Innovaci??n":    "FIDI",
    "Facultad de Negocios, Gesti??n y Sostenibilidad": "FNGS",
}
fac_inv       = {v: k for k, v in fac_labels.items()}
fac_abrev_inv = {v: k for k, v in fac_abrev.items()}

# ?????? Sidebar ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
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
        'POLI © 2025–2026</div>',
        unsafe_allow_html=True,
    )

# ?????? Header banner ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
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

# ?????? Filtros ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
_use_pills = hasattr(st, "pills")
_mods_ops  = sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
fac_ops    = sorted([fac_abrev.get(f, f) for f in df_raw["FACULTAD"].dropna().unique()])
_pers_ops  = sorted(df_raw["PERIODO DE IMPLEMENTACI??N"].dropna().unique().tolist())
_proc_ops  = ["Todos los procesos"] + PROCESOS

def _clear_p1():
    st.session_state["p1_mod"]   = []
    st.session_state["p1_fac"]   = []
    st.session_state["p1_per"]   = []
    st.session_state["p1_nivel"] = []
    st.session_state["p1_proc"]  = "Todos los procesos"

_LBL = ('style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;'
        'letter-spacing:.4px;white-space:nowrap"')

with st.container():
    # Fila 1: MODALIDAD ?? FACULTAD ?? LIMPIAR
    lb1, in1, _sp, lb2, in2, btn_col = st.columns([0.6, 2.5, 0.05, 0.6, 2.7, 0.8])
    with lb1:
        st.markdown(f'<div {_LBL}>???? MODALIDAD</div>', unsafe_allow_html=True)
    with in1:
        if _use_pills:
            sel_mod = st.pills("mod", _mods_ops, selection_mode="multi",
                               key="p1_mod", label_visibility="collapsed")
        else:
            sel_mod = st.multiselect("mod", _mods_ops, key="p1_mod",
                                     label_visibility="collapsed", placeholder="Todas")
    with lb2:
        st.markdown(f'<div {_LBL}>??????? FACULTAD</div>', unsafe_allow_html=True)
    with in2:
        if _use_pills:
            sel_fac = st.pills("fac", fac_ops, selection_mode="multi",
                               key="p1_fac", label_visibility="collapsed")
        else:
            sel_fac = st.multiselect("fac", fac_ops, key="p1_fac",
                                     label_visibility="collapsed", placeholder="Todas")
    with btn_col:
        st.button("??? LIMPIAR", on_click=_clear_p1,
                  type="primary", key="p1_clear")

    # Fila 2: PER??ODO ?? NIVEL ?? PROCESO ?? contador
    lb3, in3, lb_nivel, in_nivel, _sp2, lb4, in4, cnt_col = st.columns([0.6, 2.3, 0.65, 2.0, 0.05, 0.85, 2.3, 1.1])
    with lb3:
        st.markdown(f'<div {_LBL}>???? PER??ODO</div>', unsafe_allow_html=True)
    with in3:
        if _use_pills:
            sel_per = st.pills("per", _pers_ops, selection_mode="multi",
                               key="p1_per", label_visibility="collapsed")
        else:
            sel_per = st.multiselect("per", _pers_ops, key="p1_per",
                                     label_visibility="collapsed", placeholder="Todos")
    with lb_nivel:
        st.markdown(f'<div {_LBL}>???? NIVEL</div>', unsafe_allow_html=True)
    with in_nivel:
        if _use_pills:
            sel_nivel = st.pills("nivel", niveles, selection_mode="multi", key="p1_nivel", label_visibility="collapsed")
        else:
            sel_nivel = st.multiselect("nivel", niveles, key="p1_nivel", label_visibility="collapsed", placeholder="Todos")
    with lb4:
        st.markdown(f'<div {_LBL}>?????? PROCESO</div>', unsafe_allow_html=True)
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

# ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
# SECCI??N 1 ??? Consolidado por etapa: barra mini + conteos
# ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
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

    # T??tulo de proceso
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
        na   = int(df[f"cl_{i}"].eq("na").sum())
        inf_ = int(df[f"cl_{i}"].eq("info").sum())
        na_t = na + inf_

        applicable = max(n - na_t, 1)
        pct = round((done * 100 + inp * 50) / applicable)
        total_s = max(done + inp + nst + na_t, 1)

        w_done = done / total_s * 100
        w_inp  = inp  / total_s * 100
        w_nst  = nst  / total_s * 100
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
            f'<div style="width:{w_nst:.1f}%;background:#EC0677"></div>'
            f'<div style="width:{w_na:.1f}%;background:#ccd5dc"></div>'
            f'</div></div>'
            f'<div style="width:48px;text-align:center;font-size:13px;font-weight:600;color:#A6CE38">{done}</div>'
            f'<div style="width:48px;text-align:center;font-size:13px;font-weight:600;color:#1FB2DE">{inp}</div>'
            f'<div style="width:48px;text-align:center;font-size:13px;font-weight:600;color:#EC0677">{nst}</div>'
            f'<div style="width:48px;text-align:center;font-size:13px;color:#9aabb5">{na_t}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.divider()

# ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
# SECCI??N 2 ??? Gr??fico de barras apiladas por proceso (conteo total)
# ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
st.markdown("### Vista Gr??fica por Proceso")

proc_names_f = []
p_done_f, p_inp_f, p_nst_f, p_na_f, p_pct_f = [], [], [], [], []

for proc in PROCESOS:
    if sel_proc != "Todos los procesos" and proc != sel_proc:
        continue
    idxs = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]
    d  = sum(int(df[f"cl_{i}"].eq("done").sum())   for i in idxs)
    i_ = sum(int(df[f"cl_{i}"].eq("inprog").sum()) for i in idxs)
    ns = sum(int(df[f"cl_{i}"].eq("nostart").sum())for i in idxs)
    na = sum(int(df[f"cl_{i}"].eq("na").sum()) + int(df[f"cl_{i}"].eq("info").sum()) for i in idxs)
    vals = df[f"proc_{proc}"].dropna()
    pct  = int(vals.mean()) if len(vals) > 0 else 0

    proc_names_f.append(proc)
    p_done_f.append(d); p_inp_f.append(i_); p_nst_f.append(ns)
    p_na_f.append(na);  p_pct_f.append(pct)

col_g1, col_g2 = st.columns([2, 2])

with col_g1:
    st.markdown("##### Distribuci??n de estados por proceso (etapas ?? programas)")
    fig_sp = go.Figure()
    all_data = [
        (p_done_f, "Finalizado",  "#A6CE38"),
        (p_inp_f,  "En proceso",  "#1FB2DE"),
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

# ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
# SECCI??N 3 ??? Tabla detalle programa ?? etapa
# ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
st.markdown("### Tabla Detalle por Programa")

FAC_PALETTE = {
    "FSCC": "#EC0677",
    "FIDI": "#1FB2DE",
    "FNGS": "#A6CE38",
}

etapas_show = [(i, em) for i, em in enumerate(ETAPAS_MAP)
               if sel_proc == "Todos los procesos" or em[0] == sel_proc]

base_cols = {
    "NOMBRE DEL PROGRAMA":       "Programa",
    "FACULTAD":                  "Facultad",
    "MODALIDAD":                 "Modal.",
    "PERIODO DE IMPLEMENTACI??N": "Periodo",
    "avance_general":            "Avance %",
}
df_base = df[list(base_cols.keys())].copy().reset_index(drop=True)
df_det  = df_base.rename(columns=base_cols)
df_det["Facultad"] = df["FACULTAD"].map(fac_abrev).fillna("???").reset_index(drop=True)
df_det["Avance %"] = df_det["Avance %"].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "???")

# Guardar cl_ para cada etapa (alineado con df_det tras reset_index)
df_cl = df.reset_index(drop=True)

def _fmt_pct(val):
    """Convierte valor decimal (0-1) o entero a texto porcentaje."""
    try:
        v = float(val)
        pct = v * 100 if v <= 1.0 else v
        return f"{int(pct)}%" if pct == int(pct) else f"{pct:.1f}%"
    except (ValueError, TypeError):
        return str(val)

def _fmt_date(val):
    """Convierte n??mero serial Excel a fecha dd/mm/aaaa."""
    try:
        n = int(float(str(val).strip()))
        if n <= 0:
            return "???"
        dt = datetime.date(1899, 12, 30) + datetime.timedelta(days=n)
        return dt.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return str(val) if str(val).strip() not in ("", "None", "nan", "???") else "???"

etapa_labels = []
for i, em in etapas_show:
    _, _, _, tipo = em
    col_label = f"{em[1][:28]}???" if len(em[1]) > 28 else em[1]
    etapa_labels.append((i, col_label, tipo))
    raw = df_cl[f"val_{i}"]
    if tipo == "pct":
        df_det[col_label] = raw.apply(
            lambda v: _fmt_pct(v) if v not in ("???", "No aplica", "no aplica") else v)
    elif tipo == "date":
        df_det[col_label] = raw.apply(_fmt_date)
    else:
        cl_col = df_cl[f"cl_{i}"]
        df_det[col_label] = [
            STATUS_LABEL.get(cl, (str(v)[:1].upper() + str(v)[1:]) if v and str(v) not in ("???","nan","None","") else "???")
            for cl, v in zip(cl_col, raw)
        ]

# ?????? Colores sem??foro (aplicados columna por columna para evitar KeyError) ????????????
_CL_STYLE = {
    "done":    "background-color:#edf7e1;color:#2d6a00;font-weight:600",
    "inprog":  "background-color:#e3f4fb;color:#0a5e80;font-weight:600",
    "nostart": "background-color:#fce8f2;color:#9a003e;font-weight:600",
    "na":      "color:#9aabb5;font-style:italic",
    "info":    "color:#9aabb5;font-style:italic",
}

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

styled = df_det.style
if "Avance %" in df_det.columns:
    styled = styled.apply(_av_col, subset=["Avance %"])
if "Facultad" in df_det.columns:
    styled = styled.apply(_fac_col, subset=["Facultad"])

for i, col_label, _ in etapa_labels:
    if col_label not in df_det.columns:
        continue
    cl_vals = df_cl[f"cl_{i}"].tolist()
    def _etapa_col(s, _cl=cl_vals):
        return [_CL_STYLE.get(c, "") for c in _cl]
    styled = styled.apply(_etapa_col, subset=[col_label])

st.dataframe(
    styled,
    use_container_width=True,
    height=460,
    hide_index=True,
    column_config={
        "Programa": st.column_config.TextColumn("Programa", width="large"),
        "Facultad": st.column_config.TextColumn("Facultad", width="medium"),
        "Avance %": st.column_config.TextColumn("Avance %", width="small"),
        "Modal.":   st.column_config.TextColumn("Modal.",   width="small"),
        "Periodo":  st.column_config.TextColumn("Periodo",  width="small"),
    },
)
st.caption(f"{n} programas ?? {len(etapas_show)} etapas mostradas")

