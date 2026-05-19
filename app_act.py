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


def _render_chart_nivel(df: pd.DataFrame):
    if "NIVEL_HOMOLOGADO" not in df.columns:
        return
    
    niveles = df["NIVEL_HOMOLOGADO"].value_counts()
    colors = ["#2563eb", "#7c3aed", "#059669", "#d97706"]
    
    if len(niveles) == 0:
        return
    
    max_count = niveles.max()
    
    bars = ""
    for i, (nivel, count) in enumerate(niveles.items()):
        if not nivel:
            continue
        width = (count / max_count) * 400
        color = colors[i % len(colors)]
        y = i * 28
        fill_color = "#fff" if count/max_count > 0.25 else "#1e293b"
        
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<rect x="0" y="0" width="460" height="24" rx="5" fill="rgba(0,0,0,0.03)"/>'
            f'<rect x="0" y="0" width="{max(6, width)}" height="24" rx="5" fill="{color}" opacity="0.85"/>'
            f'<text x="6" y="13" dominant-baseline="middle" fill="{fill_color}" font-family="Segoe UI,sans-serif" font-size="11" font-weight="600">{nivel}</text>'
            f'<text x="455" y="13" dominant-baseline="middle" text-anchor="end" fill="#475569" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700">{count}</text>'
            f'</g>'
        )
    
    svg_h = len(niveles) * 28 + 10
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Distribución por Nivel Académico</div>'
        f'<svg viewBox="0 0 480 {svg_h}">{bars}</svg>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_chart_nivel_anillos(df: pd.DataFrame):
    if "NIVEL_HOMOLOGADO" not in df.columns:
        return
    
    import math
    
    niveles = df["NIVEL_HOMOLOGADO"].value_counts()
    
    if len(niveles) == 0:
        return
    
    total = niveles.sum()
    
    pregrado_count = int(niveles.get("Pregrado", 0))
    posgrado_count = int(niveles.get("Posgrado", 0))
    if pregrado_count + posgrado_count == 0:
        pregrado_keys = ["Técnico", "Tecnológico", "Profesional"]
        posgrado_keys = ["Especialización", "Maestría", "Doctorado"]
        pregrado_count = sum(int(niveles.get(k, 0)) for k in pregrado_keys)
        posgrado_count = sum(int(niveles.get(k, 0)) for k in posgrado_keys)
    
    pregrado_pct = round(pregrado_count / total * 100, 1) if total > 0 else 0
    posgrado_pct = round(posgrado_count / total * 100, 1) if total > 0 else 0
    
    # Generar segmentos solo para Pregrado y Posgrado
    segments = ""
    labels = ""
    current_angle = 0
    
    datos = [
        ("Pregrado", pregrado_count, pregrado_pct, "#2563eb"),
        ("Posgrado", posgrado_count, posgrado_pct, "#7c3aed"),
    ]
    
    for nombre, count, pct, color in datos:
        if count == 0:
            continue
        angle = (count / total) * 360
        
        radius = 55
        circumference = 2 * math.pi * radius
        dash_length = (angle / 360) * circumference
        dash_gap = circumference - dash_length
        
        segments += f'<circle cx="100" cy="100" r="{radius}" fill="none" stroke="{color}" stroke-width="22" stroke-dasharray="{dash_length} {dash_gap}" transform="rotate({-90 + current_angle} 100 100)"/>'
        
        if angle > 12:
            mid_angle = current_angle + (angle / 2)
            mid_rad = (mid_angle - 90) * math.pi / 180
            label_x = 100 + 38 * math.cos(mid_rad)
            label_y = 100 + 38 * math.sin(mid_rad)
            text_color = "#ffffff" if angle > 40 else "#1e293b"
            labels += f'<text x="{label_x}" y="{label_y}" text-anchor="middle" dominant-baseline="middle" fill="{text_color}" font-family="Segoe UI,sans-serif" font-size="10" font-weight="700">{pct}%</text>'
        
        current_angle += angle
    
    legend = ""
    legend += (
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
        f'<div style="width:12px;height:12px;border-radius:3px;background:#2563eb;flex-shrink:0"></div>'
        f'<span style="font-size:12px;color:#475569;font-weight:600">Pregrado</span>'
        f'<span style="margin-left:auto;font-size:12px;font-weight:700;color:#0f172a">{pregrado_count} ({pregrado_pct}%)</span>'
        f'</div>'
    )
    legend += (
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
        f'<div style="width:12px;height:12px;border-radius:3px;background:#7c3aed;flex-shrink:0"></div>'
        f'<span style="font-size:12px;color:#475569;font-weight:600">Posgrado</span>'
        f'<span style="margin-left:auto;font-size:12px;font-weight:700;color:#0f172a">{posgrado_count} ({posgrado_pct}%)</span>'
        f'</div>'
    )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:16px">Distribución por Nivel Académico</div>'
        f'<div style="display:flex;align-items:center;gap:20px">'
        f'<div style="width:200px;height:200px;position:relative;flex-shrink:0">'
        f'<svg viewBox="0 0 200 200" style="transform:rotate(-90deg)">{segments}</svg>'
        f'<div style="position:absolute;top:0;left:0;width:100%;height:100%;display:flex;align-items:center;justify-content:center;transform:rotate(90deg)">{labels}</div>'
        f'<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;background:#fff;width:70px;height:70px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 2px 4px rgba(0,0,0,0.1)">'
        f'<div style="font-size:22px;font-weight:800;color:{TEXT_PRIMARY}">{total}</div>'
        f'<div style="font-size:9px;color:#94a3b8">Programas</div>'
        f'</div></div>'
        f'<div style="flex:1;padding-left:10px">{legend}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def _render_chart_etapas_interactivo(df: pd.DataFrame):
    if "pct_alistamiento" not in df.columns:
        return
    
    etapas = ["Alistamiento Curricular", "Diseño Curricular", "Desarrollo Curricular", "Implementación Curricular"]
    pct_cols = ["pct_alistamiento", "pct_diseno", "pct_desarrollo", "pct_implementacion"]
    etapa_colors = {"Alistamiento Curricular": "#2980B9", "Diseño Curricular": "#1FB2DE", "Desarrollo Curricular": "#EC0677", "Implementación Curricular": "#A6CE38"}
    
    promedios = []
    for col in pct_cols:
        if col in df.columns:
            promedios.append(round(df[col].mean(), 1))
        else:
            promedios.append(0)
    
    # Toggle entre Drill Down y Stacked
    modo_viz = st.segmented_control(
        "Modo de visualización",
        options=["Drill Down", "Stacked"],
        default="Drill Down",
        key="modo_etapas_viz",
        label_visibility="collapsed"
    )
    
    if modo_viz == "Drill Down":
        _render_bar_drill_down(df, etapas, promedios, etapa_colors)
    else:
        _render_bar_stacked(df, etapas, promedios, etapa_colors)


