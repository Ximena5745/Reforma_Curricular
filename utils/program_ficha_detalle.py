"""
Detalle de actividades por etapa en la ficha de un programa (Resumen Por Programa).
"""

from __future__ import annotations

import streamlit as st

from utils.data_loader_vact import ETAPAS_ORDEN, STATUS_LABEL
from utils.poli_theme import (
    BG_ROW,
    BG_ROW_ALT,
    BORDER_ROW,
    ETAPA_CLR,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SUBTLE,
    p_bar_html,
)
from utils.vact_master_table import _p_esc, _status_legend_html, _vact_act_icon

ETAPA_SHORT = {
    "Alistamiento Curricular": "Alistamiento",
    "Diseño Curricular": "Diseño",
    "Desarrollo Curricular": "Desarrollo",
    "Implementación Curricular": "Implementación",
}


def _act_sort_key(act: dict) -> tuple:
    pct = act.get("pct")
    if isinstance(pct, (int, float)):
        return (-float(pct), act.get("nombre", ""))
    return (0, act.get("nombre", ""))


def _pct_display(act: dict) -> tuple[float | None, str]:
    pct = act.get("pct")
    if isinstance(pct, (int, float)):
        return float(pct), f"{pct:.0f}%"
    return None, "—"


def _actividades_table_html(actividades: list[dict], etapa_clr: str) -> str:
    if not actividades:
        return f'<p style="font-size:12px;color:{TEXT_MUTED};padding:8px 0">Sin actividades en esta etapa.</p>'

    header = (
        f'<tr style="background:{etapa_clr};color:#fff;font-size:10px;font-weight:700">'
        '<th style="padding:8px 10px;text-align:left;width:42%">Actividad</th>'
        '<th style="padding:8px 6px;text-align:center;width:18%">Estado</th>'
        '<th style="padding:8px 6px;text-align:left;width:22%">Responsable</th>'
        '<th style="padding:8px 8px;text-align:center;width:18%">Avance</th>'
        "</tr>"
    )
    rows = []
    for i, act in enumerate(actividades):
        bg = BG_ROW if i % 2 == 0 else BG_ROW_ALT
        cl = act.get("estado_key", "na")
        val = act.get("valor", "—")
        lbl = STATUS_LABEL.get(cl, cl)
        icon = _vact_act_icon(cl, val)
        pct_num, pct_txt = _pct_display(act)
        avance_cell = (
            p_bar_html(pct_num) if pct_num is not None else f'<span style="color:{TEXT_MUTED}">—</span>'
        )
        resp = _p_esc(str(act.get("responsable", "—")))
        resp_short = resp if len(resp) <= 36 else resp[:35] + "…"
        rows.append(
            f'<tr style="background:{bg};border-bottom:1px solid {BORDER_ROW}">'
            f'<td style="padding:8px 10px;font-size:11px;color:{TEXT_PRIMARY};vertical-align:middle;'
            f'line-height:1.35" title="{_p_esc(act.get("nombre", ""))}">'
            f'{_p_esc(act.get("nombre", "—"))}</td>'
            f'<td style="padding:6px;text-align:center;vertical-align:middle">'
            f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:10px;color:{TEXT_SUBTLE}">'
            f"{icon}<span>{_p_esc(lbl)}</span></span></td>"
            f'<td style="padding:6px 8px;font-size:10px;color:{TEXT_SUBTLE};vertical-align:middle" '
            f'title="{resp}">{resp_short}</td>'
            f'<td style="padding:6px 8px;text-align:center;vertical-align:middle">'
            f'<span style="font-size:10px;font-weight:700;color:{TEXT_PRIMARY};display:block;margin-bottom:3px">'
            f"{pct_txt}</span>{avance_cell}</td>"
            "</tr>"
        )

    return (
        f'<div style="overflow-x:auto;border:1px solid {BORDER_ROW};border-radius:8px;margin-top:4px">'
        f'<table style="width:100%;border-collapse:collapse;font-family:Segoe UI,sans-serif">'
        f"<thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"
        f"</div>"
    )


def render_program_actividades_detalle(data: dict) -> None:
    """Expanders por etapa con tabla actividad × estado × responsable × avance."""
    st.markdown(
        f'<p style="font-size:12px;font-weight:700;color:{TEXT_MUTED};margin:16px 0 8px">'
        "Detalle de actividades por etapa</p>",
        unsafe_allow_html=True,
    )

    etapas_data = data.get("etapas", {})
    for etapa in ETAPAS_ORDEN:
        et_data = etapas_data.get(etapa, {})
        acts = list(et_data.get("actividades", []))
        acts.sort(key=_act_sort_key)
        pct_e = float(et_data.get("pct", 0) or 0)
        short = ETAPA_SHORT.get(etapa, etapa)
        clr = ETAPA_CLR.get(etapa, "#6e7681")

        with st.expander(f"{short} — {pct_e:.0f}%", expanded=True):
            st.markdown(
                _actividades_table_html(acts, clr),
                unsafe_allow_html=True,
            )

    st.markdown(_status_legend_html().replace("Pulse + en cada etapa", "Referencia de estados"), unsafe_allow_html=True)
