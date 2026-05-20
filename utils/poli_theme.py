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

# ── Nivel de formación (detalle) ──────────────────────────────────────────────
NIVEL_ORDEN = ["Maestría", "Especialización", "Profesional", "Tecnológico", "Técnico"]

NIVEL_CLR = {
    "Especialización": "#2563eb",
    "Maestría": "#7c3aed",
    "Profesional": "#059669",
    "Tecnológico": BRAND_ACCENT,
    "Técnico": "#0891b2",
}

# ── Etapas reforma curricular ─────────────────────────────────────────────────
ETAPA_CLR = {
    "Alistamiento Curricular": "#2980B9",  # azul medio — distinto del avance general (#0F385A)
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

# Escala de avance % (solo colores institucionales; sin naranjas genéricos)
PCT_HIGH = SEGMENT_DONE          # >= 70 %
PCT_MID = BRAND_ACCENT           # >= 45 %
PCT_LOW = "#FBAF17"              # >= 25 % — amarillo institucional
PCT_CRITICAL = SEGMENT_NOSTART   # < 25 %
PCT_BAR_TEXT_HIGH = "#5a7a2e"
PCT_BAR_TEXT_MID = BRAND_ACCENT_DARK
PCT_BAR_TEXT_LOW = "#9a0050"


def rgba_hex(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def color_for_pct(p) -> str:
    """Color sólido para tarjetas y Gantt — escala institucional POLI."""
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return TEXT_LIGHT
    p = float(p)
    if p >= 70:
        return PCT_HIGH
    if p >= 45:
        return PCT_MID
    if p >= 25:
        return PCT_LOW
    return PCT_CRITICAL


def pct_bar_colors(pct: float) -> tuple[str, str]:
    """Texto y relleno de barra de % — escala institucional POLI."""
    try:
        pct = float(pct if pct is not None else 0)
    except (TypeError, ValueError):
        pct = 0.0
    if math.isnan(pct):
        pct = 0.0
    if pct >= 70:
        return PCT_BAR_TEXT_HIGH, PCT_HIGH
    if pct >= 40:
        return PCT_BAR_TEXT_MID, PCT_MID
    return PCT_BAR_TEXT_LOW, PCT_CRITICAL


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
        f'<div style="font-size:12px;font-weight:700;color:{clr};margin-bottom:3px">{int(pct)}%</div>'
        f'<div style="height:6px;background:{BG_TRACK};border-radius:4px;overflow:hidden">'
        f'<div style="width:{w:.0f}%;height:100%;background:{bar};border-radius:4px;'
        f'box-shadow:0 1px 2px rgba(0,0,0,.15)"></div></div></div>'
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


def _svg_esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace('"', "&quot;")


def status_icon_html(cl: str, size: int = 16, title: str = "") -> str:
    """Icono SVG institucional para estado de actividad (sustituye emojis)."""
    c = STATUS_CLR.get(cl, TEXT_LIGHT)
    tip = f' title="{_svg_esc(title)}"' if title else ""
    paths = {
        "done": (
            f'<circle cx="8" cy="8" r="6.5" fill="{c}" fill-opacity="0.15" stroke="{c}" stroke-width="1.4"/>'
            f'<path d="M5.2 8.2 L7.2 10.2 L10.8 5.8" stroke="{c}" stroke-width="1.5" '
            f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        ),
        "inprog": (
            f'<circle cx="8" cy="8" r="6.5" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-width="1.4"/>'
            f'<path d="M8 8 V5.2" stroke="{c}" stroke-width="1.4" stroke-linecap="round"/>'
            f'<path d="M8 8 H10.8" stroke="{c}" stroke-width="1.4" stroke-linecap="round"/>'
        ),
        "nostart": (
            f'<circle cx="8" cy="8" r="6.5" fill="none" stroke="{c}" stroke-width="1.4"/>'
            f'<line x1="5.5" y1="8" x2="10.5" y2="8" stroke="{c}" stroke-width="1.4" '
            f'stroke-linecap="round"/>'
        ),
        "devuelto": (
            f'<path d="M10.8 5.4a4.2 4.2 0 1 0-5.3 2.6" fill="none" stroke="{c}" '
            f'stroke-width="1.4" stroke-linecap="round"/>'
            f'<path d="M5.5 8 L5.5 5.6 M5.5 8 L7.6 8" fill="none" stroke="{c}" '
            f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
        ),
        "info": (
            f'<rect x="5" y="4.5" width="6" height="7.5" rx="1" fill="{c}" fill-opacity="0.12" '
            f'stroke="{c}" stroke-width="1.3"/>'
            f'<line x1="6.5" y1="6.5" x2="9.5" y2="6.5" stroke="{c}" stroke-width="1.2" '
            f'stroke-linecap="round"/>'
            f'<line x1="6.5" y1="8" x2="9.5" y2="8" stroke="{c}" stroke-width="1.2" '
            f'stroke-linecap="round"/>'
            f'<line x1="6.5" y1="9.5" x2="8.2" y2="9.5" stroke="{c}" stroke-width="1.2" '
            f'stroke-linecap="round"/>'
        ),
    }
    inner = paths.get(cl)
    if not inner:
        return ""
    return (
        f'<span class="poli-status-icon" style="display:inline-flex;align-items:center;'
        f"justify-content:center;width:{size}px;height:{size}px;vertical-align:middle{tip}\">"
        f'<svg width="{size}" height="{size}" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" '
        f'aria-hidden="true">{inner}</svg></span>'
    )


def streamlit_global_css() -> str:
    """Bloque CSS global alineado con app.py."""
    return f"""
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@v2.0.3/src/regular/style.css"/>
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
.f2-gantt-row-compact {{ margin-bottom: 8px; }}
.f2-gantt-label {{ width: 200px; flex-shrink: 0; font-size: 12px; font-weight: 600; color: {TEXT_PRIMARY}; }}
.f2-ficha-gantt .f2-gantt-label {{ width: 118px; font-size: 11px; }}
.f2-ficha-gantt .f2-gantt-track {{ height: 22px; }}
.f2-gantt-track {{ flex: 1; height: 28px; background: {BG_GANTT_TRACK}; border-radius: 6px; overflow: hidden; }}
.f2-gantt-fill {{ height: 100%; border-radius: 6px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; min-width: 36px; }}
.f2-gantt-pct {{ font-size: 12px; font-weight: 700; color: {TEXT_ON_DARK}; text-shadow: 0 1px 2px rgba(0,0,0,.25); }}
.f2-gantt-pct-out {{ width: 48px; text-align: right; font-size: 13px; font-weight: 700; color: {TEXT_PRIMARY}; flex-shrink: 0; }}
.f2-gantt-general .f2-gantt-label {{ font-weight: 800; }}
.f2-gantt-general .f2-gantt-track {{ height: 34px; }}
.f2-prog-card {{
    background: {BG_CARD}; border-radius: 12px; padding: 18px 22px;
    box-shadow: 0 2px 10px rgba(15,56,90,0.09); margin-bottom: 20px;
    display: flex; gap: 24px; align-items: stretch; flex-wrap: wrap;
}}
.f2-prog-card-inline {{ margin-bottom: 0; box-shadow: none; padding: 4px 0; background: transparent; }}
.f2-prog-info {{ flex: 1; min-width: 280px; }}
.f2-prog-info h3 {{ margin: 0 0 10px; font-size: 17px; line-height: 1.3; color: {TEXT_PRIMARY}; }}
.f2-prog-badges {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }}
.f2-ficha-section {{ margin: 16px 0 10px; }}
.f2-ficha-section-title {{
    font-size: 13px; font-weight: 700; color: {TEXT_MUTED};
    margin: 0 0 10px; letter-spacing: .02em;
}}
.f2-ficha-expanders {{ margin-top: 4px; }}
.f2-prog-badge {{
    min-width: 120px; text-align: center; padding: 16px; border-radius: 12px;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
}}
.f2-prog-badge-pct {{ font-size: 42px; font-weight: 800; line-height: 1; }}
.f2-prog-badge-lbl {{ font-size: 10px; text-transform: uppercase; letter-spacing: .5px; margin-top: 6px; opacity: .85; }}
</style>
"""

# Phosphor Icons - Mapeo de iconos regulares
PHOSPHOR_ICONS = {
    # Navigation
    "resumen": "ph-chart-bar",
    "alertas": "ph-warning",
    "facultad": "ph-buildings",
    "detalle": "ph-clipboard-text",
    "programa": "ph-student",
    "produccion": "ph-factory",
    
    # KPIs
    "programas": "ph-books",
    "avance": "ph-trend-up",
    "completado": "ph-check-circle",
    "ejecucion": "ph-gear-six",
    "critico": "ph-warning",
    "facultades": "ph-buildings",
    "modalidades": "ph-globe",
    "proximo": "ph-flag-checkered",
    
    # Estados y alertas
    "success": "ph-check-circle",
    "warning": "ph-warning-circle",
    "danger": "ph-warning",
    "info": "ph-info",
    "circulo_rojo": "ph-circle-fill",
    "circulo_amarillo": "ph-circle-fill",
    "circulo_verde": "ph-circle-fill",
    
    # Misceláneos
    "filtro": "ph-funnel",
    "descarga": "ph-download-simple",
    "exportar": "ph-export",
    "editar": "ph-pencil",
    "buscar": "ph-magnifying-glass",
    "calendario": "ph-calendar",
    "reloj": "ph-clock",
    "usuario": "ph-user",
    "casa": "ph-house",
    "config": "ph-gear",
}


def phosphor_icon(name: str, size: int = 16, color: str = None, weight: str = "regular") -> str:
    """Retorna HTML de icono Phosphor.
    
    Args:
        name: Nombre del icono (sin el prefijo 'ph-')
        size: Tamaño en pixels
        color: Color CSS (opcional)
        weight: 'regular' o 'fill'
    
    Returns:
        HTML string con el icono
    """
    icon_class = f"ph ph-{name}"
    if weight == "fill":
        icon_class = f"ph-fill ph-fill-{name}"
    
    style = f"font-size:{size}px;"
    if color:
        style += f"color:{color};"
    
    return f'<i class="{icon_class}" style="{style}"></i>'


def phosphor_icon_kpi(name: str, color: str = None) -> str:
    """Icono para KPIs - tamaño 24px"""
    return phosphor_icon(name, size=24, color=color)


def phosphor_icon_nav(name: str, color: str = None) -> str:
    """Icono para navegación - tamaño 20px"""
    return phosphor_icon(name, size=20, color=color)


def phosphor_icon_alert(alert_type: str) -> str:
    """Iconos para alertas según tipo"""
    icons = {
        "critico": phosphor_icon("warning", color="#dc2626", size=18),
        "atencion": phosphor_icon("warning-circle", color=PCT_LOW, size=18),
        "proximo": phosphor_icon("flag-checkered", color="#059669", size=18),
    }
    return icons.get(alert_type, "")
