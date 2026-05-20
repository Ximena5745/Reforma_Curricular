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
from utils.poli_theme import (
    BG_ROW,
    BG_ROW_ALT,
    BORDER_ROW,
    BORDER_TABLE,
    BRAND_PRIMARY,
    FACULTAD_CLR,
    MODALIDAD_CLR,
    PERIODO_CLR,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SUBTLE,
    badge_html,
    phosphor_icon,
)

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


def _p_esc(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


_ALERTAS_TABLE_CSS = f"""
<style>
.alertas-tabla-wrap {{
  border-radius: 12px;
  border: 1.5px solid {BORDER_TABLE};
  box-shadow: 0 2px 10px rgba(15,56,90,0.08);
  overflow: auto;
  background: #fff;
  margin-bottom: 8px;
}}
.alertas-tabla {{
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-family: 'Segoe UI', sans-serif;
  font-size: 12px;
}}
.alertas-tabla thead th {{
  background: {BRAND_PRIMARY};
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding: 10px 12px;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 2;
}}
.alertas-tabla thead th.th-prog {{
  text-align: left;
  min-width: 200px;
}}
.alertas-tabla tbody td {{
  padding: 9px 12px;
  border-bottom: 1px solid {BORDER_ROW};
  vertical-align: middle;
  text-align: center;
}}
.alertas-tabla tbody td.td-prog {{
  text-align: left;
  font-weight: 600;
  color: {TEXT_PRIMARY};
  min-width: 200px;
  max-width: 320px;
}}
.alertas-tabla tbody td.td-sede {{
  color: {TEXT_SUBTLE};
  font-size: 11px;
}}
.alertas-tabla tbody tr:hover td {{
  background: #E3F4FB !important;
}}
</style>
"""


def _fac_color(row: pd.Series, fac: str) -> str:
    if "FACULTAD_COLOR" in row.index and pd.notna(row.get("FACULTAD_COLOR")):
        return str(row["FACULTAD_COLOR"])
    return FACULTAD_CLR.get(fac, "#6e7681")


def _render_tabla_alerta_html(
    risk_df: pd.DataFrame,
    pendiente: str,
    accent_color: str,
) -> None:
    if risk_df.empty:
        st.caption("Sin programas en esta alerta.")
        return

    sorted_df = risk_df.sort_values("NOMBRE DEL PROGRAMA")
    rows_html = ""
    for i, (_, row) in enumerate(sorted_df.iterrows()):
        rbg = BG_ROW if i % 2 == 0 else BG_ROW_ALT
        prog = _p_esc(row.get("NOMBRE DEL PROGRAMA", "—"))
        fac = str(row.get("FACULTAD_ABREV", "—") or "—")
        mod = str(row.get("MODALIDAD", "—") or "—")
        per = str(row.get("PERIODO DE IMPLEMENTACIÓN", "—") or "—")
        sede = _p_esc(row.get("SEDE", "—"))
        fac_c = _fac_color(row, fac)
        mod_c = MODALIDAD_CLR.get(mod, "#6e7681")
        per_c = PERIODO_CLR.get(per, "#94a3b8")

        rows_html += (
            f'<tr style="background:{rbg}">'
            f'<td class="td-prog">{prog}</td>'
            f'<td>{badge_html(fac, fac_c)}</td>'
            f'<td>{badge_html(mod, mod_c)}</td>'
            f'<td>{badge_html(per, per_c)}</td>'
            f'<td class="td-sede">{sede}</td>'
            f'<td>{badge_html(pendiente, accent_color)}</td>'
            f"</tr>"
        )

    html = (
        _ALERTAS_TABLE_CSS
        + '<div class="alertas-tabla-wrap"><table class="alertas-tabla">'
        + "<thead><tr>"
        + '<th class="th-prog">Programa</th>'
        + "<th>Facultad</th><th>Modalidad</th><th>Período</th>"
        + "<th>Sede</th><th>Pendiente</th>"
        + "</tr></thead><tbody>"
        + rows_html
        + "</tbody></table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


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
            st.markdown(
                f'<div style="font-size:12px;font-weight:700;color:{TEXT_PRIMARY};margin:0 0 8px">'
                f'{phosphor_icon("table", size=14)} {n} programa{"s" if n != 1 else ""} en alerta</div>',
                unsafe_allow_html=True,
            )
            _render_tabla_alerta_html(risk_df, cfg["pendiente"], cfg["color"])
