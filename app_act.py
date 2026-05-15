"""
app_act.py — Dashboard Fase 2: Reforma Curricular por Etapas (VACT)
Fuente: hoja Etapas · CONTROL MAESTRO DE REFORMA CURRICULAR_VACT.xlsx
"""

import html as html_lib
import io
import json
import math
import time
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

st.set_page_config(
    page_title="Reforma Curricular · Fase 2 · POLI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

_DEBUG_LOG = Path(__file__).resolve().parent / "debug-758968.log"


def _dbg_log(hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    # #region agent log
    try:
        payload = {
            "sessionId": "758968",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000),
        }
        with open(_DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass
    # #endregion


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

# ── CSS global (filtros + Gantt Fase 2) ───────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #EEF3F8; }
[data-testid="stHeader"] {
    background: linear-gradient(135deg, #0F385A 0%, #1A5276 50%, #1FB2DE 100%) !important;
    border-bottom: 3px solid #42F2F2 !important;
}
h1,h2,h3,h4 { font-family: 'Segoe UI', sans-serif; color: #0F385A !important; }
.block-container { padding-top: 3.5rem !important; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F385A 0%, #1A5276 45%, #1FB2DE 100%) !important;
}
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
    color: rgba(255,255,255,0.80) !important;
}
[data-testid="stPills"] button {
    border: 2px solid #1A5276 !important; color: #1A5276 !important;
    background: #FFFFFF !important; border-radius: 20px !important;
    font-size: 12px !important; font-weight: 600 !important;
}
[data-testid="stPills"] button[aria-checked="true"],
[data-testid="stPills"] button[aria-pressed="true"] {
    background: #0F385A !important; color: #FFFFFF !important; border-color: #0F385A !important;
}
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg,#1FB2DE,#0891b2) !important;
    border-color: #1FB2DE !important; color: #FFFFFF !important;
    font-size: 11px !important; font-weight: 700 !important; border-radius: 8px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #0F385A !important; border-bottom-color: #1FB2DE !important; font-weight: 700 !important;
}
/* ── Fase 2: tarjetas etapa ── */
.f2-scard {
    background: #fff; border-radius: 12px; padding: 16px 18px;
    border-left: 5px solid var(--accent, #1FB2DE);
    box-shadow: 0 2px 8px rgba(15,56,90,0.08); height: 100%;
}
.f2-scard-title { font-size: 11px; font-weight: 700; color: #6a8a9e;
    text-transform: uppercase; letter-spacing: .5px; margin-bottom: 6px; }
.f2-scard-pct { font-size: 36px; font-weight: 800; color: #0F385A; line-height: 1; }
.f2-scard-sub { font-size: 11px; color: #6a8a9e; margin-top: 6px; }
.f2-bar-wrap { height: 8px; background: #e2e8f0; border-radius: 4px; margin-top: 10px; overflow: hidden; }
.f2-bar-fill { height: 100%; border-radius: 4px; transition: width .3s; }
/* ── Gantt ── */
.f2-gantt { font-family: 'Segoe UI', sans-serif; }
.f2-gantt-row { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.f2-gantt-label { width: 200px; flex-shrink: 0; font-size: 12px; font-weight: 600; color: #0F385A; }
.f2-gantt-track { flex: 1; height: 28px; background: #e8eef4; border-radius: 6px; overflow: hidden; position: relative; }
.f2-gantt-fill { height: 100%; border-radius: 6px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; min-width: 36px; }
.f2-gantt-pct { font-size: 12px; font-weight: 700; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,.25); }
.f2-gantt-pct-out { width: 48px; text-align: right; font-size: 13px; font-weight: 700; color: #0F385A; flex-shrink: 0; }
.f2-gantt-general .f2-gantt-label { font-weight: 800; }
.f2-gantt-general .f2-gantt-track { height: 34px; }
/* ── Programa card ── */
.f2-prog-card {
    background: #fff; border-radius: 12px; padding: 18px 22px;
    box-shadow: 0 2px 10px rgba(15,56,90,0.09); margin-bottom: 16px;
    display: flex; gap: 24px; align-items: stretch; flex-wrap: wrap;
}
.f2-prog-info { flex: 1; min-width: 280px; }
.f2-prog-info h3 { margin: 0 0 12px; font-size: 18px; color: #0F385A; }
.f2-prog-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 20px; font-size: 13px; }
.f2-prog-grid span.lbl { color: #6a8a9e; font-size: 10px; text-transform: uppercase; letter-spacing: .4px; display: block; }
.f2-prog-badge {
    min-width: 120px; text-align: center; padding: 16px; border-radius: 12px;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
}
.f2-prog-badge-pct { font-size: 42px; font-weight: 800; line-height: 1; }
.f2-prog-badge-lbl { font-size: 10px; text-transform: uppercase; letter-spacing: .5px; margin-top: 6px; opacity: .85; }
</style>
""", unsafe_allow_html=True)

# ── Datos ─────────────────────────────────────────────────────────────────────
df_raw = load_etapas_data()

fac_abrev_inv = FAC_ABREV_INV
fac_ops = sorted(df_raw["FACULTAD_ABREV"].dropna().unique().tolist()) if "FACULTAD_ABREV" in df_raw.columns else []
mods_ops = sorted(df_raw["MODALIDAD"].dropna().unique().tolist()) if "MODALIDAD" in df_raw.columns else []
pers_ops = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist()) if "PERIODO DE IMPLEMENTACIÓN" in df_raw.columns else []
niveles_ops = [n for n in ["Pregrado", "Posgrado"] if n in df_raw.get("NIVEL_HOMOLOGADO", pd.Series(dtype=str)).values]

_use_pills = hasattr(st, "pills")
_LBL = 'style="padding-top:8px;font-size:11px;font-weight:700;color:#0F385A;letter-spacing:.4px;white-space:nowrap"'


def _esc(s):
    return html_lib.escape(str(s) if s is not None else "—")


# ── Helpers HTML (patrón Priorización · app.py) ─────────────────────────────
def _p_esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _p_bar(pct):
    try:
        pct = float(pct if pct is not None else 0)
    except Exception:
        pct = 0.0
    if math.isnan(pct):
        pct = 0.0
    clr = "#15803d" if pct >= 70 else ("#d97706" if pct >= 40 else "#dc2626")
    bar = "#22c55e" if pct >= 70 else ("#f59e0b" if pct >= 40 else "#ef4444")
    return (
        f'<div style="min-width:70px;text-align:center">'
        f'<div style="font-size:12px;font-weight:700;color:{clr};margin-bottom:3px">{int(pct)}%</div>'
        f'<div style="height:6px;background:#e2e8f0;border-radius:4px;overflow:hidden">'
        f'<div style="width:{min(pct, 100):.0f}%;height:100%;background:{bar};border-radius:4px;'
        f'box-shadow:0 1px 2px rgba(0,0,0,.15)"></div></div></div>'
    )


_PER_HDR_CLR = {"2026-2": "#A6CE38", "2027-1": "#FBAF17", "2027-2": "#EC0677"}
_MOD_CLR = {"Presencial": "#1FB2DE", "Virtual": "#EC0677", "Distancia": "#A6CE38"}

_VACT_ACT_EMOJI = {
    "done": "✅",
    "inprog": "⚠️",
    "nostart": "🔴",
    "devuelto": "↩️",
    "info": "ℹ️",
}


def _p_badge(txt, clr):
    r, g, b = int(clr[1:3], 16), int(clr[3:5], 16), int(clr[5:7], 16)
    return (
        f'<span style="background:rgba({r},{g},{b},0.12);color:{clr};font-size:10px;'
        f'font-weight:700;padding:3px 9px;border-radius:12px;white-space:nowrap">{_p_esc(txt)}</span>'
    )


def _vact_act_icon(cl: str, val=None) -> str:
    lbl = STATUS_LABEL.get(cl, cl)
    if cl == "info" and val and str(val).strip() not in ("—", "", "nan", "None"):
        return (
            f'<span style="font-size:10px;color:#4a6a7e;display:inline-block;max-width:90px;'
            f'line-height:1.2;word-break:break-word" title="{_p_esc(lbl)}">{_p_esc(str(val)[:24])}</span>'
        )
    if cl == "na":
        return (
            f'<span style="color:#b0bec5;font-size:13px;font-weight:600" title="{_p_esc(lbl)}">N/A</span>'
        )
    emoji = _VACT_ACT_EMOJI.get(cl, "—")
    return f'<span style="font-size:16px" title="{_p_esc(lbl)}">{emoji}</span>'


def _status_legend_html() -> str:
    parts = []
    for cl in ("done", "inprog", "nostart", "devuelto", "info", "na"):
        lbl = STATUS_LABEL.get(cl, cl)
        if cl == "na":
            icon = '<span style="color:#b0bec5;font-weight:600">N/A</span>'
        else:
            icon = f'<span style="font-size:14px">{_VACT_ACT_EMOJI.get(cl, "")}</span>'
        parts.append(
            f'<span style="margin-right:16px;font-size:11px;color:#6a8a9e">{icon} {lbl}</span>'
        )
    return (
        '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:8px;padding:8px 4px">'
        + "".join(parts)
        + '<span style="font-size:10px;color:#9aabb5;margin-left:8px">'
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
    """Barra de filtros (mismo formato que app.py)."""
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
                    f'<div style="padding-top:9px;font-size:12px;color:#6a8a9e;text-align:right">'
                    f'Mostrando <b style="color:#0F385A">{len(df_tmp)}</b> de '
                    f'<b style="color:#0F385A">{len(df_raw)}</b></div>',
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

    hdr = f'<div style="font-size:13px;font-weight:700;color:#0F385A;margin:12px 0 8px">{_esc(title)}</div>' if title else ""
    return f'<div class="f2-gantt">{hdr}{"".join(rows_html)}</div>'


def _short_label(text: str, max_len: int = 28) -> str:
    t = str(text).strip()
    return t if len(t) <= max_len else t[: max_len - 1] + "…"


def _render_filter_summary(df: pd.DataFrame):
    """Tarjeta resumen del filtro actual."""
    # #region agent log
    _dbg_log(
        "H1",
        "app_act.py:_render_filter_summary",
        "called",
        {"n_programas": len(df), "defined": True},
    )
    # #endregion
    n = len(df)
    gen_avg = round(float(df["avance_general_vact"].mean()), 1) if n else 0
    gen_color = color_for_pct(gen_avg)
    st.markdown(
        f'<div class="f2-prog-card"><div class="f2-prog-info"><h3>Programas en el filtro actual</h3>'
        f'<p style="color:#6a8a9e;font-size:13px;margin:0"><b style="color:#0F385A">{n}</b> programa(s) · '
        f'Avance general promedio <b style="color:{gen_color}">{gen_avg:.0f}%</b><br>'
        f'Use <b>+</b> en cada etapa de la tabla para ver actividades.</p></div>'
        f'<div class="f2-prog-badge" style="background:{gen_color}22;border:2px solid {gen_color}">'
        f'<div class="f2-prog-badge-pct" style="color:{gen_color}">{gen_avg:.0f}%</div>'
        f'<div class="f2-prog-badge-lbl" style="color:{gen_color}">Promedio general</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )


_TOGGLE_JS = """
<script>
function toggleEtapa(slug) {
  var cols = document.querySelectorAll('.col-act-' + slug);
  var btn = document.getElementById('btn-etapa-' + slug);
  if (!cols.length || !btn) return;
  var show = cols[0].style.display === 'none';
  for (var i = 0; i < cols.length; i++) {
    cols[i].style.display = show ? 'table-cell' : 'none';
  }
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

    TH = (
        'style="background:#0F385A;color:#FFFFFF;font-size:9px;font-weight:700;'
        'padding:6px 4px;text-align:center;white-space:nowrap;position:sticky;top:0;z-index:2;'
        'border-right:1px solid rgba(255,255,255,0.10)"'
    )
    THL = (
        'style="background:#0F385A;color:#FFFFFF;font-size:9px;font-weight:700;'
        'padding:6px 8px;text-align:left;white-space:nowrap;position:sticky;top:0;left:0;z-index:4;'
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
        clr = ETAPA_HEADER_CLR.get(etapa, "#0F385A")
        r, g, b = int(clr[1:3], 16), int(clr[3:5], 16), int(clr[5:7], 16)
        n_span = 1 + len(meta)
        short = etapa.replace(" Curricular", "")
        h1.append(
            f'<th colspan="{n_span}" style="background:rgba({r},{g},{b},0.18);color:{clr};'
            f'font-size:10px;font-weight:800;padding:6px 8px;text-align:center;'
            f'border-right:1px solid rgba(255,255,255,0.10);position:sticky;top:0;z-index:2">'
            f'<button type="button" id="btn-etapa-{slug}" onclick="toggleEtapa(\'{slug}\')" '
            f'style="cursor:pointer;border:1px solid {clr};background:#fff;color:{clr};'
            f'border-radius:4px;width:22px;height:22px;font-weight:800;margin-right:6px">+</button>'
            f'{_p_esc(short)}</th>'
        )
        h2.append(f'<th {TH}>% Av.</th>')
        for m in meta:
            h2.append(
                f'<th class="col-act-{slug}" {TH} style="display:none" title="{_p_esc(m["name"])}">'
                f'{_p_esc(_short_label(m["name"], 22))}</th>'
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
            ph_clr = _PER_HDR_CLR.get(per, "#9aabb5")
            per_cnt = int((df_sorted["PERIODO DE IMPLEMENTACIÓN"].astype(str).str.strip() == per).sum())
            rows.append(
                f'<tr><td colspan="{ncols}" style="background:{ph_clr};color:#FFFFFF;'
                f'font-size:11px;font-weight:800;padding:7px 12px;letter-spacing:.3px">'
                f'{_p_esc(per)} · {per_cnt} PROGRAMAS</td></tr>'
            )
            row_idx = 0
        rbg = "#FFFFFF" if row_idx % 2 == 0 else "#f8fafc"
        row_idx += 1
        TD = (
            f'style="padding:4px 3px;text-align:center;vertical-align:middle;'
            f'border-bottom:1px solid #eef3f8;background:{rbg}"'
        )
        TDL = (
            f'style="padding:4px 6px;text-align:left;vertical-align:middle;'
            f'border-bottom:1px solid #eef3f8;background:{rbg};min-width:140px;max-width:200px;'
            f'position:sticky;left:0;z-index:1;box-shadow:2px 0 4px rgba(0,0,0,.04)"'
        )
        prog = _p_esc(row.get("NOMBRE DEL PROGRAMA", "—"))
        fac_s = row.get("FACULTAD_ABREV", "—")
        fac_c = row.get("FACULTAD_COLOR", "#9aabb5")
        mod = str(row.get("MODALIDAD", "—"))
        mod_c = _MOD_CLR.get(mod, "#9aabb5")
        per_c = _PER_HDR_CLR.get(per, "#9aabb5")
        nivel = row.get("NIVEL_HOMOLOGADO", row.get("NIVEL", "—"))

        cells = [
            f'<td {TDL}><span style="font-size:11px;font-weight:600;color:#0F385A">{prog}</span></td>',
            f'<td {TD}><span style="font-size:10px;font-weight:700;color:{fac_c}">{_p_esc(fac_s)}</span></td>',
            f'<td {TD}>{_p_badge(mod, mod_c)}</td>',
            f'<td {TD}><span style="font-size:10px;color:#4a6a7e">{_p_esc(nivel)}</span></td>',
            f'<td {TD}><span style="font-size:10px;color:#4a6a7e">{_p_esc(row.get("SEDE", "—"))}</span></td>',
            f'<td {TD}>{_p_badge(per, per_c)}</td>',
        ]
        for blk in etapa_blocks:
            slug = blk["slug"]
            pct = float(row.get(blk["pct_col"], 0) or 0)
            cells.append(f'<td {TD}>{_p_bar(pct)}</td>')
            for m in blk["meta"]:
                cl = row.get(f"cl_act_{m['idx']}", "na")
                val = row.get(f"val_act_{m['idx']}", "—")
                cells.append(
                    f'<td class="col-act-{slug}" {TD} style="display:none">'
                    f'{_vact_act_icon(cl, val)}</td>'
                )
        rows.append("<tr>" + "".join(cells) + "</tr>")

    if not rows:
        return "<p style='padding:20px;color:#6a8a9e'>No hay programas con los filtros seleccionados.</p>"

    return (
        _TOGGLE_JS
        + '<div style="overflow-x:auto;border-radius:12px;border:1.5px solid #b5c9d8;'
        'box-shadow:0 2px 12px rgba(15,56,90,.10);background:#fafdff">'
        '<table style="width:100%;table-layout:auto;border-collapse:separate;border-spacing:0;'
        'font-family:\'Segoe UI\',sans-serif;min-width:max-content">'
        "<thead><tr>" + "".join(h1) + "</tr><tr>" + "".join(h2) + "</tr></thead><tbody>"
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
    html_comp.html(_master_activities_table_html(df), height=h, scrolling=True)



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
    "background:linear-gradient(135deg,#0F385A 0%,#1A5276 50%,#1FB2DE 100%);"
    'padding:18px 24px 14px;border-radius:0 0 12px 12px;border-bottom:3px solid #42F2F2;">'
    '<div style="font-size:21px;font-weight:700;color:#FFFFFF">'
    "Reforma Curricular de Programas Académicos Poli</div>"
    '<div style="font-size:12px;color:rgba(255,255,255,0.70);margin-top:5px">'
    "Fase 2 · Seguimiento de avance por etapa de reforma</div></div>",
    unsafe_allow_html=True,
)

# #region agent log
_dbg_log(
    "H1",
    "app_act.py:module",
    "pre_tabs_symbol_check",
    {"has_render_filter_summary": callable(globals().get("_render_filter_summary"))},
)
# #endregion

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_avance, tab_detalle, tab_programas = st.tabs(
    ["📊 Avance General", "📋 Detalle por Etapa", "🏛️ Por Programa"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: Avance General
# ══════════════════════════════════════════════════════════════════════════════
with tab_avance:
    _render_filter_bar("t1")
    df, *_ = _apply_current_filters()
    n = len(df)

    _render_filter_summary(df)

    if n == 0:
        st.warning("No hay programas que coincidan con los filtros seleccionados.")
    else:
        st.markdown(
            '<div style="font-size:14px;font-weight:700;color:#0F385A;margin:16px 0 8px">'
            "Resumen por etapa (promedio del filtro)</div>",
            unsafe_allow_html=True,
        )
        _render_stage_cards(df)

        st.markdown(
            '<div style="font-size:14px;font-weight:700;color:#0F385A;margin:20px 0 8px">'
            "Línea de avance (Gantt)</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            _render_gantt_bars(df=df, title="Promedio de programas filtrados"),
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="font-size:14px;font-weight:700;color:#0F385A;margin:24px 0 8px">'
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
    _render_filter_bar("t2", show_count=False)
    df, *_ = _apply_current_filters()

    if len(df) == 0:
        st.warning("No hay programas con los filtros actuales.")
    else:
        _render_filter_summary(df)
        st.markdown(
            '<div style="font-size:13px;color:#6a8a9e;margin:12px 0">'
            "Tabla única por programa. Pulse + en el encabezado de cada etapa para ver sus actividades.</div>",
            unsafe_allow_html=True,
        )
        _render_master_table(df)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: Por Programa
# ══════════════════════════════════════════════════════════════════════════════
with tab_programas:
    _render_filter_bar("t3", show_count=False)
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
