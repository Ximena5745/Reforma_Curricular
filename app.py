"""
app.py  —  Control Maestro de Reforma Curricular
Página principal: Resumen General
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

# ── CSS modo claro · colores institucionales ───────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #F0F4F8; }
[data-testid="stSidebar"]          { background: #FFFFFF; border-right: 1px solid rgba(15,56,90,0.10); }
[data-testid="stHeader"]           { background: #F0F4F8 !important; }
h1,h2,h3,h4,h5                     { font-family: 'Segoe UI', sans-serif; color: #0F385A !important; }
p, li, label, caption               { color: #2a4a5e; }
[data-testid="stCaption"]           { color: #6a8a9e !important; }
/* Selectbox control */
div[data-baseweb="select"] > div   { background: #FFFFFF !important; border-color: rgba(15,56,90,0.20) !important; color: #0F385A !important; }
div[data-baseweb="select"] span    { color: #0F385A !important; }
[data-testid="stSelectbox"] label  { font-size: 12px; color: #4a6a7e; }
/* Dropdown list options */
ul[data-baseweb="menu"]            { background: #FFFFFF !important; border: 1px solid rgba(15,56,90,0.15) !important; box-shadow: 0 4px 16px rgba(15,56,90,0.12) !important; }
ul[data-baseweb="menu"] li         { color: #0F385A !important; background: #FFFFFF !important; }
ul[data-baseweb="menu"] li:hover   { background: #F0F4F8 !important; }
li[aria-selected="true"]           { background: #e8f0f7 !important; }
/* Tabs */
button[data-baseweb="tab"]         { color: #6a8a9e !important; background: transparent !important; font-size: 13px !important; font-weight: 500 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #0F385A !important; border-bottom-color: #1FB2DE !important; font-weight: 700 !important; }
[data-testid="stDataFrame"]        { border-radius: 10px; overflow: hidden; box-shadow: 0 1px 6px rgba(15,56,90,0.08); }
hr                                  { border-color: rgba(15,56,90,0.10) !important; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
[data-testid="stExpander"]         { background: #FFFFFF; border: 1px solid rgba(15,56,90,0.10); border-radius: 10px; }
/* Sidebar nav links */
[data-testid="stSidebarNav"] a     { color: #0F385A !important; }
[data-testid="stSidebarNav"] a:hover { color: #1FB2DE !important; }
/* Info box */
[data-testid="stNotification"]     { background: #e8f6fc !important; color: #0F385A !important; border-color: #1FB2DE !important; }
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
    "<h2 style='margin-bottom:2px;color:#0F385A'>🎓 Control Maestro · Reforma Curricular</h2>",
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
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="rgba(15,56,90,0.10)" stroke-width="5"/>'
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
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);'
        f'border-left:4px solid {color};border-radius:12px;'
        f'padding:14px 16px;display:flex;align-items:center;gap:12px;min-height:84px;'
        f'box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="flex-shrink:0">{arc}</div>'
        f'<div style="flex:1;min-width:0">'
        f'<div style="font-size:10px;color:#6a8a9e;text-transform:uppercase;'
        f'letter-spacing:.5px;margin-bottom:3px">{label}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{color};line-height:1.1">{val}</div>'
        f'<div style="font-size:10px;color:#8aabb0;margin-top:2px">{sub}</div>'
        f'</div></div>'
    )

st.caption(f"Mostrando **{n}** de {len(df_raw)} programas")
c1, c2, c3, c4 = st.columns(4)
c1.markdown(_kpi("Programas en reforma",  n,        f"de {len(df_raw)} en total",         "#0F385A", None, "📚"), unsafe_allow_html=True)
c2.markdown(_kpi("Avance promedio",        f"{avg_av}%", "sobre todos los procesos",      "#A6CE38", avg_av),       unsafe_allow_html=True)
c3.markdown(_kpi("Avanzados ≥ 70%",       cnt_adv,  f"de {n} programas",                 "#1FB2DE", round(cnt_adv/n*100) if n else 0), unsafe_allow_html=True)
c4.markdown(_kpi("Críticos < 30%",        cnt_crit, "requieren atención urgente",         "#EC0677", round(cnt_crit/n*100) if n else 0), unsafe_allow_html=True)

st.markdown("<div style='margin:6px 0'></div>", unsafe_allow_html=True)

# ── Fila 2: métricas por periodo y proceso ─────────────────────────────────────
cnt_2026 = int(df["PERIODO DE IMPLEMENTACIÓN"].str.contains("2026", na=False).sum())
cnt_2027_1 = int(df["PERIODO DE IMPLEMENTACIÓN"].str.contains("2027-1", na=False).sum())
cnt_2027_2 = int(df["PERIODO DE IMPLEMENTACIÓN"].str.contains("2027-2", na=False).sum())

# Proceso más rezagado y más adelantado (excluyendo NaN)
proc_avgs = {p: (df[f"proc_{p}"].dropna().mean() if df[f"proc_{p}"].dropna().shape[0] > 0 else 0)
             for p in PROCESOS}
proc_min = min(proc_avgs, key=proc_avgs.get)
proc_max = max(proc_avgs, key=proc_avgs.get)
proc_min_pct = int(proc_avgs[proc_min])
proc_max_pct = int(proc_avgs[proc_max])

proc_short_map = {
    "Gestión Académica": "Gest. Académica",
    "Gestión Financiera": "Gest. Financiera",
    "Aseguramiento de la Calidad": "Aseg. Calidad",
    "Ger. Planeación y Gestión Institucional": "Ger. Planeación",
    "Producción de Contenidos": "Prod. Contenidos",
    "Convenios Institucionales": "Convenios",
    "Parametrizar Reforma en Banner": "Banner",
    "Publicación en Página Web": "Pág. Web",
}

c5, c6, c7, c8 = st.columns(4)
c5.markdown(_kpi("Periodo 2026-2",       cnt_2026,   "programas más urgentes",            "#F47B20", round(cnt_2026/n*100)   if n else 0), unsafe_allow_html=True)
c6.markdown(_kpi("Periodo 2027-1",       cnt_2027_1, "programas próximo semestre",        "#FBAF17", round(cnt_2027_1/n*100) if n else 0), unsafe_allow_html=True)
c7.markdown(_kpi("Proceso más crítico",  f"{proc_min_pct}%", proc_short_map.get(proc_min, proc_min), "#EC0677", proc_min_pct), unsafe_allow_html=True)
c8.markdown(_kpi("Proceso más avanzado", f"{proc_max_pct}%", proc_short_map.get(proc_max, proc_max), "#A6CE38", proc_max_pct), unsafe_allow_html=True)

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

# ── Helper: tarjeta SVG donut + stats integrados ──────────────────────────────
def _donut_card(proc, pct, done, inp, nst, na_val, color, size=128, r=44, sw=13):
    circ  = 2 * math.pi * r
    cx    = size // 2
    total = max(done + inp + nst + na_val, 1)
    segs  = [(done, "#A6CE38"), (inp, "#1FB2DE"), (nst, "#EC0677"), (na_val, "#c8d8e0")]
    arcs  = f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="#edf1f5" stroke-width="{sw}"/>'
    off   = 0.0
    for cnt, sc in segs:
        if cnt == 0:
            continue
        dash = circ * cnt / total
        arcs += (
            f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" stroke="{sc}" '
            f'stroke-width="{sw}" stroke-dasharray="{dash:.3f} {circ:.3f}" '
            f'stroke-dashoffset="-{off:.3f}" transform="rotate(-90 {cx} {cx})"/>'
        )
        off += dash
    arcs += (
        f'<text x="{cx}" y="{cx}" text-anchor="middle" dominant-baseline="central" '
        f'font-size="17" font-weight="bold" font-family="Segoe UI,sans-serif" fill="{color}">{pct}%</text>'
    )
    svg   = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">{arcs}</svg>'
    label = proc_short_map.get(proc, proc)
    return (
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,.10);'
        f'border-top:3px solid {color};border-radius:10px;'
        f'padding:10px 8px 8px;box-shadow:0 2px 8px rgba(15,56,90,.06);text-align:center">'
        f'<div style="font-size:10px;font-weight:700;color:{color};text-transform:uppercase;'
        f'letter-spacing:.4px;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;'
        f'white-space:nowrap" title="{proc}">{label}</div>'
        f'<div style="display:flex;justify-content:center;margin:0">{svg}</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:3px;margin-top:5px">'
        f'<div style="font-size:9px;color:#5a7a2e;background:#f0f8e8;padding:2px 4px;border-radius:3px;text-align:center"><b>{done}</b> Fin.</div>'
        f'<div style="font-size:9px;color:#0a6a8e;background:#e8f6fc;padding:2px 4px;border-radius:3px;text-align:center"><b>{inp}</b> Proc.</div>'
        f'<div style="font-size:9px;color:#9a0050;background:#fce8f2;padding:2px 4px;border-radius:3px;text-align:center"><b>{nst}</b> Sin ini.</div>'
        f'<div style="font-size:9px;color:#6a8a9e;background:#f0f4f8;padding:2px 4px;border-radius:3px;text-align:center"><b>{na_val}</b> N/A</div>'
        f'</div></div>'
    )

# ── Renderizar 8 tarjetas en 2 filas de 4 ─────────────────────────────────────
row1_cols = st.columns(4)
row2_cols = st.columns(4)
for idx, proc in enumerate(PROCESOS):
    col = (row1_cols + row2_cols)[idx]
    with col:
        st.markdown(
            _donut_card(proc, pct_avgs[idx], done_l[idx], inp_l[idx], nst_l[idx], na_l[idx], PROCESO_COLOR[proc]),
            unsafe_allow_html=True,
        )


st.divider()

# ── Visualizaciones ────────────────────────────────────────────────────────────
st.markdown("### Análisis y Visualizaciones")
tab1, tab2, tab3 = st.tabs(["📊 Estado por Etapa", "🏛️ Por Facultad y Programa", "📈 Distribución"])

# ── Tab 1: Estado por etapa ────────────────────────────────────────────────────
with tab1:
    cats       = ["done", "inprog", "nostart", "na"]
    cat_labels = ["Finalizado", "En proceso", "Sin iniciar", "No aplica"]
    cat_colors = ["#A6CE38", "#1FB2DE", "#EC0677", "#c8d8e0"]

    # Construir lista de etapas agrupadas por proceso, con spacers entre grupos
    # Solo incluir etapas con al menos un programa con datos
    def _etapa_has_data(j):
        # Solo mostrar etapas con al menos un programa en done/inprog/nostart
        return sum(int(df[f"cl_{j}"].eq(c).sum()) for c in ["done", "inprog", "nostart"]) > 0

    etapa_names, etapa_idxs, etapa_proc = [], [], []
    for proc in PROCESOS:
        items = [(i, em[1]) for i, em in enumerate(ETAPAS_MAP)
                 if em[0] == proc and _etapa_has_data(i)]
        if not items:
            continue
        if etapa_names:  # spacer entre grupos (solo si ya hay filas previas)
            sp_key = f"__sp_{proc}__"
            etapa_names.append(sp_key)
            etapa_idxs.append(None)
            etapa_proc.append(None)
        for i, name in items:
            etapa_names.append(name)
            etapa_idxs.append(i)
            etapa_proc.append(proc)

    N = len(etapa_names)
    totals = [
        max(sum(int(df[f"cl_{j}"].eq(c).sum()) for c in cats) if j is not None else 1, 1)
        for j in etapa_idxs
    ]

    col_chart, col_legend = st.columns([3, 2])
    with col_chart:
        fig_bar = go.Figure()
        for cat, lbl, clr in zip(cats, cat_labels, cat_colors):
            cnts = [int(df[f"cl_{j}"].eq(cat).sum()) if j is not None else 0 for j in etapa_idxs]
            pcts = [round(cnts[k] / totals[k] * 100, 1) for k in range(N)]
            htxt = [
                f"<b>{etapa_names[k]}</b><br>{lbl}: {cnts[k]} ({pcts[k]}%)"
                if etapa_idxs[k] is not None else ""
                for k in range(N)
            ]
            txt = [str(cnts[k]) if pcts[k] >= 9 and etapa_idxs[k] is not None else "" for k in range(N)]
            fig_bar.add_trace(go.Bar(
                name=lbl, y=etapa_names, x=pcts, orientation="h",
                marker_color=clr, marker_line_width=0,
                text=txt, textposition="inside", insidetextanchor="middle",
                constraintext="none", textangle=0,
                textfont=dict(size=10, color="white", family="Segoe UI"),
                hovertext=htxt, hoverinfo="text",
                showlegend=False,
            ))

        # Fondo de color suave + etiqueta en la parte superior del grupo (sin superposición)
        for proc in PROCESOS:
            color     = PROCESO_COLOR[proc]
            grp_idxs  = [k for k, p in enumerate(etapa_proc) if p == proc]
            if not grp_idxs:
                continue
            fig_bar.add_shape(
                type="rect", layer="below",
                x0=0, x1=100,
                y0=etapa_names[grp_idxs[0]], y1=etapa_names[grp_idxs[-1]],
                yref="y", xref="x",
                fillcolor=color, opacity=0.06,
                line_color=color, line_width=0.8,
            )
            # Etiqueta sobre la primera barra del grupo (en la franja del spacer)
            # yanchor="bottom" → el label crece hacia arriba desde el borde de la 1ª barra
            fig_bar.add_annotation(
                x=2, y=grp_idxs[0],
                xref="x", yref="y",
                text=f"<b>{proc_short_map.get(proc, proc)}</b>",
                showarrow=False,
                font=dict(size=8, color=color, family="Segoe UI"),
                xanchor="left", yanchor="bottom",
                bgcolor="rgba(255,255,255,0.0)",
            )

        tick_text = ["" if nm.startswith("__sp") else nm for nm in etapa_names]
        fig_bar.update_layout(
            barmode="stack", height=520,
            margin=dict(l=190, r=10, t=6, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            uniformtext=dict(minsize=8, mode="hide"),
            xaxis=dict(range=[0, 100], ticksuffix="%", showgrid=True,
                       gridcolor="rgba(15,56,90,.07)", color="#6a8a9e", tickfont=dict(size=10)),
            yaxis=dict(
                color="#4a6a7e", tickfont=dict(size=9.5), autorange="reversed",
                tickvals=etapa_names, ticktext=tick_text,
                side="left", automargin=False, ticklabelposition="outside left",
                ticklen=0,
            ),
            font=dict(family="Segoe UI"),
            bargap=0.28,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    with col_legend:
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
        for lbl, clr in zip(cat_labels, cat_colors):
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">'
                f'<div style="width:12px;height:12px;border-radius:3px;background:{clr};flex-shrink:0"></div>'
                f'<span style="font-size:11px;color:#4a6a7e">{lbl}</span></div>',
                unsafe_allow_html=True,
            )

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
                color_continuous_scale=[[0, "#EC0677"], [0.3, "#FBAF17"], [0.7, "#1FB2DE"], [1, "#A6CE38"]],
                range_color=[0, 100],
            )
            fig_tree.update_traces(textfont=dict(size=11, family="Segoe UI"))
            fig_tree.update_layout(
                height=430,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Segoe UI", color="#0F385A"),
                coloraxis_colorbar=dict(
                    tickfont=dict(color="#4a6a7e"),
                    title=dict(text="%", font=dict(color="#4a6a7e")),
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
            textfont=dict(size=9, color="#4a6a7e"),
        ))
        fig_prg.update_layout(
            height=max(350, n * 22 + 60),
            margin=dict(l=0, r=50, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0, 118], showgrid=True, gridcolor="rgba(15,56,90,.07)",
                       color="#6a8a9e", tickfont=dict(size=9)),
            yaxis=dict(color="#4a6a7e", tickfont=dict(size=9)),
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
            number={"suffix": "%", "font": {"size": 42, "color": "#0F385A", "family": "Segoe UI"}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickfont": {"color": "#4a6a7e", "size": 10},
                    "tickcolor": "rgba(15,56,90,0.2)",
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
            marker_color="#1FB2DE",
            marker_line_color="rgba(15,56,90,0.2)",
            marker_line_width=1.5,
            opacity=0.85,
        ))
        fig_hist.add_vline(x=30, line_dash="dash", line_color="#EC0677", line_width=1.5,
                           annotation_text=" 30%", annotation_font_color="#EC0677", annotation_font_size=10)
        fig_hist.add_vline(x=70, line_dash="dash", line_color="#A6CE38", line_width=1.5,
                           annotation_text=" 70%", annotation_font_color="#A6CE38", annotation_font_size=10)
        fig_hist.update_layout(
            height=300,
            margin=dict(l=0, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Avance %", color="#6a8a9e",
                       gridcolor="rgba(15,56,90,.07)", tickfont=dict(size=10)),
            yaxis=dict(title="Nº Programas", color="#6a8a9e",
                       gridcolor="rgba(15,56,90,.07)", tickfont=dict(size=10)),
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
