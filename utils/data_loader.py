"""
utils/data_loader.py
Carga y procesa la hoja 'Maestro' del archivo Excel de Control Maestro de Reforma Curricular.
Fuente: data/raw/CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx
"""

import pandas as pd
import numpy as np
from pathlib import Path

ROOT      = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "raw" / "CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx"

# ─── Mapeo Etapas col B (Estructura) → columna Excel ──────────────────────────
# Tupla: (proceso, nombre_etapa, columna_en_excel, tipo_clasificacion)
ETAPAS_MAP = [
    ("Gestión Académica",                        "Formato creación de programas Banner",             "Formato creación de programas Banner",                      "status"),
    ("Gestión Académica",                        "La reforma cumple con la política curricular",      "LA REFORMA CUMPLE CON LA POLITICA CURRICULAR",              "status"),
    ("Gestión Académica",                        "Formato de proyecciones académicas y financieras", "Formato de proyecciones académicas y financieras",           "status"),
    ("Gestión Financiera",                       "Concepto financiero",                              "CONCEPTO FINANCIERO",                                       "status"),
    ("Aseguramiento de la Calidad",              "Tipo de trámite",                                  "Tipo de trámite de aseguramiento de la calidad",            "info"),
    ("Aseguramiento de la Calidad",              "Estado del trámite",                               "Estado del trámite",                                        "estado_tramite"),
    ("Ger. Planeación y Gestión Institucional",  "Correo para implementación",                       "CORREO PARA IMPLEMENTACIÓN",                                "status"),
    ("Producción de Contenidos",                 "Número de syllabus",                               "Número de syllabus",                                        "info"),
    ("Producción de Contenidos",                 "Total módulos con cambios",                        "TOTAL  MÓDULOS CON CAMBIOS",                                "info"),
    ("Producción de Contenidos",                 "% avance contenidos virtuales",                    "% avance contenidos virtuales",                             "pct"),
    ("Convenios Institucionales",                "Acta de homologación",                             "Acta de homologación",                                      "status"),
    ("Convenios Institucionales",                "Ruta sugerida homologación/articulación",          "Ruta sugerida programa homologación/articulación convenio", "status"),
    ("Convenios Institucionales",                "% avance",                                         "% avance .1",                                               "pct"),
    ("Parametrizar Reforma en Banner",           "Total aulas master",                               "Total Aulas Master",                                        "num"),
    ("Parametrizar Reforma en Banner",           "Avance de aulas master",                           "Avance de Aulas Master",                                    "num"),
    ("Parametrizar Reforma en Banner",           "% de avance",                                      "% de Avance",                                               "pct"),
    ("Parametrizar Reforma en Banner",           "Configurar plan de estudios en Banner",            "Configurar plan de estudios en Banner",                     "status"),
    ("Publicación en Página Web",                "Publicar plan de estudios en web",                 "Publicar plan de estudios en Web",                          "status"),
    ("Publicación en Página Web",                "Fecha fin",                                        "FECHA FIN",                                                 "date"),
    ("Publicación en Página Web",                "Periodo de implementación",                        "PERIODO DE IMPLEMENTACIÓN",                                 "info"),
]

PROCESOS = [
    "Gestión Académica",
    "Gestión Financiera",
    "Aseguramiento de la Calidad",
    "Ger. Planeación y Gestión Institucional",
    "Producción de Contenidos",
    "Convenios Institucionales",
    "Parametrizar Reforma en Banner",
    "Publicación en Página Web",
]

# Colores institucionales: #EC0677 #FBAF17 #0F385A #1FB2DE #42F2F2 #A6CE38
PROCESO_COLOR = {
    "Gestión Académica":                       "#0F385A",
    "Gestión Financiera":                      "#FBAF17",
    "Aseguramiento de la Calidad":             "#EC0677",
    "Ger. Planeación y Gestión Institucional": "#1FB2DE",
    "Producción de Contenidos":                "#A6CE38",
    "Convenios Institucionales":               "#42B0B5",
    "Parametrizar Reforma en Banner":          "#5C89B5",
    "Publicación en Página Web":               "#F47B20",
}

STATUS_LABEL = {
    "done":    "Finalizado",
    "inprog":  "En proceso",
    "nostart": "Sin iniciar",
    "info":    "Informativo",
    "na":      "No aplica",
}

