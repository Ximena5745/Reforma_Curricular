"""
app_act.py — Dashboard Fase 2: Reforma Curricular por Etapas (VACT)
Fuente: hoja Etapas · CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx
Página: Resumen Ejecutivo
"""

import html as html_lib
import io
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as html_comp

from utils.data_loader_vact import (
    ETAPAS_ORDEN,
    ETAPA_HEADER_CLR,
    ETAPA_PCT_COL,
    ETAPA_SLUG,
    FAC_ABREV_INV,
    STATUS_LABEL,
    _ensure_activities_meta,
    load_etapas_data,
)
from utils.charts_vact import render_etapas_drilldown
from utils.f2_components import (
    apply_current_filters as f2_apply_filters,
    render_f2_header,
    render_f2_sidebar,
    render_filter_bar as f2_render_filter_bar,
)
from utils.poli_theme import (
    BG_ROW,
    BG_ROW_ALT,
    BG_TABLE,
    BORDER_ROW,
    BORDER_TABLE,
    BRAND_ACCENT,
    BRAND_HIGHLIGHT,
    BRAND_PRIMARY,
    BRAND_SECONDARY,
    MODALIDAD_CLR,
    PERIODO_CLR,
    TEXT_LIGHT,
    TEXT_MUTED,
    TEXT_NA,
    TEXT_PRIMARY,
    TEXT_SUBTLE,
    badge_html,
    p_bar_html,
    status_icon_html,
    streamlit_global_css,
    FACULTAD_CLR,
    ETAPA_CLR,
    STATUS_CLR,
    phosphor_icon,
    phosphor_icon_kpi,
    phosphor_icon_nav,
    PHOSPHOR_ICONS,
)

st.set_page_config(
    page_title="Reforma Curricular · Fase 2 · POLI",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded",
)

def _registered_page_targets() -> set[str]:
    targets: set[str] = set()
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx is None:
            return targets
        pm = ctx.pages_manager
        for info in pm.get_pages().values():
            sp = str(info.get("script_path", "")).replace("\\", "/")
            if not sp:
                continue
            targets.add(sp)
            targets.add(Path(sp).name)
            targets.add(Path(sp).as_posix())
    except Exception:
        pass
    return targets


def _safe_page_link(page: str, **kwargs) -> bool:
    try:
        st.page_link(page, **kwargs)
        return True
    except st.errors.StreamlitPageNotFoundError:
        return False


st.markdown(streamlit_global_css(), unsafe_allow_html=True)

# ── Datos ─────────────────────────────────────────────────────────────────────
df_raw = load_etapas_data()

fac_abrev_inv = FAC_ABREV_INV
fac_ops = sorted(df_raw["FACULTAD_ABREV"].dropna().unique().tolist()) if "FACULTAD_ABREV" in df_raw.columns else []
mods_ops = sorted(df_raw["MODALIDAD"].dropna().unique().tolist()) if "MODALIDAD" in df_raw.columns else []
pers_ops = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist()) if "PERIODO DE IMPLEMENTACIÓN" in df_raw.columns else []
niveles_ops = [n for n in ["Pregrado", "Posgrado"] if n in df_raw.get("NIVEL_HOMOLOGADO", pd.Series(dtype=str)).values]

def _esc(s):
    return html_lib.escape(str(s) if s is not None else "—")


def _p_esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _etapa_repr_color(etapa: str | None = None, *, general: bool = False) -> str:
    if general:
        return BRAND_PRIMARY
    return ETAPA_HEADER_CLR.get(etapa or "", BRAND_PRIMARY)


# ══════════════════════════════════════════════════════════════════════════════
# NUEVOS COMPONENTES - RESUMEN EJECUTIVO
# ══════════════════════════════════════════════════════════════════════════════

def _arc(pct, color, r=22, sz=56):
    circ = 2 * 3.14159 * r
    dash = circ * min(pct, 100) / 100
    gap = circ - dash
    c = sz // 2
    return (
        f'<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">'
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="rgba(15,56,90,0.10)" stroke-width="5"/>'
        f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{color}" stroke-width="5"'
        f' stroke-dasharray="{dash:.2f} {gap:.2f}" stroke-linecap="round"'
        f' transform="rotate(-90 {c} {c})"/>'
        f'</svg>'
    )


