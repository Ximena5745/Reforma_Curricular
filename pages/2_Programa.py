"""
pages/2_Programa.py
Vista general de programas con conteo de etapas + ficha detallada por programa.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
fac_inv = {v: k for k, v in FAC_LABELS.items()}

PROC_SHORT = {
    "Gestión Académica":                       "Gest. Académica",
    "Gestión Financiera":                      "Gest. Financiera",
    "Aseguramiento de la Calidad":             "Aseg. Calidad",
    "Ger. Planeación y Gestión Institucional": "Ger. Planeación",
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
    st.page_link("app.py",                          label="Resumen General",     icon="📊")
    st.page_link("pages/1_Detalle_por_Etapa.py",    label="Detalle por Etapa",   icon="📋")
    st.page_link("pages/2_Programa.py",             label="Ficha de Programa",   icon="🔍")
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
    'Ficha de Programa</div>'
    f'<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    f'Vista general con conteo de etapas completadas · {len(df_raw)} programas totales</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Filtros inline ─────────────────────────────────────────────────────────────
f1, f2, f3 = st.columns(3)
with f1:
    fac_ops = [FAC_LABELS.get(f, f) for f in sorted(df_raw["FACULTAD"].dropna().unique())]
    sel_fac = st.selectbox("Facultad", ["Todas las facultades"] + fac_ops)
with f2:
    mods = ["Todas las modalidades"] + sorted(df_raw["MODALIDAD"].dropna().unique().tolist())
    sel_mod = st.selectbox("Modalidad", mods)
with f3:
    pers = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist())
    sel_per = st.selectbox("Periodo", ["Todos los periodos"] + pers)

facultad_f  = "" if sel_fac == "Todas las facultades"  else fac_inv.get(sel_fac, sel_fac)
modalidad_f = "" if sel_mod == "Todas las modalidades" else sel_mod
periodo_f   = "" if sel_per == "Todos los periodos"    else sel_per
df = apply_filters(df_raw.copy(), modalidad_f, facultad_f, periodo_f)

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
        "Facultad":        FAC_LABELS.get(row["FACULTAD"], row["FACULTAD"]),
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
        "Facultad":       st.column_config.TextColumn("Facultad",      width="medium"),
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
            val        = row[f"val_{i}"]
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

# ── Tabla valores brutos ───────────────────────────────────────────────────────
st.divider()
with st.expander("Ver tabla completa de valores Excel para este programa"):
    rows_data = []
    for i, (proc, etapa, col_excel, tipo) in enumerate(ETAPAS_MAP):
        rows_data.append({
            "Proceso":  proc,
            "Etapa":    etapa,
            "Columna":  col_excel,
            "Valor":    row[f"val_{i}"],
            "Estado":   STATUS_LABEL.get(row[f"cl_{i}"], "—"),
        })
    st.dataframe(pd.DataFrame(rows_data), use_container_width=True, hide_index=True, height=400)
