"""
pages/3_Detalle_Etapa.py — Fase 2: Detalle por Etapa
Vista agregada por etapa con drill-down.
"""

import pandas as pd
import streamlit as st

from utils.charts_vact import ETAPA_SHORT, render_etapas_drilldown
from utils.data_loader_vact import (
    ETAPAS_ORDEN,
    FAC_ABREV_INV,
    get_estadisticas_etapa,
    load_etapas_data,
)
from utils.f2_components import (
    apply_current_filters,
    render_f2_header,
    render_f2_sidebar,
    render_filter_bar,
)
from utils.poli_theme import ETAPA_CLR, TEXT_MUTED, TEXT_PRIMARY, phosphor_icon, streamlit_global_css

st.set_page_config(
    page_title="Detalle por Etapa · POLI",
    page_icon=":material/assignment:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(streamlit_global_css(), unsafe_allow_html=True)

df_raw = load_etapas_data()
fac_abrev_inv = FAC_ABREV_INV
fac_ops = sorted(df_raw["FACULTAD_ABREV"].dropna().unique().tolist()) if "FACULTAD_ABREV" in df_raw.columns else []
mods_ops = sorted(df_raw["MODALIDAD"].dropna().unique().tolist()) if "MODALIDAD" in df_raw.columns else []
pers_ops = sorted(df_raw["PERIODO DE IMPLEMENTACIÓN"].dropna().unique().tolist()) if "PERIODO DE IMPLEMENTACIÓN" in df_raw.columns else []
niveles_ops = [n for n in ["Pregrado", "Posgrado"] if n in df_raw.get("NIVEL_HOMOLOGADO", pd.Series(dtype=str)).values]

render_f2_sidebar()
render_f2_header("Detalle por Etapa")
render_filter_bar(
    df_raw, fac_abrev_inv, mods_ops, fac_ops, pers_ops, niveles_ops, key_prefix="detalle"
)

df, *_ = apply_current_filters(df_raw, fac_abrev_inv, key_prefix="detalle")

if len(df) == 0:
    st.warning("No hay programas con los filtros actuales.")
else:
    gen_avg = round(float(df["avance_general_vact"].mean()), 1) if len(df) else 0
    st.markdown(
        f'<div style="font-size:18px;font-weight:700;color:{TEXT_PRIMARY};margin:20px 0 12px">'
        f'{phosphor_icon("clipboard-text", size=22)} Detalle por Etapa</div>'.replace("motion.", ""),
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="background:#fff;border:1px solid rgba(15,56,90,.1);border-radius:12px;padding:14px;margin-bottom:16px">'
        f'<motion.span style="font-size:13px;color:{TEXT_MUTED}">{len(df)} programa(s) · Avance general promedio '
        f'<b style="color:{TEXT_PRIMARY}">{gen_avg}%</b></motion.span></div>'.replace("motion.", ""),
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    for i, etapa in enumerate(ETAPAS_ORDEN):
        stats = get_estadisticas_etapa(df, etapa)
        clr = ETAPA_CLR.get(etapa, "#6e7681")
        with cols[i]:
            st.markdown(
                f'<div style="background:#fff;border-left:4px solid {clr};border-radius:10px;'
                f'padding:12px;border:1px solid rgba(15,56,90,.08)">'
                f'<div style="font-size:9px;color:#6a8a9e;text-transform:uppercase">'
                f'{ETAPA_SHORT[etapa]}</div>'
                f'<div style="font-size:22px;font-weight:800;color:{clr}">{stats["pct_promedio"]}%</div>'
                f'<div style="font-size:10px;color:{TEXT_MUTED}">{stats["n_programas"]} prog.</div>'
                f"</div>".replace("motion.", ""),
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin:20px 0 8px'></div>".replace("motion.", ""), unsafe_allow_html=True)
    render_etapas_drilldown(df, key_prefix="detalle_etapa")

    st.markdown(
        f'<div style="font-size:14px;font-weight:700;color:{TEXT_PRIMARY};margin:24px 0 8px">'
        f'{phosphor_icon("chart-bar", size=16)} Resumen agregado por etapa</div>'.replace("motion.", ""),
        unsafe_allow_html=True,
    )
    from utils.data_loader_vact import _ensure_activities_meta
    from utils.poli_theme import STATUS_CLR
    meta = _ensure_activities_meta(df)

    STATUS_COLS = [
        ("Finalizado",  "done",    STATUS_CLR["done"]),
        ("En proceso",  "inprog",  STATUS_CLR["inprog"]),
        ("Sin iniciar", "nostart", STATUS_CLR["nostart"]),
        ("Devuelto",    "devuelto",STATUS_CLR["devuelto"]),
        ("No aplica",   "na",      STATUS_CLR["na"]),
    ]

    table_rows = []
    for etapa in ETAPAS_ORDEN:
        s = get_estadisticas_etapa(df, etapa)
        n_acts = len([m for m in meta if m["phase"] == etapa])
        total = max(s["done"]+s["inprog"]+s["devuelto"]+s["nostart"]+s["info"]+s["na"], 1)
        table_rows.append((etapa, s, n_acts, total))

    # Cabecera
    th_base = (
        "padding:10px 14px;text-align:center;font-size:10px;font-weight:700;"
        "text-transform:uppercase;letter-spacing:.5px;color:#6a8a9e;"
        "border-bottom:2px solid rgba(15,56,90,.12);white-space:nowrap;"
    )
    th_left = th_base + "text-align:left;"

    dot = lambda c: f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{c};margin-right:4px;vertical-align:middle"></span>'

    header_cells = f'<th style="{th_left}">Etapa</th>'
    header_cells += f'<th style="{th_base}">Acts.</th>'
    header_cells += f'<th style="{th_base}">Progs.</th>'
    header_cells += f'<th style="{th_base}">% Prom.</th>'
    for lbl, _, clr in STATUS_COLS:
        header_cells += f'<th style="{th_base}">{dot(clr)}{lbl}</th>'
    header_cells += f'<th style="{th_base}">Total celdas</th>'

    # Filas
    td_base = "padding:10px 14px;text-align:center;font-size:12px;border-bottom:1px solid rgba(15,56,90,.07);"
    td_left = td_base + "text-align:left;"

    body_html = ""
    for i, (etapa, s, n_acts, total) in enumerate(table_rows):
        clr = ETAPA_CLR.get(etapa, "#6e7681")
        short = ETAPA_SHORT.get(etapa, etapa)
        pct = s["pct_promedio"]
        bg = "background:#f8fafc;" if i % 2 == 1 else "background:#ffffff;"

        # Barra de progreso inline para % promedio
        bar_w = min(pct, 100)
        pct_cell = (
            f'<div style="display:flex;align-items:center;gap:6px;justify-content:center">'
            f'<div style="width:56px;height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden">'
            f'<div style="width:{bar_w:.0f}%;height:100%;background:{clr};border-radius:3px"></div></div>'
            f'<span style="font-weight:700;color:{clr};min-width:36px">{pct}%</span>'
            f'</div>'
        )

        row_cells = (
            f'<td style="{td_left}{bg}">'
            f'<span style="display:inline-block;width:10px;height:10px;border-radius:2px;'
            f'background:{clr};margin-right:6px;vertical-align:middle"></span>'
            f'<span style="font-weight:700;color:#0f172a">{short}</span>'
            f'</td>'
            f'<td style="{td_base}{bg}"><span style="font-weight:600;color:#475569">{n_acts}</span></td>'
            f'<td style="{td_base}{bg}"><span style="color:#475569">{s["n_programas"]}</span></td>'
            f'<td style="{td_base}{bg}">{pct_cell}</td>'
        )
        for _, key, sclr in STATUS_COLS:
            cnt = s[key]
            pct_s = round(cnt / total * 100, 0)
            weight = "font-weight:700;" if cnt > 0 else "color:#cbd5e1;"
            row_cells += (
                f'<td style="{td_base}{bg}">'
                f'<span style="{weight}color:{'#0f172a' if cnt > 0 else '#cbd5e1'}">{cnt}</span>'
                f'<span style="font-size:9px;color:#94a3b8;margin-left:3px">({pct_s:.0f}%)</span>'
                f'</td>'
            )
        row_cells += (
            f'<td style="{td_base}{bg}'
            f'font-weight:600;color:#64748b;font-size:11px">{total}</td>'
        )
        body_html += f"<tr>{row_cells}</tr>"

    html_table = f"""
    <div style="background:#fff;border:1px solid rgba(15,56,90,.10);border-radius:12px;
                overflow:hidden;box-shadow:0 2px 8px rgba(15,56,90,.07);margin-bottom:8px">
      <table style="width:100%;border-collapse:collapse;font-family:Segoe UI,sans-serif">
        <thead style="background:#f8fafc">
          <tr>{header_cells}</tr>
        </thead>
        <tbody>{body_html}</tbody>
      </table>
    </div>
    <div style="font-size:10px;color:#94a3b8;margin-bottom:16px">
      Conteos por celda (programa × actividad) &nbsp;·&nbsp;
      Total celdas = Actividades × Programas
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)

    st.info(
        "La tabla detallada programa × actividad está en **Por Programa**.",
        icon=":material/info:",
    )
