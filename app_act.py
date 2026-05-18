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
    apply_filters_vact,
    load_etapas_data,
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
    page_icon="🎓",
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

_use_pills = hasattr(st, "pills")
_LBL = (
    f'style="padding-top:8px;font-size:11px;font-weight:700;color:{TEXT_PRIMARY};'
    f'letter-spacing:.4px;white-space:nowrap"'
)


def _esc(s):
    return html_lib.escape(str(s) if s is not None else "—")


def _p_esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
            st.markdown(f'<div {_LBL}>📋 MODALIDAD</div>', unsafe_allow_html=True)
        with in1:
            if _use_pills:
                st.pills("mod", mods_ops, selection_mode="multi", key="flt_mod", label_visibility="collapsed")
            else:
                st.multiselect("mod", mods_ops, key="flt_mod", label_visibility="collapsed", placeholder="Todas")
        with lb2:
            st.markdown(f'<div {_LBL}>🏛️ FACULTAD</div>', unsafe_allow_html=True)
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
    
    niveles = df["NIVEL_HOMOLOGADO"].value_counts()
    colors = ["#2563eb", "#7c3aed", "#059669", "#d97706", "#dc2626"]
    
    if len(niveles) == 0:
        return
    
    total = niveles.sum()
    
    # Crear gradiente para gráfico de anillos
    gradient_defs = ""
    for i, (nivel, count) in enumerate(niveles.items()):
        color = colors[i % len(colors)]
        gradient_defs += f'<stop offset="0%" stop-color="{color}"/><stop offset="100%" stop-color="{color}"/>'
    
    # Calcular segmentos
    segments = ""
    current_angle = 0
    for i, (nivel, count) in enumerate(niveles.items()):
        if not nivel:
            continue
        pct = count / total * 100
        angle = (count / total) * 360
        color = colors[i % len(colors)]
        
        # Calcular coordenadas del arco
        start_angle = current_angle
        end_angle = current_angle + angle
        
        start_rad = (start_angle - 90) * 3.14159 / 180
        end_rad = (end_angle - 90) * 3.14159 / 180
        
        x1 = 70 + 50 * (1 if angle <= 180 else -1) * abs(1 - (angle > 180))
        x1 = 70 + 50 * (1 if angle <= 180 else 0) if angle <= 180 else 70 + 50 * (-1) if angle > 180 else 70
        
        # Usar path simple para el arco
        large_arc = 1 if angle > 180 else 0
        
        x_start = 70 + 45 * (1 if start_angle <= 180 else -1) if start_angle <= 180 else 70 - 45 * (1 - (start_angle - 180) / 180)
        y_start = 70 + 45 * ((start_angle % 180) / 180) if start_angle <= 90 or start_angle > 270 else 70 - 45 * ((start_angle % 180) / 180)
        
        # Simplificar con stroke-dasharray
        radius = 40
        circumference = 2 * 3.14159 * radius
        dash_length = (angle / 360) * circumference
        dash_gap = circumference - dash_length
        
        segments += f'<circle cx="70" cy="70" r="{radius}" fill="none" stroke="{color}" stroke-width="12" stroke-dasharray="{dash_length} {dash_gap}" transform="rotate({-90 + current_angle} 70 70)"/>'
        current_angle += angle
    
    # Leyenda
    legend = ""
    for i, (nivel, count) in enumerate(niveles.items()):
        if not nivel:
            continue
        pct = round(count / total * 100, 1)
        color = colors[i % len(colors)]
        legend += (
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">'
            f'<div style="width:10px;height:10px;border-radius:3px;background:{color};flex-shrink:0"></div>'
            f'<span style="font-size:11px;color:#475569;font-weight:600">{nivel}</span>'
            f'<span style="margin-left:auto;font-size:11px;font-weight:700;color:#0f172a">{count} ({pct}%)</span>'
            f'</div>'
        )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Distribución por Nivel Académico</div>'
        f'<div style="display:flex;align-items:center;gap:20px">'
        f'<div style="width:140px;height:140px;position:relative">'
        f'<svg viewBox="0 0 140 140" style="transform:rotate(-90deg)">{segments}</svg>'
        f'<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">'
        f'<div style="font-size:20px;font-weight:800;color:{TEXT_PRIMARY}">{total}</div>'
        f'<div style="font-size:9px;color:#94a3b8">Programas</div>'
        f'</div></div>'
        f'<div style="flex:1">{legend}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def _render_chart_etapas_interactivo(df: pd.DataFrame):
    if "pct_alistamiento" not in df.columns:
        return
    
    etapas = ["Alistamiento Curricular", "Diseño Curricular", "Desarrollo Curricular", "Implementación Curricular"]
    pct_cols = ["pct_alistamiento", "pct_diseno", "pct_desarrollo", "pct_implementacion"]
    colors = ["#2980B9", "#1FB2DE", "#EC0677", "#A6CE38"]
    
    # Calcular promedios por etapa
    promedios = []
    for col in pct_cols:
        if col in df.columns:
            promedios.append(round(df[col].mean(), 1))
        else:
            promedios.append(0)
    
    # Calcular进度 por estado
    done_counts = []
    inprog_counts = []
    nostart_counts = []
    
    for etapa in etapas:
        slug = etapa.lower().replace(" curricular", "").replace(" ", "_")
        cl_col = f"cl_act_0"
        
        done = 0
        inprog = 0
        nostart = 0
        
        for i in range(10):
            cl_col = f"cl_act_{i}"
            if cl_col in df.columns:
                fase = df.get(f"act_phase_{i}", pd.Series([""] * len(df)))
                if fase.str.contains(etapa).any():
                    done += (df[cl_col] == "done").sum()
                    inprog += (df[cl_col] == "inprog").sum()
                    nostart += (df[cl_col] == "nostart").sum()
        
        done_counts.append(done)
        inprog_counts.append(inprog)
        nostart_counts.append(nostart)
    
    # Gráfico de barras agrupadas
    bars = ""
    max_val = max(sum(x) for x in zip(done_counts, inprog_counts, nostart_counts)) if done_counts else 1
    
    for i, etapa in enumerate(etapas):
        y = i * 50
        
        done_w = (done_counts[i] / max(max_val, 1)) * 100
        inprog_w = (inprog_counts[i] / max(max_val, 1)) * 100
        nostart_w = (nostart_counts[i] / max(max_val, 1)) * 100
        
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<text x="0" y="18" font-family="Segoe UI,sans-serif" font-size="12" font-weight="600" fill="#0f172a">{etapa}</text>'
            f'<text x="0" y="36" font-family="Segoe UI,sans-serif" font-size="10" fill="#64748b">Avg: {promedios[i]}%</text>'
            f'<rect x="120" y="8" width="{done_w}%" height="10" rx="2" fill="#22c55e"/>'
            f'<rect x="120" y="22" width="{inprog_w}%" height="10" rx="2" fill="#f59e0b"/>'
            f'<rect x="120" y="36" width="{nostart_w}%" height="10" rx="2" fill="#94a3b8"/>'
            f'</g>'
        )
    
    # Leyenda
    legend = (
        f'<div style="display:flex;gap:16px;margin-top:16px;font-size:11px;color:#64748b">'
        f'<div style="display:flex;align-items:center;gap:6px"><div style="width:10px;height:10px;background:#22c55e;border-radius:2px"></div>Finalizado</div>'
        f'<div style="display:flex;align-items:center;gap:6px"><div style="width:10px;height:10px;background:#f59e0b;border-radius:2px"></div>En Proceso</div>'
        f'<div style="display:flex;align-items:center;gap:6px"><div style="width:10px;height:10px;background:#94a3b8;border-radius:2px"></div>Sin Iniciar</div>'
        f'</div>'
    )
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:16px">Avance Consolidado por Etapa</div>'
        f'<svg viewBox="0 0 500 220">{bars}</svg>'
        f'{legend}'
        f'</div>',
        unsafe_allow_html=True,
    )


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


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:18px 6px;text-align:center">'
        '<div style="font-size:16px;font-weight:700;color:#FFFFFF">'
        "Reforma Curricular</div>"
        '<div style="font-size:11px;color:rgba(255,255,255,.6);margin-top:4px">Fase 2 · Etapas</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:10px 0;border-color:rgba(255,255,255,.2)'>", unsafe_allow_html=True)
    
    # Navigation
    if not _safe_page_link("app.py", label="Fase 1 · Producción", icon="🏭"):
        st.caption("Fase 1 no disponible en este despliegue (entrada: app_act.py).")
    _safe_page_link("app_act.py", label="Resumen Ejecutivo", icon="📊")
    _safe_page_link("pages/1_Alertas_Riesgos.py", label="Alertas y Riesgos", icon="🚨")
    _safe_page_link("pages/2_Vista_Facultad.py", label="Vista por Facultad", icon="🏛️")
    _safe_page_link("pages/3_Detalle_Etapa.py", label="Detalle por Etapa", icon="📋")
    _safe_page_link("pages/4_Por_Programa.py", label="Por Programa", icon="🎓")
    
    st.markdown("<hr style='margin:10px 0'>", unsafe_allow_html=True)
    st.markdown(
        '<div style="padding:12px;font-size:10px;color:rgba(255,255,255,.4);text-align:center">POLI - VACT - 2025-2026</div>',
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="'
    f"background:linear-gradient(135deg,{BRAND_PRIMARY} 0%,{BRAND_SECONDARY} 50%,{BRAND_ACCENT} 100%);"
    f'padding:18px 24px 14px;border-radius:0 0 12px 12px;border-bottom:3px solid {BRAND_HIGHLIGHT};">'
    '<div style="font-size:21px;font-weight:700;color:#FFFFFF">'
    "Reforma Curricular de Programas Académicos Poli</div>"
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    "Fase 2 · Panel Ejecutivo</div></div>",
    unsafe_allow_html=True,
)

# Filtros
_render_filter_bar("global", show_count=True)

# ── Contenido Principal ─────────────────────────────────────────────────────
df, *_ = _apply_current_filters()
n = len(df)

if n == 0:
    st.warning("No hay programas que coincidan con los filtros seleccionados.")
else:
    # Título sección
    st.markdown(
        f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">'
        "📊 Resumen Ejecutivo</div>",
        unsafe_allow_html=True,
    )
    
    # KPIs
    _render_kpis(df)
    
    st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)
    
    # Gráficos fila 1: Nivel Académico (anillos) + Facultad
    col_chart1, col_chart2 = st.columns([1, 2])
    with col_chart1:
        _render_chart_nivel_anillos(df)
    with col_chart2:
        _render_chart_facultad(df)
    
    st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)
    
    # Gráficos fila 2: Avance Consolidado por Etapa (gráfico interactivo)
    _render_chart_etapas_interactivo(df)