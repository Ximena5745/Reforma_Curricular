"""
pages/3_Detalle_Etapa.py — Fase 2: Detalle por Etapa
Tabla con toggle para ver actividades
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
    MODALIDAD_CLR,
    PERIODO_CLR,
    p_bar_html,
    badge_html,
    status_icon_html,
)

_HDR_ROW1_H = 36

st.set_page_config(
    page_title="Detalle por Etapa · Fase 2 · POLI",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _safe_page_link(page: str, **kwargs) -> bool:
    try:
        st.page_link(page, **kwargs)
        return True
    except st.errors.StreamlitPageNotFoundError:
        return False


def _esc(s):
    return html_lib.escape(str(s) if s is not None else "—")


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


def _vact_act_icon(cl: str, val=None) -> str:
    lbl = STATUS_LABEL.get(cl, cl)
    if cl == "info" and val and str(val).strip() not in ("—", "", "nan", "None"):
        return (
            f'<span style="font-size:10px;color:{TEXT_SUBTLE};display:inline-block;max-width:90px;'
            f'line-height:1.2;word-break:break-word" title="{_p_esc(lbl)}">{_p_esc(str(val)[:24])}</span>'
        )
    if cl == "na":
        return f'<span style="color:{TEXT_NA};font-size:13px;font-weight:600" title="{_p_esc(lbl)}">N/A</span>'
    icon = status_icon_html(cl, size=16, title=lbl)
    return icon if icon else f'<span style="color:{TEXT_LIGHT}">—</span>'


def _status_legend_html() -> str:
    parts = []
    for cl in ("done", "inprog", "nostart", "devuelto", "info", "na"):
        lbl = STATUS_LABEL.get(cl, cl)
        if cl == "na":
            icon = f'<span style="color:{TEXT_NA};font-weight:600">N/A</span>'
        else:
            icon = status_icon_html(cl, size=14, title=lbl)
        parts.append(
            f'<span style="margin-right:16px;font-size:11px;color:{TEXT_MUTED}">{icon} {lbl}</span>'
        )
    return (
        '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:8px;padding:8px 4px">'
        + "".join(parts)
        + f'<span style="font-size:10px;color:{TEXT_LIGHT};margin-left:8px">'
        "· Pulse + en cada etapa para ver actividades</span></div>"
    )


def _blend_with_white(hex_color: str, tint: float) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return BG_ROW
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    w = 1.0 - tint
    return (
        f"#{int(255 * w + r * tint):02x}"
        f"{int(255 * w + g * tint):02x}"
        f"{int(255 * w + b * tint):02x}"
    )


def _etapa_hdr_tints(clr: str) -> dict[str, str]:
    return {
        "etapa_bg": clr,
        "etapa_fg": "#FFFFFF",
        "act_bg": _blend_with_white(clr, 0.09),
        "act_fg": TEXT_PRIMARY,
        "pct_bg": _blend_with_white(clr, 0.17),
        "pct_fg": TEXT_PRIMARY,
        "cell_act": _blend_with_white(clr, 0.06),
        "cell_act_alt": _blend_with_white(clr, 0.11),
        "border": _blend_with_white(clr, 0.28),
    }


_MASTER_TABLE_CSS = f"""
<style>
html, body {{ margin: 0; padding: 0; height: 100%; background: {BG_TABLE}; }}
.vact-table-scroller {{
  height: 100%;
  overflow: auto;
  -webkit-overflow-scrolling: touch;
  border-radius: 12px;
  border: 1.5px solid {BORDER_TABLE};
  box-shadow: 0 2px 12px rgba(15,56,90,.10);
  background: {BG_TABLE};
}}
.vact-master-table {{
  width: 100%; table-layout: auto; border-collapse: separate; border-spacing: 0;
  font-family: 'Segoe UI', sans-serif; min-width: max-content;
}}
.vact-master-table thead tr.hdr-etapa th {{
  position: sticky;
  top: 0;
  z-index: 4;
  height: {_HDR_ROW1_H}px;
  padding: 5px 8px;
  border-bottom: none;
  background-clip: padding-box;
  vertical-align: middle;
}}
.vact-master-table thead tr.hdr-act th {{
  position: sticky;
  top: {_HDR_ROW1_H}px;
  z-index: 3;
  padding: 5px 5px;
  border-top: none;
  background-clip: padding-box;
  vertical-align: bottom;
  opacity: 1;
}}
.vact-master-table td[class^="col-act-"] {{
  opacity: 1;
}}
.vact-master-table thead th.th-pin-left {{
  left: 0;
  z-index: 6 !important;
  box-shadow: 2px 0 4px rgba(0,0,0,.06);
}}
.vact-master-table thead th.th-pin-gen {{
  z-index: 5 !important;
}}
</style>
"""


_TOGGLE_JS = """
<script>
function toggleEtapa(slug) {
  var cols = document.querySelectorAll('.col-act-' + slug);
  var hdr = document.getElementById('hdr-etapa-' + slug);
  var btn = document.getElementById('btn-etapa-' + slug);
  if (!hdr || !btn) return;
  var show = cols.length && cols[0].style.display === 'none';
  for (var i = 0; i < cols.length; i++) {
    cols[i].style.display = show ? 'table-cell' : 'none';
  }
  var expanded = parseInt(hdr.getAttribute('data-colspan-expanded') || '1', 10);
  hdr.colSpan = show ? expanded : 1;
  btn.textContent = show ? '\u2212' : '+';
}
</script>
"""


def _short_label(text: str, max_len: int = 28) -> str:
    t = str(text).strip()
    return t if len(t) <= max_len else t[: max_len - 1] + "…"


def _master_activities_table_html(df: pd.DataFrame) -> str:
    meta_all = _ensure_activities_meta(df)
    etapa_blocks = []
    ncols = 6
    for etapa in ETAPAS_ORDEN:
        meta = [m for m in meta_all if m["phase"] == etapa]
        clr_etapa = ETAPA_HEADER_CLR.get(etapa, BRAND_PRIMARY)
        etapa_blocks.append({
            "etapa": etapa,
            "slug": ETAPA_SLUG[etapa],
            "meta": meta,
            "pct_col": ETAPA_PCT_COL[etapa],
            "tints": _etapa_hdr_tints(clr_etapa),
        })
        ncols += 1 + len(meta)
    ncols += 1

    TH = (
        f'style="background:{BRAND_PRIMARY};color:#FFFFFF;font-size:9px;font-weight:700;'
        'padding:6px 4px;text-align:center;white-space:nowrap;'
        'border-right:1px solid rgba(255,255,255,0.10)"'
    )
    TH_GEN = (
        f'class="th-pin-gen" style="background:{BRAND_PRIMARY};color:#FFFFFF;font-size:9px;font-weight:800;'
        'padding:8px 6px;text-align:center;white-space:normal;line-height:1.25;'
        f'border-left:2px solid {BRAND_HIGHLIGHT};min-width:88px"'
    )
    THL = (
        f'class="th-pin-left" style="background:{BRAND_PRIMARY};color:#FFFFFF;font-size:9px;font-weight:700;'
        'padding:6px 8px;text-align:left;white-space:nowrap;'
        'border-right:1px solid rgba(255,255,255,0.10);min-width:140px;max-width:200px"'
    )

    h1 = [
        f'<th rowspan="2" {THL}>Programa</th>',
        f'<th rowspan="2" {TH}>Facultad</th>',
        f'<th rowspan="2" {TH}>Modalidad</th>',
        f'<th rowspan="2" {TH}>Nivel</th>',
        f'<th rowspan="2" {TH}>Sede</th>',
        f'<th rowspan="2" {TH}>Período</th>',
    ]
    h2 = []
    for blk in etapa_blocks:
        slug, etapa, meta = blk["slug"], blk["etapa"], blk["meta"]
        t = blk["tints"]
        n_span_expanded = 1 + len(meta)
        short = etapa.replace(" Curricular", "")
        pct_lbl = f"% Av. {_short_label(short, 18)}"
        h1.append(
            f'<th id="hdr-etapa-{slug}" colspan="1" data-colspan-expanded="{n_span_expanded}"'
            f' class="hdr-etapa-{slug}"'
            f' style="background:{t["etapa_bg"]};color:{t["etapa_fg"]};'
            f'font-size:10px;font-weight:800;text-align:center;'
            f'border-right:1px solid rgba(255,255,255,0.15)">'
            f'<button type="button" id="btn-etapa-{slug}" onclick="toggleEtapa(\'{slug}\')" '
            f'style="cursor:pointer;border:1px solid rgba(255,255,255,0.55);background:rgba(255,255,255,0.15);'
            f'color:#fff;border-radius:4px;width:22px;height:22px;font-weight:800;margin-right:6px">+</button>'
            f'{_p_esc(short)}</th>'
        )
        th_act = (
            f'style="background:{t["act_bg"]};color:{t["act_fg"]};font-size:9px;font-weight:700;'
            f'text-align:center;white-space:normal;line-height:1.3;'
            f'word-break:break-word;overflow-wrap:anywhere;min-width:90px;max-width:180px;'
            f'border-right:1px solid {t["border"]};display:none"'
        )
        th_pct_etapa = (
            f'style="background:{t["pct_bg"]};color:{t["pct_fg"]};font-size:9px;font-weight:700;'
            f'text-align:center;white-space:normal;line-height:1.2;'
            f'border-right:1px solid {t["border"]};min-width:72px"'
        )
        for m in meta:
            h2.append(
                f'<th class="col-act-{slug}" {th_act} title="{_p_esc(m["name"])}">'
                f'{_p_esc(m["name"])}</th>'
            )
        h2.append(
            f'<th class="col-pct-{slug}" {th_pct_etapa} title="{_p_esc(etapa)}">{_p_esc(pct_lbl)}</th>'
        )

    h1.append(
        f'<th rowspan="2" {TH_GEN} title="Avance General de Reforma">'
        f'% Av.<br>General<br>Reforma</th>'
    )

    rows = []
    cur_per = None
    row_idx = 0
    sort_cols = [c for c in ("PERIODO DE IMPLEMENTACIÓN", "NOMBRE DEL PROGRAMA") if c in df.columns]
    df_sorted = df.sort_values(sort_cols) if sort_cols else df

    for _, row in df_sorted.iterrows():
        per = str(row.get("PERIODO DE IMPLEMENTACIÓN", "—")).strip()
        if per != cur_per:
            cur_per = per
            ph_clr = PERIODO_CLR.get(per, TEXT_LIGHT)
            per_cnt = int((df_sorted["PERIODO DE IMPLEMENTACIÓN"].astype(str).str.strip() == per).sum())
            rows.append(
                f'<tr><td colspan="{ncols}" style="background:{ph_clr};color:#FFFFFF;'
                f'font-size:11px;font-weight:800;padding:7px 12px;letter-spacing:.3px">'
                f'{_p_esc(per)} · {per_cnt} PROGRAMAS</td></tr>'
            )
            row_idx = 0
        rbg = BG_ROW if row_idx % 2 == 0 else BG_ROW_ALT
        row_idx += 1
        TD = (
            f'style="padding:4px 3px;text-align:center;vertical-align:middle;'
            f'border-bottom:1px solid {BORDER_ROW};background:{rbg}"'
        )
        TDL = (
            f'style="padding:4px 6px;text-align:left;vertical-align:middle;'
            f'border-bottom:1px solid {BORDER_ROW};background:{rbg};min-width:140px;max-width:200px;'
            f'position:sticky;left:0;z-index:1;box-shadow:2px 0 4px rgba(0,0,0,.04)"'
        )
        prog = _p_esc(row.get("NOMBRE DEL PROGRAMA", "—"))
        fac_s = row.get("FACULTAD_ABREV", "—")
        fac_c = row.get("FACULTAD_COLOR", "#9aabb5")
        mod = str(row.get("MODALIDAD", "—"))
        mod_c = MODALIDAD_CLR.get(mod, TEXT_LIGHT)
        per_c = PERIODO_CLR.get(per, TEXT_LIGHT)
        nivel = row.get("NIVEL_HOMOLOGADO", row.get("NIVEL", "—"))

        cells = [
            f'<td {TDL}><span style="font-size:11px;font-weight:600;color:{TEXT_PRIMARY}">{prog}</span></td>',
            f'<td {TD}><span style="font-size:10px;font-weight:700;color:{fac_c}">{_p_esc(fac_s)}</span></td>',
            f'<td {TD}>{badge_html(mod, mod_c)}</td>',
            f'<td {TD}><span style="font-size:10px;color:{TEXT_SUBTLE}">{_p_esc(nivel)}</span></td>',
            f'<td {TD}><span style="font-size:10px;color:{TEXT_SUBTLE}">{_p_esc(row.get("SEDE", "—"))}</span></td>',
            f'<td {TD}>{badge_html(per, per_c)}</td>',
        ]
        for blk in etapa_blocks:
            slug = blk["slug"]
            t = blk["tints"]
            pct = float(row.get(blk["pct_col"], 0) or 0)
            act_bg = t["cell_act_alt"] if row_idx % 2 == 0 else t["cell_act"]
            for m in blk["meta"]:
                cl = row.get(f"cl_act_{m['idx']}", "na")
                val = row.get(f"val_act_{m['idx']}", "—")
                cells.append(
                    f'<td class="col-act-{slug}" style="display:none;padding:4px 3px;text-align:center;'
                    f'vertical-align:middle;border-bottom:1px solid {BORDER_ROW};background:{act_bg}">'
                    f'{_vact_act_icon(cl, val)}</td>'
                )
            cells.append(
                f'<td class="col-pct-{slug}" style="padding:4px 3px;text-align:center;'
                f'vertical-align:middle;border-bottom:1px solid {BORDER_ROW};background:{rbg}">'
                f'{p_bar_html(pct)}</td>'
            )
        gen_pct = float(row.get("avance_general_vact", 0) or 0)
        cells.append(
            f'<td class="col-pct-general" {TD} style="border-left:2px solid {BORDER_ROW}">'
            f'{p_bar_html(gen_pct)}</td>'
        )
        rows.append("<tr>" + "".join(cells) + "</tr>")

    if not rows:
        return f"<p style='padding:20px;color:{TEXT_MUTED}'>No hay programas con los filtros seleccionados.</p>"

    return (
        _TOGGLE_JS
        + _MASTER_TABLE_CSS
        + '<div class="vact-table-scroller">'
        '<table class="vact-master-table">'
        '<thead><tr class="hdr-etapa">' + "".join(h1) + '</tr><tr class="hdr-act">' + "".join(h2) + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
        + _status_legend_html()
    )


def _render_master_table(df: pd.DataFrame):
    if len(df) == 0:
        st.info("Sin programas para los filtros seleccionados.")
        return
    n_per = df["PERIODO DE IMPLEMENTACIÓN"].nunique() if "PERIODO DE IMPLEMENTACIÓN" in df.columns else 0
    h = min(120 + 42 * len(df) + 42 * n_per, 900)
    html_comp.html(_master_activities_table_html(df), height=h, scrolling=False)


def _excel_export_bytes(df: pd.DataFrame) -> bytes:
    export = df[
        [
            "NOMBRE DEL PROGRAMA",
            "FACULTAD",
            "ESCUELA",
            "MODALIDAD",
            "NIVEL",
            "SEDE",
            "PERIODO DE IMPLEMENTACIÓN",
            "pct_alistamiento",
            "pct_diseno",
            "pct_desarrollo",
            "pct_implementacion",
            "avance_general_vact",
        ]
    ].copy()
    export.columns = [
        "Programa",
        "Facultad",
        "Escuela",
        "Modalidad",
        "Nivel",
        "Sede",
        "Período",
        "% Alistamiento",
        "% Diseño",
        "% Desarrollo",
        "% Implementación",
        "% General",
    ]
    buf = io.BytesIO()
    export.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    return buf.getvalue()


def _render_filter_summary(df: pd.DataFrame):
    n = len(df)
    gen_avg = round(float(df["avance_general_vact"].mean()), 1) if n else 0
    gen_color = BRAND_PRIMARY
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid rgba(15,56,90,0.10);border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(15,56,90,0.07)">'
        f'<div style="display:flex;align-items:center;justify-content:space-between">'
        f'<div><div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY}">Programas en el filtro actual</div>'
        f'<div style="font-size:12px;color:{TEXT_MUTED};margin-top:4px">{n} programa(s) · Avance general promedio <b style="color:{gen_color}">{gen_avg:.0f}%</b></div></div>'
        f'<div style="background:{gen_color}22;border:2px solid {gen_color};border-radius:12px;padding:12px 20px;text-align:center">'
        f'<div style="font-size:24px;font-weight:800;color:{gen_color}">{gen_avg:.0f}%</div>'
        f'<div style="font-size:10px;color:{gen_color}">Promedio general</div></div>'
        f'</div></div>',
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
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">Fase 2 · Detalle por Etapa</div></div>',
    unsafe_allow_html=True,
)

# Filtros
_render_filter_bar("global", show_count=True)

# Contenido
df, *_ = _apply_current_filters()

if len(df) == 0:
    st.warning("No hay programas con los filtros actuales.")
else:
    st.markdown(f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">📋 Detalle por Etapa</div>', unsafe_allow_html=True)
    
    _render_filter_summary(df)
    
    st.markdown(f'<div style="font-size:12px;color:{TEXT_MUTED};margin:12px 0">Pulse + en el encabezado de cada etapa para ver sus actividades.</div>', unsafe_allow_html=True)
    
    _render_master_table(df)
    
    st.download_button(
        "⬇ Descargar Excel",
        data=_excel_export_bytes(df),
        file_name="reforma_curricular_fase2.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )