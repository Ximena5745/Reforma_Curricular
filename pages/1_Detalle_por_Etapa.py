"""
pages/1_Detalle_por_Etapa.py
Vista consolidada de todas las etapas con conteo de programas por estado.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import (
    load_data, apply_filters, ETAPAS_MAP, PROCESOS,
    PROCESO_COLOR, STATUS_LABEL, STATUS_COLOR, color_for_pct,
)

st.set_page_config(
    page_title="Detalle por Etapa · Reforma Curricular",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #F0F4F8; }
[data-testid="stSidebar"]          { background: #e8edf2; border-right: 1px solid rgba(15,56,90,0.10); }
[data-testid="stHeader"]           { background: #F0F4F8 !important; }
h1,h2,h3,h4,h5 { font-family: 'Segoe UI', sans-serif; color: #0F385A; }
p, li, span { color: #0F385A; }
div[data-baseweb="select"] > div   { background: #FFFFFF !important; border-color: rgba(15,56,90,0.20) !important; color: #0F385A !important; }
div[data-baseweb="select"] span    { color: #0F385A !important; }
[data-testid="stSelectbox"] label  { font-size: 12px; color: #4a6a7e; }
ul[data-baseweb="menu"]            { background: #FFFFFF !important; border: 1px solid rgba(15,56,90,0.15) !important; box-shadow: 0 4px 16px rgba(15,56,90,0.12) !important; }
ul[data-baseweb="menu"] li         { color: #0F385A !important; background: #FFFFFF !important; }
ul[data-baseweb="menu"] li:hover   { background: #F0F4F8 !important; }
li[aria-selected="true"]           { background: #e8f0f7 !important; }
[data-testid="stDataFrame"]        { border-radius: 10px; overflow: hidden; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; }
[data-testid="stMarkdownContainer"] p { color: #0F385A; }
</style>
""", unsafe_allow_html=True)

# ── Datos ──────────────────────────────────────────────────────────────────────
df_raw = load_data()

fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}
fac_inv = {v: k for k, v in fac_labels.items()}

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='margin-bottom:2px;color:#0F385A'>📋 Detalle por Etapa</h2>",
    unsafe_allow_html=True,
)
st.caption("Estado consolidado de etapas con conteo de programas por estado")

# ── Filtros inline ─────────────────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns(4)
with f1:
    modalidades = ["Todas las modalidades"] + sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
    sel_mod  = st.selectbox("Modalidad", modalidades)
with f2:
    fac_ops  = [fac_labels.get(f, f) for f in sorted(df_raw["FACULTAD"].dropna().unique())]
    sel_fac  = st.selectbox("Facultad", ["Todas las facultades"] + fac_ops)
with f3:
    periodos = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())
    sel_per  = st.selectbox("Periodo", ["Todos los periodos"] + periodos)
with f4:
    sel_proc = st.selectbox("Proceso", ["Todos los procesos"] + PROCESOS)

