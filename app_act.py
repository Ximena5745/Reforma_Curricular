"""
app_act.py — Dashboard Fase 2: Reforma Curricular por Etapas (VACT)
Fuente: hoja Etapas · CONTROL MAESTRO DE REFORMA CURRICULAR_VACT.xlsx
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
    color_for_pct,
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
)

st.set_page_config(
    page_title="Reforma Curricular · Fase 2 · POLI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

def _registered_page_targets() -> set[str]:
    """Rutas/nombres de script registrados como páginas Streamlit."""
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
    """Solo enlaza si la página existe en el registro multipágina actual."""
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


def _vact_act_icon(cl: str, val=None) -> str:
    lbl = STATUS_LABEL.get(cl, cl)
    if cl == "info" and val and str(val).strip() not in ("—", "", "nan", "None"):
        return (
            f'<span style="font-size:10px;color:{TEXT_SUBTLE};display:inline-block;max-width:90px;'
            f'line-height:1.2;word-break:break-word" title="{_p_esc(lbl)}">{_p_esc(str(val)[:24])}</span>'
        )
    if cl == "na":
        return (
            f'<span style="color:{TEXT_NA};font-size:13px;font-weight:600" title="{_p_esc(lbl)}">N/A</span>'
        )
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
    """Barra de filtros (mismo formato que app.py). Una sola instancia por página."""
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


def _mini_bar(pct: float, color: str) -> str:
    w = min(max(float(pct), 0), 100)
    return (
        f'<div class="f2-bar-wrap"><div class="f2-bar-fill" '
        f'style="width:{w:.0f}%;background:{color}"></div></div>'
    )


def _render_stage_cards(df: pd.DataFrame):
    cols = st.columns(len(ETAPAS_ORDEN) + 1)
    for i, etapa in enumerate(ETAPAS_ORDEN):
        pct_col = ETAPA_PCT_COL[etapa]
        avg = round(float(df[pct_col].mean()), 1) if len(df) and pct_col in df.columns else 0
        color = color_for_pct(avg)
        with cols[i]:
            st.markdown(
                f'<div class="f2-scard" style="--accent:{color}">'
                f'<div class="f2-scard-title">% Avance {_esc(etapa)}</div>'
                f'<div class="f2-scard-pct" style="color:{color}">{avg:.0f}%</div>'
                f'<div class="f2-scard-sub">Promedio · {len(df)} programa(s)</div>'
                f'{_mini_bar(avg, color)}</div>',
                unsafe_allow_html=True,
            )

    gen_avg = round(float(df["avance_general_vact"].mean()), 1) if len(df) else 0
    gen_color = color_for_pct(gen_avg)
    with cols[-1]:
        st.markdown(
            f'<div class="f2-scard" style="--accent:{gen_color};border-left-width:6px">'
            f'<div class="f2-scard-title">% Avance General de Reforma</div>'
            f'<div class="f2-scard-pct" style="color:{gen_color}">{gen_avg:.0f}%</div>'
            f'<div class="f2-scard-sub">Consolidado por programa</div>'
            f'{_mini_bar(gen_avg, gen_color)}</div>',
            unsafe_allow_html=True,
        )


def _render_gantt_bars(row=None, df: pd.DataFrame | None = None, title: str = ""):
    """Barras Gantt horizontales: una por etapa + consolidado."""
    rows_html = []
    items = [("Avance General de Reforma", "avance_general_vact", True)]
    for etapa in ETAPAS_ORDEN:
        items.append((etapa, ETAPA_PCT_COL[etapa], False))

    for label, col_key, is_general in items:
        if row is not None:
            pct = float(row.get(col_key, 0) or 0)
        elif df is not None and len(df):
            pct = round(float(df[col_key].mean()), 1) if col_key in df.columns else 0
        else:
            pct = 0
        color = color_for_pct(pct)
        short = label.replace(" Curricular", "").replace("Avance General de Reforma", "General")
        cls = "f2-gantt-row f2-gantt-general" if is_general else "f2-gantt-row"
        rows_html.append(
            f'<div class="{cls}">'
            f'<div class="f2-gantt-label">{_esc(short)}</div>'
            f'<div class="f2-gantt-track">'
            f'<div class="f2-gantt-fill" style="width:{min(pct,100):.0f}%;background:{color}">'
            f'<span class="f2-gantt-pct">{pct:.0f}%</span></div></div>'
            f'<div class="f2-gantt-pct-out">{pct:.0f}%</div></div>'
        )

    hdr = f'<div style="font-size:13px;font-weight:700;color:{TEXT_PRIMARY};margin:12px 0 8px">{_esc(title)}</div>' if title else ""
    return f'<div class="f2-gantt">{hdr}{"".join(rows_html)}</div>'


def _short_label(text: str, max_len: int = 28) -> str:
    t = str(text).strip()
    return t if len(t) <= max_len else t[: max_len - 1] + "…"


def _render_filter_summary(df: pd.DataFrame):
    """Tarjeta resumen del filtro actual."""
    n = len(df)
    gen_avg = round(float(df["avance_general_vact"].mean()), 1) if n else 0
    gen_color = color_for_pct(gen_avg)
    st.markdown(
        f'<div class="f2-prog-card"><div class="f2-prog-info"><h3>Programas en el filtro actual</h3>'
        f'<p style="color:{TEXT_MUTED};font-size:13px;margin:0"><b style="color:{TEXT_PRIMARY}">{n}</b> programa(s) · '
        f'Avance general promedio <b style="color:{gen_color}">{gen_avg:.0f}%</b><br>'
        f'Use <b>+</b> en cada etapa de la tabla para ver actividades.</p></div>'
        f'<div class="f2-prog-badge" style="background:{gen_color}22;border:2px solid {gen_color}">'
        f'<div class="f2-prog-badge-pct" style="color:{gen_color}">{gen_avg:.0f}%</div>'
        f'<div class="f2-prog-badge-lbl" style="color:{gen_color}">Promedio general</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )


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
  background-clip: padding-box;
}}
.vact-master-table thead tr.hdr-act th {{
  position: sticky;
  top: 40px;
  z-index: 3;
  background-clip: padding-box;
  box-shadow: 0 2px 4px rgba(15,56,90,0.08);
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


def _master_activities_table_html(df: pd.DataFrame) -> str:
    meta_all = _ensure_activities_meta(df)
    etapa_blocks = []
    ncols = 6
    for etapa in ETAPAS_ORDEN:
        meta = [m for m in meta_all if m["phase"] == etapa]
        etapa_blocks.append({
            "etapa": etapa,
            "slug": ETAPA_SLUG[etapa],
            "meta": meta,
            "pct_col": ETAPA_PCT_COL[etapa],
        })
        ncols += 1 + len(meta)
    ncols += 1  # columna % Avance General Reforma

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
        clr = ETAPA_HEADER_CLR.get(etapa, BRAND_PRIMARY)
        r, g, b = int(clr[1:3], 16), int(clr[3:5], 16), int(clr[5:7], 16)
        n_span_expanded = 1 + len(meta)
        short = etapa.replace(" Curricular", "")
        pct_lbl = f"% Av. {_short_label(short, 18)}"
        h1.append(
            f'<th id="hdr-etapa-{slug}" colspan="1" data-colspan-expanded="{n_span_expanded}"'
            f' class="hdr-etapa-{slug}"'
            f' style="background:rgba({r},{g},{b},0.92);color:{clr};'
            f'font-size:10px;font-weight:800;padding:6px 8px;text-align:center;'
            f'border-right:1px solid rgba(255,255,255,0.10)">'
            f'<button type="button" id="btn-etapa-{slug}" onclick="toggleEtapa(\'{slug}\')" '
            f'style="cursor:pointer;border:1px solid {clr};background:#fff;color:{clr};'
            f'border-radius:4px;width:22px;height:22px;font-weight:800;margin-right:6px">+</button>'
            f'{_p_esc(short)}</th>'
        )
        th_act = (
            f'style="background:rgba({r},{g},{b},0.95);color:{clr};font-size:9px;font-weight:700;'
            f'padding:6px 5px;text-align:center;white-space:normal;line-height:1.3;'
            f'word-break:break-word;overflow-wrap:anywhere;min-width:90px;max-width:180px;'
            f'vertical-align:bottom;'
            f'border-right:1px solid rgba({r},{g},{b},0.35);display:none"'
        )
        th_pct_etapa = (
            f'style="background:rgba({r},{g},{b},0.90);color:{clr};font-size:9px;font-weight:700;'
            f'padding:6px 4px;text-align:center;white-space:normal;line-height:1.2;'
            f'border-right:1px solid rgba({r},{g},{b},0.25);min-width:72px"'
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
            pct = float(row.get(blk["pct_col"], 0) or 0)
            for m in blk["meta"]:
                cl = row.get(f"cl_act_{m['idx']}", "na")
                val = row.get(f"val_act_{m['idx']}", "—")
                cells.append(
                    f'<td class="col-act-{slug}" {TD} style="display:none">'
                    f'{_vact_act_icon(cl, val)}</td>'
                )
            cells.append(f'<td class="col-pct-{slug}" {TD}>{p_bar_html(pct)}</td>')
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
    if not _safe_page_link("app.py", label="Fase 1 · Producción", icon="📊"):
        st.caption("Fase 1 no disponible en este despliegue (entrada: app_act.py).")
    _safe_page_link("app_act.py", label="Fase 2 · Etapas (VACT)", icon="📋")
    st.markdown("<hr style='margin:10px 0'>", unsafe_allow_html=True)
    st.markdown(
        '<div style="padding:12px;font-size:10px;color:rgba(255,255,255,.4);text-align:center">'
        "POLI · VACT · 2025–2026</div>",
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
    "Fase 2 · Seguimiento de avance por etapa de reforma</div></div>",
    unsafe_allow_html=True,
)


# Filtros globales (una sola vez; evita StreamlitDuplicateElementKey en tabs)
_render_filter_bar("global", show_count=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_avance, tab_detalle, tab_programas = st.tabs(
    ["📊 Avance General", "📋 Detalle por Etapa", "🏛️ Por Programa"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: Avance General
# ══════════════════════════════════════════════════════════════════════════════
with tab_avance:
    df, *_ = _apply_current_filters()
    n = len(df)

    _render_filter_summary(df)

    if n == 0:
        st.warning("No hay programas que coincidan con los filtros seleccionados.")
    else:
        st.markdown(
            f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin:16px 0 8px">'
            "Resumen por etapa (promedio del filtro)</div>",
            unsafe_allow_html=True,
        )
        _render_stage_cards(df)

        st.markdown(
            f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 8px">'
            "Línea de avance (Gantt)</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            _render_gantt_bars(df=df, title="Promedio de programas filtrados"),
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin:24px 0 8px">'
            "Estado de actividades · todos los programas</div>",
            unsafe_allow_html=True,
        )
        _render_master_table(df)

        st.download_button(
            "⬇ Descargar Excel",
            data=_excel_export_bytes(df),
            file_name="reforma_curricular_fase2.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: Detalle por Etapa
# ══════════════════════════════════════════════════════════════════════════════
with tab_detalle:
    df, *_ = _apply_current_filters()

    if len(df) == 0:
        st.warning("No hay programas con los filtros actuales.")
    else:
        _render_filter_summary(df)
        st.markdown(
            f'<div style="font-size:13px;color:{TEXT_MUTED};margin:12px 0">'
            "Tabla única por programa. Pulse + en el encabezado de cada etapa para ver sus actividades.</div>",
            unsafe_allow_html=True,
        )
        _render_master_table(df)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: Por Programa
# ══════════════════════════════════════════════════════════════════════════════
with tab_programas:
    df, *_ = _apply_current_filters()

    if len(df) == 0:
        st.warning("No hay programas con los filtros actuales.")
    else:
        _render_filter_summary(df)

        _render_master_table(df)

        st.download_button(
            "⬇ Descargar Excel",
            data=_excel_export_bytes(df),
            file_name="reforma_curricular_fase2.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tab3",
        )
