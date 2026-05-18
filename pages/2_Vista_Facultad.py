"""
pages/2_Vista_Facultad.py — Fase 2: Vista por Facultad
Análisis comparativo entre facultades
"""

from pathlib import Path

import html as html_lib

import pandas as pd
import streamlit as st

from utils.data_loader_vact import (
    ETAPAS_ORDEN,
    ETAPA_PCT_COL,
    FAC_ABREV_INV,
    _ensure_activities_meta,
    apply_filters_vact,
    load_etapas_data,
)
from utils.poli_theme import (
    BRAND_PRIMARY,
    BRAND_SECONDARY,
    BRAND_ACCENT,
    BRAND_HIGHLIGHT,
    TEXT_PRIMARY,
    TEXT_MUTED,
    TEXT_LIGHT,
    TEXT_SUBTLE,
    streamlit_global_css,
    FACULTAD_CLR,
    ETAPA_CLR,
    MODALIDAD_CLR,
    phosphor_icon,
    phosphor_icon_kpi,
    phosphor_icon_nav,
)

st.set_page_config(
    page_title="Vista por Facultad · Fase 2 · POLI",
    page_icon="buildings",
    layout="wide",
    initial_sidebar_state="expanded",
)


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

_use_pills = hasattr(st, "pills")
_LBL = 'style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;letter-spacing:.4px;white-space:nowrap"'


def _clear_filters():
    st.session_state["flt_mod"] = []
    st.session_state["flt_fac"] = []
    st.session_state["flt_per"] = []
    st.session_state["flt_nivel"] = []


def _apply_current_filters():
    sel_mod = list(st.session_state.get("flt_mod") or [])
    sel_fac = list(st.session_state.get("flt_fac") or [])
    sel_per = list(st.session_state.get("flt_per") or [])
    sel_nivel = list(st.session_state.get("flt_nivel") or [])
    facultad_f = [fac_abrev_inv.get(f, f) for f in sel_fac]
    df = apply_filters_vact(df_raw.copy(), sel_mod, facultad_f, sel_per, sel_nivel)
    return df, sel_mod, sel_fac, sel_per, sel_nivel


