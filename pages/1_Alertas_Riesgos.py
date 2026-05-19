"""
pages/1_Alertas_Riesgos.py — Fase 2: Alertas y Riesgos
Dashboard de alertas y riesgos operativos
"""

from pathlib import Path

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
    activity_in_progress,
    activity_not_done,
    activity_val_contains,
    apply_filters_vact,
    load_etapas_data,
)
from utils.f2_components import (
    apply_current_filters as f2_apply_filters,
    render_f2_header,
    render_f2_sidebar,
    render_filter_bar as f2_render_filter_bar,
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
    phosphor_icon,
    phosphor_icon_kpi,
    phosphor_icon_nav,
)

st.set_page_config(
    page_title="Alertas y Riesgos · Fase 2 · POLI",
    page_icon="warning",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _parse_pct(val) -> float:
    """Convierte valor de porcentaje string a float."""
    if pd.isna(val):
        return 0.0
    s = str(val).strip().lower()
    if not s or s in ("none", "nan", "no aplica", "—", ""):
        return 0.0
    try:
        return float(s.replace("%", "").replace(",", "."))
    except:
        return 0.0


def _is_not_finished(val) -> bool:
    """Retorna True si el valor no indica estado Finalizado."""
    if pd.isna(val):
        return True
    s = str(val).strip().lower()
    return s != "finalizado"


def _get_r1_produccion_sin_aval(df: pd.DataFrame) -> pd.DataFrame:
    """R1: Virtual/Híbrido sin formato de proyecciones financieras finalizado."""
    mask = df["MODALIDAD"].isin(["Virtual", "Híbrido"]) & activity_not_done(df, "proyecciones_fin")
    return df[mask]


def _get_r2_contenidos_incompletos(df: pd.DataFrame) -> pd.DataFrame:
    """R2: Lanzamiento 2026-2 con contenidos incompletos."""
    mask = (df["PERIODO DE IMPLEMENTACIÓN"] == "2026-2") & activity_not_done(df, "produccion_contenido")
    return df[mask]


def _get_r3_banner_sin_produccion(df: pd.DataFrame) -> pd.DataFrame:
    """R3: Parametrización en Banner en proceso sin producción de contenidos."""
    mask = activity_in_progress(df, "banner_convenios") & activity_not_done(df, "produccion_contenido")
    return df[mask]


def _get_r4_syllabus_incompleto(df: pd.DataFrame) -> pd.DataFrame:
    """R4: Virtual/Híbrido con syllabus incompleto."""
    mask = df["MODALIDAD"].isin(["Virtual", "Híbrido"]) & activity_not_done(df, "syllabus")
    return df[mask]


def _get_r5_banner_sin_convenios(df: pd.DataFrame) -> pd.DataFrame:
    """R5: Banner en proceso sin trámites de convenios."""
    mask = activity_in_progress(df, "banner_convenios") & activity_not_done(df, "convenios")
    return df[mask]


def _get_r6_aprobados_men(df: pd.DataFrame) -> pd.DataFrame:
    """R6: Trámite MEN aprobado sin producción virtual completa."""
    mask = activity_val_contains(df, "cronograma_men", "aprobado") & activity_not_done(
        df, "produccion_contenido"
    )
    return df[mask]


def _render_riesgo(title: str, desc: str, color: str, risk_df: pd.DataFrame) -> None:
    """Renderiza una card de riesgo con lista de programas."""
    items = ""
    for _, row in risk_df.iterrows():
        nombre = row.get("NOMBRE DEL PROGRAMA", "—")
        fac = row.get("FACULTAD_ABREV", "—")
        mod = row.get("MODALIDAD", "—")
        sede = row.get("SEDE", "—")
        pct = int(row.get("avance_general_vact", 0))
        
        items += (
            f'<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 12px;'
            f'background:rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.05);'
            f'border-left:3px solid {color};border-radius:6px;margin-bottom:6px">'
            f'{phosphor_icon("warning", size=14, color=color)}'
            f'<div style="flex:1;min-width:0"><div style="font-size:12px;font-weight:600;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{nombre}</div>'
            f'<div style="font-size:10px;color:#64748b;margin-top:2px">{fac} · {mod} · {sede}</div></div>'
            f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:100px;font-size:10px;font-weight:600">{pct}%</span>'
            f'</div>'
        )
    
    if not items:
        items = f'<div style="padding:16px;text-align:center;color:#94a3b8;font-size:12px">Sin programas en este riesgo</div>'
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:14px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:6px">{phosphor_icon("warning", size=16, color=color)} {title}</div>'
        f'<div style="font-size:10px;color:#94a3b8;margin-bottom:10px">{desc}</div>'
        f'{items}</div>',
        unsafe_allow_html=True,
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
    r1 = _get_r1_produccion_sin_aval(df)
    r2 = _get_r2_contenidos_incompletos(df)
    r3 = _get_r3_banner_sin_produccion(df)
    r4 = _get_r4_syllabus_incompleto(df)
    r5 = _get_r5_banner_sin_convenios(df)
    r6 = _get_r6_aprobados_men(df)
    
    kpis = [
        ("R1: Prod. Virtual sin Aval", str(len(r1)), "Virtual/Híbrido sin formato financiero", "#dc2626"),
        ("R2: 2026-2 Cont. Incompletos", str(len(r2)), "Período 2026-2 sin contenidos", "#d97706"),
        ("R3: Banner sin Producción", str(len(r3)), "Param. Banner sin contenidos", "#7c3aed"),
        ("R4: Syllabus Incompleto", str(len(r4)), "Virtual/Híbrido sin syllabus", "#0d9488"),
        ("R5: Banner sin Convenios", str(len(r5)), "Banner sin trámites de convenios", "#2563eb"),
        ("R6: Aprobados MEN sin Prod.", str(len(r6)), "Trámite MEN sin contenidos", "#f59e0b"),
    ]
    
    cols = st.columns(6)
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
            f'{phosphor_icon("circle-fill", size=16, color="#dc2626")}'
            f'<div style="flex:1"><div style="font-size:13px;font-weight:700;color:#0f172a">{nombre}</div>'
            f'<div style="font-size:11px;color:#64748b;margin-top:2px">{fac} · {mod} · {sede}</div></div>'
            f'<span style="background:#dc2626;color:#fff;padding:4px 10px;border-radius:100px;font-size:11px;font-weight:700">{pct}%</span>'
            f'</div>'
        )
    
    if not items:
        items = f'<div style="padding:20px;text-align:center;color:#94a3b8;font-size:13px">Sin alertas críticas</div>'
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:14px;font-weight:700;color:#0f172a;margin-bottom:12px">{phosphor_icon("warning", size=18, color="#dc2626")} Alertas Críticas</div>'
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
            f'{phosphor_icon("warning-circle", size=16, color="#d97706")}'
            f'<div style="flex:1"><div style="font-size:13px;font-weight:700;color:#0f172a">{nombre}</div>'
            f'<div style="font-size:11px;color:#64748b;margin-top:2px">Desfase entre etapas</div>'
            f'<div style="font-size:10px;color:#94a3b8;margin-top:4px">Alist: {alist}% · Diseño: {diseno}% · Desarrollo: {desarr}%</div></div>'
            f'</div>'
        )
    
    if not items:
        items = f'<div style="padding:20px;text-align:center;color:#94a3b8;font-size:13px">Sin alertas de atención</div>'
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:14px;font-weight:700;color:#0f172a;margin-bottom:12px">{phosphor_icon("circle-fill", size=18, color="#d97706")} Alertas de Atención</div>'
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
            f'{phosphor_icon("flag-checkered", size=16, color="#059669")}'
            f'<div style="flex:1"><div style="font-size:13px;font-weight:700;color:#0f172a">{nombre}</div>'
            f'<div style="font-size:11px;color:#64748b;margin-top:2px">{fac} · {mod}</div></div>'
            f'<span style="background:#059669;color:#fff;padding:4px 10px;border-radius:100px;font-size:11px;font-weight:700">{pct}%</span>'
            f'</div>'
        )
    
    if not items:
        items = f'<div style="padding:20px;text-align:center;color:#94a3b8;font-size:13px">Sin programas próximos a finalizar</div>'
    
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="font-size:14px;font-weight:700;color:#0f172a;margin-bottom:12px">{phosphor_icon("circle-fill", size=18, color="#059669")} Programas Próximos a Finalizar</div>'
        f'<div style="font-size:11px;color:#94a3b8;margin-bottom:12px">Programas con avance general superior al 70%</div>'
        f'{items}</div>',
        unsafe_allow_html=True,
    )


