"""
Componentes compartidos Fase 2: sidebar (solo navegacion), filtros en area principal, header.
Los filtros NUNCA van en st.sidebar.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.data_loader_vact import (
    DATA_SOURCE_NAME,
    apply_filters_vact,
    get_raw_data_updated_label,
)
from utils.poli_theme import (
    BG_MUTED,
    BRAND_ACCENT,
    BRAND_HIGHLIGHT,
    BRAND_PRIMARY,
    BRAND_SECONDARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    phosphor_icon,
)

_LBL = (
    f'style="padding-top:8px;font-size:11px;font-weight:700;color:{TEXT_PRIMARY};'
    f'letter-spacing:.4px;white-space:nowrap;display:flex;align-items:center;gap:4px"'
)

LOGO_PATH = Path(__file__).parent / "Wallpaper-POLI.jpg.jpg"

F2_NAV = [
    ("app_act.py", "Resumen Ejecutivo", ":material/bar_chart:"),
    ("pages/4_Por_Programa.py", "Resumen Por Programa", ":material/school:"),
    ("pages/2_Vista_Facultad.py", "Resumen por Facultad", ":material/apartment:"),
    ("pages/3_Detalle_Etapa.py", "Detalle por Etapa", ":material/assignment:"),
    ("pages/1_Alertas_Riesgos.py", "Alertas y Riesgos", ":material/warning:"),
]


def safe_page_link(page: str, **kwargs) -> bool:
    try:
        st.page_link(page, **kwargs)
        return True
    except st.errors.StreamlitPageNotFoundError:
        return False


def render_f2_sidebar() -> None:
    """Solo navegacion. Sin filtros."""
    with st.sidebar:
        if LOGO_PATH.is_file():
            st.image(str(LOGO_PATH), use_container_width=True)
        st.markdown("<hr style='margin:10px 0;border-color:rgba(255,255,255,.2)'>", unsafe_allow_html=True)
        for page, label, icon in F2_NAV:
            safe_page_link(page, label=label, icon=icon)
        st.markdown("<hr style='margin:10px 0'>", unsafe_allow_html=True)
        updated = get_raw_data_updated_label()
        st.markdown(
            '<div style="padding:12px;font-size:10px;color:rgba(255,255,255,.55);text-align:center;line-height:1.4">'
            f"Fecha de actualización del {DATA_SOURCE_NAME}<br>"
            f'<span style="color:rgba(255,255,255,.85);font-weight:600">{updated}</span>'
            "</div>",
            unsafe_allow_html=True,
        )



def _filter_keys(key_prefix: str) -> dict[str, str]:
    p = key_prefix.strip() or "global"
    return {
        "mod": f"{p}_flt_mod",
        "fac": f"{p}_flt_fac",
        "per": f"{p}_flt_per",
        "nivel": f"{p}_flt_nivel",
        "clear": f"{p}_flt_clear",
    }


def clear_filters(key_prefix: str = "global") -> None:
    keys = _filter_keys(key_prefix)
    st.session_state[keys["mod"]] = []
    st.session_state[keys["fac"]] = []
    st.session_state[keys["per"]] = []
    st.session_state[keys["nivel"]] = []


def apply_current_filters(df_raw, fac_abrev_inv, key_prefix: str = "global"):
    keys = _filter_keys(key_prefix)
    sel_mod = list(st.session_state.get(keys["mod"]) or [])
    sel_fac = list(st.session_state.get(keys["fac"]) or [])
    sel_per = list(st.session_state.get(keys["per"]) or [])
    sel_nivel = list(st.session_state.get(keys["nivel"]) or [])
    facultad_f = [fac_abrev_inv.get(f, f) for f in sel_fac]
    df = apply_filters_vact(df_raw.copy(), sel_mod, facultad_f, sel_per, sel_nivel)
    return df, sel_mod, sel_fac, sel_per, sel_nivel


def render_filter_bar(
    df_raw,
    fac_abrev_inv,
    mods_ops: list,
    fac_ops: list,
    pers_ops: list,
    niveles_ops: list,
    *,
    key_prefix: str = "global",
    show_count: bool = True,
) -> None:
    keys = _filter_keys(key_prefix)
    use_pills = hasattr(st, "pills")

    st.markdown(
        f'<div class="f2-filter-panel" style="background:{BG_MUTED};'
        f"border:1px solid rgba(15,56,90,0.08);border-radius:0 0 10px 10px;"
        f'padding:10px 14px 8px;margin:-0.5rem 0 12px 0"></div>',
        unsafe_allow_html=True,
    )

    with st.container():
        lb1, in1, sp, lb2, in2, btn = st.columns([0.55, 2.2, 0.05, 0.65, 1.9, 0.65])
        with lb1:
            st.markdown(f"<div {_LBL}>{phosphor_icon('clipboard-text', size=14)} MODALIDAD</div>", unsafe_allow_html=True)
        with in1:
            if use_pills:
                st.pills("mod", mods_ops, selection_mode="multi", key=keys["mod"], label_visibility="collapsed")
            else:
                st.multiselect("mod", mods_ops, key=keys["mod"], label_visibility="collapsed", placeholder="Todas")
        with lb2:
            st.markdown(f"<div {_LBL}>{phosphor_icon('buildings', size=14)} FACULTAD</div>", unsafe_allow_html=True)
        with in2:
            if use_pills:
                st.pills("fac", fac_ops, selection_mode="multi", key=keys["fac"], label_visibility="collapsed")
            else:
                st.multiselect("fac", fac_ops, key=keys["fac"], label_visibility="collapsed", placeholder="Todas")
        with btn:
            st.button(
                "",
                on_click=lambda: clear_filters(key_prefix),
                type="primary",
                key=keys["clear"],
                icon=":material/close:",
                help="Limpiar filtros",
            )

        lb3, in3, sp2, lbn, inn, cnt = st.columns([0.55, 2.2, 0.05, 0.65, 1.9, 0.65])
        with lb3:
            st.markdown(f"<div {_LBL}>{phosphor_icon('calendar', size=14)} PERIODO</div>", unsafe_allow_html=True)
        with in3:
            if use_pills:
                st.pills("per", pers_ops, selection_mode="multi", key=keys["per"], label_visibility="collapsed")
            else:
                st.multiselect("per", pers_ops, key=keys["per"], label_visibility="collapsed", placeholder="Todos")
        with lbn:
            st.markdown(f"<div {_LBL}>{phosphor_icon('graduation-cap', size=14)} NIVEL</div>", unsafe_allow_html=True)
        with inn:
            if use_pills:
                st.pills("nivel", niveles_ops, selection_mode="multi", key=keys["nivel"], label_visibility="collapsed")
            else:
                st.multiselect("nivel", niveles_ops, key=keys["nivel"], label_visibility="collapsed", placeholder="Todos")
        if show_count:
            df_tmp, *_ = apply_current_filters(df_raw, fac_abrev_inv, key_prefix)
            with cnt:
                st.markdown(
                    f'<div style="padding-top:9px;font-size:12px;color:{TEXT_MUTED};text-align:right">'
                    f'Mostrando <b style="color:{TEXT_PRIMARY}">{len(df_tmp)}</b> de '
                    f'<b style="color:{TEXT_PRIMARY}">{len(df_raw)}</b></div>',
                    unsafe_allow_html=True,
                )


def render_f2_header(subtitle: str) -> None:
    st.markdown(
        '<div style="'
        f"background:linear-gradient(135deg,{BRAND_PRIMARY} 0%,{BRAND_SECONDARY} 50%,{BRAND_ACCENT} 100%);"
        f'padding:18px 24px 14px;border-bottom:3px solid {BRAND_HIGHLIGHT};">'
        '<div style="font-size:21px;font-weight:700;color:#FFFFFF">'
        "Reforma Curricular de Programas Academicos Poli</div>"
        f'<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">{subtitle}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