def _kpi_card(label, val, sub, color, pct_bar=None, icon="◈"):
    pct_val = min(pct_bar * 100, 100) if pct_bar is not None else 0
    return (
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);'
        f'border-left:4px solid {color};border-radius:12px;'
        f'padding:14px 16px;display:flex;align-items:center;gap:12px;min-height:84px;'
        f'box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="flex-shrink:0">{_arc(pct_val, color)}</div>'
        f'<div style="flex:1;min-width:0">'
        f'<div style="font-size:10px;color:#6a8a9e;text-transform:uppercase;'
        f'letter-spacing:.5px;margin-bottom:3px">{label}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{color};line-height:1.1">{val}</div>'
        f'<div style="font-size:10px;color:#8aabb0;margin-top:2px">{sub}</div>'
        f'</div></div>'
    )


def _render_kpis(df: pd.DataFrame):
    n = len(df)
    avg_general = round(df["avance_general_vact"].mean(), 1) if n > 0 else 0
    presencial = int((df["MODALIDAD"] == "Presencial").sum()) if n > 0 else 0
    virtual = int((df["MODALIDAD"] == "Virtual").sum()) if n > 0 else 0
    hibrido = int((df["MODALIDAD"] == "Híbrido").sum()) if n > 0 else 0
    pct_presencial = round(presencial / n * 100, 1) if n > 0 else 0
    pct_virtual = round(virtual / n * 100, 1) if n > 0 else 0
    pct_hibrido = round(hibrido / n * 100, 1) if n > 0 else 0

    kpis = [
        ("Total Programas", str(n), "Programas activos", "#0F385A", 1, phosphor_icon_kpi("books")),
        ("Avance Promedio", f"{avg_general}%", "Avance general", "#059669", avg_general / 100, phosphor_icon_kpi("trend-up")),
        ("Presencial", f"{pct_presencial}%", f"{presencial} programas", "#2980B9", pct_presencial / 100, phosphor_icon_kpi("school")),
        ("Virtual", f"{pct_virtual}%", f"{virtual} programas", "#1FB2DE", pct_virtual / 100, phosphor_icon_kpi("monitor-play")),
        ("Híbrido", f"{pct_hibrido}%", f"{hibrido} programas", "#FBAF17", pct_hibrido / 100, phosphor_icon_kpi("presentation-chart")),
    ]

    cols = st.columns(5)
    for i, (label, val, sub, color, pct_bar, icon) in enumerate(kpis):
        with cols[i]:
            st.markdown(_kpi_card(label, val, sub, color, pct_bar, icon), unsafe_allow_html=True)