def _render_filter_bar(key_prefix: str, show_count: bool = True):
    with st.container():
        lb1, in1, sp, lb2, in2, btn = st.columns([0.55, 2.2, 0.05, 0.65, 1.9, 0.65])
        with lb1:
            st.markdown(f'<div {_LBL}>{phosphor_icon("clipboard-text", size=16)} MODALIDAD</div>', unsafe_allow_html=True)
        with in1:
            if _use_pills:
                st.pills("mod", mods_ops, selection_mode="multi", key="flt_mod", label_visibility="collapsed")
            else:
                st.multiselect("mod", mods_ops, key="flt_mod", label_visibility="collapsed", placeholder="Todas")
        with lb2:
            st.markdown(f'<div {_LBL}>{phosphor_icon("buildings", size=16)} FACULTAD</div>', unsafe_allow_html=True)
        with in2:
            if _use_pills:
                st.pills("fac", fac_ops, selection_mode="multi", key="flt_fac", label_visibility="collapsed")
            else:
                st.multiselect("fac", fac_ops, key="flt_fac", label_visibility="collapsed", placeholder="Todas")
        with btn:
            st.button("✕ LIMPIAR", on_click=_clear_filters, type="primary", key=f"{key_prefix}_clear")

        lb3, in3, sp2, lbn, inn, cnt = st.columns([0.55, 2.2, 0.05, 0.65, 1.9, 0.65])
        with lb3:
            st.markdown(f'<div {_LBL}>📅 PERÍODO</div>', unsafe_allow_html=True)
        with in3:
            if _use_pills:
                st.pills("per", pers_ops, selection_mode="multi", key="flt_per", label_visibility="collapsed")
            else:
                st.multiselect("per", pers_ops, key="flt_per", label_visibility="collapsed", placeholder="Todos")
        with lbn:
            st.markdown(f'<div {_LBL}>🎓 NIVEL</div>', unsafe_allow_html=True)
        with inn:
            if _use_pills:
                st.pills("nivel", niveles_ops, selection_mode="multi", key="flt_nivel", label_visibility="collapsed")
            else:
                st.multiselect("nivel", niveles_ops, key="flt_nivel", label_visibility="collapsed", placeholder="Todos")
        if show_count:
            df_tmp, *_ = _apply_current_filters()
            with cnt:
                st.markdown(
                    f'<div style="padding-top:9px;font-size:12px;color:{TEXT_MUTED};text-align:right">'
                    f'Mostrando <b style="color:{TEXT_PRIMARY}">{len(df_tmp)}</b> de '
                    f'<b style="color:{TEXT_PRIMARY}">{len(df_raw)}</b></div>',
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════════════════════════════════
# COMPONENTES DE VISTA POR FACULTAD
# ══════════════════════════════════════════════════════════════════════════════════════

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


def _render_kpis_facultad(df_fac: pd.DataFrame, fac_name: str):
    n = len(df_fac)
    avg = round(df_fac["avance_general_vact"].mean(), 1) if n > 0 else 0
    avanzados = int((df_fac["avance_general_vact"] >= 80).sum()) if n > 0 else 0
    criticos = int((df_fac["avance_general_vact"] < 20).sum()) if n > 0 else 0
    
    color = FACULTAD_CLR.get(fac_name, "#6e7681")
    
    kpis = [
        ("Programas", str(n), color),
        ("Avance Promedio", f"{avg}%", color),
        ("Avanzados (≥80%)", str(avanzados), "#059669"),
        ("Críticos (<20%)", str(criticos), "#dc2626"),
    ]
    
    cols = st.columns(4)
    for i, (label, val, kpi_color) in enumerate(kpis):
        with cols[i]:
            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);'
                f'border-left:4px solid {kpi_color};border-radius:12px;'
                f'padding:12px 14px;box-shadow:0 2px 8px rgba(15,56,90,0.07);min-height:70px">'
                f'<div style="font-size:9px;color:#6a8a9e;text-transform:uppercase;letter-spacing:.5px">{label}</div>'
                f'<div style="font-size:20px;font-weight:700;color:{kpi_color};margin-top:4px">{val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_chart_programas_facultad(df_fac: pd.DataFrame, fac_name: str):
    color = FACULTAD_CLR.get(fac_name, "#6e7681")
    sorted_df = df_fac.nlargest(15, "avance_general_vact")
    
    svg_w = 460
    bar_h = 18
    gap = 5
    svg_h = len(sorted_df) * (bar_h + gap) + 10
    
    bars = ""
    for i, (_, row) in enumerate(sorted_df.iterrows()):
        pct = row.get("avance_general_vact", 0)
        width = pct * 4.4
        nombre = row.get("NOMBRE DEL PROGRAMA", "—")[:40]
        y = i * (bar_h + gap)
        
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<rect x="0" y="0" width="440" height="{bar_h}" rx="4" fill="rgba(0,0,0,0.03)"/>'
            f'<rect x="0" y="0" width="{max(3, width)}" height="{bar_h}" rx="4" fill="{color}" opacity="0.82"/>'
            f'<text x="4" y="{bar_h/2+1}" dominant-baseline="middle" fill="{("#fff" if pct > 15 else "#1e293b")}" font-family="Segoe UI,sans-serif" font-size="9.5" font-weight="500">{nombre}</text>'
            f'</g>'
        )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Avance por Programa</div>'
        f'<div style="max-height:340px;overflow-y:auto"><svg viewBox="0 0 {svg_w} {svg_h}">{bars}</svg></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_chart_etapas_facultad(df_fac: pd.DataFrame):
    etapa_colors = {
        "Alistamiento Curricular": "#2980B9",
        "Diseño Curricular": "#1FB2DE",
        "Desarrollo Curricular": "#EC0677",
        "Implementación Curricular": "#A6CE38",
    }
    
    svg_w = 400
    bar_h = 30
    gap = 10
    svg_h = len(ETAPAS_ORDEN) * (bar_h + gap) + 10
    
    bars = ""
    for i, etapa in enumerate(ETAPAS_ORDEN):
        pct_col = ETAPA_PCT_COL.get(etapa)
        avg = round(df_fac[pct_col].mean(), 1) if pct_col and pct_col in df_fac.columns else 0
        width = avg * 3.6
        color = etapa_colors.get(etapa, "#6e7681")
        y = i * (bar_h + gap)
        
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<rect x="0" y="0" width="380" height="{bar_h}" rx="6" fill="rgba(0,0,0,0.03)"/>'
            f'<rect x="0" y="0" width="{max(4, width)}" height="{bar_h}" rx="6" fill="{color}" opacity="0.85"/>'
            f'<text x="6" y="{bar_h/2+1}" dominant-baseline="middle" fill="{("#fff" if avg > 20 else "#1e293b")}" font-family="Segoe UI,sans-serif" font-size="10.5" font-weight="600">{etapa.replace(" Curricular", "")}</text>'
            f'<text x="376" y="{bar_h/2+1}" dominant-baseline="middle" text-anchor="end" fill="#475569" font-family="Segoe UI,sans-serif" font-size="10.5" font-weight="700">{avg}%</text>'
            f'</g>'
        )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Comparativa de Etapas</div>'
        f'<svg viewBox="0 0 {svg_w} {svg_h}">{bars}</svg>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_chart_modalidad_facultad(df_fac: pd.DataFrame):
    if "MODALIDAD" not in df_fac.columns:
        return
    
    mods = df_fac["MODALIDAD"].value_counts()
    colors_map = {"Virtual": "#1FB2DE", "Presencial": "#A6CE38", "Híbrido": "#FBAF17"}
    total = mods.sum()
    
    if total == 0:
        return
    
    # Donut simple
    grad = ""
    current = 0
    for mod, count in mods.items():
        color = colors_map.get(mod, "#6e7681")
        pct = count / total * 100
        grad += f"{color} {current}% {current + pct}%,"
        current += pct
    grad = grad.rstrip(",")
    
    legend = ""
    for mod, count in mods.items():
        color = colors_map.get(mod, "#6e7681")
        pct = round(count / total * 100)
        legend += (
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
            f'<div style="width:10px;height:10px;border-radius:3px;background:{color}"></div>'
            f'<span style="font-size:11px;font-weight:600;flex:1">{mod}</span>'
            f'<span style="font-size:11px;font-weight:700">{count} ({pct}%)</span>'
            f'</div>'
        )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Distribución por Modalidad</div>'
        f'<div style="display:flex;align-items:center;gap:16px">'
        f'<div style="width:120px;height:120px;border-radius:50%;background:conic-gradient({grad});display:flex;align-items:center;justify-content:center">'
        f'<div style="width:70px;height:70px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center">'
        f'<div style="text-align:center"><div style="font-size:18px;font-weight:800;color:{TEXT_PRIMARY}">{total}</div><div style="font-size:8px;color:#94a3b8">Programas</div></div>'
        f'</div></div>'
        f'<div style="flex:1">{legend}</div></div></div>',
        unsafe_allow_html=True,
    )