STATUS_COLOR = {
    "done":    "#A6CE38",
    "inprog":  "#1FB2DE",
    "nostart": "#EC0677",
    "info":    "#FBAF17",
    "na":      "#9aabb5",
}


# ─── Clasificadores ────────────────────────────────────────────────────────────
def _cls_status(v):
    s = str(v).strip().lower()
    if not s or s in ("none", "nan"):
        return "na"
    if "no aplica" in s:
        return "na"
    if s == "finalizado" or s in ("si", "sí"):
        return "done"
    if "sin iniciar" in s or s == "no":
        return "nostart"
    if s == "en proceso":
        return "inprog"
    if "aprobado por el men" in s:
        return "done"
    keywords_inprog = [
        "visita de pares", "evaluación de sala", "elaboración",
        "completitud", "con resolución", "notificado",
        "con notificación", "pendiente",
    ]
    if any(k in s for k in keywords_inprog):
        return "inprog"
    return "inprog" if s else "na"


def _cls_pct(v):
    s = str(v).strip().lower()
    if not s or s in ("none", "nan", "no aplica"):
        return "na"
    try:
        f = float(s.replace("%", "").replace(",", "."))
        fv = f if f > 1 else f * 100
        if fv >= 100:
            return "done"
        if fv > 0:
            return "inprog"
        return "nostart"
    except Exception:
        return "inprog"


def _cls_num(v):
    s = str(v).strip().lower()
    if not s or s in ("none", "nan", "no aplica"):
        return "na"
    try:
        return "done" if float(s) > 0 else "nostart"
    except Exception:
        return "na"


def _classify(tipo, v):
    s = str(v).strip()
    if tipo == "pct":
        return _cls_pct(s)
    if tipo in ("status", "estado_tramite"):
        return _cls_status(s)
    if tipo == "num":
        return _cls_num(s)
    if tipo in ("info", "date"):
        return "info" if s and s not in ("", "—", "None", "nan") else "na"
    return "na"


def _find_col(df, name):
    nl = name.lower().strip()
    for c in df.columns:
        if c.lower().strip() == nl:
            return c
    for c in df.columns:
        if nl in c.lower():
            return c
    return None


