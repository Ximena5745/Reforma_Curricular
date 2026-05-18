"""
pages/1_Alertas_Riesgos.py — Fase 2: Alertas y Riesgos
Dashboard de alertas y riesgos operativos
"""

import html as html_lib

import pandas as pd
import streamlit as st
import streamlit.components.v1 as html_comp

from utils.data_loader_vact import (
    ETAPAS_ORDEN,
    ETAPA_PCT_COL,
    FAC_ABREV_INV,
    STATUS_LABEL,
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
    TEXT_NA,
    streamlit_global_css,
    FACULTAD_CLR,
    ETAPA_CLR,
    STATUS_CLR,
    MODALIDAD_CLR,
    PERIODO_CLR,
    p_bar_html,
    badge_html,
)

st.set_page_config(
    page_title="Alertas y Riesgos · Fase 2 · POLI",
    page_icon="🚨",
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


def _p_esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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


# ══════════════════════════════════════════════════════════════════════════════════════
# COMPONENTES DE ALERTAS
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


def _kpi_alert(label, val, sub, color):
    return (
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);'
        f'border-left:4px solid {color};border-radius:12px;'
        f'padding:14px 16px;display:flex;align-items:center;gap:12px;min-height:84px;'
        f'box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="flex-shrink:0">{_arc(100, color)}</div>'
        f'<div style="flex:1;min-width:0">'
        f'<div style="font-size:10px;color:#6a8a9e;text-transform:uppercase;letter-spacing:.5px;margin-bottom:3px">{label}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{color};line-height:1.1">{val}</div>'
        f'<div style="font-size:10px;color:#8aabb0;margin-top:2px">{sub}</div>'
        f'</div></div>'
    )


def _render_kpis_alertas(df: pd.DataFrame):
    n = len(df)
    criticos = int((df["avance_general_vact"] < 20).sum()) if n > 0 else 0
    
    # Desbalance: etapas desbalanceadas
    desbalance = df[
        (abs(df["pct_alistamiento"] - df["pct_diseno"]) > 50) |
        (abs(df["pct_diseno"] - df["pct_desarrollo"]) > 60)
    ]
    desbalance_count = len(desbalance)
    
    # Próximos a finalizar
    proximos = int((df["avance_general_vact"] >= 70).sum()) if n > 0 else 0
    
    # Implementación 100%
    impl_100 = int((df["pct_implementacion"] >= 100).sum()) if "pct_implementacion" in df.columns else 0
    
    kpis = [
        ("Alertas Críticas", str(criticos), "Avance < 20%", "#dc2626"),
        ("Requieren Atención", str(desbalance_count), "Etapas desbalanceadas", "#d97706"),
        ("Próximos a Finalizar", str(proximos), "Avance ≥ 70%", "#059669"),
        ("Implementación 100%", str(impl_100), "Completamente implementados", "#2563eb"),
    ]
    
    cols = st.columns(4)
    for i, (label, val, sub, color) in enumerate(kpis):
        with cols[i]:
            st.markdown(_kpi_alert(label, val, sub, color), unsafe_allow_html=True)


def _render_alertas_criticas(df: pd.DataFrame):
    criticos = df[df["avance_general_vact"] < 20].sort_values("avance_general_vact")
    
    items = ""
    for _, row in criticos.iterrows():
        nombre = row.get("NOMBRE DEL PROGRAMA", "—")
        fac = row.get("FACULTAD_ABREV", "—")
        mod = row.get("MODALIDAD", "—")
        sede = row.get("SEDE", "—")
        pct = int(row.get("avance_general_vact", 0))
        
        items += (
            f'<div style="display:flex;align-items:flex-start;gap:10px;padding:12px 14px;'
            f'background:rgba(220,38,38,0.05);border-left:3px solid #dc2626;border-radius:6px;margin-bottom:8px">'
            f'<span style="font-size:16px">🔴</span>'
            f'<div style="flex:1"><div style="font-size:13px;font-weight:700;color:#0f172a">{nombre}</div>'
            f'<div style="font-size:11px;color:#64748b;margin-top:2px">{fac} · {mod} · {sede}</div></div>'
            f'<span style="background:#dc2626;color:#fff;padding:4px 10px;border-radius:100px;font-size:11px;font-weight:700">{pct}%</span>'
            f'</div>'
        )
    
    if not items:
        items = f'<div style="padding:20px;text-align:center;color:#94a3b8;font-size:13px">Sin alertas críticas</div>'
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:14px;font-weight:700;color:#0f172a;margin-bottom:12px">🔴 Alertas Críticas</div>'
        f'<div style="font-size:11px;color:#94a3b8;margin-bottom:12px">Programas con avance menor al 20%</div>'
        f'{items}</div>',
        unsafe_allow_html=True,
    )


