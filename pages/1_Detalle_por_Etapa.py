"""
pages/1_Detalle_por_Etapa.py
Vista de detalle: todas las etapas (col B Estructura) por programa
con totales consolidados por etapa.
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
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0d1117; }
[data-testid="stSidebar"] { background: #161b27; border-right: 1px solid rgba(255,255,255,0.06); }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
.block-container { padding-top: 1rem; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Datos ──────────────────────────────────────────────────────────────────────
df_raw = load_data()

fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad": "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación": "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}
fac_inv = {v: k for k, v in fac_labels.items()}

# ── Sidebar filtros ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Reforma Curricular")
    st.markdown("**Vicerrectoría Académica**")
    st.divider()
    st.markdown("### Filtros")

    modalidades = ["Todas las modalidades"] + sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
    periodos_raw = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())

    sel_mod = st.selectbox("Modalidad", modalidades)
    sel_fac = st.selectbox("Facultad", ["Todas las facultades"] + [fac_labels.get(f, f) for f in sorted(df_raw["FACULTAD"].dropna().unique())])
    sel_per = st.selectbox("Periodo", ["Todos los periodos"] + periodos_raw)
    sel_proc = st.selectbox("Proceso (filtrar tabla)", ["Todos los procesos"] + PROCESOS)

    st.divider()
    st.caption("📂 Datos: data/raw/CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx · Hoja: Maestro")

modalidad_f = "" if sel_mod == "Todas las modalidades" else sel_mod
facultad_f  = "" if sel_fac == "Todas las facultades" else fac_inv.get(sel_fac, sel_fac)
periodo_f   = "" if sel_per == "Todos los periodos" else sel_per

df = apply_filters(df_raw.copy(), modalidad_f, facultad_f, periodo_f)
n = len(df)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## Detalle por Etapa")
st.caption(f"20 etapas según hoja Estructura · {n} programas")
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: Totales por etapa (tarjetas agrupadas por proceso)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Totales por Etapa")

for proc in PROCESOS:
    color = PROCESO_COLOR[proc]
    proc_idxs = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]
    etapas_del_proc = [(i, ETAPAS_MAP[i][1]) for i in proc_idxs]

    # Título del proceso
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;margin-top:8px">
      <div style="width:4px;height:20px;background:{color};border-radius:2px;flex-shrink:0"></div>
      <span style="font-family:'Segoe UI',sans-serif;font-size:13px;font-weight:700;
                   color:{color};text-transform:uppercase;letter-spacing:.5px">{proc}</span>
    </div>
    """, unsafe_allow_html=True)

    # Tarjetas de etapas en columnas
    ncols = min(len(etapas_del_proc), 4)
    cols = st.columns(ncols)

    for col_idx, (i, etapa_name) in enumerate(etapas_del_proc):
        done   = int(df[f"cl_{i}"].eq("done").sum())
        inp    = int(df[f"cl_{i}"].eq("inprog").sum())
        nst    = int(df[f"cl_{i}"].eq("nostart").sum())
        na_c   = int(df[f"cl_{i}"].eq("na").sum())
        inf_c  = int(df[f"cl_{i}"].eq("info").sum())
        applicable = n - na_c - inf_c
        pct = round((done * 100 + inp * 50) / applicable) if applicable > 0 else 0

        with cols[col_idx % ncols]:
            st.markdown(f"""
            <div style="background:#161b27;border:1px solid rgba(255,255,255,.06);
                        border-top:2px solid {color};border-radius:10px;
                        padding:12px 14px;margin-bottom:6px">
              <div style="font-size:10px;color:#6e7681;margin-bottom:4px;line-height:1.3">{etapa_name}</div>
              <div style="height:3px;background:rgba(255,255,255,.06);border-radius:2px;
                          margin-bottom:8px;overflow:hidden">
                <div style="height:100%;width:{pct}%;background:{color};border-radius:2px"></div>
              </div>
              <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
                <span style="font-size:14px;font-weight:700;color:{color}">{pct}%</span>
                <span style="font-size:9px;color:#6ee7b7;margin-left:4px">✓ {done}</span>
                <span style="font-size:9px;color:#93c5fd">◎ {inp}</span>
                <span style="font-size:9px;color:#fca5a5">— {nst}</span>
                {'<span style="font-size:9px;color:#6e7681">N/A '+str(na_c)+'</span>' if na_c > 0 else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: Tabla detalle por programa × etapa
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Tabla Detalle por Programa")

# Filtrar etapas por proceso seleccionado
if sel_proc != "Todos los procesos":
    etapas_show = [(i, em) for i, em in enumerate(ETAPAS_MAP) if em[0] == sel_proc]
else:
    etapas_show = [(i, em) for i, em in enumerate(ETAPAS_MAP)]

# Construir DataFrame de visualización
base_cols = {
    "NOMBRE DEL PROGRAMA": "Programa",
    "FACULTAD": "Facultad",
    "MODALIDAD": "Modal.",
    "PERIODO DE IMPLEMENTACIÓN": "Periodo",
    "avance_general": "Avance %",
}
df_det = df[list(base_cols.keys())].copy().rename(columns=base_cols)
df_det["Facultad"] = df_det["Facultad"].map(fac_labels).fillna(df_det["Facultad"])
df_det["Avance %"] = df_det["Avance %"].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "—")

# Añadir columna por cada etapa seleccionada con el valor del Excel
for i, em in etapas_show:
    col_label = f"{em[1][:30]}…" if len(em[1]) > 30 else em[1]
    df_det[col_label] = df[f"val_{i}"].values

# Columna config
col_cfg = {
    "Programa":  st.column_config.TextColumn("Programa", width="large"),
    "Facultad":  st.column_config.TextColumn("Facultad", width="medium"),
    "Modal.":    st.column_config.TextColumn("Modal.", width="small"),
    "Periodo":   st.column_config.TextColumn("Periodo", width="small"),
    "Avance %":  st.column_config.TextColumn("Avance %", width="small"),
}

st.dataframe(
    df_det,
    use_container_width=True,
    height=500,
    hide_index=True,
    column_config=col_cfg,
)

st.caption(f"{n} programas · {len(etapas_show)} etapas mostradas")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3: Gráfico de calor — programa × etapa
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Mapa de Calor — Estado por Programa y Etapa")
st.caption("Verde = Finalizado · Azul = En proceso · Rojo = Sin iniciar · Gris = No aplica")

cl_to_num = {"done": 1.0, "inprog": 0.6, "nostart": 0.2, "info": 0.8, "na": 0.0}

etapas_labels = [em[1][:28] + ("…" if len(em[1]) > 28 else "") for _, em in etapas_show]
prog_labels = df["NOMBRE DEL PROGRAMA"].apply(lambda x: x[:30] + ("…" if len(x) > 30 else "")).tolist()

z = []
hover = []
for _, row in df.iterrows():
    row_z = []
    row_h = []
    for i, em in etapas_show:
        cl = row[f"cl_{i}"]
        val = row[f"val_{i}"]
        row_z.append(cl_to_num.get(cl, 0))
        row_h.append(f"<b>{row['NOMBRE DEL PROGRAMA']}</b><br>{em[1]}<br>{STATUS_LABEL.get(cl,'—')}: {val}")
    z.append(row_z)
    hover.append(row_h)

colorscale = [
    [0.0,  "#1c2333"],
    [0.19, "#1c2333"],
    [0.2,  "#ef4444"],
    [0.59, "#ef4444"],
    [0.6,  "#4f8ef7"],
    [0.79, "#4f8ef7"],
    [0.8,  "#eab308"],
    [0.99, "#eab308"],
    [1.0,  "#3ecf8e"],
]

fig_heat = go.Figure(go.Heatmap(
    z=z,
    x=etapas_labels,
    y=prog_labels,
    colorscale=colorscale,
    showscale=False,
    hoverinfo="text",
    text=hover,
    xgap=2,
    ygap=1,
))
fig_heat.update_layout(
    height=max(300, n * 18 + 80),
    margin=dict(l=0, r=0, t=10, b=60),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(
        tickfont=dict(size=9, color="#8b949e"),
        tickangle=-40,
        side="bottom",
    ),
    yaxis=dict(
        tickfont=dict(size=9, color="#8b949e"),
        autorange="reversed",
    ),
    font=dict(family="Segoe UI"),
)
st.plotly_chart(fig_heat, use_container_width=True)
