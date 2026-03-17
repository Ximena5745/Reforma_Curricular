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

fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}
fac_inv = {v: k for k, v in fac_labels.items()}

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
    'Detalle por Etapa</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    'Estado consolidado de etapas con conteo de programas por estado</div>'
    '</div>',
    unsafe_allow_html=True,
)

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
    "Sociedad, Cultura y Creatividad":    "#EC0677",
    "Ingeniería, Diseño e Innovación":    "#1FB2DE",
    "Negocios, Gestión y Sostenibilidad": "#A6CE38",
}

etapas_show = [(i, em) for i, em in enumerate(ETAPAS_MAP)
               if sel_proc == "Todos los procesos" or em[0] == sel_proc]

base_cols = {
    "NOMBRE DEL PROGRAMA":       "Programa",
    "FACULTAD":                  "Facultad",
    "MODALIDAD":                 "Modal.",
    "PERIODO DE IMPLEMENTACIÓN": "Periodo",
    "avance_general":            "Avance %",
}
df_base = df[list(base_cols.keys())].copy().reset_index(drop=True)
df_det  = df_base.rename(columns=base_cols)
df_det["Facultad"] = df_det["Facultad"].map(fac_labels).fillna(df_det["Facultad"])
df_det["Avance %"] = df_det["Avance %"].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "—")

# Guardar cl_ para cada etapa (alineado con df_det tras reset_index)
df_cl = df.reset_index(drop=True)

def _fmt_pct(val):
    """Convierte valor decimal o entero a texto porcentaje."""
    try:
        v = float(val)
        pct = v * 100 if v <= 1.0 else v
        return f"{pct:.1f}%".rstrip("0").rstrip(".") + "%" if "." in f"{pct:.1f}" else f"{pct:.0f}%"
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
for i, em in etapas_show:
    _, _, _, tipo = em
    col_label = f"{em[1][:28]}…" if len(em[1]) > 28 else em[1]
    etapa_labels.append((i, col_label, tipo))
    raw = df_cl[f"val_{i}"]
    if tipo == "pct":
        df_det[col_label] = raw.apply(
            lambda v: _fmt_pct(v) if v not in ("—", "No aplica", "no aplica") else v)
    elif tipo == "date":
        df_det[col_label] = raw.apply(_fmt_date)
    else:
        df_det[col_label] = raw.values

# Columna Programa como índice → queda fija al desplazarse horizontalmente
df_det = df_det.set_index("Programa")

# ── Colores semáforo ────────────────────────────────────────────────────────
_ST_STYLE = {
    "done":    ("background-color:#edf7e1;color:#2d6a00;font-weight:600",
                "background-color:#A6CE38;color:#FFFFFF;font-weight:700"),
    "inprog":  ("background-color:#e3f4fb;color:#0a5e80;font-weight:600",
                "background-color:#1FB2DE;color:#FFFFFF;font-weight:700"),
    "nostart": ("background-color:#fce8f2;color:#9a003e;font-weight:600",
                "background-color:#EC0677;color:#FFFFFF;font-weight:700"),
    "na":      ("color:#9aabb5;font-style:italic", ""),
    "info":    ("color:#9aabb5;font-style:italic", ""),
}

def _style_det(df_s):
    res = pd.DataFrame("", index=df_s.index, columns=df_s.columns)

    # Avance %
    if "Avance %" in df_s.columns:
        def _av(val):
            try:
                p = int(str(val).replace("%", ""))
                if p >= 70:   return "background-color:#edf7e1;color:#2d6a00;font-weight:700"
                elif p >= 40: return "background-color:#EBF5FB;color:#0a5e80;font-weight:700"
                else:         return "background-color:#fce8f2;color:#9a003e;font-weight:700"
            except:
                return ""
        res["Avance %"] = df_s["Avance %"].apply(_av)

    # Facultad
    if "Facultad" in df_s.columns:
        def _fac(val):
            c = FAC_PALETTE.get(str(val), "#1FB2DE")
            h = c.lstrip("#")
            r2, g2, b2 = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return (f"background-color:rgba({r2},{g2},{b2},0.12);"
                    f"color:{c};font-weight:700;border-left:3px solid {c}")
        res["Facultad"] = df_s["Facultad"].apply(_fac)

    # Etapas — usar cl_ para definir color
    for i, col_label, _ in etapa_labels:
        if col_label not in df_s.columns:
            continue
        cl_series = df_cl[f"cl_{i}"]
        res[col_label] = [_ST_STYLE.get(cl, ("", ""))[0] for cl in cl_series]

    return res

styled = df_det.style.apply(_style_det, axis=None)

st.dataframe(
    styled,
    use_container_width=True,
    height=460,
    hide_index=False,   # índice=Programa queda fijo al desplazarse
    column_config={
        "Facultad": st.column_config.TextColumn("Facultad", width="medium"),
        "Avance %": st.column_config.TextColumn("Avance %", width="small"),
        "Modal.":   st.column_config.TextColumn("Modal.",   width="small"),
        "Periodo":  st.column_config.TextColumn("Periodo",  width="small"),
    },
)
st.caption(f"{n} programas · {len(etapas_show)} etapas mostradas")