def _render_alertas_atencion(df: pd.DataFrame):
    # Desbalance: etapas desbalanceadas
    desbalance = df[
        (abs(df["pct_alistamiento"] - df["pct_diseno"]) > 50) |
        (abs(df["pct_diseno"] - df["pct_desarrollo"]) > 60)
    ].head(10)
    
    items = ""
    for _, row in desbalance.iterrows():
        nombre = row.get("NOMBRE DEL PROGRAMA", "—")
        alist = int(row.get("pct_alistamiento", 0))
        diseno = int(row.get("pct_diseno", 0))
        desarr = int(row.get("pct_desarrollo", 0))
        
        items += (
            f'<div style="display:flex;align-items:flex-start;gap:10px;padding:12px 14px;'
            f'background:rgba(217,119,6,0.05);border-left:3px solid #d97706;border-radius:6px;margin-bottom:8px">'
            f'<span style="font-size:16px">⚠️</span>'
            f'<div style="flex:1"><div style="font-size:13px;font-weight:700;color:#0f172a">{nombre}</div>'
            f'<div style="font-size:11px;color:#64748b;margin-top:2px">Desfase entre etapas</div>'
            f'<div style="font-size:10px;color:#94a3b8;margin-top:4px">Alist: {alist}% · Diseño: {diseno}% · Desarrollo: {desarr}%</div></div>'
            f'</div>'
        )
    
    if not items:
        items = f'<div style="padding:20px;text-align:center;color:#94a3b8;font-size:13px">Sin alertas de atención</div>'
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:14px;font-weight:700;color:#0f172a;margin-bottom:12px">🟡 Alertas de Atención</div>'
        f'<div style="font-size:11px;color:#94a3b8;margin-bottom:12px">Programas con etapas desbalanceadas</div>'
        f'{items}</div>',
        unsafe_allow_html=True,
    )


def _render_proximos_finalizar(df: pd.DataFrame):
    proximos = df[df["avance_general_vact"] >= 70].sort_values("avance_general_vact", ascending=False)
    
    items = ""
    for _, row in proximos.iterrows():
        nombre = row.get("NOMBRE DEL PROGRAMA", "—")
        fac = row.get("FACULTAD_ABREV", "—")
        mod = row.get("MODALIDAD", "—")
        pct = int(row.get("avance_general_vact", 0))
        
        items += (
            f'<div style="display:flex;align-items:flex-start;gap:10px;padding:12px 14px;'
            f'background:rgba(5,150,105,0.05);border-left:3px solid #059669;border-radius:6px;margin-bottom:8px">'
            f'<span style="font-size:16px">🏁</span>'
            f'<div style="flex:1"><div style="font-size:13px;font-weight:700;color:#0f172a">{nombre}</div>'
            f'<div style="font-size:11px;color:#64748b;margin-top:2px">{fac} · {mod}</div></div>'
            f'<span style="background:#059669;color:#fff;padding:4px 10px;border-radius:100px;font-size:11px;font-weight:700">{pct}%</span>'
            f'</div>'
        )
    
    if not items:
        items = f'<div style="padding:20px;text-align:center;color:#94a3b8;font-size:13px">Sin programas próximos a finalizar</div>'
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:14px;font-weight:700;color:#0f172a;margin-bottom:12px">🟢 Programas Próximos a Finalizar</div>'
        f'<div style="font-size:11px;color:#94a3b8;margin-bottom:12px">Programas con avance general superior al 70%</div>'
        f'{items}</div>',
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
    
    _safe_page_link("app_act.py", label="📊 Resumen Ejecutivo", icon="📊")
    _safe_page_link("pages/1_Alertas_Riesgos.py", label="🚨 Alertas y Riesgos", icon="🚨")
    _safe_page_link("pages/2_Vista_Facultad.py", label="🏛️ Vista por Facultad", icon="🏛️")
    _safe_page_link("pages/3_Detalle_Etapa.py", label="📋 Detalle por Etapa", icon="📋")
    _safe_page_link("pages/4_Por_Programa.py", label="🏛️ Por Programa", icon="🏛️")
    
    st.markdown("<hr style='margin:10px 0'>", unsafe_allow_html=True)
    st.markdown('<div style="padding:12px;font-size:10px;color:rgba(255,255,255,.4);text-align:center">POLI · VACT · 2025–2026</div>', unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="'
    f"background:linear-gradient(135deg,{BRAND_PRIMARY} 0%,{BRAND_SECONDARY} 50%,{BRAND_ACCENT} 100%);"
    f'padding:18px 24px 14px;border-radius:0 0 12px 12px;border-bottom:3px solid {BRAND_HIGHLIGHT};">'
    '<div style="font-size:21px;font-weight:700;color:#FFFFFF">Reforma Curricular de Programas Académicos Poli</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">Fase 2 · Alertas y Riesgos Operativos</div></div>',
    unsafe_allow_html=True,
)

# Filtros
_render_filter_bar("global", show_count=True)

# Contenido
df, *_ = _apply_current_filters()
n = len(df)

if n == 0:
    st.warning("No hay programas que coincidan con los filtros seleccionados.")
else:
    st.markdown(f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">🚨 Alertas y Riesgos</div>', unsafe_allow_html=True)
    
    _render_kpis_alertas(df)
    
    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        _render_alertas_criticas(df)
    with col2:
        _render_alertas_atencion(df)
    
    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)
    
    _render_proximos_finalizar(df)