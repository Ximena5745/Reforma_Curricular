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
[data-testid="stAppViewContainer"] { background: #0d1117; }
[data-testid="stSidebar"] { background: #161b27; border-right: 1px solid rgba(255,255,255,0.06); }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

df_raw = load_data()

fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad": "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación": "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}

# Construir lista de programas únicos
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
av = int(row["avance_general"])
av_color = color_for_pct(av)

st.markdown(f"## {row['NOMBRE DEL PROGRAMA']}")
st.caption(f"{row['ESCUELA']} · {fac_short}")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Modalidad",  row["MODALIDAD"])
c2.metric("Nivel",      row["NIVEL"])
c3.metric("Sede",       row["SEDE"])
c4.metric("Periodo",    row["PERIODO DE IMPLEMENTACIÓN"])
c5.metric("Avance",     f"{av}%")

st.divider()

# ── Radar del avance por proceso ───────────────────────────────────────────────
st.markdown("### Avance por Proceso")

proc_pcts = []
for proc in PROCESOS:
    val = row.get(f"proc_{proc}")
    proc_pcts.append(int(val) if pd.notna(val) and val == val else 0)

fig_radar = go.Figure(go.Scatterpolar(
    r=proc_pcts + [proc_pcts[0]],
    theta=PROCESOS + [PROCESOS[0]],
    fill="toself",
    fillcolor="rgba(79,142,247,0.15)",
    line=dict(color="#4f8ef7", width=2),
    marker=dict(size=6, color="#4f8ef7"),
))
fig_radar.update_layout(
    polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9, color="#6e7681"),
                        gridcolor="rgba(255,255,255,.08)", linecolor="rgba(255,255,255,.08)"),
        angularaxis=dict(tickfont=dict(size=10, color="#8b949e"), gridcolor="rgba(255,255,255,.08)"),
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=30, r=30, t=30, b=30),
    height=360,
    font=dict(family="Segoe UI"),
    showlegend=False,
)
_, radar_col, _ = st.columns([1, 2, 1])
with radar_col:
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# ── Detalle por proceso y etapa ────────────────────────────────────────────────
st.markdown("### Detalle de Etapas — Valores del Excel")

CL_ICON = {"done": "✅", "inprog": "🔵", "nostart": "🔴", "info": "ℹ️", "na": "⬜"}

for proc in PROCESOS:
    color = PROCESO_COLOR[proc]
    proc_idxs = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]
    proc_pct = row.get(f"proc_{proc}")
    proc_pct_disp = f"{int(proc_pct)}%" if pd.notna(proc_pct) and proc_pct == proc_pct else "N/A"

    with st.expander(f"{proc}  —  {proc_pct_disp}", expanded=True):
        ecols = st.columns(min(len(proc_idxs), 4))
        for col_i, i in enumerate(proc_idxs):
            _, etapa_name, _, tipo = ETAPAS_MAP[i]
            cl = row[f"cl_{i}"]
            val = row[f"val_{i}"]
            status_lbl = STATUS_LABEL.get(cl, "—")
            status_clr = STATUS_COLOR.get(cl, "#6e7681")
            icon = CL_ICON.get(cl, "")

            with ecols[col_i % len(ecols)]:
                st.markdown(f"""
                <div style="background:#1c2333;border:1px solid rgba(255,255,255,.06);
                            border-left:3px solid {color};border-radius:8px;
                            padding:10px 12px;margin-bottom:6px">
                  <div style="font-size:10px;color:#6e7681;margin-bottom:5px;line-height:1.3">{etapa_name}</div>
                  <div style="font-size:12px;font-weight:500;color:#e6edf3;word-break:break-word;
                               margin-bottom:6px">{val}</div>
                  <div style="font-size:10px;font-weight:600;color:{status_clr}">{icon} {status_lbl}</div>
                </div>
                """, unsafe_allow_html=True)

# ── Tabla de todos los valores brutos ─────────────────────────────────────────
st.divider()
with st.expander("Ver todos los valores del Excel para este programa"):
    rows_data = []
    for i, (proc, etapa, col_csv, tipo) in enumerate(ETAPAS_MAP):
        rows_data.append({
            "Proceso": proc,
            "Etapa": etapa,
            "Columna CSV": col_csv,
            "Valor": row[f"val_{i}"],
            "Estado": STATUS_LABEL.get(row[f"cl_{i}"], "—"),
        })
    st.dataframe(pd.DataFrame(rows_data), use_container_width=True, hide_index=True, height=400)