render_f2_sidebar(show_fase1=False)
render_f2_header("Fase 2 · Alertas y Riesgos Operativos")
f2_render_filter_bar(
    df_raw, fac_abrev_inv, mods_ops, fac_ops, pers_ops, niveles_ops, key_prefix="alertas"
)

df, *_ = f2_apply_filters(df_raw, fac_abrev_inv, key_prefix="alertas")
n = len(df)

if n == 0:
    st.warning("No hay programas que coincidan con los filtros seleccionados.")
else:
    st.markdown(f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">{phosphor_icon("warning", size=22)} Alertas y Riesgos</div>', unsafe_allow_html=True)
    
    _render_kpis_alertas(df)
    
    st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)
    
    r1_df = _get_r1_produccion_sin_aval(df)
    r2_df = _get_r2_contenidos_incompletos(df)
    r3_df = _get_r3_banner_sin_produccion(df)
    r4_df = _get_r4_syllabus_incompleto(df)
    r5_df = _get_r5_banner_sin_convenios(df)
    r6_df = _get_r6_aprobados_men(df)
    
    row1_cols = st.columns(3)
    with row1_cols[0]:
        _render_riesgo("R1: Prod. Virtual sin Aval", "Virtual/Híbrido sin formato financiero", "#dc2626", r1_df)
    with row1_cols[1]:
        _render_riesgo("R2: 2026-2 Cont. Incompletos", "Período 2026-2 sin contenidos", "#d97706", r2_df)
    with row1_cols[2]:
        _render_riesgo("R3: Banner sin Producción", "Param. Banner sin contenidos", "#7c3aed", r3_df)
    
    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)
    
    row2_cols = st.columns(3)
    with row2_cols[0]:
        _render_riesgo("R4: Syllabus Incompleto", "Virtual/Híbrido sin syllabus", "#0d9488", r4_df)
    with row2_cols[1]:
        _render_riesgo("R5: Banner sin Convenios", "Banner sin trámites de convenios", "#2563eb", r5_df)
    with row2_cols[2]:
        _render_riesgo("R6: Aprobados MEN sin Prod.", "Trámite MEN sin contenidos", "#f59e0b", r6_df)