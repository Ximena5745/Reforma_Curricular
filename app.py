"""
app.py  —  Control Maestro de Reforma Curricular
Página principal: Resumen General
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import math
from utils.data_loader import (
    load_data, apply_filters, ETAPAS_MAP, PROCESOS,
    PROCESO_COLOR, STATUS_LABEL, STATUS_COLOR, color_for_pct,
)

st.set_page_config(
    page_title="Control Maestro · Reforma Curricular",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS tema azul oscuro ────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #071428; }
[data-testid="stSidebar"]          { background: #091a30; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stHeader"]           { background: #071428 !important; }
h1,h2,h3,h4 { font-family: 'Segoe UI', sans-serif; color: #e6edf3; }
div[data-baseweb="select"] > div   { background: #0b1e38 !important; border-color: rgba(255,255,255,0.14) !important; color: #e6edf3 !important; }
[data-testid="stSelectbox"] label  { font-size: 12px; color: #8b9fc0; }
button[data-baseweb="tab"]         { color: #8b9fc0 !important; background: transparent !important; font-size: 13px !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #e6edf3 !important; border-bottom-color: #4f8ef7 !important; }
[data-testid="stDataFrame"]        { border-radius: 10px; overflow: hidden; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
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
    "<h2 style='margin-bottom:2px;color:#e6edf3'>🎓 Control Maestro · Reforma Curricular</h2>",
    unsafe_allow_html=True,
)
st.caption("Vicerrectoría Académica · Seguimiento de avance por proceso y etapa")

# ── Filtros inline ─────────────────────────────────────────────────────────────
st.markdown("<div style='margin:10px 0 4px'></div>", unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
with f1:
    modalidades = ["Todas las modalidades"] + sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
    sel_mod = st.selectbox("Modalidad", modalidades)
with f2:
    fac_ops = [fac_labels.get(f, f) for f in sorted(df_raw["FACULTAD"].dropna().unique())]
    sel_fac = st.selectbox("Facultad", ["Todas las facultades"] + fac_ops)
with f3:
    periodos = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())
    sel_per  = st.selectbox("Periodo de implementación", ["Todos los periodos"] + periodos)
with f4:
    st.caption(f"📊 Total: **{len(df_raw)}** programas")
    st.caption("📂 Excel · Hoja: Maestro")

modalidad_f = "" if sel_mod == "Todas las modalidades" else sel_mod
facultad_f  = "" if sel_fac == "Todas las facultades" else fac_inv.get(sel_fac, sel_fac)
periodo_f   = "" if sel_per == "Todos los periodos"   else sel_per
df = apply_filters(df_raw.copy(), modalidad_f, facultad_f, periodo_f)
n  = len(df)

st.divider()

# ── KPIs ───────────────────────────────────────────────────────────────────────
all_cl      = []
for i in range(len(ETAPAS_MAP)):
    all_cl.extend(df[f"cl_{i}"].tolist())
total_e  = len(all_cl)
cnt_done = all_cl.count("done")
cnt_inp  = all_cl.count("inprog")
cnt_nst  = all_cl.count("nostart")
cnt_na   = all_cl.count("na") + all_cl.count("info")
avg_av   = int(df["avance_general"].mean()) if n > 0 else 0
cnt_crit = int((df["avance_general"] < 30).sum())
cnt_adv  = int((df["avance_general"] >= 70).sum())

def _arc(pct, color, r=22, sz=56):
    circ = 2 * math.pi * r
    dash = circ * min(pct, 100) / 100
    gap  = circ - dash
    c    = sz // 2
    return (
        f'<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">'
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="5"/>'
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{color}" stroke-width="5"'
        f' stroke-dasharray="{dash:.2f} {gap:.2f}" stroke-linecap="round"'
        f' transform="rotate(-90 {c} {c})"/>'
        f'</svg>'
    )

def _kpi(label, val, sub, color, pct=None, icon="◈"):
    arc = _arc(pct, color) if pct is not None else (
        f'<div style="width:56px;height:56px;display:flex;align-items:center;'
        f'justify-content:center;font-size:28px">{icon}</div>'
    )
    return (
        f'<div style="background:#0b1e38;border:1px solid rgba(255,255,255,0.09);'
        f'border-left:3px solid {color};border-radius:14px;'
        f'padding:14px 16px;display:flex;align-items:center;gap:12px;min-height:84px">'
        f'<div style="flex-shrink:0">{arc}</div>'
        f'<div style="flex:1;min-width:0">'
        f'<div style="font-size:10px;color:#8b9fc0;text-transform:uppercase;'
        f'letter-spacing:.5px;margin-bottom:3px">{label}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{color};line-height:1.1">{val}</div>'
        f'<div style="font-size:10px;color:#5a6a7e;margin-top:2px">{sub}</div>'
        f'</div></div>'
    )

st.caption(f"Mostrando **{n}** de {len(df_raw)} programas")
c1, c2, c3, c4 = st.columns(4)
c1.markdown(_kpi("Programas en reforma",  n,        f"de {len(df_raw)} en total",         "#4f8ef7", None, "📚"), unsafe_allow_html=True)
c2.markdown(_kpi("Avance promedio",        f"{avg_av}%", "sobre todos los procesos",      "#3ecf8e", avg_av),       unsafe_allow_html=True)
c3.markdown(_kpi("Avanzados ≥ 70%",       cnt_adv,  f"de {n} programas",                 "#9b7aed", round(cnt_adv/n*100) if n else 0), unsafe_allow_html=True)
c4.markdown(_kpi("Críticos < 30%",        cnt_crit, "requieren atención urgente",         "#ef4444", round(cnt_crit/n*100) if n else 0), unsafe_allow_html=True)

st.markdown("<div style='margin:6px 0'></div>", unsafe_allow_html=True)
c5, c6, c7, c8 = st.columns(4)
c5.markdown(_kpi("Etapas finalizadas", cnt_done, f"de {total_e} etapas totales",    "#3ecf8e", round(cnt_done/total_e*100) if total_e else 0), unsafe_allow_html=True)
c6.markdown(_kpi("En proceso",         cnt_inp,  "etapas activas",                  "#4f8ef7", round(cnt_inp/total_e*100) if total_e else 0),  unsafe_allow_html=True)
c7.markdown(_kpi("Sin iniciar",        cnt_nst,  "etapas pendientes",               "#f97316", round(cnt_nst/total_e*100) if total_e else 0),  unsafe_allow_html=True)
c8.markdown(_kpi("No aplica / Info",   cnt_na,   "etapas no contabilizadas",        "#6e7681", None, "ℹ"),           unsafe_allow_html=True)

st.divider()

# ── Avance consolidado por proceso (8 donuts en 1 figura) ──────────────────────
st.markdown("### Avance Consolidado por Proceso")

pct_avgs, done_l, inp_l, nst_l, na_l = [], [], [], [], []
for proc in PROCESOS:
    vals = df[f"proc_{proc}"].dropna()
    pct_avgs.append(int(vals.mean()) if len(vals) > 0 else 0)
    idxs = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]
    done_l.append(sum(int(df[f"cl_{i}"].eq("done").sum())   for i in idxs))
    inp_l .append(sum(int(df[f"cl_{i}"].eq("inprog").sum()) for i in idxs))
    nst_l .append(sum(int(df[f"cl_{i}"].eq("nostart").sum())for i in idxs))
    na_l  .append(sum(int(df[f"cl_{i}"].eq("na").sum()) + int(df[f"cl_{i}"].eq("info").sum()) for i in idxs))

proc_short = [
    "Gest. Académica", "Gest. Financiera", "Aseg. Calidad", "Ger. Planeación",
    "Prod. Contenidos", "Convenios", "Banner", "Pág. Web",
]

fig_proc = make_subplots(
    rows=2, cols=4,
    specs=[[{"type": "domain"}] * 4] * 2,
    subplot_titles=proc_short,
    horizontal_spacing=0.04,
    vertical_spacing=0.14,
)

for idx, proc in enumerate(PROCESOS):
    r, c = idx // 4 + 1, idx % 4 + 1
    color = PROCESO_COLOR[proc]
    d, i_, ns, na = done_l[idx], inp_l[idx], nst_l[idx], na_l[idx]
    fig_proc.add_trace(
        go.Pie(
            values=[max(d, 0.001), max(i_, 0.001), max(ns, 0.001), max(na, 0.001)],
            hole=0.68,
            marker_colors=["#3ecf8e", "#4f8ef7", "#ef4444", "#374151"],
            showlegend=False,
            textinfo="none",
            hovertemplate=f"<b>{proc}</b><br>%{{label}}: %{{value}}<extra></extra>",
            sort=False,
            name=proc,
        ),
        row=r, col=c,
    )

# Estilar los títulos de cada subplot (aparecen antes de las anotaciones de %)
fig_proc.update_annotations(font=dict(size=10, color="#8b9fc0"))

# Agregar anotaciones de % DESPUÉS de update_annotations para no sobreescribirlas
for idx in range(len(PROCESOS)):
    tr = fig_proc.data[idx]
    xc = (tr.domain.x[0] + tr.domain.x[1]) / 2
    yc = (tr.domain.y[0] + tr.domain.y[1]) / 2
    color = PROCESO_COLOR[PROCESOS[idx]]
    fig_proc.add_annotation(
        x=xc, y=yc, xref="paper", yref="paper",
        text=f"<b>{pct_avgs[idx]}%</b>",
        font=dict(size=15, color=color, family="Segoe UI"),
        showarrow=False,
    )

fig_proc.update_layout(
    height=320,
    margin=dict(l=10, r=10, t=30, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Segoe UI", color="#8b9fc0"),
    showlegend=False,
)
st.plotly_chart(fig_proc, use_container_width=True, config={"displayModeBar": False})

# Leyenda de colores + stats por proceso
st.markdown(
    '<div style="display:flex;gap:16px;justify-content:center;margin:-4px 0 8px">'
    '<span style="font-size:10px;color:#3ecf8e">■ Finalizado</span>'
    '<span style="font-size:10px;color:#4f8ef7">■ En proceso</span>'
    '<span style="font-size:10px;color:#ef4444">■ Sin iniciar</span>'
    '<span style="font-size:10px;color:#374151">■ N/A</span>'
    '</div>',
    unsafe_allow_html=True,
)

# Detalle numérico por proceso en 4 + 4 columnas
sc1 = st.columns(4)
sc2 = st.columns(4)
for idx, proc in enumerate(PROCESOS):
    col = (sc1 + sc2)[idx]
    color = PROCESO_COLOR[proc]
    d, i_, ns, na = done_l[idx], inp_l[idx], nst_l[idx], na_l[idx]
    with col:
        st.markdown(
            f'<div style="background:#0b1e38;border:1px solid rgba(255,255,255,.08);'
            f'border-top:2px solid {color};border-radius:0 0 10px 10px;'
            f'padding:6px 10px;text-align:center">'
            f'<div style="display:flex;gap:5px;justify-content:center;flex-wrap:wrap">'
            f'<span style="font-size:9px;color:#3ecf8e;background:rgba(62,207,142,.1);padding:1px 5px;border-radius:3px">✓ {d}</span>'
            f'<span style="font-size:9px;color:#93c5fd;background:rgba(79,142,247,.1);padding:1px 5px;border-radius:3px">◎ {i_}</span>'
            f'<span style="font-size:9px;color:#fca5a5;background:rgba(239,68,68,.1);padding:1px 5px;border-radius:3px">✗ {ns}</span>'
            + (f'<span style="font-size:9px;color:#6e7681;background:rgba(110,118,129,.1);padding:1px 5px;border-radius:3px">N/A {na}</span>' if na else "")
            + '</div></div>',
            unsafe_allow_html=True,
        )

st.divider()

# ── Visualizaciones ────────────────────────────────────────────────────────────
st.markdown("### Análisis y Visualizaciones")
tab1, tab2, tab3 = st.tabs(["📊 Estado por Etapa", "🏛️ Por Facultad y Programa", "📈 Distribución"])

# ── Tab 1: Estado por etapa ────────────────────────────────────────────────────
with tab1:
    etapa_names = [em[1] for em in ETAPAS_MAP]
    cats       = ["done", "inprog", "nostart", "na"]
    cat_labels = ["Finalizado", "En proceso", "Sin iniciar", "No aplica"]
    cat_colors = ["#3ecf8e", "#4f8ef7", "#ef4444", "#374151"]

    fig_bar = go.Figure()
    for cat, lbl, clr in zip(cats, cat_labels, cat_colors):
        counts = [int(df[f"cl_{i}"].eq(cat).sum()) for i in range(len(ETAPAS_MAP))]
        fig_bar.add_trace(go.Bar(
            name=lbl, y=etapa_names, x=counts, orientation="h",
            marker_color=clr,
            text=[str(c) if c > 0 else "" for c in counts],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(size=9, color="white"),
        ))

    fig_bar.update_layout(
        barmode="stack", height=500,
        margin=dict(l=0, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=10, color="#8b9fc0"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)", color="#6e7681", tickfont=dict(size=10)),
        yaxis=dict(color="#8b9fc0", tickfont=dict(size=10), autorange="reversed"),
        font=dict(family="Segoe UI"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Tab 2: Por facultad ────────────────────────────────────────────────────────
with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("##### Treemap — Avance por Facultad y Programa")
        rows_t = []
        for _, row in df.iterrows():
            rows_t.append({
                "Facultad": fac_labels.get(row["FACULTAD"], row["FACULTAD"]),
                "Programa": row["NOMBRE DEL PROGRAMA"][:38],
                "Avance":   max(float(row["avance_general"]), 1),
            })
        if rows_t:
            df_t = pd.DataFrame(rows_t)
            fig_tree = px.treemap(
                df_t, path=["Facultad", "Programa"], values="Avance",
                color="Avance",
                color_continuous_scale=[[0, "#ef4444"], [0.3, "#f97316"], [0.7, "#4f8ef7"], [1, "#3ecf8e"]],
                range_color=[0, 100],
            )
            fig_tree.update_traces(textfont=dict(size=11, family="Segoe UI"))
            fig_tree.update_layout(
                height=430,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Segoe UI", color="#e6edf3"),
                coloraxis_colorbar=dict(
                    tickfont=dict(color="#8b9fc0"),
                    title=dict(text="%", font=dict(color="#8b9fc0")),
                ),
            )
            st.plotly_chart(fig_tree, use_container_width=True)

    with col_r:
        st.markdown("##### Ranking de programas por avance")
        df_s = df[["NOMBRE DEL PROGRAMA", "avance_general", "FACULTAD"]].copy()
        df_s["label"] = df_s["NOMBRE DEL PROGRAMA"].apply(lambda x: x[:34] + ("…" if len(x) > 34 else ""))
        df_s = df_s.sort_values("avance_general")
        colors_bar = [color_for_pct(v) for v in df_s["avance_general"]]

        fig_prg = go.Figure(go.Bar(
            x=df_s["avance_general"].tolist(),
            y=df_s["label"].tolist(),
            orientation="h",
            marker_color=colors_bar,
            text=[f"{int(v)}%" for v in df_s["avance_general"]],
            textposition="outside",
            textfont=dict(size=9, color="#8b9fc0"),
        ))
        fig_prg.update_layout(
            height=max(350, n * 22 + 60),
            margin=dict(l=0, r=50, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0, 118], showgrid=True, gridcolor="rgba(255,255,255,.05)",
                       color="#6e7681", tickfont=dict(size=9)),
            yaxis=dict(color="#8b9fc0", tickfont=dict(size=9)),
            font=dict(family="Segoe UI"),
            showlegend=False,
        )
        st.plotly_chart(fig_prg, use_container_width=True)

# ── Tab 3: Distribución ────────────────────────────────────────────────────────
with tab3:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### Velocímetro — Avance General Promedio")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_av,
            domain={"x": [0, 1], "y": [0, 1]},
            number={"suffix": "%", "font": {"size": 42, "color": "#e6edf3", "family": "Segoe UI"}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickfont": {"color": "#8b9fc0", "size": 10},
                    "tickcolor": "rgba(255,255,255,0.2)",
                },
                "bar": {"color": color_for_pct(avg_av), "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  30], "color": "rgba(239,68,68,0.12)"},
                    {"range": [30, 70], "color": "rgba(249,115,22,0.08)"},
                    {"range": [70,100], "color": "rgba(62,207,142,0.12)"},
                ],
                "threshold": {
                    "line": {"color": "#ffffff", "width": 2},
                    "thickness": 0.75, "value": avg_av,
                },
            },
        ))
        fig_gauge.update_layout(
            height=300,
            margin=dict(l=30, r=30, t=30, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Segoe UI"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_b:
        st.markdown("##### Distribución de programas por % de avance")
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=df["avance_general"].tolist(),
            nbinsx=10,
            marker_color="#4f8ef7",
            marker_line_color="rgba(0,0,30,0.4)",
            marker_line_width=1.5,
            opacity=0.85,
        ))
        fig_hist.add_vline(x=30, line_dash="dash", line_color="#ef4444", line_width=1.5,
                           annotation_text=" 30%", annotation_font_color="#ef4444", annotation_font_size=10)
        fig_hist.add_vline(x=70, line_dash="dash", line_color="#3ecf8e", line_width=1.5,
                           annotation_text=" 70%", annotation_font_color="#3ecf8e", annotation_font_size=10)
        fig_hist.update_layout(
            height=300,
            margin=dict(l=0, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Avance %", color="#8b9fc0",
                       gridcolor="rgba(255,255,255,.05)", tickfont=dict(size=10)),
            yaxis=dict(title="Nº Programas", color="#8b9fc0",
                       gridcolor="rgba(255,255,255,.05)", tickfont=dict(size=10)),
            font=dict(family="Segoe UI"),
            showlegend=False,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ── Tabla resumen ──────────────────────────────────────────────────────────────
st.markdown("### Programas — Avance Detallado por Proceso")

display_cols = {
    "NOMBRE DEL PROGRAMA":     "Programa",
    "FACULTAD":                "Facultad",
    "MODALIDAD":               "Modalidad",
    "NIVEL":                   "Nivel",
    "PERIODO DE IMPLEMENTACIÓN": "Periodo",
    "avance_general":          "Avance %",
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

st.dataframe(
    df_show,
    use_container_width=True,
    height=380,
    hide_index=True,
    column_config={
        "Programa":  st.column_config.TextColumn(width="large"),
        "Facultad":  st.column_config.TextColumn(width="medium"),
        "Avance %":  st.column_config.TextColumn(width="small"),
    },
)