def _render_heatmap_facultad(df_fac: pd.DataFrame):
    sorted_df = df_fac.nlargest(15, "avance_general_vact")
    
    etapa_colors = {
        "Alistamiento Curricular": "#2980B9",
        "Diseño Curricular": "#1FB2DE",
        "Desarrollo Curricular": "#EC0677",
        "Implementación Curricular": "#A6CE38",
    }
    
    def get_color(val):
        if val >= 80:
            return "#059669"
        if val >= 50:
            return "#2563eb"
        if val >= 30:
            return "#d97706"
        return "#dc2626"
    
    header = (
        f'<div style="display:grid;grid-template-columns:180px repeat(4,1fr);gap:4px;margin-bottom:6px">'
        f'<div style="font-size:10px;color:#94a3b8;font-weight:700">PROGRAMA</div>'
        f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-align:center">Alist.</div>'
        f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-align:center">Diseño</div>'
        f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-align:center">Desarr.</div>'
        f'<div style="font-size:10px;color:#94a3b8;font-weight:700;text-align:center">Impl.</div>'
        f'</div>'
    )
    
    rows = ""
    for _, row in sorted_df.iterrows():
        nombre = row.get("NOMBRE DEL PROGRAMA", "—")[:22] + ".."
        alist = int(row.get("pct_alistamiento", 0))
        diseno = int(row.get("pct_diseno", 0))
        desarr = int(row.get("pct_desarrollo", 0))
        impl = int(row.get("pct_implementacion", 0))
        
        cells = ""
        for val in [alist, diseno, desarr, impl]:
            bg = get_color(val)
            cells += f'<div style="background:{bg};opacity:0.8;height:28px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff">{val}%</div>'
        
        rows += (
            f'<div style="display:grid;grid-template-columns:180px repeat(4,1fr);gap:4px;margin-bottom:4px">'
            f'<div style="font-size:11px;font-weight:600;color:#0f172a;display:flex;align-items:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="{row.get("NOMBRE DEL PROGRAMA", "")}">{nombre}</div>'
            f'{cells}'
            f'</div>'
        )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Heatmap — Avance por Programa y Etapa</div>'
        f'{header}{rows}</div>',
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:18px 6px;text-align:center">'
        '<div style="font-size:16px;font-weight:700;color:#FFFFFF">Reforma Curricular</div>'
        '<div style="font-size:11px;color:rgba(255,255,255,.6);margin-top:4px">Fase 2 · Etapas</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:10px 0;border-color:rgba(255,255,255,.2)'>", unsafe_allow_html=True)
    
    _safe_page_link("app_act.py", label=f"{phosphor_icon_nav('chart-bar')} Resumen Ejecutivo", icon="chart-bar")
    _safe_page_link("pages/1_Alertas_Riesgos.py", label=f"{phosphor_icon_nav('warning')} Alertas y Riesgos", icon="warning")
    _safe_page_link("pages/2_Vista_Facultad.py", label=f"{phosphor_icon_nav('buildings')} Vista por Facultad", icon="buildings")
    _safe_page_link("pages/3_Detalle_Etapa.py", label=f"{phosphor_icon_nav('clipboard-text')} Detalle por Etapa", icon="clipboard-text")
    _safe_page_link("pages/4_Por_Programa.py", label=f"{phosphor_icon_nav('student')} Por Programa", icon="student")
    
    st.markdown("<hr style='margin:10px 0'>", unsafe_allow_html=True)
    st.markdown('<div style="padding:12px;font-size:10px;color:rgba(255,255,255,.4);text-align:center">POLI · VACT · 2025–2026</div>', unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="'
    f"background:linear-gradient(135deg,{BRAND_PRIMARY} 0%,{BRAND_SECONDARY} 50%,{BRAND_ACCENT} 100%);"
    f'padding:18px 24px 14px;border-radius:0 0 12px 12px;border-bottom:3px solid {BRAND_HIGHLIGHT};">'
    '<div style="font-size:21px;font-weight:700;color:#FFFFFF">Reforma Curricular de Programas Académicos Poli</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">Fase 2 · Vista Comparativa por Facultad</div></div>',
    unsafe_allow_html=True,
)

