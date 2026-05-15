"""
Paleta institucional POLI — fuente única de colores.
Extraída de app.py (Fase 1) y utils/data_loader.py.
"""

from __future__ import annotations

import math

# ── Marca institucional ───────────────────────────────────────────────────────
BRAND_PRIMARY = "#0F385A"
BRAND_SECONDARY = "#1A5276"
BRAND_ACCENT = "#1FB2DE"
BRAND_HIGHLIGHT = "#42F2F2"
BRAND_ACCENT_DARK = "#0891b2"

# ── Texto ─────────────────────────────────────────────────────────────────────
TEXT_PRIMARY = "#0F385A"
TEXT_BODY = "#2a4a5e"
TEXT_MUTED = "#6a8a9e"
TEXT_LIGHT = "#9aabb5"
TEXT_SUBTLE = "#4a6a7e"
TEXT_ON_DARK = "#FFFFFF"
TEXT_NA = "#b0bec5"

# ── Fondos ────────────────────────────────────────────────────────────────────
BG_APP = "#EEF3F8"
BG_CARD = "#FFFFFF"
BG_TABLE = "#fafdff"
BG_ROW = "#FFFFFF"
BG_ROW_ALT = "#f8fafc"
BG_TRACK = "#e2e8f0"
BG_GANTT_TRACK = "#e8eef4"
BG_HOVER = "#E3F4FB"
BG_MUTED = "#f0f4f8"
BG_NOTIFICATION = "#e8f6fc"

# ── Bordes ────────────────────────────────────────────────────────────────────
BORDER_TABLE = "#b5c9d8"
BORDER_ROW = "#eef3f8"
BORDER_CARD = "rgba(15,56,90,0.10)"
BORDER_TABLE_SHADOW = "rgba(15,56,90,0.10)"

# ── Facultad (app.py _P_FAC_CLR) ──────────────────────────────────────────────
FACULTAD_CLR = {
    "FSCC": "#EC0677",
    "FIDI": "#1FB2DE",
    "FNGS": "#A6CE38",
}

# ── Modalidad (app.py tab Priorización _P_MOD_CLR) ────────────────────────────
MODALIDAD_CLR = {
    "Virtual": "#1FB2DE",
    "Presencial": "#A6CE38",
    "Híbrido": "#FBAF17",
    "Distancia": "#A6CE38",
}

# ── Período implementación (app.py _PER_HDR_CLR) ──────────────────────────────
PERIODO_CLR = {
    "2026-2": "#A6CE38",
    "2027-1": "#FBAF17",
    "2027-2": "#EC0677",
}

# ── Estados de actividad (data_loader STATUS_COLOR) ───────────────────────────
STATUS_CLR = {
    "done": "#A6CE38",
    "inprog": "#1FB2DE",
    "nostart": "#EC0677",
    "devuelto": "#F47B20",
    "info": "#FBAF17",
    "na": "#9aabb5",
}

# ── Etapas reforma curricular ─────────────────────────────────────────────────
ETAPA_CLR = {
    "Alistamiento Curricular": "#0F385A",
    "Diseño Curricular": "#1FB2DE",
    "Desarrollo Curricular": "#EC0677",
    "Implementación Curricular": "#A6CE38",
}

# ── Clasificación priorización (app.py) ───────────────────────────────────────
CLASIF_CLR = {
    "Urgente": ("#EC0677", "#fce8f2"),
    "Prioritario": ("#FBAF17", "#fdf8e8"),
    "En seguimiento": ("#2980B9", "#EBF5FB"),
    "En curso": ("#A6CE38", "#f0f8e8"),
}

SEGMENT_DONE = "#A6CE38"
SEGMENT_INPROG = "#1FB2DE"
SEGMENT_NOSTART = "#EC0677"
SEGMENT_NA = "#c8d8e0"


def rgba_hex(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def color_for_pct(p) -> str:
    """Color sólido para tarjetas y Gantt (utils/data_loader.py)."""
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return TEXT_LIGHT
    p = float(p)
    if p >= 70:
        return "#3ecf8e"
    if p >= 45:
        return "#4f8ef7"
    if p >= 25:
        return "#f97316"
    return "#ef4444"


def pct_bar_colors(pct: float) -> tuple[str, str]:
    """Texto y relleno de barra de % (app.py _p_bar)."""
    try:
        pct = float(pct if pct is not None else 0)
    except (TypeError, ValueError):
        pct = 0.0
    if math.isnan(pct):
        pct = 0.0
    if pct >= 70:
        return "#15803d", "#22c55e"
    if pct >= 40:
        return "#d97706", "#f59e0b"
    return "#dc2626", "#ef4444"


def p_bar_html(pct, min_width: int = 70) -> str:
    """Mini-barra de avance (patrón app.py Priorización)."""
    try:
        pct = float(pct if pct is not None else 0)
    except (TypeError, ValueError):
        pct = 0.0
    if math.isnan(pct):
        pct = 0.0
    clr, bar = pct_bar_colors(pct)
    w = min(max(pct, 0), 100)
    return (
        f'<div style="min-width:{min_width}px;text-align:center">'
        f'<motion style="display:none"></motion>'
    )


def badge_html(txt: str, fg_hex: str) -> str:
    """Badge suave (app.py _p_badge)."""
    h = fg_hex.lstrip("#")
    if len(h) != 6:
        return txt
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    esc = str(txt).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f'<span style="background:rgba({r},{g},{b},0.12);color:{fg_hex};font-size:10px;'
        f'font-weight:700;padding:3px 9px;border-radius:12px;white-space:nowrap">{esc}</span>'
    )


