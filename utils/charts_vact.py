"""
Gráficos Plotly Fase 2 — drill-down avance por etapa.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader_vact import (
    ETAPAS_ORDEN,
    ETAPA_PCT_COL,
    _ensure_activities_meta,
    get_detalle_etapa,
)
from utils.poli_theme import ETAPA_CLR, STATUS_CLR, TEXT_MUTED, TEXT_PRIMARY

ETAPA_SHORT = {
    "Alistamiento Curricular": "Alistamiento",
    "Diseño Curricular": "Diseño",
    "Desarrollo Curricular": "Desarrollo",
    "Implementación Curricular": "Implementación",
}

STATUS_STACK = [
    ("done", "Finalizado", STATUS_CLR["done"]),
    ("inprog", "En proceso", STATUS_CLR["inprog"]),
    ("nostart", "Sin iniciar", STATUS_CLR["nostart"]),
    ("na", "No aplica", STATUS_CLR["na"]),
]

_PLOTLY_CONFIG = {"displayModeBar": False}


def _etapa_promedios(df: pd.DataFrame) -> list[float]:
    out = []
    for etapa in ETAPAS_ORDEN:
        col = ETAPA_PCT_COL.get(etapa)
        if col and col in df.columns and len(df):
            out.append(round(float(df[col].mean()), 1))
        else:
            out.append(0.0)
    return out


def _resolve_etapa_from_point(pt: dict) -> str | None:
    cd = pt.get("customdata")
    if cd is not None:
        if isinstance(cd, str) and cd in ETAPAS_ORDEN:
            return cd
        if isinstance(cd, (list, tuple)) and cd:
            val = cd[0]
            if isinstance(val, (list, tuple)):
                val = val[0]
            if val in ETAPAS_ORDEN:
                return val
    idx = pt.get("point_index", pt.get("pointNumber"))
    if idx is not None and 0 <= int(idx) < len(ETAPAS_ORDEN):
        return ETAPAS_ORDEN[int(idx)]
    return None


def _fig_etapas_level(df: pd.DataFrame) -> go.Figure:
    promedios = _etapa_promedios(df)
    labels = [ETAPA_SHORT[e] for e in ETAPAS_ORDEN]
    colors = [ETAPA_CLR.get(e, "#6e7681") for e in ETAPAS_ORDEN]
    x_max = max(105, max(promedios, default=0) + 8)

    fig = go.Figure(
        go.Bar(
            x=promedios,
            y=labels,
            orientation="h",
            marker=dict(color=colors, line=dict(width=1, color="white")),
            text=[f"{p}%" for p in promedios],
            textposition="outside",
            textfont=dict(size=11, color="#475569"),
            hovertemplate="<b>%{y}</b><br>Avance: %{x}%<extra></extra>",
            customdata=[[e] for e in ETAPAS_ORDEN],
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=4, r=48, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            range=[0, x_max],
            ticksuffix="%",
            showgrid=True,
            gridcolor="rgba(15,56,90,0.07)",
            zeroline=False,
        ),
        yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
        font=dict(family="Segoe UI", color=TEXT_PRIMARY),
        showlegend=False,
        clickmode="event",
    )
    return fig


def _fig_actividades_level(df: pd.DataFrame, etapa: str) -> go.Figure:
    meta = _ensure_activities_meta(df)
    acts = [m for m in meta if m["phase"] == etapa]
    n_prog = max(len(df), 1)

    act_rows = []
    for m in acts:
        col = f"cl_act_{m['idx']}"
        if col not in df.columns:
            continue
        done = int((df[col] == "done").sum())
        act_rows.append((m, done / n_prog))

    act_rows.sort(key=lambda x: -x[1])
    acts_sorted = [m for m, _ in act_rows]
    names_short = [_short(m["name"], 42) for m in acts_sorted]
    names_full = [m["name"] for m in acts_sorted]

    fig = go.Figure()
    for cl_key, lbl, clr in STATUS_STACK:
        vals = []
        for m in acts_sorted:
            col = f"cl_act_{m['idx']}"
            vals.append(int((df[col] == cl_key).sum()) if col in df.columns else 0)
        txt_color = "#475569" if cl_key == "na" else "#ffffff"
        fig.add_trace(
            go.Bar(
                name=lbl,
                y=names_short,
                x=vals,
                orientation="h",
                marker_color=clr,
                customdata=names_full,
                text=[str(v) if v > 0 else "" for v in vals],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(size=10, color=txt_color),
                hovertemplate="<b>%{customdata}</b><br>" + lbl + ": %{x}<extra></extra>",
            )
        )

    fig.update_layout(
        barmode="stack",
        bargap=0.28,
        height=max(280, len(acts_sorted) * 28 + 72),
        margin=dict(l=4, r=24, t=40, b=8),
        uniformtext=dict(minsize=8, mode="hide"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=10)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
        xaxis=dict(showgrid=True, gridcolor="rgba(15,56,90,0.06)", title="Programas"),
        font=dict(family="Segoe UI"),
        title=dict(text=f"Actividades — {ETAPA_SHORT.get(etapa, etapa)}", font=dict(size=13)),
    )
    return fig


def _short(text: str, n: int) -> str:
    t = str(text).strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def _render_panel_resumen(df: pd.DataFrame) -> None:
    promedios = _etapa_promedios(df)
    avg_global = round(sum(promedios) / len(promedios), 1) if promedios else 0
    rows = ""
    for etapa, pct in zip(ETAPAS_ORDEN, promedios):
        clr = ETAPA_CLR.get(etapa, "#6e7681")
        short = ETAPA_SHORT.get(etapa, etapa)
        rows += (
            '<motion.div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
            f'<motion.div style="width:8px;height:8px;border-radius:2px;background:{clr}"></motion.div>'
            f'<span style="font-size:11px;color:#475569;flex:1">{short}</span>'
            f'<span style="font-size:11px;font-weight:700;color:#0f172a">{pct}%</span>'
            "</motion.div>"
        )
    rows = rows.replace("motion.div", "div")
    html = (
        '<motion.div style="background:#fff;border:1px solid rgba(15,56,90,.1);border-radius:12px;padding:14px">'
        f'<motion.div style="font-size:11px;font-weight:700;color:{TEXT_MUTED};text-transform:uppercase;letter-spacing:.4px">'
        "Resumen general</motion.div>"
        f'<motion.div style="font-size:26px;font-weight:800;color:{TEXT_PRIMARY};margin:4px 0">{avg_global}%</motion.div>'
        f'<motion.div style="font-size:10px;color:{TEXT_MUTED};margin-bottom:10px">'
        f"Promedio de avance · {len(df)} programas</motion.div>"
        f"{rows}</motion.div>"
    )
    st.markdown(html.replace("motion.div", "div"), unsafe_allow_html=True)


def _render_panel_etapa(df: pd.DataFrame, etapa: str | None) -> None:
    if not etapa:
        _render_panel_resumen(df)
        return

    det = get_detalle_etapa(df, etapa)
    color = ETAPA_CLR.get(etapa, "#6e7681")

    acts_html = ""
    for act in det.get("actividades", [])[:8]:
        pct = act["pct_done"]
        acts_html += (
            '<motion.div style="margin-bottom:6px">'
            '<motion.div style="display:flex;justify-content:space-between;font-size:10px;margin-bottom:2px">'
            f'<span style="color:#475569;max-width:78%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'
            f'{_short(act["nombre"], 32)}</span>'
            f'<span style="font-weight:700;color:#0f172a">{pct}%</span>'
            "</motion.div>"
            '<motion.div style="height:4px;background:#e2e8f0;border-radius:2px">'
            f'<motion.div style="width:{min(100, pct)}%;height:100%;background:{color};border-radius:2px;opacity:.85">'
            "</motion.div></motion.div></motion.div>"
        )
    acts_html = acts_html.replace("motion.div", "div")

    html = (
        f'<motion.div style="background:#fff;border:1px solid rgba(15,56,90,.1);border-radius:12px;'
        f'padding:14px;border-left:4px solid {color}">'
        f'<motion.div style="font-size:12px;font-weight:700;color:{color}">'
        f'{ETAPA_SHORT.get(etapa, etapa)}</motion.div>'
        f'<motion.div style="font-size:28px;font-weight:800;color:{color}">{det["pct_promedio"]}%</motion.div>'
        f'<motion.div style="font-size:10px;color:{TEXT_MUTED};margin:6px 0 12px">'
        f'{det.get("n_programas", len(df))} programas · {det.get("n_actividades", 0)} actividades</motion.div>'
        f'<motion.div style="font-size:10px;font-weight:700;color:{TEXT_MUTED};margin-bottom:6px">Actividades</motion.div>'
        f"{acts_html}</motion.div>"
    )
    st.markdown(html.replace("motion.div", "div"), unsafe_allow_html=True)

    n_acts = len(det.get("actividades", []))
    if n_acts > 8:
        with st.expander(f"Ver las {n_acts} actividades"):
            for act in det["actividades"]:
                st.caption(
                    f"{act['nombre']}: {act['pct_done']}% finalizado "
                    f"({act['done']}/{det.get('n_programas', len(df))})"
                )


def render_etapas_drilldown(df: pd.DataFrame, *, key_prefix: str = "etapas") -> None:
    """Gráfica de barras con drill-down etapa → actividades."""
    if len(df) == 0 or "pct_alistamiento" not in df.columns:
        st.info("Sin datos para mostrar avance por etapa.")
        return

    sk = f"{key_prefix}_drill"
    if sk not in st.session_state:
        st.session_state[sk] = None

    etapa_sel = st.session_state[sk]
    col_chart, col_panel = st.columns([2.2, 1])

    with col_chart:
        if etapa_sel:
            if st.button("Volver a etapas", key=f"{key_prefix}_back", icon=":material/arrow_back:"):
                st.session_state[sk] = None
                st.rerun()
            fig = _fig_actividades_level(df, etapa_sel)
        else:
            fig = _fig_etapas_level(df)
            if all(p == 0 for p in _etapa_promedios(df)):
                st.caption("Los porcentajes de avance por etapa son 0 con los filtros actuales.")

        event = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=f"{key_prefix}_plotly",
            config=_PLOTLY_CONFIG,
        )

        if not etapa_sel and event and getattr(event, "selection", None):
            points = getattr(event.selection, "points", None) or []
            if points:
                picked = _resolve_etapa_from_point(points[0])
                if picked:
                    st.session_state[sk] = picked
                    st.rerun()

    with col_panel:
        _render_panel_etapa(df, etapa_sel)
