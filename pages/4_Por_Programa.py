"""
pages/4_Por_Programa.py — Fase 2: Resumen Por Programa
Tabla maestra paginada por período, ficha gráfica por programa seleccionado.
"""

import pandas as pd
import streamlit as st

from utils.charts_vact import render_program_ficha_grafica
from utils.data_loader_vact import FAC_ABREV_INV, load_etapas_data
from utils.f2_components import (
    apply_current_filters,
    render_f2_header,
    render_f2_sidebar,
    render_filter_bar,
)
from utils.poli_theme import TEXT_PRIMARY, phosphor_icon, streamlit_global_css
from utils.vact_master_table import excel_export_bytes, render_master_table_by_periodo

st.set_page_config(
    page_title="Resumen Por Programa · POLI",
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

render_f2_sidebar()
render_f2_header("Resumen Por Programa")
render_filter_bar(
    df_raw, fac_abrev_inv, mods_ops, fac_ops, pers_ops, niveles_ops, key_prefix="programa"
)

df, *_ = apply_current_filters(df_raw, fac_abrev_inv, key_prefix="programa")

if len(df) == 0:
    st.warning("No hay programas con los filtros actuales.")
else:
    st.markdown(
        f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">'
        f'{phosphor_icon("student", size=22)} Resumen Por Programa</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin:8px 0 8px">'
        f'{phosphor_icon("table", size=16)} Detalle completo por programa</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Listado de todos los programas según los filtros superiores. "
        "Navegue por período en las pestañas. Pulse + en cada etapa para ver actividades."
    )
    render_master_table_by_periodo(df, key_prefix="programa_tabla")

    st.divider()

    # Construir etiquetas únicas: Nombre · Modalidad · Sede
    # Necesario porque puede haber programas con el mismo nombre pero distinta
    # modalidad o sede (ej. "Contaduría Pública · Presencial · Bogotá" vs
    # "Contaduría Pública · Virtual · Nacional")
    def _build_label(row: pd.Series) -> str:
        nombre = str(row.get("NOMBRE DEL PROGRAMA", "")).strip()
        mod    = str(row.get("MODALIDAD", "")).strip()
        sede   = str(row.get("SEDE", "")).strip()
        partes = [p for p in [mod, sede] if p and p.lower() not in ("", "none", "nan")]
        return f"{nombre} · {' · '.join(partes)}" if partes else nombre

    df_sel = df.copy().reset_index(drop=True)
    df_sel["_label"] = df_sel.apply(_build_label, axis=1)

    # Si el label es duplicado (mismo nombre+modalidad+sede), añadir índice
    seen: dict[str, int] = {}
    labels_uniq: list[str] = []
    for lbl in df_sel["_label"]:
        if lbl in seen:
            seen[lbl] += 1
            labels_uniq.append(f"{lbl} ({seen[lbl]})")
        else:
            seen[lbl] = 1
            labels_uniq.append(lbl)
    df_sel["_label_uniq"] = labels_uniq

    opciones = sorted(df_sel["_label_uniq"].tolist())
    sel_label = st.selectbox(
        "Buscar programa",
        opciones,
        index=0,
        placeholder="Seleccione un programa",
        key="programa_sel",
    )

    if sel_label:
        st.caption(
            "Ficha del programa: avance por etapa, estado y responsable de cada actividad."
        )
        # Filtrar al programa exacto seleccionado (una sola fila)
        mask = df_sel["_label_uniq"] == sel_label
        df_prog = df_sel[mask].drop(columns=["_label", "_label_uniq"])
        nombre_prog = df_prog["NOMBRE DEL PROGRAMA"].iloc[0] if len(df_prog) else sel_label
        render_program_ficha_grafica(df_prog, nombre_prog)

    st.markdown("<div style='margin:24px 0 8px'></div>", unsafe_allow_html=True)
    st.download_button(
        "Descargar Excel",
        data=excel_export_bytes(df),
        file_name="reforma_curricular_fase2.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon=":material/download:",
        key="dl_prog",
    )