modalidad_f = "" if sel_mod  == "Todas las modalidades" else sel_mod
facultad_f  = "" if sel_fac  == "Todas las facultades"  else fac_inv.get(sel_fac, sel_fac)
periodo_f   = "" if sel_per  == "Todos los periodos"    else sel_per
df = apply_filters(df_raw.copy(), modalidad_f, facultad_f, periodo_f)
n  = len(df)

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
    '<div style="width:220px;font-size:10px;color:#4a6a7e;text-transform:uppercase;letter-spacing:.5px">Etapa</div>'
    '<div style="width:54px;font-size:10px;color:#4a6a7e;text-align:center">Avance</div>'
    '<div style="flex:1;font-size:10px;color:#4a6a7e">Distribución</div>'
    '<div style="width:48px;font-size:10px;color:#A6CE38;text-align:center">✓ Final</div>'
    '<div style="width:48px;font-size:10px;color:#1FB2DE;text-align:center">◎ Proc.</div>'
    '<div style="width:48px;font-size:10px;color:#EC0677;text-align:center">✗ Sin ini.</div>'
    '<div style="width:48px;font-size:10px;color:#9aabb5;text-align:center">N/A</div>'
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
            f'<div style="width:48px;text-align:center;font-size:11px;font-weight:600;color:#A6CE38">{done}</div>'
            f'<div style="width:48px;text-align:center;font-size:11px;font-weight:600;color:#1FB2DE">{inp}</div>'
            f'<div style="width:48px;text-align:center;font-size:11px;font-weight:600;color:#EC0677">{nst}</div>'
            f'<div style="width:48px;text-align:center;font-size:11px;color:#9aabb5">{na_t}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — Gráfico de barras apiladas por proceso (conteo total)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Vista Gráfica por Proceso")

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
    st.markdown("##### Distribución de estados por proceso (etapas × programas)")
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
            constraintext="none",
            textfont=dict(size=10, color="white", family="Segoe UI"),
            hovertext=htxt, hoverinfo="text",
        ))
    fig_sp.update_layout(
        barmode="stack", height=max(200, len(proc_names_f) * 38 + 60),
        margin=dict(l=0, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=10, color="#4a6a7e"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(range=[0, 100], ticksuffix="%", showgrid=True,
                   gridcolor="rgba(15,56,90,0.07)", color="#4a6a7e", tickfont=dict(size=10)),
        yaxis=dict(color="#0F385A", tickfont=dict(size=10), autorange="reversed"),
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

etapas_show = [(i, em) for i, em in enumerate(ETAPAS_MAP)
               if sel_proc == "Todos los procesos" or em[0] == sel_proc]

base_cols = {
    "NOMBRE DEL PROGRAMA":       "Programa",
    "FACULTAD":                  "Facultad",
    "MODALIDAD":                 "Modal.",
    "PERIODO DE IMPLEMENTACIÓN": "Periodo",
    "avance_general":            "Avance %",
}
df_det = df[list(base_cols.keys())].copy().rename(columns=base_cols)
df_det["Facultad"] = df_det["Facultad"].map(fac_labels).fillna(df_det["Facultad"])
df_det["Avance %"] = df_det["Avance %"].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "—")

for i, em in etapas_show:
    col_label = f"{em[1][:28]}…" if len(em[1]) > 28 else em[1]
    df_det[col_label] = df[f"val_{i}"].values

st.dataframe(
    df_det,
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
st.caption(f"{n} programas · {len(etapas_show)} etapas mostradas")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — Mapa de calor (colapsado)
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("🗺️ Ver Mapa de Calor — Programa × Etapa"):
    cl_to_num = {"done": 1.0, "inprog": 0.6, "nostart": 0.2, "info": 0.8, "na": 0.0}
    etapas_labels = [em[1][:25] + ("…" if len(em[1]) > 25 else "") for _, em in etapas_show]
    prog_labels   = df["NOMBRE DEL PROGRAMA"].apply(
        lambda x: x[:28] + ("…" if len(x) > 28 else "")
    ).tolist()

    z, hover = [], []
    for _, row in df.iterrows():
        rz, rh = [], []
        for i, em in etapas_show:
            cl  = row[f"cl_{i}"]
            val = row[f"val_{i}"]
            rz.append(cl_to_num.get(cl, 0))
            rh.append(
                f"<b>{row['NOMBRE DEL PROGRAMA']}</b><br>"
                f"{em[1]}<br>{STATUS_LABEL.get(cl, '—')}: {val}"
            )
        z.append(rz); hover.append(rh)

    colorscale = [
        [0.0,  "#f0f4f8"], [0.19, "#f0f4f8"],
        [0.2,  "#EC0677"], [0.59, "#EC0677"],
        [0.6,  "#1FB2DE"], [0.79, "#1FB2DE"],
        [0.8,  "#FBAF17"], [0.99, "#FBAF17"],
        [1.0,  "#A6CE38"],
    ]
    fig_heat = go.Figure(go.Heatmap(
        z=z, x=etapas_labels, y=prog_labels,
        colorscale=colorscale, showscale=False,
        hoverinfo="text", text=hover, xgap=2, ygap=1,
    ))
    fig_heat.update_layout(
        height=max(300, n * 18 + 80),
        margin=dict(l=0, r=0, t=10, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(size=9, color="#4a6a7e"), tickangle=-40, side="bottom"),
        yaxis=dict(tickfont=dict(size=9, color="#4a6a7e"), autorange="reversed"),
        font=dict(family="Segoe UI"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)