# Filtros
_render_filter_bar("global", show_count=True)

# Contenido
df, *_ = _apply_current_filters()

if len(df) == 0:
    st.warning("No hay programas que coincidan con los filtros seleccionados.")
else:
    st.markdown(f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">{phosphor_icon("buildings", size=22)} Vista por Facultad</div>', unsafe_allow_html=True)
    
    # Tabs de facultades
    facs = sorted(df["FACULTAD_ABREV"].unique().tolist()) if "FACULTAD_ABREV" in df.columns else []
    
    if not facs:
        st.warning("No hay facultades en los datos.")
    else:
        tabs = st.tabs(facs)
        
        for i, fac in enumerate(facs):
            with tabs[i]:
                df_fac = df[df["FACULTAD_ABREV"] == fac]
                
                # KPIs
                _render_kpis_facultad(df_fac, fac)
                
                st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)
                
                # Gráficos fila 1
                col1, col2 = st.columns([3, 2])
                with col1:
                    _render_chart_programas_facultad(df_fac, fac)
                with col2:
                    _render_chart_modalidad_facultad(df_fac)
                
                st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)
                
                # Gráficos fila 2
                col3, col4 = st.columns([2, 3])
                with col3:
                    _render_chart_etapas_facultad(df_fac)
                with col4:
                    _render_heatmap_facultad(df_fac)