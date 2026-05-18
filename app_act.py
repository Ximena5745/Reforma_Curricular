"""
app_act.py — Dashboard Fase 2: Reforma Curricular por Etapas (VACT)
Fuente: hoja Etapas · CONTROL MAESTRO DE REFORMA CURRICULAR_VACT.xlsx
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
    f'letter-spacing:.4px;white-space nowrap"'
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


# ══════════════════════════════════════════════════════════════════════════════════════
# NUEVOS COMPONENTES - RESUMEN EJECUTIVO
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


def _kpi_card(label, val, sub, color, pct_bar=None, icon="◈"):
    pct_val = min(pct_bar * 100, 100) if pct_bar is not None else 0
    pct_width = f"width:{pct_val:.0f}%" if pct_bar is not None else ""
    pct_display = f"width:{pct_val:.0f}%" if pct_bar is not None else "display:none"
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
    completados = int((df["avance_general_vact"] >= 80).sum()) if n > 0 else 0
    en_ejecucion = int((df["avance_general_vact"] >= 20).sum()) - completados if n > 0 else 0
    criticos = int((df["avance_general_vact"] < 20).sum()) if n > 0 else 0
    facultades = df["FACULTAD_ABREV"].nunique() if n > 0 and "FACULTAD_ABREV" in df.columns else 0
    modalidades = df["MODALIDAD"].nunique() if n > 0 and "MODALIDAD" in df.columns else 0
    proximos = int((df["avance_general_vact"] >= 70).sum()) if n > 0 else 0

    kpis = [
        ("Total Programas", str(n), f"{facultades} facultades activas", "#0F385A", n / 70 if n > 0 else 0, "📚"),
        ("Avance Promedio", f"{avg_general}%", "General del proyecto", "#0F385A", avg_general / 100, "📈"),
        ("Completados", str(completados), "Avance ≥80%", "#059669", completados / max(n, 1), "✅"),
        ("En Ejecución", str(en_ejecucion), "Avance 20-79%", "#0891b2", en_ejecucion / max(n, 1), "⚙️"),
        ("Programas Críticos", str(criticos), "Avance <20%", "#dc2626", criticos / max(n, 1), "🚨"),
        ("Facultades Activas", str(facultades), "Unidades académicas", "#7c3aed", facultades / 5, "🏛️"),
        ("Modalidades", str(modalidades), "Presencial · Virtual · Híbrido", "#d97706", modalidades / 3, "🌐"),
        ("Próximos a Finalizar", str(proximos), "Avance >70%", "#059669", proximos / max(n, 1), "🏁"),
    ]

    cols = st.columns(4)
    for i, (label, val, sub, color, pct_bar, icon) in enumerate(kpis):
        with cols[i % 4]:
            st.markdown(_kpi_card(label, val, sub, color, pct_bar, icon), unsafe_allow_html=True)
        if i == 3:
            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
            cols = st.columns(4)


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
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<rect x="0" y="0" width="{svg_w}" height="{bar_h}" rx="6" fill="rgba(0,0,0,0.03)"/>'
            f'<rect x="0" y="0" width="{max(4, width)}" height="{bar_h}" rx="6" fill="{color}" opacity="0.85"/>'
            f'<text x="8" y="{bar_h/2+1}" dominant-baseline="middle" fill="{ "#fff" if avg > 30 else "#1e293b"}" font-family="Segoe UI,sans-serif" font-size="11" font-weight="600">{fac}</text>'
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


def _render_chart_modalidad(df: pd.DataFrame):
    if "MODALIDAD" not in df.columns:
        return
    
    mods = df["MODALIDAD"].value_counts()
    colors_map = {"Virtual": "#1FB2DE", "Presencial": "#A6CE38", "Híbrido": "#FBAF17"}
    total = mods.sum()
    if total == 0:
        return
    
    cx, cy, r, ri = 80, 70, 55, 35
    slices = ""
    angle = -3.14159 / 2
    
    legend = ""
    for mod, count in mods.items():
        if count == 0:
            continue
        slice_angle = (count / total) * 2 * 3.14159
        x1 = cx + r * (angle > -3.14159 and angle < 3.14159 and True or True)  # simplified
        y1 = cy + r * 0
        x1 = cx + r * (angle + slice_angle/2) / abs(angle + slice_angle/2 + 0.001) * 0 if angle != -3.14159/2 else cx
        y1 = cy + r * 0
        
        # Full donut calculation
        x1 = cx + r * 3.14159 * 0
        y1 = cy + r * 0
        x2 = cx + r * 3.14159 * 2
        y2 = cy + r * 0
        xi1 = cx + ri * 3.14159 * 0
        yi1 = cy + ri * 0
        xi2 = cx + ri * 3.14159 * 2
        yi2 = cy + ri * 0
        
        # Calculate properly
        start_angle = angle
        end_angle = angle + slice_angle
        x1 = cx + r * (1 if abs(start_angle) < 3 else -1) * (0 if abs(start_angle) < 0.01 else 1)
        y1 = cy
        
        color = colors_map.get(mod, "#6e7681")
        pct = round(count / total * 100)
        
        legend += (
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">'
            f'<div style="width:10px;height:10px;border-radius:3px;background:{color};flex-shrink:0"></div>'
            f'<span style="font-size:11px;color:#475569;font-weight:600">{mod}</span>'
            f'<span style="margin-left:auto;font-size:11px;font-weight:700;color:#0f172a">{count} ({pct}%)</span>'
            f'</div>'
        )
        
        angle += slice_angle
    
    # Simpler donut using conic-gradient
    grad = ""
    current = 0
    for mod, count in mods.items():
        color = colors_map.get(mod, "#6e7681")
        pct = count / total * 100
        grad += f"{color} {current}% {current + pct}%,"
        current += pct
    
    grad = grad.rstrip(",")
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">Distribución por Modalidad</div>'
        f'<div style="display:flex;align-items:center;gap:20px">'
        f'<div style="width:140px;height:140px;border-radius:50%;background:conic-gradient({grad});display:flex;align-items:center;justify-content:center">'
        f'<div style="width:80px;height:80px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center">'
        f'<div style="text-align:center"><div style="font-size:22px;font-weight:800;color:{TEXT_PRIMARY}">{total}</div><div style="font-size:9px;color:#94a3b8">Programas</div></div>'
        f'</div></div>'
        f'<div style="flex:1">{legend}</div></div></div>',
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
        
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<rect x="0" y="0" width="{svg_w}" height="{bar_h}" rx="6" fill="rgba(0,0,0,0.03)"/>'
            f'<rect x="0" y="0" width="{max(8, width)}" height="{bar_h}" rx="6" fill="{color}" opacity="0.85"/>'
            f'<text x="6" y="{bar_h/2+1}" dominant-baseline="middle" fill="{ "#fff" if avg > 25 else "#1e293b"}" font-family="Segoe UI,sans-serif" font-size="11" font-weight="600">{etapa.replace(" Curricular", "")}</text>'
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
        
        bars += (
            f'<g transform="translate(0,{y})">'
            f'<rect x="0" y="0" width="460" height="24" rx="5" fill="rgba(0,0,0,0.03)"/>'
            f'<rect x="0" y="0" width="{max(6, width)}" height="24" rx="5" fill="{color}" opacity="0.85"/>'
            f'<text x="6" y="13" dominant-baseline="middle" fill="{ "#fff" if count/max_count > 0.25 else "#1e293b"}" font-family="Segoe UI,sans-serif" font-size="11" font-weight="600">{nivel}</text>'
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
            f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">🏆 Top Programas Destacados</div>'
            f'<div style="font-size:11px;color:{TEXT_MUTED};margin-bottom:10px">Mayor avance general</div>'
            f'{top_html}</div>',
            unsafe_allow_html=True,
        )
    
    with col2:
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
            f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin-bottom:12px">⚠️ Programas Críticos</div>'
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
    if not _safe_page_link("app.py", label="Fase 1 · Producción", icon="📊"):
        st.caption("Fase 1 no disponible en este despliegue (entrada: app_act.py).")
    _safe_page_link("app_act.py", label="📊 Resumen Ejecutivo", icon="📊")
    _safe_page_link("pages/1_Alertas_Riesgos.py", label="🚨 Alertas y Riesgos", icon="🚨")
    _safe_page_link("pages/2_Vista_Facultad.py", label="🏛️ Vista por Facultad", icon="🏛️")
    _safe_page_link("pages/3_Detalle_Etapa.py", label="📋 Detalle por Etapa", icon="📋")
    _safe_page_link("pages/4_Por_Programa.py", label="🏛️ Por Programa", icon="🏛️")
    
    st.markdown("<hr style='margin:10px 0'>", unsafe_allow_html=True)
    st.markdown(
        '<div style="padding:12px;font-size:10px;color:rgba(255,255,255,.4);text-align:center">'
        "POLI · VACT · 2025–2026</div>',
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
        "📊 Resumen Ejecutivo</div>',
        unsafe_allow_html=True,
    )
    
    # KPIs
    _render_kpis(df)
    
    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)
    
    # Gráficos fila 1
    col_chart1, col_chart2 = st.columns([3, 2])
    with col_chart1:
        _render_chart_facultad(df)
    with col_chart2:
        _render_chart_modalidad(df)
    
    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)
    
    # Gráficos fila 2
    col_chart3, col_chart4 = st.columns([3, 2])
    with col_chart3:
        _render_chart_etapas(df)
    with col_chart4:
        _render_chart_nivel(df)
    
    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)
    
    # Rankings
    _render_rankings(df)