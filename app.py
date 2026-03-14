"""
app.py  —  Control Maestro de Reforma Curricular
Página principal: Resumen General
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils.data_loader import (
    load_data, apply_filters, ETAPAS_MAP, PROCESOS,
    PROCESO_COLOR, STATUS_LABEL, STATUS_COLOR, color_for_pct,
)

# ── Config de página ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Control Maestro · Reforma Curricular",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Fondo y tipografía */
[data-testid="stAppViewContainer"] { background: #0d1117; }
[data-testid="stSidebar"] { background: #161b27; border-right: 1px solid rgba(255,255,255,0.06); }
h1,h2,h3 { font-family: 'Segoe UI', sans-serif; }

/* KPI metric */
[data-testid="stMetric"] {
    background: #161b27;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 16px 18px;
}
[data-testid="stMetric"] > div:first-child { color: #8b949e !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700 !important; }

/* Sidebar selects */
[data-testid="stSelectbox"] label { font-size: 12px; color: #8b949e; }

/* Ocultar footer */
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ─────────────────────────────────────────────────────────────
df_raw = load_data()

# ── Sidebar - Filtros ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Reforma Curricular")
    st.markdown("**Vicerrectoría Académica**")
    st.divider()
    st.markdown("### Filtros")

    modalidades = ["Todas las modalidades"] + sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
    facultades_raw = df_raw["FACULTAD"].dropna().unique().tolist()
    fac_labels = {
        "Facultad de Sociedad, Cultura y Creatividad": "Sociedad, Cultura y Creatividad",
        "Facultad de Ingeniería, Diseño e Innovación": "Ingeniería, Diseño e Innovación",
        "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
    }
    periodos_raw = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())

    sel_mod = st.selectbox("Modalidad", modalidades)
    sel_fac = st.selectbox("Facultad", ["Todas las facultades"] + [fac_labels.get(f, f) for f in sorted(facultades_raw)])
    sel_per = st.selectbox("Periodo de implementación", ["Todos los periodos"] + periodos_raw)

    st.divider()
    st.caption("📂 Datos: data/raw/CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx · Hoja: Maestro")
    st.caption(f"📊 {len(df_raw)} programas en total")

# Resolver filtros
fac_inv = {v: k for k, v in fac_labels.items()}
modalidad_f = "" if sel_mod == "Todas las modalidades" else sel_mod
facultad_f  = "" if sel_fac == "Todas las facultades" else fac_inv.get(sel_fac, sel_fac)
periodo_f   = "" if sel_per == "Todos los periodos" else sel_per

df = apply_filters(df_raw.copy(), modalidad_f, facultad_f, periodo_f)
n = len(df)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## Control Maestro · Reforma Curricular")
st.caption(f"Mostrando **{n}** de {len(df_raw)} programas")
st.divider()

# ── KPIs ───────────────────────────────────────────────────────────────────────
# Contar estados sobre todas las etapas del conjunto filtrado
all_cl = []
for i in range(len(ETAPAS_MAP)):
    all_cl.extend(df[f"cl_{i}"].tolist())

cnt_done   = all_cl.count("done")
cnt_inp    = all_cl.count("inprog")
cnt_nst    = all_cl.count("nostart")
avg_avance = int(df["avance_general"].mean()) if n > 0 else 0
cnt_crit   = int((df["avance_general"] < 30).sum())

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Programas en reforma", n)
k2.metric("Avance promedio", f"{avg_avance}%")
k3.metric("Etapas finalizadas", cnt_done)
k4.metric("Etapas en proceso", cnt_inp)
k5.metric("Sin iniciar", cnt_nst)
k6.metric("Críticos (<30%)", cnt_crit)

st.divider()

# ── Avance consolidado por proceso ────────────────────────────────────────────
st.markdown("### Avance Consolidado por Proceso")
st.caption("Promedio del conjunto filtrado — 8 procesos según hoja Estructura")

cols_proc = st.columns(4)
for idx, proc in enumerate(PROCESOS):
    col = cols_proc[idx % 4]
    col_name = f"proc_{proc}"
    vals = df[col_name].dropna()
    pct_avg = int(vals.mean()) if len(vals) > 0 else 0
    color = PROCESO_COLOR[proc]

    # contar estados de etapas del proceso
    proc_idxs = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]
    done = sum(df[f"cl_{i}"].eq("done").sum() for i in proc_idxs)
    inp  = sum(df[f"cl_{i}"].eq("inprog").sum() for i in proc_idxs)
    nst  = sum(df[f"cl_{i}"].eq("nostart").sum() for i in proc_idxs)
    na   = sum(df[f"cl_{i}"].eq("na").sum() for i in proc_idxs)

    with col:
        st.markdown(f"""
        <div style="background:#161b27;border:1px solid rgba(255,255,255,.06);border-top:3px solid {color};
                    border-radius:12px;padding:14px 16px;margin-bottom:10px">
          <div style="font-size:10px;color:#8b949e;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">{proc}</div>
          <div style="font-family:'Segoe UI',sans-serif;font-size:26px;font-weight:700;color:{color};line-height:1;margin-bottom:8px">{pct_avg}%</div>
          <div style="height:4px;background:rgba(255,255,255,.06);border-radius:2px;margin-bottom:8px;overflow:hidden">
            <div style="height:100%;width:{pct_avg}%;background:{color};border-radius:2px"></div>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <span style="font-size:10px;color:#6ee7b7"><b>{done}</b> Final.</span>
            <span style="font-size:10px;color:#93c5fd"><b>{inp}</b> Proc.</span>
            <span style="font-size:10px;color:#fca5a5"><b>{nst}</b> Sin inic.</span>
            <span style="font-size:10px;color:#6e7681"><b>{na}</b> N/A</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Gráficas ───────────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2)