def _render_bar_drill_down(df, etapas, promedios, etapa_colors):
    # Inicializar session state para etapa activa
    if "etapa_activa" not in st.session_state:
        st.session_state.etapa_activa = "Resumen"
    
    col_graf, col_panel = st.columns([2, 1])
    
    with col_graf:
        bars = ""
        for i, etapa in enumerate(etapas):
            y = i * 50
            avg = promedios[i]
            color = etapa_colors.get(etapa, "#6e7681")
            bar_w = avg
            
            es_activa = st.session_state.etapa_activa == etapa
            border_style = f"border:2px solid {color}" if es_activa else ""
            
            bars += (
                f'<g transform="translate(0,{y})" style="cursor:pointer" onclick="window.parent.postMessage({{type:\'streamlit:setComponentValue\',value:\'{etapa}\'}},\'*\')">'
                f'<text x="0" y="18" font-family="Segoe UI,sans-serif" font-size="12" font-weight="600" fill="#0f172a">{etapa}</text>'
                f'<rect x="130" y="6" width="200" height="14" rx="4" fill="#e2e8f0"/>'
                f'<rect x="130" y="6" width="{bar_w * 2}" height="14" rx="4" fill="{color}"/>'
                f'<text x="340" y="18" font-family="Segoe UI,sans-serif" font-size="12" font-weight="700" fill="#0f172a">{avg}%</text>'
                f'</g>'
            )
        
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
            f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Avance por Etapa - Drill Down</div>'
            f'<div style="font-size:10px;color:#64748b;margin-bottom:12px">Click en una barra para ver el detalle</div>'
            f'<svg viewBox="0 0 380 220">{bars}</svg>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        # Botones para cambiar etapa activa (alternativa al click)
        st.caption("Seleccionar etapa:")
        btn_cols = st.columns(4)
        for i, etapa in enumerate(etapas):
            with btn_cols[i]:
                if st.button(etapa[:10], key=f"btn_etapa_{i}", use_container_width=True):
                    st.session_state.etapa_activa = etapa
    
    with col_panel:
        etapa_sel = st.session_state.etapa_activa
        if etapa_sel == "Resumen":
            idx = -1
        else:
            idx = etapas.index(etapa_sel)
        
        color_etapa = etapa_colors.get(etapa_sel, "#6e7681") if etapa_sel != "Resumen" else "#6e7681"
        
        # Calcular estados
        done = inprog = nostart = 0
        if idx >= 0:
            for i in range(20):
                cl_col = f"cl_act_{i}"
                if cl_col in df.columns:
                    fase_col = f"act_phase_{i}"
                    if fase_col in df.columns:
                        fase_vals = df[fase_col].unique()
                        if any(etapas[idx] in str(f) for f in fase_vals):
                            done += (df[cl_col] == "done").sum()
                            inprog += (df[cl_col] == "inprog").sum()
                            nostart += (df[cl_col] == "nostart").sum()
        
        pct_actual = promedios[idx] if idx >= 0 else sum(promedios) / len(promedios)
        
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:14px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
            f'<div style="font-size:13px;font-weight:700;color:{color_etapa};margin-bottom:12px">{"RESUMEN GENERAL" if etapa_sel=="Resumen" else etapa_sel}</div>'
            f'<div style="font-size:28px;font-weight:800;color:{color_etapa};margin-bottom:8px">{pct_actual}%</div>'
            f'<div style="height:8px;background:#e2e8f0;border-radius:4px;margin-bottom:12px">'
            f'<div style="height:100%;width:{pct_actual}%;background:{color_etapa};border-radius:4px"></div>'
            f'</div>'
            f'<div style="font-size:11px;margin-bottom:8px">'
            f'{phosphor_icon("check-circle", color="#22c55e", size=14)} {done} · '
            f'{phosphor_icon("arrows-clockwise", color="#0ea5e9", size=14)} {inprog} · '
            f'{phosphor_icon("circle", color="#94a3b8", size=14)} {nostart}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
        if etapa_sel != "Resumen" and idx >= 0:
            acts = []
            for i in range(20):
                fase_col = f"act_phase_{i}"
                name_col = f"act_name_{i}"
                cl_col = f"cl_act_{i}"
                
                if fase_col in df.columns and name_col in df.columns:
                    fase_vals = df[fase_col].unique()
                    if any(etapa_sel in str(f) for f in fase_vals):
                        acts.append({"name": name_col, "cl": cl_col})
            
            if acts:
                st.markdown(f'<div style="font-size:11px;font-weight:600;color:#64748b;margin-top:12px;margin-bottom:8px">ACTIVIDADES:</div>', unsafe_allow_html=True)
                
                for act in acts[:6]:
                    if act["cl"] not in df.columns:
                        continue
                    done_c = (df[act["cl"]] == "done").sum()
                    inprog_c = (df[act["cl"]] == "inprog").sum()
                    nostart_c = (df[act["cl"]] == "nostart").sum()
                    
                    max_c = max(done_c, inprog_c, nostart_c)
                    if max_c == done_c and done_c > 0:
                        icon, color = phosphor_icon("check-circle", color="#22c55e", size=12), "#22c55e"
                    elif max_c == inprog_c and inprog_c > 0:
                        icon, color = phosphor_icon("arrows-clockwise", color="#0ea5e9", size=12), "#0ea5e9"
                    else:
                        icon, color = phosphor_icon("circle", color="#94a3b8", size=12), "#94a3b8"
                    
                    nombre = df[act["name"]].iloc[0] if len(df) > 0 else "Actividad"
                    nombre_corto = nombre[:25] + "..." if len(nombre) > 25 else nombre
                    
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:6px;padding:6px 0;border-bottom:1px solid #f1f5f9;font-size:10px">'
                        f'<span style="color:{color}">{icon}</span>'
                        f'<span style="color:#475569">{nombre_corto}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


