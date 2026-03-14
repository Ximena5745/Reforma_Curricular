"""
pages/2_Programa.py
Vista de un programa individual: todas sus etapas con valores reales.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import (
    load_data, ETAPAS_MAP, PROCESOS, PROCESO_COLOR,
    STATUS_LABEL, STATUS_COLOR, color_for_pct,
)

st.set_page_config(
    page_title="Ficha de Programa · Reforma Curricular",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #071428; }
[data-testid="stSidebar"]          { background: #091a30; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stHeader"]           { background: #071428 !important; }
h1,h2,h3,h4 { font-family: 'Segoe UI', sans-serif; color: #e6edf3; }
div[data-baseweb="select"] > div   { background: #0f2040 !important; border-color: rgba(255,255,255,0.12) !important; color: #e6edf3 !important; }
[data-testid="stSelectbox"] label  { font-size: 12px; color: #8b9fc0; }
[data-testid="stMetric"]           { background: #0b1e38; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 16px; }
[data-testid="stMetric"] > div:first-child { color: #8b9fc0 !important; font-size: 11px !important; text-transform: uppercase; }
[data-testid="stMetricValue"]      { font-size: 22px !important; font-weight: 700 !important; color: #e6edf3 !important; }
[data-testid="stDataFrame"]        { border-radius: 10px; overflow: hidden; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

df_raw = load_data()

fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}

prog_options = (
    df_raw[["NOMBRE DEL PROGRAMA", "MODALIDAD", "SEDE", "FACULTAD"]]
    .apply(lambda r: f"{r['NOMBRE DEL PROGRAMA']} — {r['MODALIDAD']} — {r['SEDE']}", axis=1)
    .tolist()
)

with st.sidebar:
    st.markdown("## 🎓 Reforma Curricular")
    st.markdown("**Vicerrectoría Académica**")
    st.divider()
    st.markdown("### Seleccionar Programa")
    sel_prog = st.selectbox("Programa", prog_options)
    st.divider()
    st.caption("📂 Datos: data/raw/CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx · Hoja: Maestro")

# Encontrar la fila
idx = prog_options.index(sel_prog)
row = df_raw.iloc[idx]

# ── Header del programa ────────────────────────────────────────────────────────
fac_short = fac_labels.get(row["FACULTAD"], row["FACULTAD"])
av        = int(row["avance_general"])
av_color  = color_for_pct(av)

st.markdown(
    f'<div style="background:#0b1e38;border:1px solid rgba(255,255,255,.08);'
    f'border-left:4px solid {av_color};border-radius:12px;padding:16px 20px;margin-bottom:16px">'
    f'<div style="font-size:20px;font-weight:700;color:#e6edf3;margin-bottom:4px">{row["NOMBRE DEL PROGRAMA"]}</div>'
    f'<div style="font-size:12px;color:#8b9fc0">{row.get("ESCUELA","")}</div>'
    f'<div style="font-size:11px;color:#6e7681;margin-top:2px">{fac_short}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Modalidad", row["MODALIDAD"])
c2.metric("Nivel",     row["NIVEL"])
c3.metric("Sede",      row["SEDE"])
c4.metric("Periodo",   row["PERIODO DE IMPLEMENTACIÓN"])
c5.metric("Avance",    f"{av}%")

st.divider()

# ── Radar del avance por proceso + barra horizontal ───────────────────────────
st.markdown("### Avance por Proceso")
col_r, col_b = st.columns([1, 1])

proc_pcts = []
for proc in PROCESOS:
    val = row.get(f"proc_{proc}")
    proc_pcts.append(int(val) if pd.notna(val) and val == val else 0)

with col_r:
    fig_radar = go.Figure(go.Scatterpolar(
        r=proc_pcts + [proc_pcts[0]],
        theta=PROCESOS + [PROCESOS[0]],
        fill="toself",
        fillcolor="rgba(79,142,247,0.12)",
        line=dict(color="#4f8ef7", width=2),
        marker=dict(size=5, color="#4f8ef7"),
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=8, color="#6e7681"),
                gridcolor="rgba(255,255,255,.08)",
                linecolor="rgba(255,255,255,.08)",
            ),
            angularaxis=dict(
                tickfont=dict(size=9, color="#8b9fc0"),
                gridcolor="rgba(255,255,255,.08)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=30, b=30),
        height=320,
        font=dict(family="Segoe UI"),
        showlegend=False,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_b:
    proc_short = [
        "Gest. Académica", "Gest. Financiera", "Aseg. Calidad", "Ger. Planeación",
        "Prod. Contenidos", "Convenios", "Banner", "Pág. Web",
    ]
    colors_p = [PROCESO_COLOR[p] for p in PROCESOS]
    fig_bar_p = go.Figure(go.Bar(
        x=proc_pcts,
        y=proc_short,
        orientation="h",
        marker_color=colors_p,
        text=[f"{v}%" for v in proc_pcts],
        textposition="outside",
        textfont=dict(size=10, color="#8b9fc0"),
    ))
    fig_bar_p.update_layout(
        height=320,
        margin=dict(l=0, r=40, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 118], showgrid=True, gridcolor="rgba(255,255,255,.05)",
                   color="#6e7681", tickfont=dict(size=9)),
        yaxis=dict(color="#8b9fc0", tickfont=dict(size=10), autorange="reversed"),
        font=dict(family="Segoe UI"),
        showlegend=False,
    )
    st.plotly_chart(fig_bar_p, use_container_width=True)

st.divider()

# ── Detalle por proceso y etapa ────────────────────────────────────────────────
st.markdown("### Detalle de Etapas — Valores del Excel")

CL_ICON = {"done": "✅", "inprog": "🔵", "nostart": "🔴", "info": "ℹ️", "na": "⬜"}

for proc in PROCESOS:
    color      = PROCESO_COLOR[proc]
    proc_idxs  = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]
    proc_pct   = row.get(f"proc_{proc}")
    pct_disp   = f"{int(proc_pct)}%" if pd.notna(proc_pct) and proc_pct == proc_pct else "N/A"

    with st.expander(f"{proc}  —  {pct_disp}", expanded=True):
        ecols = st.columns(min(len(proc_idxs), 4))
        for col_i, i in enumerate(proc_idxs):
            _, etapa_name, _, tipo = ETAPAS_MAP[i]
            cl         = row[f"cl_{i}"]
            val        = row[f"val_{i}"]
            status_lbl = STATUS_LABEL.get(cl, "—")
            status_clr = STATUS_COLOR.get(cl, "#6e7681")
            icon       = CL_ICON.get(cl, "")

            with ecols[col_i % len(ecols)]:
                st.markdown(
                    f'<div style="background:#0d2040;border:1px solid rgba(255,255,255,.07);'
                    f'border-left:3px solid {color};border-radius:8px;'
                    f'padding:10px 12px;margin-bottom:6px">'
                    f'<div style="font-size:10px;color:#6e7681;margin-bottom:5px;line-height:1.3">{etapa_name}</div>'
                    f'<div style="font-size:12px;font-weight:500;color:#e6edf3;word-break:break-word;margin-bottom:6px">{val}</div>'
                    f'<div style="font-size:10px;font-weight:600;color:{status_clr}">{icon} {status_lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

# ── Tabla todos los valores ────────────────────────────────────────────────────
st.divider()
with st.expander("Ver todos los valores del Excel para este programa"):
    rows_data = []
    for i, (proc, etapa, col_csv, tipo) in enumerate(ETAPAS_MAP):
        rows_data.append({
            "Proceso":  proc,
            "Etapa":    etapa,
            "Columna":  col_csv,
            "Valor":    row[f"val_{i}"],
            "Estado":   STATUS_LABEL.get(row[f"cl_{i}"], "—"),
        })
    st.dataframe(pd.DataFrame(rows_data), use_container_width=True, hide_index=True, height=400)