def streamlit_global_css() -> str:
    """Bloque CSS global alineado con app.py."""
    return f"""
<style>
[data-testid="stAppViewContainer"] {{ background: {BG_APP}; }}
[data-testid="stHeader"] {{
    background: linear-gradient(135deg, {BRAND_PRIMARY} 0%, {BRAND_SECONDARY} 50%, {BRAND_ACCENT} 100%) !important;
    border-bottom: 3px solid {BRAND_HIGHLIGHT} !important;
}}
h1,h2,h3,h4 {{ font-family: 'Segoe UI', sans-serif; color: {TEXT_PRIMARY} !important; }}
p, li, label, caption {{ color: {TEXT_BODY}; }}
.block-container {{ padding-top: 3.5rem !important; }}
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {BRAND_PRIMARY} 0%, {BRAND_SECONDARY} 45%, {BRAND_ACCENT} 100%) !important;
}}
[data-testid="stSidebarNav"] {{ display: none !important; }}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
    color: rgba(255,255,255,0.80) !important;
}}
[data-testid="stPills"] button {{
    border: 2px solid {BRAND_SECONDARY} !important; color: {BRAND_SECONDARY} !important;
    background: {BG_CARD} !important; border-radius: 20px !important;
    font-size: 12px !important; font-weight: 600 !important;
}}
[data-testid="stPills"] button[aria-checked="true"],
[data-testid="stPills"] button[aria-pressed="true"] {{
    background: {BRAND_PRIMARY} !important; color: {TEXT_ON_DARK} !important;
    border-color: {BRAND_PRIMARY} !important;
}}
[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg,{BRAND_ACCENT},{BRAND_ACCENT_DARK}) !important;
    border-color: {BRAND_ACCENT} !important; color: {TEXT_ON_DARK} !important;
    font-size: 11px !important; font-weight: 700 !important; border-radius: 8px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {TEXT_PRIMARY} !important; border-bottom-color: {BRAND_ACCENT} !important; font-weight: 700 !important;
}}
[data-testid="stNotification"] {{
    background: {BG_NOTIFICATION} !important; color: {TEXT_PRIMARY} !important;
    border-color: {BRAND_ACCENT} !important;
}}
.f2-scard {{
    background: {BG_CARD}; border-radius: 12px; padding: 16px 18px;
    border-left: 5px solid var(--accent, {BRAND_ACCENT});
    box-shadow: 0 2px 8px rgba(15,56,90,0.08); height: 100%;
}}
.f2-scard-title {{ font-size: 11px; font-weight: 700; color: {TEXT_MUTED};
    text-transform: uppercase; letter-spacing: .5px; margin-bottom: 6px; }}
.f2-scard-pct {{ font-size: 36px; font-weight: 800; color: {TEXT_PRIMARY}; line-height: 1; }}
.f2-scard-sub {{ font-size: 11px; color: {TEXT_MUTED}; margin-top: 6px; }}
.f2-bar-wrap {{ height: 8px; background: {BG_TRACK}; border-radius: 4px; margin-top: 10px; overflow: hidden; }}
.f2-bar-fill {{ height: 100%; border-radius: 4px; transition: width .3s; }}
.f2-gantt {{ font-family: 'Segoe UI', sans-serif; }}
.f2-gantt-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }}
.f2-gantt-label {{ width: 200px; flex-shrink: 0; font-size: 12px; font-weight: 600; color: {TEXT_PRIMARY}; }}
.f2-gantt-track {{ flex: 1; height: 28px; background: {BG_GANTT_TRACK}; border-radius: 6px; overflow: hidden; }}
.f2-gantt-fill {{ height: 100%; border-radius: 6px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; min-width: 36px; }}
.f2-gantt-pct {{ font-size: 12px; font-weight: 700; color: {TEXT_ON_DARK}; text-shadow: 0 1px 2px rgba(0,0,0,.25); }}
.f2-gantt-pct-out {{ width: 48px; text-align: right; font-size: 13px; font-weight: 700; color: {TEXT_PRIMARY}; flex-shrink: 0; }}
.f2-prog-card {{
    background: {BG_CARD}; border-radius: 12px; padding: 18px 22px;
    box-shadow: 0 2px 10px rgba(15,56,90,0.09); margin-bottom: 16px;
}}
.f2-prog-info h3 {{ margin: 0 0 12px; font-size: 18px; color: {TEXT_PRIMARY}; }}
</style>
"""