def _render_bar_stacked(df, etapas, promedios, etapa_colors):
    if "etapa_expandida" not in st.session_state:
        st.session_state.etapa_expandida = None
    
    # Generar barras con botón de expansión
    bars = ""
    for i, etapa in enumerate(etapas):
        y = i * 70
        avg = promedios[i]
        color = etapa_colors.get(etapa, "#6e7681")
        es_expandida = st.session_state.etapa_expandida == etapa
        
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<text x="0" y="16" font-family="Segoe UI,sans-serif" font-size="11" font-weight="600" fill="#0f172a">{etapa}</text>'
            f'<text x="0" y="32" font-family="Segoe UI,sans-serif" font-size="10" fill="#64748b">Presiona "Ver" para detalle</text>'
            f'<rect x="100" y="4" width="180" height="12" rx="3" fill="#e2e8f0"/>'
            f'<rect x="100" y="4" width="{avg * 1.8}" height="12" rx="3" fill="{color}"/>'
            f'<text x="290" y="14" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#0f172a">{avg}%</text>'
            f'</g>'
        )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:16px">Avance por Etapa - Stacked</div>'
        f'<svg viewBox="0 0 320 300">{bars}</svg>'
        f'</div>',
        unsafe_allow_html=True,
    )
    
    # Botones para cada etapa
    st.caption("Ver detalle de etapa:")
    btn_cols = st.columns(4)
    for i, etapa in enumerate(etapas):
        with btn_cols[i]:
            if st.button(f"Ver {i+1}", key=f"btn_exp_{i}", use_container_width=True):
                if st.session_state.etapa_expandida == etapa:
                    st.session_state.etapa_expandida = None
                else:
                    st.session_state.etapa_expandida = etapa
    
    # Mostrar detalle si hay una etapa expandida
    if st.session_state.etapa_expandida:
        idx = etapas.index(st.session_state.etapa_expandida)
        etapa_sel = st.session_state.etapa_expandida
        
        acts = []
        for i in range(20):
            fase_col = f"act_phase_{i}"
            name_col = f"act_name_{i}"
            cl_col = f"cl_act_{i}"
            
            if fase_col in df.columns and name_col in df.columns:
                fase_vals = df[fase_col].unique()
                if any(etapa_sel in str(f) for f in fase_vals):
                    acts.append({"name": name_col, "cl": cl_col})
        
        if acts:
            items = ""
            for act in acts:
                if act["cl"] not in df.columns:
                    continue
                
                done_c = (df[act["cl"]] == "done").sum()
                inprog_c = (df[act["cl"]] == "inprog").sum()
                nostart_c = (df[act["cl"]] == "nostart").sum()
                
                max_c = max(done_c, inprog_c, nostart_c)
                if max_c == done_c and done_c > 0:
                    estado_label, estado_color, estado_icon = "Finalizado", "#22c55e", phosphor_icon("check-circle", color="#22c55e", size=14)
                elif max_c == inprog_c and inprog_c > 0:
                    estado_label, estado_color, estado_icon = "En Proceso", "#0ea5e9", phosphor_icon("arrows-clockwise", color="#0ea5e9", size=14)
                else:
                    estado_label, estado_color, estado_icon = "Sin Iniciar", "#94a3b8", phosphor_icon("circle", color="#94a3b8", size=14)
                
                nombre = df[act["name"]].iloc[0] if len(df) > 0 else "Actividad"
                
                items += (
                    f'<div style="display:flex;align-items:center;gap:10px;padding:10px;border-bottom:1px solid #e2e8f0">'
                    f'<div style="width:24px;height:24px;border-radius:50%;background:{estado_color}20;display:flex;align-items:center;justify-content:center;color:{estado_color};font-size:12px">{estado_icon}</div>'
                    f'<div style="flex:1"><div style="font-size:12px;font-weight:600;color:#0f172a">{nombre}</div>'
                    f'<div style="font-size:10px;color:#64748b">F:{done_c} I:{inprog_c} N:{nostart_c}</div></div>'
                    f'<div style="background:{estado_color};color:#fff;padding:3px 8px;border-radius:10px;font-size:9px;font-weight:600">{estado_label}</div>'
                    f'</div>'
                )
            
            color_etapa = etapa_colors.get(etapa_sel, "#6e7681")
            st.markdown(
                f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:14px;box-shadow:0 2px 8px rgba(15,56,90,0.07);margin-top:16px">'
                f'<div style="font-size:13px;font-weight:700;color:{color_etapa};margin-bottom:12px">Detalle: {etapa_sel} (Promedio: {promedios[idx]}%)</div>'
                f'{items}'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info(f"No hay actividades para {etapa_sel}")


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
    
    # Gráficos fila 1: Nivel Académico (anillos) + Facultad
    col_chart1, col_chart2 = st.columns([1, 1])
    with col_chart1:
        _render_chart_nivel_anillos(df)
    with col_chart2:
        _render_chart_facultad(df)
    
    st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)
    
    st.markdown(
        f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin:8px 0 4px">'
        f'{phosphor_icon("chart-bar-horizontal", size=16)} Avance por Etapa</div>'
        f'<div style="font-size:11px;color:{TEXT_MUTED};margin-bottom:8px">'
        "Seleccione una barra o un botón para ver el detalle de actividades.</div>",
        unsafe_allow_html=True,
    )
    render_etapas_drilldown(df, key_prefix="resumen")

    st.markdown(
        f'<div style="font-size:11px;color:{TEXT_MUTED};margin-top:16px;padding:8px 12px;'
        f'background:#fff;border-radius:8px;border:1px solid rgba(15,56,90,.08)">'
        f"{phosphor_icon('info', size=12)} "
        f"Finalizado · En proceso · Sin iniciar · No aplica — datos: Control Maestro VACT</div>".replace(
            "motion.", ""
        ),
        unsafe_allow_html=True,
    )