def _render_chart_facultad(df: pd.DataFrame):
    if "FACULTAD_ABREV" not in df.columns:
        return
    
    facs = df["FACULTAD_ABREV"].unique()
    colors_map = {"FSCC": "#EC0677", "FIDI": "#1FB2DE", "FNGS": "#A6CE38"}
    max_val = 100
    bar_h = 32
    gap = 12
    svg_w = 480
    svg_h = len(facs) * (bar_h + gap) + 20
    
    bars = ""
    for i, fac in enumerate(sorted(facs)):
        fac_df = df[df["FACULTAD_ABREV"] == fac]
        avg = round(fac_df["avance_general_vact"].mean(), 1) if len(fac_df) > 0 else 0
        width = (avg / max_val) * (svg_w - 80)
        color = colors_map.get(fac, "#6e7681")
        y = i * (bar_h + gap)
        fill_color = "#fff" if avg > 30 else "#1e293b"
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<rect x="0" y="0" width="{svg_w}" height="{bar_h}" rx="6" fill="rgba(0,0,0,0.03)"/>'
            f'<rect x="0" y="0" width="{max(4, width)}" height="{bar_h}" rx="6" fill="{color}" opacity="0.85"/>'
            f'<text x="8" y="{bar_h/2+1}" dominant-baseline="middle" fill="{fill_color}" font-family="Segoe UI,sans-serif" font-size="11" font-weight="600">{fac}</text>'
            f'<text x="{svg_w-8}" y="{bar_h/2+1}" dominant-baseline="middle" text-anchor="end" fill="#475569" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700">{avg}%</text>'
            f'</g>'
        )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Avance por Facultad</div>'
        f'<svg viewBox="0 0 {svg_w} {svg_h}">{bars}</svg>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_chart_etapas(df: pd.DataFrame):
    etapa_colors = {
        "Alistamiento Curricular": "#2980B9",
        "Diseño Curricular": "#1FB2DE",
        "Desarrollo Curricular": "#EC0677",
        "Implementación Curricular": "#A6CE38",
    }
    
    svg_w = 480
    bar_h = 30
    gap = 12
    svg_h = len(ETAPAS_ORDEN) * (bar_h + gap) + 20
    
    bars = ""
    for i, etapa in enumerate(ETAPAS_ORDEN):
        pct_col = ETAPA_PCT_COL.get(etapa)
        avg = round(df[pct_col].mean(), 1) if pct_col and pct_col in df.columns else 0
        width = avg * 3.6
        color = etapa_colors.get(etapa, "#6e7681")
        y = i * (bar_h + gap)
        fill_color = "#fff" if avg > 25 else "#1e293b"
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<rect x="0" y="0" width="{svg_w}" height="{bar_h}" rx="6" fill="rgba(0,0,0,0.03)"/>'
            f'<rect x="0" y="0" width="{max(8, width)}" height="{bar_h}" rx="6" fill="{color}" opacity="0.85"/>'
            f'<text x="6" y="{bar_h/2+1}" dominant-baseline="middle" fill="{fill_color}" font-family="Segoe UI,sans-serif" font-size="11" font-weight="600">{etapa.replace(" Curricular", "")}</text>'
            f'<text x="{svg_w-4}" y="{bar_h/2+1}" dominant-baseline="middle" text-anchor="end" fill="#475569" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700">{avg}%</text>'
            f'</g>'
        )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Avance Consolidado por Etapa</div>'
        f'<svg viewBox="0 0 {svg_w} {svg_h}">{bars}</svg>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_chart_nivel_detalle(df: pd.DataFrame) -> None:
    """Barras horizontales por nivel de formación (columna NIVEL)."""
    if "NIVEL" not in df.columns:
        return
    from utils.poli_theme import NIVEL_CLR, NIVEL_ORDEN

    raw = df["NIVEL"].dropna().astype(str).str.strip()
    raw = raw[raw != ""]
    if len(raw) == 0:
        return
    vc = raw.value_counts()
    items = [(n, int(vc[n])) for n in NIVEL_ORDEN if n in vc.index]
    items += [(n, int(vc[n])) for n in vc.index if n not in NIVEL_ORDEN]
    if not items:
        return
    max_c = max(c for _, c in items)

    rows = ""
    for nivel, count in items:
        color = NIVEL_CLR.get(nivel, "#6e7681")
        pct = (count / max_c * 100) if max_c else 0
        fill_color = "#fff" if pct >= 28 else "#1e293b"
        rows += (
            f'<TAG style="display:flex;align-items:center;gap:12px;margin-bottom:10px">'
            f'<TAG style="flex:1;position:relative;height:26px;background:rgba(15,56,90,0.05);border-radius:6px;overflow:hidden">'
            f'<TAG style="width:{max(5, pct):.1f}%;height:100%;background:{color};border-radius:6px"></TAG>'
            f'<span style="position:absolute;left:10px;top:50%;transform:translateY(-50%);'
            f'font-size:11px;font-weight:600;color:{fill_color}">{nivel}</span>'
            f"</TAG>"
            f'<span style="font-size:12px;font-weight:700;color:#0f172a;min-width:24px;text-align:right">{count}</span>'
            f"</TAG>"
        )
    rows = rows.replace("TAG", "div")

    card = (
        f'<TAG style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;'
        f'box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<TAG style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:2px">'
        f"Distribución por Nivel Académico</TAG>"
        f'<TAG style="font-size:11px;color:#94a3b8;margin-bottom:14px">Programas por nivel de formación</TAG>'
        f"{rows}</TAG>"
    )
    st.markdown(card.replace("TAG", "div"), unsafe_allow_html=True)