# ─── Carga y cálculo ──────────────────────────────────────────────────────────
def _build_df():
    df = pd.read_excel(DATA_PATH, sheet_name="Maestro", header=9, dtype=str).fillna("")

    # Normalizar nombres de columnas (quitar espacios al inicio/fin)
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    # Renombrar columna de periodo (viene como Unnamed: 73)
    if "Unnamed: 73" in df.columns:
        df = df.rename(columns={"Unnamed: 73": "PERIODO DE IMPLEMENTACIÓN"})

    # Filtrar filas sin programa
    df = df[df["NOMBRE DEL PROGRAMA"].str.strip() != ""].copy()
    df = df.reset_index(drop=True)

    # Normalizar periodo
    df["PERIODO DE IMPLEMENTACIÓN"] = (
        df["PERIODO DE IMPLEMENTACIÓN"].str.split("\n").str[0].str.strip()
    )

    # Clasificación + valor por cada etapa
    for i, (proc, etapa, col_csv, tipo) in enumerate(ETAPAS_MAP):
        col = col_csv if col_csv in df.columns else _find_col(df, col_csv)
        if col:
            df[f"cl_{i}"]  = df[col].apply(lambda v, t=tipo: _classify(t, v))
            df[f"val_{i}"] = df[col].apply(
                lambda v: str(v).strip() if str(v).strip() not in ("", "None", "nan") else "—"
            )
        else:
            df[f"cl_{i}"]  = "na"
            df[f"val_{i}"] = "—"

    # Avance por proceso
    for proc in PROCESOS:
        idxs = [i for i, (p, _, _, _) in enumerate(ETAPAS_MAP) if p == proc]
        cl_cols = [f"cl_{i}" for i in idxs]

        def _pct(row, cols=cl_cols):
            app = [row[c] for c in cols if row[c] not in ("na", "info")]
            if not app:
                return np.nan
            return round(sum(100 if v == "done" else 50 if v == "inprog" else 0 for v in app) / len(app))

        df[f"proc_{proc}"] = df.apply(_pct, axis=1)

    # Avance general
    p_cols = [f"proc_{p}" for p in PROCESOS]

    def _avg(row, cols=p_cols):
        vals = [row[c] for c in cols if pd.notna(row[c])]
        return round(sum(vals) / len(vals)) if vals else 0

    df["avance_general"] = df.apply(_avg, axis=1)

    # ── Columnas auxiliares para Riesgos / Periodo Propuesto ─────────────────
    def _to_pct_num(v):
        s = str(v).strip().lower()
        if not s or s in ("none", "nan", "no aplica", "—", ""):
            return 0.0
        try:
            f = float(s.replace("%", "").replace(",", "."))
            return round(f if f > 1 else f * 100, 1)
        except Exception:
            return 0.0

    # Porcentajes numéricos
    df["pc_pct"]   = df["val_9"].apply(_to_pct_num)   # AK: % avance contenidos
    df["conv_pct"] = df["val_12"].apply(_to_pct_num)  # AS: % avance convenios
    df["ban_pct"]  = df["val_15"].apply(_to_pct_num)  # BB: % avance banner

    # Estado directo de Concepto Financiero (col T)
    df["cf_st"] = df["cl_3"]
    # Estado directo de Producción de Contenidos (col AK)
    df["pc_st"] = df["cl_9"]   # "na" = No aplica (Presencial)

    # syl_val: buscar columna "Syllabus completos" o derivar de Número de syllabus
    syl_col = (_find_col(df, "SYLLABUS COMPLETOS") or
               _find_col(df, "Syllabus completos") or
               _find_col(df, "Syllabus completados"))
    if syl_col:
        def _syl_from_col(v):
            s = str(v).strip().lower()
            if s in ("si", "sí", "yes", "1"):
                return "Si"
            if s in ("no aplica", "nan", "none", "—", ""):
                return "N/A"
            return "NO"
        df["syl_val"] = df[syl_col].apply(_syl_from_col)
        df.loc[df["MODALIDAD"] == "Presencial", "syl_val"] = "N/A"
    else:
        # Derivar desde "Número de syllabus" (val_7): si tiene valor positivo → Si
        def _derive_syl(row):
            if row.get("MODALIDAD", "") == "Presencial":
                return "N/A"
            v = str(row.get("val_7", "—")).strip()
            if v in ("—", "no aplica", "None", "nan", ""):
                return "NO"
            try:
                return "Si" if float(v) > 0 else "NO"
            except Exception:
                return "NO" if v.lower() in ("0", "no", "no aplica") else "Si"
        df["syl_val"] = df.apply(_derive_syl, axis=1)

    # periodo propuesto (lógica simplificada)
    def _proposed_period(row):
        per = str(row.get("PERIODO DE IMPLEMENTACIÓN", "")).strip()
        if "oferta" in per.lower():
            return "Ya está en oferta"
        cf  = str(row.get("cf_st", "nostart"))
        cf_done = cf in ("done", "inprog")
        pc_pct  = float(row.get("pc_pct", 0) or 0)
        pc_na   = str(row.get("pc_st", "nostart")) == "na"
        if cf_done:
            if not pc_na and pc_pct > 0:
                return "2026-2"
            else:
                return "2027-1"
        return per if per else "2027-2"

    df["periodo_propuesto"] = df.apply(_proposed_period, axis=1)

    return df


def load_data():
    """Retorna DataFrame procesado, usando st.cache_data si Streamlit está disponible."""
    try:
        import streamlit as st

        @st.cache_data
        def _cached():
            return _build_df()

        return _cached()
    except Exception:
        return _build_df()


# ─── Filtros ──────────────────────────────────────────────────────────────────
def apply_filters(df, modalidad=None, facultad=None, periodo=None):
    """Acepta str o lista en cada parámetro. Vacío / None = sin filtro."""
    def _to_list(v):
        if not v:
            return []
        return list(v) if not isinstance(v, str) else [v]

    mods = _to_list(modalidad)
    facs = _to_list(facultad)
    pers = _to_list(periodo)

    if mods:
        df = df[df["MODALIDAD"].isin(mods)]
    if facs:
        df = df[df["FACULTAD"].isin(facs)]
    if pers:
        mask = df["PERIODO DE IMPLEMENTACIÓN"].isin(pers)
        if "2027-1" in pers:
            mask = mask | df["PERIODO DE IMPLEMENTACIÓN"].str.contains("2027-1", na=False)
        df = df[mask]
    return df.copy()


def color_for_pct(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "#6e7681"
    if p >= 70:
        return "#3ecf8e"
    if p >= 45:
        return "#4f8ef7"
    if p >= 25:
        return "#f97316"
    return "#ef4444"
