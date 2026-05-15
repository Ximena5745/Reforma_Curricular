"""
app_act.py — Dashboard Fase 2: Reforma Curricular por Etapas (VACT)
Fuente: hoja Etapas · CONTROL MAESTRO DE REFORMA CURRICULAR_VACT.xlsx
"""

import html as html_lib
import io
import json
import time
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as html_comp

from utils.data_loader_vact import (
    ETAPAS_ORDEN,
    ETAPA_PCT_COL,
    FAC_ABREV_INV,
    STATUS_COLOR,
    STATUS_LABEL,
    _activity_score,
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


def _agent_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
    try:
        payload = {
            "sessionId": "758968",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
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
    except Exception as exc:
        _agent_log("H3", "app_act.py:_registered_page_targets", "pages_manager_error", {"error": str(exc)})
    return targets


def _safe_page_link(page: str, **kwargs) -> bool:
    """Solo enlaza si la página existe en el registro multipágina actual."""
    targets = _registered_page_targets()
    page_norm = page.replace("\\", "/")
    _agent_log(
        "H1",
        "app_act.py:_safe_page_link",
        "page_link_attempt",
        {"page": page, "page_norm": page_norm, "registered": sorted(targets)},
    )
    try:
        st.page_link(page, **kwargs)
        _agent_log("H1", "app_act.py:_safe_page_link", "page_link_ok", {"page": page})
        return True
    except st.errors.StreamlitPageNotFoundError as exc:
        _agent_log(
            "H1",
            "app_act.py:_safe_page_link",
            "page_link_not_found",
            {"page": page, "error": type(exc).__name__},
        )
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
.f2-fac-badge {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 11px; font-weight: 700; color: #fff;
}
/* ── Tabla actividades ── */
.f2-act-tbl { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
.f2-act-tbl th { background: #f1f5f9; padding: 8px 10px; text-align: left; font-weight: 700; color: #0F385A; }
.f2-act-tbl td { padding: 7px 10px; border-bottom: 1px solid #eef2f6; color: #2a4a5e; }
.f2-act-tbl tr:hover td { background: #f8fafc; }
.f2-st-badge {
    display: inline-block; padding: 2px 10px; border-radius: 10px;
    font-size: 10px; font-weight: 700; color: #fff;
}
/* ── Tabla programas ── */
.f2-tbl { width: 100%; border-collapse: collapse; font-size: 12px; }
.f2-tbl th { background: #0F385A; color: #fff; padding: 10px 8px; text-align: center; font-weight: 600; }
.f2-tbl td { padding: 8px; border-bottom: 1px solid #e8eef4; text-align: center; }
.f2-tbl td.prog-name { text-align: left; font-weight: 600; color: #0F385A; cursor: pointer; }
.f2-tbl tr:hover td { background: #f0f7fc; }
.f2-mini-bar { height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; margin-top: 3px; }
/* ── Matriz programas × actividades ── */
.f2-matrix-scroll {
    overflow-x: auto; max-width: 100%; background: #fff;
    border-radius: 8px; border: 1px solid rgba(15,56,90,0.10);
    box-shadow: 0 1px 4px rgba(15,56,90,0.06);
}
.f2-matrix { min-width: max-content; }
.f2-matrix th { font-size: 10px; padding: 8px 6px; vertical-align: bottom; max-width: 120px;
    white-space: normal; line-height: 1.2; }
.f2-matrix td { font-size: 11px; padding: 6px 8px; text-align: center; }
.f2-matrix td.prog-name { text-align: left; font-weight: 600; color: #0F385A;
    min-width: 160px; max-width: 220px; white-space: normal; position: sticky; left: 0;
    background: #fff; z-index: 1; box-shadow: 2px 0 4px rgba(0,0,0,.04); }
.f2-matrix thead th:first-child { position: sticky; left: 0; z-index: 3; }
.f2-matrix .f2-act-hdr { display: block; max-width: 110px; }
.f2-matrix .f2-val-cell { font-size: 10px; color: #6a8a9e; display: block; margin-top: 2px; }
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


def _activities_matrix_html(df: pd.DataFrame, etapa: str) -> str:
    meta = [m for m in _ensure_activities_meta(df) if m["phase"] == etapa]
    if not meta:
        return "<p style='color:#6a8a9e;padding:12px'>Sin actividades en esta etapa.</p>"
    pct_col = ETAPA_PCT_COL[etapa]
    headers = ["<th>Programa</th>", "<th>Fac.</th>", "<th>% Etapa</th>"]
    for m in meta:
        headers.append(
            f'<th title="{_esc(m["name"])}"><span class="f2-act-hdr">{_esc(_short_label(m["name"]))}</span></th>'
        )
    rows = []
    for _, row in df.sort_values("NOMBRE DEL PROGRAMA").iterrows():
        fac, fc = row.get("FACULTAD_ABREV", "—"), row.get("FACULTAD_COLOR", "#6e7681")
        pct, pc = float(row.get(pct_col, 0) or 0), color_for_pct(float(row.get(pct_col, 0) or 0))
        cells = [
            f'<td class="prog-name">{_esc(row["NOMBRE DEL PROGRAMA"])}</td>',
            f'<td><span class="f2-fac-badge" style="background:{fc}">{_esc(fac)}</span></td>',
            f'<td><b style="color:{pc}">{pct:.0f}%</b></td>',
        ]
        for m in meta:
            cl = row.get(f"cl_act_{m['idx']}", "na")
            val = row.get(f"val_act_{m['idx']}", "—")
            color, lbl = STATUS_COLOR.get(cl, "#9aabb5"), STATUS_LABEL.get(cl, cl)
            score = _activity_score(cl)
            pct_act = f"{score:.0f}%" if score is not None else "—"
            val_short = _short_label(val, 18) if str(val).strip() not in ("—", "", "None", "nan") else ""
            val_html = f'<span class="f2-val-cell">{_esc(val_short)}</span>' if val_short else ""
            cells.append(
                f'<td><span class="f2-st-badge" style="background:{color}">{_esc(lbl)}</span>'
                f'<span style="display:block;font-size:10px;font-weight:700;color:#0F385A;margin-top:2px">'
                f"{_esc(pct_act)}</span>{val_html}</td>"
            )
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        '<div class="f2-matrix-scroll"><table class="f2-tbl f2-matrix"><thead><tr>'
        + "".join(headers) + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def _render_filter_summary(df: pd.DataFrame):
    n = len(df)
    gen_avg = round(float(df["avance_general_vact"].mean()), 1) if n else 0
    gen_color = color_for_pct(gen_avg)
    st.markdown(
        f'<div class="f2-prog-card"><div class="f2-prog-info"><h3>Programas en el filtro actual</h3>'
        f'<p style="color:#6a8a9e;font-size:13px;margin:0"><b style="color:#0F385A">{n}</b> programa(s) · '
        f'Avance general promedio <b style="color:{gen_color}">{gen_avg:.0f}%</b><br>'
        f'Las tablas muestran el estado de <b>cada actividad</b> para todos los programas filtrados.</p></div>'
        f'<div class="f2-prog-badge" style="background:{gen_color}22;border:2px solid {gen_color}">'
        f'<div class="f2-prog-badge-pct" style="color:{gen_color}">{gen_avg:.0f}%</div>'
        f'<div class="f2-prog-badge-lbl" style="color:{gen_color}">Promedio general</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )


def _render_etapas_actividades(df: pd.DataFrame, expanded_first: bool = False):
    for i, etapa in enumerate(ETAPAS_ORDEN):
        pct_col = ETAPA_PCT_COL[etapa]
        pct_avg = round(float(df[pct_col].mean()), 1) if len(df) and pct_col in df.columns else 0
        meta = [m for m in _ensure_activities_meta(df) if m["phase"] == etapa]
        done = sum(
            1 for _, row in df.iterrows() for m in meta if row.get(f"cl_act_{m['idx']}") == "done"
        )
        color = color_for_pct(pct_avg)
        with st.expander(
            f"Etapa: {etapa}  ·  {pct_avg:.0f}% promedio  ·  {len(df)} programas  ·  "
            f"{len(meta)} actividades  ·  {done} finalizadas",
            expanded=(expanded_first and i == 0),
        ):
            st.markdown(
                f'<div style="margin-bottom:10px">{_mini_bar(pct_avg, color)}</div>',
                unsafe_allow_html=True,
            )
            html_comp.html(_activities_matrix_html(df, etapa), height=min(90 + 34 * len(df), 900), scrolling=True)



def _programs_table_html(df: pd.DataFrame) -> str:
    rows = []
    for _, r in df.sort_values("avance_general_vact", ascending=False).iterrows():
        prog = r["NOMBRE DEL PROGRAMA"]
        fac = r.get("FACULTAD_ABREV", "—")
        fc = r.get("FACULTAD_COLOR", "#6e7681")
        pa = r.get("pct_alistamiento", 0)
        pd_ = r.get("pct_diseno", 0)
        pde = r.get("pct_desarrollo", 0)
        pi = r.get("pct_implementacion", 0)
        pg = r.get("avance_general_vact", 0)

        def _cell(p):
            c = color_for_pct(p)
            return (
                f"<td><b style='color:{c}'>{p:.0f}%</b>"
                f'<div class="f2-mini-bar"><div style="width:{min(p,100):.0f}%;height:100%;background:{c}"></div></div></td>'
            )

        rows.append(
            f"<tr>"
            f'<td class="prog-name">{_esc(prog)}</td>'
            f'<td><span class="f2-fac-badge" style="background:{fc}">{_esc(fac)}</span></td>'
            f"<td>{_esc(r.get('MODALIDAD','—'))}</td>"
            f"<td>{_esc(r.get('PERIODO DE IMPLEMENTACIÓN','—'))}</td>"
            f"{_cell(pa)}{_cell(pd_)}{_cell(pde)}{_cell(pi)}{_cell(pg)}"
            f"</tr>"
        )
    if not rows:
        return "<p style='padding:20px;color:#6a8a9e'>No hay programas con los filtros seleccionados.</p>"
    return (
        '<table class="f2-tbl"><thead><tr>'
        "<th>Programa</th><th>Facultad</th><th>Modalidad</th><th>Período</th>"
        "<th>Alistamiento</th><th>Diseño</th><th>Desarrollo</th><th>Implementación</th><th>General</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


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
    _main_script = ""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        if ctx is not None:
            _main_script = Path(ctx.pages_manager.main_script_path).name.replace("\\", "/")
    except Exception:
        pass
    _agent_log(
        "H2",
        "app_act.py:sidebar",
        "main_script",
        {"main_script": _main_script, "registered": sorted(_registered_page_targets())},
    )
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
        _render_etapas_actividades(df, expanded_first=True)

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
            "Cada fila es un programa; cada columna es una actividad. "
            "Desplace horizontalmente si hay muchas actividades.</div>",
            unsafe_allow_html=True,
        )
        _render_etapas_actividades(df, expanded_first=True)

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

        st.markdown(
            '<div style="font-size:14px;font-weight:700;color:#0F385A;margin:16px 0 8px">'
            "Resumen por programa (% por etapa)</div>",
            unsafe_allow_html=True,
        )
        html_comp.html(_programs_table_html(df), height=min(120 + 42 * len(df), 700), scrolling=True)

        st.markdown(
            '<div style="font-size:14px;font-weight:700;color:#0F385A;margin:24px 0 8px">'
            "Detalle de actividades · todos los programas</div>",
            unsafe_allow_html=True,
        )
        _render_etapas_actividades(df, expanded_first=False)


        st.download_button(
            "⬇ Descargar Excel",
            data=_excel_export_bytes(df),
            file_name="reforma_curricular_fase2.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tab3",
        )
