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
    STATUS_LABEL,
    _ensure_activities_meta,
    get_estadisticas_etapa,
)
from utils.poli_theme import ETAPA_CLR, STATUS_CLR, TEXT_MUTED, TEXT_PRIMARY, phosphor_icon


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


def _etapa_promedios(df: pd.DataFrame) -> list[float]:
    out = []
    for etapa in ETAPAS_ORDEN:
        col = ETAPA_PCT_COL.get(etapa)
        if col and col in df.columns and len(df):
            out.append(round(float(df[col].mean()), 1))
        else:
            out.append(0.0)
    return out


def _activity_status_counts(df: pd.DataFrame, etapa: str) -> dict[str, int]:
    meta = _ensure_activities_meta(df)
    acts = [m for m in meta if m["phase"] == etapa]
    counts = {k: 0 for k, _, _ in STATUS_STACK}
    for m in acts:
        col = f"cl_act_{m['idx']}"
        if col not in df.columns:
            continue
        for cl in df[col]:
            if cl in counts:
                counts[cl] += 1
            else:
                counts["na"] += 1
    return counts


def _fig_etapas_level(df: pd.DataFrame) -> go.Figure:
    promedios = _etapa_promedios(df)
    labels = [ETAPA_SHORT[e] for e in ETAPAS_ORDEN]
    colors = [ETAPA_CLR.get(e, "#6e7681") for e in ETAPAS_ORDEN]
    fig = go.Figure(
        go.Bar(
            x=promedios,
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{p}%" for p in promedios],
            textposition="outside",
            textfont=dict(size=11, color="#475569"),
            hovertemplate="<b>%{y}</b><br>Avance: %{x}%<extra></extra>",
            customdata=ETAPAS_ORDEN,
        )
    )
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=50, t=24, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 105], ticksuffix="%", showgrid=True, gridcolor="rgba(15,56,90,0.07)"),
        yaxis=dict(autorange="reversed"),
        font=dict(family="Segoe UI", color=TEXT_PRIMARY),
        showlegend=False,
        title=dict(text="Avance por Etapa", font=dict(size=14)),
    )
    return fig


def _fig_actividades_level(df: pd.DataFrame, etapa: str) -> go.Figure:
    meta = _ensure_activities_meta(df)
    acts = [m for m in meta if m["phase"] == etapa]
    names = [_short(m["name"], 36) for m in acts]
    fig = go.Figure()
    for cl_key, lbl, clr in STATUS_STACK:
        vals = []
        for m in acts:
            col = f"cl_act_{m['idx']}"
            if col not in df.columns:
                vals.append(0)
            else:
                vals.append(int((df[col] == cl_key).sum()))
        fig.add_trace(
            go.Bar(
                name=lbl,
                y=names,
                x=vals,
                orientation="h",
                marker_color=clr,
                hovertemplate="<b>%{y}</b><br>" + lbl + ": %{x}<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="stack",
        height=max(220, len(acts) * 32 + 80),
        margin=dict(l=10, r=20, t=36, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=10)),
        yaxis=dict(autorange="reversed"),
        font=dict(family="Segoe UI"),
        title=dict(text=f"Actividades — {ETAPA_SHORT.get(etapa, etapa)}", font=dict(size=13)),
    )
    return fig


def _short(text: str, n: int) -> str:
    t = str(text).strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def _render_panel_etapa(df: pd.DataFrame, etapa: str | None) -> None:
    if not etapa:
        st.markdown(
            f'<p style="font-size:12px;color:{TEXT_MUTED}">Seleccione una etapa en el gráfico '
            f"o use los botones inferiores.</p>".replace("", ""),
            unsafe_allow_html=True,
        )
        return
    stats = get_estadisticas_etapa(df, etapa)
    color = ETAPA_CLR.get(etapa, "#6e7681")
    st.markdown(
        f'<div style="background:#fff;border:1px solid rgba(15,56,90,.1);border-radius:12px;'
        f'padding:14px;border-left:4px solid {color}">'
        f'<div style="font-size:12px;font-weight:700;color:{color}">{ETAPA_SHORT.get(etapa, etapa)}</div>'
        f'<div style="font-size:28px;font-weight:800;color:{color}">{stats["pct_promedio"]}%</div>'
        f'<div style="font-size:11px;color:{TEXT_MUTED};margin-top:8px">'
        f'{phosphor_icon("check-circle", color="#22c55e", size=12)} {stats["done"]} finalizadas · '
        f'{phosphor_icon("arrows-clockwise", color="#0ea5e9", size=12)} {stats["inprog"]} en proceso · '
        f'{phosphor_icon("circle", color="#94a3b8", size=12)} {stats["nostart"]} sin iniciar'
        f"</div></div>".replace("", ""),
        unsafe_allow_html=True,
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

        event = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=f"{key_prefix}_plotly",
        )

        if not etapa_sel and event and event.selection and event.selection.points:
            pt = event.selection.points[0]
            cd = pt.get("customdata")
            if cd:
                picked = cd if isinstance(cd, str) else cd[0]
                if picked in ETAPAS_ORDEN:
                    st.session_state[sk] = picked
                    st.rerun()

    with col_panel:
        _render_panel_etapa(df, etapa_sel)

    st.caption("Seleccionar etapa:")
    btn_cols = st.columns(len(ETAPAS_ORDEN))
    for i, etapa in enumerate(ETAPAS_ORDEN):
        with btn_cols[i]:
            if st.button(
                ETAPA_SHORT[etapa],
                key=f"{key_prefix}_btn_{i}",
                use_container_width=True,
                type="primary" if etapa_sel == etapa else "secondary",
            ):
                st.session_state[sk] = etapa if st.session_state.get(sk) != etapa else None
                st.rerun()
