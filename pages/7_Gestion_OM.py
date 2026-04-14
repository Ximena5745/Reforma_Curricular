"""
pages/7_Gestion_OM.py
Seguimiento Operativo · Gestión OM
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from utils.data_loader import load_data, enrich_df, PROCESOS, ETAPAS_MAP

st.set_page_config(
    page_title="Seguimiento Operativo · Gestión OM",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
[data-testid="stAppViewContainer"] { background: #EEF3F8; }
[data-testid="stHeader"] {
    background: linear-gradient(135deg, #0F385A 0%, #1A5276 50%, #1FB2DE 100%) !important;
    border-bottom: 3px solid #42F2F2 !important;
}
h1,h2,h3,h4,h5  { font-family: 'Segoe UI', sans-serif; color: #0F385A !important; }
p, li, label, caption { color: #2a4a5e; }
.block-container { padding-top: 3.5rem !important; padding-bottom: 2rem !important; }
div[data-baseweb="select"] > div {
    background: #E3F4FB !important; border-color: rgba(31,178,222,0.45) !important;
    color: #0F385A !important; border-radius: 8px !important;
}
div[data-baseweb="select"] span    { color: #0F385A !important; }
ul[data-baseweb="menu"]            { background: #FFFFFF !important; border-radius: 8px !important; }
ul[data-baseweb="menu"] li         { color: #0F385A !important; background: #FFFFFF !important; }
ul[data-baseweb="menu"] li:hover   { background: #E3F4FB !important; }
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
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    color: rgba(255,255,255,0.82) !important; background: rgba(255,255,255,0.08) !important;
    border-radius: 8px !important; padding: 8px 12px 8px 10px !important;
    margin-bottom: 3px !important; font-size: 13px !important; font-weight: 500 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(255,255,255,0.18) !important; color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: rgba(255,255,255,0.22) !important; color: #FFFFFF !important;
    font-weight: 700 !important; border-left: 3px solid #42F2F2 !important;
}
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
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg,#1FB2DE,#0891b2) !important;
    border-color: #1FB2DE !important; color: #FFFFFF !important;
    font-size: 11px !important; font-weight: 700 !important;
    border-radius: 8px !important; letter-spacing:.3px !important;
    box-shadow: 0 2px 8px rgba(31,178,222,0.35) !important;
}
[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg,#0891b2,#0F385A) !important;
    border-color: #0891b2 !important;
}
[data-testid="stBaseButton-primary"] > button,
[data-testid="stBaseButton-primary"] button {
    height: 32px !important; min-height: 32px !important;
    padding: 0 10px !important; line-height: 1 !important; white-space: nowrap !important;
}
[data-testid="stColumn"]:has([data-testid="stBaseButton-primary"]) {
    display: flex !important; flex-direction: column !important; justify-content: center !important;
}
.stVerticalBlock:has([data-testid="stPills"]) { gap: 0.1rem !important; row-gap: 0.1rem !important; }
[data-testid="stPills"] { padding-bottom: 0 !important; margin-bottom: 0 !important; min-height: unset !important; }
[data-testid="stHorizontalBlock"]:has([data-testid="stPills"]) { align-items: center !important; padding-bottom: 0 !important; margin-bottom: 0 !important; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ── Datos ──────────────────────────────────────────────────────────────────────
df_raw = enrich_df(load_data())

ROOT = Path(__file__).parent.parent
OM_CSV_PATH = ROOT / "data" / "raw" / "om_data.csv"

MESES_ES = {
    "enero": "Enero", "febrero": "Febrero", "marzo": "Marzo", "abril": "Abril",
    "mayo": "Mayo", "junio": "Junio", "julio": "Julio", "agosto": "Agosto",
    "septiembre": "Septiembre", "octubre": "Octubre", "noviembre": "Noviembre", "diciembre": "Diciembre",
}

MES_ORDER = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

PROCESOS_OM = PROCESOS
SUBPROCESOS_OM = [etapa for _, etapa, _, _ in ETAPAS_MAP]


def _parse_date(value):
    if pd.isna(value):
        return pd.NaT
    text = str(value).strip()
    if not text or text.lower() in ("nan", "none", "-", "—"):
        return pd.NaT
    try:
        return pd.to_datetime(text, dayfirst=True, errors="coerce")
    except Exception:
        pass
    lower = text.lower()
    for key, display in MESES_ES.items():
        if key in lower:
            parts = [p for p in lower.replace("de", "").split() if p.isdigit() and len(p) == 4]
            if parts:
                year = int(parts[0])
                month = list(MESES_ES.keys()).index(key) + 1
                return pd.Timestamp(year=year, month=month, day=1)
    return pd.to_datetime(text, errors="coerce")


def _build_om_dataset(df):
    if OM_CSV_PATH.exists():
        df_saved = pd.read_csv(OM_CSV_PATH, dtype=str).fillna("")
        if not df_saved.empty:
            df_saved["Mes"] = df_saved["Mes"].astype(str)
            df_saved["Año"] = df_saved["Año"].astype(str)
            return df_saved

    rows = []
    date_col = next((c for c in df.columns if "documentos" in c.lower() and "men" in c.lower()), None)
    for idx, row in df.iterrows():
        prog = str(row.get("NOMBRE DEL PROGRAMA", "—")).strip()
        if not prog or prog == "—":
            continue
        for proc in PROCESOS_OM:
            proc_val = row.get(f"proc_{proc}")
            try:
                proc_num = float(proc_val) if proc_val not in (None, "", "nan") else np.nan
            except Exception:
                proc_num = np.nan
            if np.isnan(proc_num) or proc_num >= 60:
                continue
            subprocs = [etapa for p, etapa, _, _ in ETAPAS_MAP if p == proc]
            if not subprocs:
                continue
            fecha = _parse_date(row.get(date_col)) if date_col else pd.NaT
            if pd.isna(fecha):
                fecha = pd.Timestamp.today()
            mes = fecha.strftime("%B")
            año = str(fecha.year)
            estado_om = "Abierta" if proc_num < 40 else "Pendiente"
            om_value = f"OM-{idx+1:03d}-{len(rows)%50+1:02d}"
            observacion = (
                f"{proc}: {subprocs[0]} en riesgo con avance {int(proc_num)}%."
            )
            rows.append({
                "Mes": mes,
                "Año": año,
                "Proceso": proc,
                "Subproceso": subprocs[0],
                "Programa": prog,
                "Estado OM": estado_om,
                "OM": om_value,
                "Observación": observacion,
                "Peligro": "Peligro",
            })
            if len(rows) >= 120:
                break
        if len(rows) >= 120:
            break

    if not rows:
        rows = [
            {
                "Mes": "Mayo", "Año": "2026", "Proceso": "Gestión Académica",
                "Subproceso": "Formato creación de programas Banner",
                "Programa": "Programa Ejemplo",
                "Estado OM": "Abierta",
                "OM": "OM-000",
                "Observación": "Ejemplo de observación. Requiere asociar nueva OM.",
                "Peligro": "Peligro",
            }
        ]
    return pd.DataFrame(rows)


def _sort_months(values):
    order = {m: i for i, m in enumerate(MES_ORDER)}
    return sorted(values, key=lambda v: order.get(v, 999))


df_om = _build_om_dataset(df_raw)
if "om_extra" not in st.session_state:
    st.session_state["om_extra"] = []

if st.session_state["om_extra"]:
    df_om = pd.concat([df_om, pd.DataFrame(st.session_state["om_extra"])], ignore_index=True)

mes_options = _sort_months(sorted(df_om["Mes"].dropna().unique()))
año_options = sorted(df_om["Año"].dropna().unique())
proceso_options = sorted(df_om["Proceso"].dropna().unique())
subproceso_options = sorted(df_om["Subproceso"].dropna().unique())

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
    st.page_link("pages/4_Gestion_Academica.py",        label="Gestión Académica",    icon="📑")
    st.page_link("pages/7_Gestion_OM.py",               label="Gestión OM",           icon="⚙️")
    st.markdown(
        '<div style="padding:12px 6px;font-size:10px;color:rgba(255,255,255,0.40);text-align:center">'
        'POLI · 2025–2026</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div style="background:linear-gradient(135deg,#0F385A 0%,#1A5276 50%,#1FB2DE 100%);'
    'padding:18px 24px 14px;border-radius:0 0 12px 12px;border-bottom:3px solid #42F2F2;">'
    '<div style="font-size:21px;font-weight:700;color:#FFFFFF;letter-spacing:-.3px">'
    '⚙️ Seguimiento Operativo · Gestión OM</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    'Filtros por Mes/Año, Proceso, Subproceso y tabla de indicadores en Peligro.</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

with st.container():
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1])
    with c1:
        sel_mes = st.multiselect("Mes", mes_options, default=mes_options, label_visibility="collapsed")
    with c2:
        sel_año = st.multiselect("Año", año_options, default=año_options, label_visibility="collapsed")
    with c3:
        sel_proceso = st.multiselect("Proceso", proceso_options, default=proceso_options, label_visibility="collapsed")
    with c4:
        sel_subproceso = st.multiselect("Subproceso", subproceso_options, default=subproceso_options, label_visibility="collapsed")
    with c5:
        st.markdown("<div style='padding-top:6px'></div>", unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Descargar CSV",
            data=df_om.to_csv(index=False).encode("utf-8"),
            file_name="gestion_om.csv",
            mime="text/csv",
        )

filtered = df_om.copy()
if sel_mes:
    filtered = filtered[filtered["Mes"].isin(sel_mes)]
if sel_año:
    filtered = filtered[filtered["Año"].isin(sel_año)]
if sel_proceso:
    filtered = filtered[filtered["Proceso"].isin(sel_proceso)]
if sel_subproceso:
    filtered = filtered[filtered["Subproceso"].isin(sel_subproceso)]

filtered = filtered[filtered["Peligro"] == "Peligro"].reset_index(drop=True)

st.markdown(
    '<div style="padding:12px 14px;margin-bottom:14px;border-radius:12px;'
    'background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);box-shadow:0 2px 10px rgba(15,56,90,0.05);">'
    f'<div style="font-size:13px;font-weight:700;color:#0F385A;">Indicadores en Peligro</div>'
    f'<div style="font-size:12px;color:#4a6a7e;margin-top:6px">Mostrando ' 
    f'<strong>{len(filtered)}</strong> OM(s) con estado Abierta/Pendiente.</div>'
    '</div>',
    unsafe_allow_html=True,
)

if filtered.empty:
    st.info("No hay OM en estado de Peligro para los filtros seleccionados.")
else:
    display_cols = [
        "Mes", "Año", "Proceso", "Subproceso", "Programa",
        "Estado OM", "OM", "Observación", "Peligro",
    ]
    st.dataframe(filtered[display_cols].astype(str), use_container_width=True)

with st.expander("➕ Asociar nueva OM", expanded=False):
    with st.form("om_association_form"):
        new_prog = st.text_input("Programa")
        new_proc = st.selectbox("Proceso", proceso_options)
        new_subproc = st.selectbox("Subproceso", subproceso_options)
        new_mes = st.selectbox("Mes", mes_options)
        new_año = st.selectbox("Año", año_options)
        new_estado = st.selectbox("Estado OM", ["Abierta", "Pendiente"])
        new_om = st.text_input("OM")
        new_obs = st.text_area("Observación")
        submit = st.form_submit_button("Guardar asociación")

    if submit:
        if not new_prog or not new_om:
            st.error("Debe completar al menos Programa y OM.")
        else:
            new_row = {
                "Mes": new_mes,
                "Año": new_año,
                "Proceso": new_proc,
                "Subproceso": new_subproc,
                "Programa": new_prog,
                "Estado OM": new_estado,
                "OM": new_om,
                "Observación": new_obs,
                "Peligro": "Peligro",
            }
            st.session_state["om_extra"].append(new_row)
            st.success("Asociación de OM registrada correctamente.")
            st.experimental_rerun()

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

st.caption(
    "Nota: el campo OM y Observación se pueden sincronizar con Supabase reemplazando `load_om_data()` por la fuente real de datos."
)
