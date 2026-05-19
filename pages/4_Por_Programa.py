"""
pages/4_Por_Programa.py — Fase 2: Por Programa
Ficha por programa, matriz de avance y tabla detallada.
"""

import pandas as pd
import streamlit as st

from utils.data_loader_vact import FAC_ABREV_INV, load_etapas_data
from utils.f2_components import (
    apply_current_filters,
    render_f2_header,
    render_f2_sidebar,
    render_filter_bar,
)
from utils.poli_theme import TEXT_MUTED, TEXT_PRIMARY, phosphor_icon, streamlit_global_css
from utils.vact_master_table import (
    excel_export_bytes,
    render_heatmap_programas_etapa,
    render_master_table,
    render_program_ficha,
)

st.set_page_config(
    page_title="Por Programa · Fase 2 · POLI",
    page_icon=":material/school:",
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

render_f2_sidebar(show_fase1=False)
render_f2_header("Fase 2 · Por Programa")
render_filter_bar(
    df_raw, fac_abrev_inv, mods_ops, fac_ops, pers_ops, niveles_ops, key_prefix="programa"
)

df, *_ = apply_current_filters(df_raw, fac_abrev_inv, key_prefix="programa")

if len(df) == 0:
    st.warning("No hay programas con los filtros actuales.")
else:
    st.markdown(
        f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">'
        f'{phosphor_icon("student", size=22)} Por Programa</div>'.replace("motion.", ""),
        unsafe_allow_html=True,
    )

    programas = sorted(df["NOMBRE DEL PROGRAMA"].dropna().astype(str).unique().tolist())
    sel = st.selectbox(
        "Buscar programa",
        programas,
        index=0,
        placeholder="Seleccione un programa",
    )

    if sel:
        render_program_ficha(df, sel)

    st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

    top_n = st.select_slider("Programas en matriz", options=[10, 15, 25, 50], value=15)
    render_heatmap_programas_etapa(df, top_n=top_n)

    st.markdown(
        f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin:24px 0 8px">'
        f'{phosphor_icon("table", size=16)} Detalle completo por programa</div>'.replace("motion.", ""),
        unsafe_allow_html=True,
    )
    st.caption("Pulse + en el encabezado de cada etapa para ver actividades.")

    render_master_table(df)

    st.download_button(
        "Descargar Excel",
        data=excel_export_bytes(df),
        file_name="reforma_curricular_fase2.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon=":material/download:",
        key="dl_prog",
    )
