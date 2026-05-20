"""
pages/1_Alertas_Riesgos.py — Fase 2: Alertas
Dashboard de alertas operativas por pestañas.
"""

import pandas as pd
import streamlit as st

from utils.alertas_vact import render_alertas_tabs
from utils.data_loader_vact import FAC_ABREV_INV, load_etapas_data
from utils.f2_components import (
    apply_current_filters as f2_apply_filters,
    render_f2_header,
    render_f2_sidebar,
    render_filter_bar as f2_render_filter_bar,
)
from utils.poli_theme import TEXT_PRIMARY, phosphor_icon, streamlit_global_css

st.set_page_config(
    page_title="Alertas · POLI",
    page_icon=":material/warning:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(streamlit_global_css(), unsafe_allow_html=True)

df_raw = load_etapas_data()
fac_abrev_inv = FAC_ABREV_INV
fac_ops = sorted(df_raw["FACULTAD_ABREV"].dropna().unique().tolist()) if "FACULTAD_ABREV" in df_raw.columns else []
mods_ops = sorted(df_raw["MODALIDAD"].dropna().unique().tolist()) if "MODALIDAD" in df_raw.columns else []
pers_ops = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist()) if "PERIODO DE IMPLEMENTACIÓN" in df_raw.columns else []
niveles_ops = [n for n in ["Pregrado", "Posgrado"] if n in df_raw.get("NIVEL_HOMOLOGADO", pd.Series(dtype=str)).values]

render_f2_sidebar()
render_f2_header("Alertas")
f2_render_filter_bar(
    df_raw, fac_abrev_inv, mods_ops, fac_ops, pers_ops, niveles_ops, key_prefix="alertas"
)

df, *_ = f2_apply_filters(df_raw, fac_abrev_inv, key_prefix="alertas")

if len(df) == 0:
    st.warning("No hay programas que coincidan con los filtros seleccionados.")
else:
    st.markdown(
        f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">'
        f'{phosphor_icon("warning", size=22)} Alertas</div>',
        unsafe_allow_html=True,
    )
    render_alertas_tabs(df)