def _render_rankings(df: pd.DataFrame):
    # Top programas
    top = df.nlargest(8, "avance_general_vact")
    rank_colors = ["#f59e0b", "#94a3b8", "#d97706"]
    
    top_html = ""
    for i, (_, row) in enumerate(top.iterrows()):
        color = rank_colors[i] if i < 3 else "#94a3b8"
        nombre = row.get("NOMBRE DEL PROGRAMA", "—")[:35]
        fac = row.get("FACULTAD_ABREV", "—")
        mod = row.get("MODALIDAD", "—")
        pct = int(row.get("avance_general_vact", 0))
        
        top_html += (
            f'<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;background:#f8fafc;border-radius:6px;margin-bottom:4px">'
            f'<span style="font-family:Segoe UI,sans-serif;font-size:12px;font-weight:800;width:20px;text-align:center;color:{color}">{i+1}</span>'
            f'<div style="flex:1;min-width:0"><div style="font-size:12px;font-weight:600;color:{TEXT_PRIMARY};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{nombre}</div>'
            f'<div style="font-size:10px;color:{TEXT_MUTED}">{fac} · {mod}</div></div>'
            f'<span style="font-family:Segoe UI,sans-serif;font-size:13px;font-weight:800;color:{color}">{pct}%</span></div>'
        )
    
    # Programas críticos
    criticos = df.nsmallest(8, "avance_general_vact")
    criticos_html = ""
    for i, (_, row) in enumerate(criticos.iterrows()):
        nombre = row.get("NOMBRE DEL PROGRAMA", "—")[:35]
        fac = row.get("FACULTAD_ABREV", "—")
        mod = row.get("MODALIDAD", "—")
        pct = int(row.get("avance_general_vact", 0))
        
        criticos_html += (
            f'<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;background:#fef2f2;border-radius:6px;margin-bottom:4px">'
            f'<span style="font-family:Segoe UI,sans-serif;font-size:12px;font-weight:800;width:20px;text-align:center;color:#dc2626">{i+1}</span>'
            f'<div style="flex:1;min-width:0"><div style="font-size:12px;font-weight:600;color:{TEXT_PRIMARY};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{nombre}</div>'
            f'<div style="font-size:10px;color:{TEXT_MUTED}">{fac} · {mod}</div></div>'
            f'<span style="font-family:Segoe UI,sans-serif;font-size:13px;font-weight:800;color:#dc2626">{pct}%</span></div>'
        )
    
    # Render rankings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
            f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">{phosphor_icon("trophy", size=18)} Top Programas Destacados</div>'
            f'<div style="font-size:11px;color:{TEXT_MUTED};margin-bottom:10px">Mayor avance general</div>'
            f'{top_html}</div>',
            unsafe_allow_html=True,
        )
    
    with col2:
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
            f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">{phosphor_icon("warning-circle", size=18, color="#d97706")} Programas Críticos</div>'
            f'<div style="font-size:11px;color:{TEXT_MUTED};margin-bottom:10px">Avance general menor al 20%</div>'
            f'{criticos_html}</div>',
            unsafe_allow_html=True,
        )


render_f2_sidebar()

render_f2_header("Fase 2 · Panel Ejecutivo")

f2_render_filter_bar(
    df_raw, fac_abrev_inv, mods_ops, fac_ops, pers_ops, niveles_ops, key_prefix="ejecutivo"
)

df, *_ = f2_apply_filters(df_raw, fac_abrev_inv, key_prefix="ejecutivo")
n = len(df)

if n == 0:
    st.warning("No hay programas que coincidan con los filtros seleccionados.")
else:
    # Título sección
    st.markdown(
        f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">{phosphor_icon("chart-bar", size=18)} Resumen Ejecutivo</div>',
        unsafe_allow_html=True,
    )
    
    # KPIs
    _render_kpis(df)
    
    st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)
    
    # Gráficos fila 1: Nivel Académico + Facultad
    col_chart1, col_chart2 = st.columns([1, 1])
    with col_chart1:
        _render_chart_nivel_detalle(df)
    with col_chart2:
        _render_chart_facultad(df)
    
    st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)
    
    st.markdown(
        f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin:8px 0 4px">'
        f'{phosphor_icon("chart-bar-horizontal", size=16)} Avance por Etapa</div>'
        f'<div style="font-size:11px;color:{TEXT_MUTED};margin-bottom:8px">'
        "Seleccione una barra del gráfico para ver el detalle de actividades.</div>",
        unsafe_allow_html=True,
    )
    render_etapas_drilldown(df, key_prefix="resumen")

    st.markdown(
        f'<div style="font-size:11px;color:{TEXT_MUTED};margin-top:16px;padding:8px 12px;'
        f'background:#fff;border-radius:8px;border:1px solid rgba(15,56,90,.08)">'
        f"{phosphor_icon('info', size=12)} "
        f"Finalizado · En proceso · Sin iniciar · No aplica — datos: Control Maestro VACT</div>",
        unsafe_allow_html=True,
    )