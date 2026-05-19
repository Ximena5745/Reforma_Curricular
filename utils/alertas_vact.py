"""
Alertas operativas Fase 2 — pestañas en lenguaje claro.
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import streamlit as st

from utils.data_loader_vact import (
    activity_in_progress,
    activity_not_done,
    activity_status_is,
    activity_val_contains,
)
from utils.poli_theme import TEXT_MUTED, TEXT_PRIMARY, phosphor_icon

RIESGOS_ALERTA: list[dict] = [
    {
        "id": "proyecciones",
        "tab": "Proyecciones devueltas",
        "titulo": "Formato de proyecciones devuelto — aval financiero",
        "explicacion": (
            "El formato «5. Formato de proyecciones académicas y financieras» está en estado "
            "Devuelto. Esto bloquea o retrasa la emisión del Concepto Financiero (gate de aval "
            "financiero)."
        ),
        "accion": (
            "Revisar observaciones, corregir el formato de proyecciones y gestionar el aval "
            "hacia Concepto Financiero."
        ),
        "pendiente": "Formato de proyecciones devuelto",
        "color": "#dc2626",
    },
    {
        "id": "contenidos_2026",
        "tab": "Contenidos 2026-2",
        "titulo": "Lanzamiento 2026-2 con contenidos incompletos",
        "explicacion": (
            "Programas con período de implementación 2026-2 cuya producción de contenidos "
            "no está finalizada."
        ),
        "accion": "Avanzar la producción de contenidos antes del lanzamiento.",
        "pendiente": "Producción de contenidos pendiente",
        "color": "#d97706",
    },
    {
        "id": "banner_prod",
        "tab": "Banner sin contenidos",
        "titulo": "Parametrización en Banner sin producción de contenidos",
        "explicacion": (
            "La parametrización en Banner está en proceso, pero la producción de contenidos "
            "aún no ha finalizado."
        ),
        "accion": "Finalizar producción de contenidos o ajustar estado en Banner.",
        "pendiente": "Producción de contenidos pendiente",
        "color": "#7c3aed",
    },
    {
        "id": "syllabus",
        "tab": "Syllabus pendiente",
        "titulo": "Syllabus incompleto en modalidad virtual o híbrida",
        "explicacion": (
            "Programas virtuales o híbridos con syllabus de programa o completos sin finalizar."
        ),
        "accion": "Completar syllabus de programa y syllabus completos.",
        "pendiente": "Syllabus pendiente",
        "color": "#0d9488",
    },
    {
        "id": "convenios",
        "tab": "Convenios pendientes",
        "titulo": "Banner en proceso sin trámites de convenios",
        "explicacion": (
            "La parametrización en Banner avanza, pero los trámites de convenios no están finalizados."
        ),
        "accion": "Gestionar y cerrar trámites de convenios asociados.",
        "pendiente": "Convenios pendientes",
        "color": "#2563eb",
    },
    {
        "id": "men_prod",
        "tab": "MEN sin producción",
        "titulo": "Trámite MEN aprobado sin producción virtual completa",
        "explicacion": (
            "El cronograma ante el MEN está aprobado, pero la producción de contenidos virtuales "
            "no está finalizada."
        ),
        "accion": "Completar producción de contenidos tras aprobación MEN.",
        "pendiente": "Producción virtual pendiente",
        "color": "#f59e0b",
    },
]


def get_r1_produccion_sin_aval(df: pd.DataFrame) -> pd.DataFrame:
    mask = activity_status_is(df, "proyecciones_formato_5", "devuelto")
    return df[mask]


def get_r2_contenidos_incompletos(df: pd.DataFrame) -> pd.DataFrame:
    mask = (df["PERIODO DE IMPLEMENTACIÓN"] == "2026-2") & activity_not_done(df, "produccion_contenido")
    return df[mask]


def get_r3_banner_sin_produccion(df: pd.DataFrame) -> pd.DataFrame:
    mask = activity_in_progress(df, "banner_convenios") & activity_not_done(df, "produccion_contenido")
    return df[mask]


def get_r4_syllabus_incompleto(df: pd.DataFrame) -> pd.DataFrame:
    mask = df["MODALIDAD"].isin(["Virtual", "Híbrido"]) & activity_not_done(df, "syllabus")
    return df[mask]


def get_r5_banner_sin_convenios(df: pd.DataFrame) -> pd.DataFrame:
    mask = activity_in_progress(df, "banner_convenios") & activity_not_done(df, "convenios")
    return df[mask]


def get_r6_aprobados_men(df: pd.DataFrame) -> pd.DataFrame:
    mask = activity_val_contains(df, "cronograma_men", "aprobado") & activity_not_done(
        df, "produccion_contenido"
    )
    return df[mask]


_GETTERS: list[Callable[[pd.DataFrame], pd.DataFrame]] = [
    get_r1_produccion_sin_aval,
    get_r2_contenidos_incompletos,
    get_r3_banner_sin_produccion,
    get_r4_syllabus_incompleto,
    get_r5_banner_sin_convenios,
    get_r6_aprobados_men,
]


def _programas_con_alertas(df: pd.DataFrame) -> int:
    seen: set[str] = set()
    for fn in _GETTERS:
        for name in fn(df)["NOMBRE DEL PROGRAMA"].dropna().astype(str):
            seen.add(name.strip())
    return len(seen)


def _tabla_riesgo(risk_df: pd.DataFrame, pendiente: str) -> pd.DataFrame:
    if risk_df.empty:
        return pd.DataFrame(columns=["Programa", "Facultad", "Modalidad", "Período", "Sede", "Pendiente"])
    out = pd.DataFrame({
        "Programa": risk_df["NOMBRE DEL PROGRAMA"],
        "Facultad": risk_df["FACULTAD_ABREV"] if "FACULTAD_ABREV" in risk_df.columns else "—",
        "Modalidad": risk_df["MODALIDAD"] if "MODALIDAD" in risk_df.columns else "—",
        "Período": risk_df["PERIODO DE IMPLEMENTACIÓN"] if "PERIODO DE IMPLEMENTACIÓN" in risk_df.columns else "—",
        "Sede": risk_df["SEDE"] if "SEDE" in risk_df.columns else "—",
        "Pendiente": pendiente,
    })
    return out.sort_values("Programa").reset_index(drop=True)


def render_alertas_tabs(df: pd.DataFrame) -> None:
    n_total = len(df)
    n_alert = _programas_con_alertas(df)
    st.markdown(
        f'<p style="font-size:13px;color:{TEXT_MUTED};margin:0 0 16px">'
        f"<b style=\"color:{TEXT_PRIMARY}\">{n_alert}</b> de <b>{n_total}</b> programas "
        f"tienen al menos una alerta activa con los filtros actuales.</p>",
        unsafe_allow_html=True,
    )

    items = []
    for cfg, getter in zip(RIESGOS_ALERTA, _GETTERS):
        risk_df = getter(df)
        n = len(risk_df)
        if n > 0:
            items.append((cfg, risk_df, n))

    items.sort(key=lambda x: -x[2])

    if not items:
        st.success("Ningún programa en alerta con los filtros actuales.")
        return

    tabs = st.tabs([f"{cfg['tab']} ({n})" for cfg, _, n in items])

    for tab, (cfg, risk_df, n) in zip(tabs, items):
        with tab:
            st.markdown(
                f'<div style="border-left:4px solid {cfg["color"]};padding:12px 14px;'
                f'background:rgba(15,56,90,.03);border-radius:8px;margin-bottom:14px">'
                f'<div style="font-size:15px;font-weight:700;color:#0f172a">{cfg["titulo"]}</div>'
                f'<div style="font-size:12px;color:#64748b;margin-top:6px">'
                f'<b>Qué significa:</b> {cfg["explicacion"]}</div>'
                f'<div style="font-size:12px;color:#64748b;margin-top:4px">'
                f'<b>Acción recomendada:</b> {cfg["accion"]}</div>'
                f"</div>".replace("div", "div"),
                unsafe_allow_html=True,
            )
            st.dataframe(
                _tabla_riesgo(risk_df, cfg["pendiente"]),
                use_container_width=True,
                hide_index=True,
            )