# --- Izquierda: distribución de estados por etapa (barra apilada) ----
with col_l:
    st.markdown("#### Estado por Etapa")
    etapa_names = [em[1] for em in ETAPAS_MAP]
    cats = ["done", "inprog", "nostart", "na"]
    cat_labels = ["Finalizado", "En proceso", "Sin iniciar", "No aplica"]
    cat_colors = ["#3ecf8e", "#4f8ef7", "#ef4444", "#374151"]

    fig_bar = go.Figure()
    for cat, lbl, clr in zip(cats, cat_labels, cat_colors):
        counts = [int(df[f"cl_{i}"].eq(cat).sum()) for i in range(len(ETAPAS_MAP))]
        fig_bar.add_trace(go.Bar(
            name=lbl,
            y=etapa_names,
            x=counts,
            orientation="h",
            marker_color=clr,
            text=[str(c) if c > 0 else "" for c in counts],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=9, color="white"),
        ))

    fig_bar.update_layout(
        barmode="stack",
        height=480,
        margin=dict(l=0, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                    font=dict(size=10, color="#8b949e"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)", color="#6e7681", tickfont=dict(size=10)),
        yaxis=dict(color="#8b949e", tickfont=dict(size=10), autorange="reversed"),
        font=dict(family="Segoe UI"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Derecha: avance por facultad ----------------------------------------
with col_r:
    st.markdown("#### Avance por Facultad y Programa")
    for fac_key in sorted(df["FACULTAD"].dropna().unique()):
        dff = df[df["FACULTAD"] == fac_key].copy()
        if dff.empty:
            continue
        fac_label = fac_labels.get(fac_key, fac_key)
        fac_avg = int(dff["avance_general"].mean())
        fac_color = color_for_pct(fac_avg)

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;padding-bottom:4px;
                    border-bottom:1px solid rgba(255,255,255,.06)">
          <span style="font-size:12px;font-weight:600;color:#e6edf3;flex:1">{fac_label}</span>
          <span style="font-size:12px;font-weight:700;color:{fac_color}">{fac_avg}%</span>
          <span style="font-size:10px;color:#6e7681">{len(dff)} prog.</span>
        </div>
        """, unsafe_allow_html=True)

        for _, row in dff.sort_values("avance_general", ascending=False).iterrows():
            av = int(row["avance_general"])
            c = color_for_pct(av)
            prog = str(row["NOMBRE DEL PROGRAMA"])[:40]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px">
              <div style="font-size:10px;color:#8b949e;width:180px;flex-shrink:0;overflow:hidden;
                          text-overflow:ellipsis;white-space:nowrap" title="{row['NOMBRE DEL PROGRAMA']}">{prog}</div>
              <div style="flex:1;height:5px;background:rgba(255,255,255,.05);border-radius:3px;overflow:hidden">
                <div style="width:{av}%;height:100%;background:{c};border-radius:3px"></div>
              </div>
              <div style="font-size:10px;font-weight:600;color:{c};width:28px;text-align:right">{av}%</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)

st.divider()

# ── Tabla resumen ──────────────────────────────────────────────────────────────
st.markdown("### Programas — Avance por Proceso")

display_cols = {
    "NOMBRE DEL PROGRAMA": "Programa",
    "FACULTAD": "Facultad",
    "MODALIDAD": "Modalidad",
    "NIVEL": "Nivel",
    "PERIODO DE IMPLEMENTACIÓN": "Periodo",
    "avance_general": "Avance %",
}
for proc in PROCESOS:
    display_cols[f"proc_{proc}"] = proc

df_show = df[list(display_cols.keys())].copy().rename(columns=display_cols)
df_show["Facultad"] = df_show["Facultad"].map(fac_labels).fillna(df_show["Facultad"])

# Formatear porcentajes
df_show["Avance %"] = df_show["Avance %"].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "—")
for proc in PROCESOS:
    df_show[proc] = df_show[proc].apply(lambda x: f"{int(x)}%" if pd.notna(x) and x == x else "N/A")

st.dataframe(
    df_show,
    use_container_width=True,
    height=400,
    hide_index=True,
    column_config={
        "Programa": st.column_config.TextColumn(width="large"),
        "Facultad": st.column_config.TextColumn(width="medium"),
        "Avance %": st.column_config.TextColumn(width="small"),
    }
)
