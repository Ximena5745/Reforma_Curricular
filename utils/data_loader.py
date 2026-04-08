def homologar_nivel(nivel_bd):
    """
    Homologa el valor de NIVEL (columna G) a 'Pregrado' o 'Posgrado' según la tabla de equivalencias.
    """
    if not isinstance(nivel_bd, str):
        return ""
    nivel = nivel_bd.strip().lower()
    if nivel in ["profesional", "técnico", "tecnológico"]:
        return "Pregrado"
    if nivel in ["maestría", "especialización"]:
        return "Posgrado"
    return ""
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
    ("Producción de Contenidos",                 "Número de syllabus",                               "Número de syllabus",                                        "info"),
    ("Producción de Contenidos",                 "Total módulos con cambios",                        "TOTAL  MÓDULOS CON CAMBIOS",                                "info"),
    ("Producción de Contenidos",                 "% avance contenidos virtuales",                    "% avance contenidos virtuales",                             "pct"),
    ("Convenios Institucionales",                "Acta de homologación",                             "Acta de homologación",                                      "status"),
    ("Convenios Institucionales",                "Ruta sugerida homologación/articulación",          "Ruta sugerida programa homologación/articulación convenio", "status"),
    ("Convenios Institucionales",                "% avance",                                         "% avance",                                                  "pct"),
    ("Parametrizar Reforma en Banner",           "Total aulas master",                               "Total Aulas Master",                                        "num"),
    ("Parametrizar Reforma en Banner",           "Avance de aulas master",                           "Avance de Aulas Master",                                    "num"),
    ("Parametrizar Reforma en Banner",           "% de avance",                                      "% de Avance",                                               "pct"),
    ("Parametrizar Reforma en Banner",           "Configurar plan de estudios en Banner",            "Configurar plan de estudios en Banner",                     "status"),
    ("Publicación en Página Web",                "Publicar plan de estudios en web",                 "Publicar plan de estudios en Web",                          "status"),
    ("Publicación en Página Web",                "Fecha fin",                                        "FECHA FIN",                                                 "date"),
    ("Publicación en Página Web",                "Periodo de implementación",                        "PERIODO DE IMPLEMENTACIÓN",                                 "info"),
    ("Publicación en Página Web",                "% de avance web",                                  "% de Avance.1",                                             "pct_nostart"),
    ("Syllabus",                                 "Syllabus completos",                               "SYLLABUS COMPLETOS.1",                                      "syllabus"),
]

PROCESOS = [
    "Gestión Académica",
    "Gestión Financiera",
    "Aseguramiento de la Calidad",
    "Syllabus",
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
    "Syllabus":                                "#9333ea",
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
    if tipo == "syllabus":
        sl = s.lower()
        if sl in ("si", "sí", "yes", "1"):      return "done"
        if sl in ("no",):                        return "inprog"
        return "na"
    if tipo == "pct_nostart":
        # Como pct pero vacío/nulo → "nostart" en lugar de "na"
        s2 = s.lower()
        if not s2 or s2 in ("none", "nan", "no aplica", "—"):
            return "nostart"
        return _cls_pct(s2)
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


def homologar_nivel(val):
    """Homologa el valor de la columna NIVEL de la BD a Pregrado o Posgrado."""
    v = str(val).strip().lower()
    if v in ("profesional", "t\u00e9cnico", "tecnol\u00f3gico", "tecnico", "tecnologico"):
        return "Pregrado"
    if v in ("maestr\u00eda", "especializaci\u00f3n", "maestria", "especializacion"):
        return "Posgrado"
    return ""


# ─── Carga y cálculo ──────────────────────────────────────────────────────────
def _build_df():
    df = pd.read_excel(DATA_PATH, sheet_name="Borrador", header=9, dtype=str).fillna("")

    # Normalizar nombres de columnas (quitar espacios al inicio/fin)
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    # Renombrar columna de periodo (viene como Unnamed: 73)
    if "Unnamed: 73" in df.columns:
        df = df.rename(columns={"Unnamed: 73": "PERIODO DE IMPLEMENTACIÓN"})

    # Filtrar filas sin programa
    df = df[df["NOMBRE DEL PROGRAMA"].str.strip() != ""].copy()
    df = df.reset_index(drop=True)

<<<<<<< HEAD
    # Homologar columna NIVEL (columna G, índice 6) a Pregrado/Posgrado
    col_nivel = _find_col(df, "NIVEL")
    if not col_nivel and len(df.columns) > 6:
        col_nivel = df.columns[6]
=======
    # Homologar columna NIVEL (columna G) a Pregrado/Posgrado
    col_nivel = _find_col(df, "NIVEL")
>>>>>>> fbaef3fd2f237446123814ceb6816a340e0bfb0e
    if col_nivel:
        df["NIVEL_HOMOLOGADO"] = df[col_nivel].apply(homologar_nivel)
    else:
        df["NIVEL_HOMOLOGADO"] = ""

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

    # ── Override Syllabus: Presencial → "na" ─────────────────────────────────
    _syl_idx = next(i for i, (p,_,_,_) in enumerate(ETAPAS_MAP) if p == "Syllabus")
    df.loc[df["MODALIDAD"].str.strip().str.lower() == "presencial", f"cl_{_syl_idx}"] = "na"

    # ── Override Banner: Presencial → "na" en todos sus índices ──────────────
    # También Virtual/Híbrido con "No aplica" en BB (cl_15="na") → todos "na"
    _ban_idxs = [i for i, (p,_,_,_) in enumerate(ETAPAS_MAP) if p == "Parametrizar Reforma en Banner"]
    _pres_mask   = df["MODALIDAD"].str.strip().str.lower() == "presencial"
    _ban_pct_idx = next(i for i, (p,_,c,t) in enumerate(ETAPAS_MAP)
                        if p == "Parametrizar Reforma en Banner" and t == "pct")
    _noapl_mask  = (
        ~_pres_mask &
        (df["MODALIDAD"].str.strip().str.lower().isin(["virtual", "híbrido", "hibrido"])) &
        (df[f"cl_{_ban_pct_idx}"] == "na")
    )
    for _bi in _ban_idxs:
        df.loc[_pres_mask | _noapl_mask, f"cl_{_bi}"] = "na"

    # ── Override Aseguramiento de Calidad: lógica MEN ────────────────────────
    # Si col Z "¿Requiere informarse al MEN previa implementación?" = "Si"
    #   → col X "Fecha de Documentos de notificación MEN" mes/año < hoy → done
    #   → fecha >= hoy o vacía → inprog
    # Si No / vacío → mantiene clasificación de cl_5 (Estado del trámite)
    _col_req   = "¿Requiere informarse al MEN previa implementación?"
    _col_fecha = "Fecha de\nDocumentos de notificación MEN"
    _MESES_ES  = {
        "enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
        "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12,
    }

    def _parse_fecha_es(s):
        """Parsea 'Mes de YYYY' en español. Retorna Timestamp o NaT."""
        s = str(s).strip().lower()
        for mes, num in _MESES_ES.items():
            if mes in s:
                parts = s.replace("de", "").split()
                years = [p for p in parts if p.isdigit() and len(p) == 4]
                if years:
                    return pd.Timestamp(year=int(years[0]), month=num, day=1)
        return pd.NaT

    if _col_req in df.columns and _col_fecha in df.columns:
        _today_m = pd.Timestamp.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        def _cls_men(row):
            req = str(row[_col_req]).strip().lower()
            if req not in ("si", "sí"):
                return row["cl_5"]
            fecha_raw = str(row[_col_fecha]).strip()
            if not fecha_raw or fecha_raw in ("", "—", "None", "nan"):
                return "inprog"
            dt = _parse_fecha_es(fecha_raw)
            if pd.isna(dt):
                return "inprog"
            return "done" if dt < _today_m else "inprog"

        df["cl_5"] = df.apply(_cls_men, axis=1)

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

    # Índices dinámicos (se recalculan si cambia ETAPAS_MAP)
    _pc_pct_idx   = next((i for i, (p,_,_,t) in enumerate(ETAPAS_MAP)
                          if p == "Producción de Contenidos" and t == "pct"), None)
    _conv_pct_idx = next((i for i, (p,_,_,t) in enumerate(ETAPAS_MAP)
                          if p == "Convenios Institucionales" and t == "pct"), None)
    _web_pct_idx  = next((i for i, (p,_,_,t) in enumerate(ETAPAS_MAP)
                          if p == "Publicación en Página Web" and t == "pct_nostart"), None)
    # Porcentajes numéricos
    df["pc_pct"]   = (df[f"val_{_pc_pct_idx}"].apply(_to_pct_num)
                      if _pc_pct_idx   is not None else pd.Series([0.0]*len(df)))  # % avance contenidos
    df["conv_pct"] = (df[f"val_{_conv_pct_idx}"].apply(_to_pct_num)
                      if _conv_pct_idx is not None else pd.Series([0.0]*len(df)))  # % avance convenios
    df["ban_pct"]  = (df[f"val_{_ban_pct_idx}"].apply(_to_pct_num)
                      if _ban_pct_idx  is not None else pd.Series([0.0]*len(df)))  # % avance Banner
    df["web_pct"]  = (df[f"val_{_web_pct_idx}"].apply(_to_pct_num)
                      if _web_pct_idx is not None else 0.0)  # BH: % avance web

    # Presencial: ban_pct = 0 (No aplica — excluye de riesgos y cálculos)
    _pres = df["MODALIDAD"].str.strip().str.lower() == "presencial"
    df.loc[_pres, "ban_pct"] = 0.0

    # proc_Banner = ban_pct directamente (BB column determina el estado del proceso)
    # Así 100% BB → Finalizado, aunque otras sub-columnas Banner no estén completas
    _proc_ban = "proc_Parametrizar Reforma en Banner"
    if _proc_ban in df.columns:
        _ban_notna = df[_proc_ban].notna()
        df.loc[_ban_notna, _proc_ban] = df.loc[_ban_notna, "ban_pct"]

    # proc_Web = web_pct directamente (BH determina el estado del proceso)
    # Vacío en BH → 0 (Sin iniciar)
    _proc_web = "proc_Publicación en Página Web"
    if _proc_web in df.columns:
        df[_proc_web] = df["web_pct"]

    # Estado directo de Concepto Financiero (col T)
    df["cf_st"] = df["cl_3"]
    # Estado directo de Producción de Contenidos (% avance)
    df["pc_st"] = (df[f"cl_{_pc_pct_idx}"]
                   if _pc_pct_idx is not None else pd.Series(["nostart"]*len(df)))

    # syl_val: columna AD = "SYLLABUS COMPLETOS.1" (segunda ocurrencia, la correcta)
    # pandas renombra duplicados: la primera queda "SYLLABUS COMPLETOS", la segunda ".1"
    syl_col = (_find_col(df, "SYLLABUS COMPLETOS.1") or
               _find_col(df, "SYLLABUS COMPLETOS") or
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
        # Derivar desde "N\u00famero de syllabus" (val din\u00e1mico)
        _syl_num_idx = next((i for i,(p,_,_,_) in enumerate(ETAPAS_MAP)
                             if p == "Producci\u00f3n de Contenidos" and _ == "N\u00famero de syllabus"), None)
        _syl_num_col = f"val_{_syl_num_idx}" if _syl_num_idx is not None else None
        def _derive_syl(row):
            if row.get("MODALIDAD", "") == "Presencial":
                return "N/A"
            v = str(row.get(_syl_num_col, "—") if _syl_num_col else "—").strip()
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


def enrich_df(df):
    """
    Agrega columnas auxiliares al DataFrame si aún no existen.
    Llamar después de load_data() para garantizar disponibilidad en todas las páginas.
    """
    if "pc_pct" in df.columns:
        return df          # ya fue enriquecido

    def _to_pct_num(v):
        s = str(v).strip().lower()
        if not s or s in ("none", "nan", "no aplica", "—", ""):
            return 0.0
        try:
            f = float(s.replace("%", "").replace(",", "."))
            return round(f if f > 1 else f * 100, 1)
        except Exception:
            return 0.0

    # Índices dinámicos
    _pci = next((i for i,(p,_,_,t) in enumerate(ETAPAS_MAP) if p=="Producción de Contenidos" and t=="pct"), 8)
    _ci  = next((i for i,(p,_,_,t) in enumerate(ETAPAS_MAP) if p=="Convenios Institucionales" and t=="pct"), 11)
    _bi  = next((i for i,(p,_,_,t) in enumerate(ETAPAS_MAP) if p=="Parametrizar Reforma en Banner" and t=="pct"), 14)
    # Verificar que existan las columnas val_N necesarias
    v_pc = df[f"val_{_pci}"] if f"val_{_pci}" in df.columns else pd.Series(["—"] * len(df))
    v_cv = df[f"val_{_ci}"]  if f"val_{_ci}"  in df.columns else pd.Series(["—"] * len(df))
    v_bn = df[f"val_{_bi}"]  if f"val_{_bi}"  in df.columns else pd.Series(["—"] * len(df))
    c3   = df["cl_3"]        if "cl_3"        in df.columns else pd.Series(["nostart"] * len(df))
    c_pc = df[f"cl_{_pci}"]  if f"cl_{_pci}"  in df.columns else pd.Series(["nostart"] * len(df))

    df = df.copy()
    df["pc_pct"]   = v_pc.apply(_to_pct_num)
    df["conv_pct"] = v_cv.apply(_to_pct_num)
    df["ban_pct"]  = v_bn.apply(_to_pct_num)
    df["cf_st"]    = c3
    df["pc_st"]    = c_pc

    # syl_val: columna AD = "SYLLABUS COMPLETOS.1" (segunda ocurrencia, la correcta)
    syl_col = (_find_col(df, "SYLLABUS COMPLETOS.1") or
               _find_col(df, "SYLLABUS COMPLETOS") or
               _find_col(df, "Syllabus completos"))
    if syl_col:
        def _syl(v):
            s = str(v).strip().lower()
            if s in ("si", "sí", "yes", "1"):   return "Si"
            if s in ("no aplica", "nan", "none", "—", ""): return "N/A"
            return "NO"
        df["syl_val"] = df[syl_col].apply(_syl)
        df.loc[df["MODALIDAD"] == "Presencial", "syl_val"] = "N/A"
    else:
        _syl_n_idx = next((i for i,(p,e,_,_) in enumerate(ETAPAS_MAP)
                           if p == "Producci\u00f3n de Contenidos" and e == "N\u00famero de syllabus"), None)
        _syl_n_col = f"val_{_syl_n_idx}" if _syl_n_idx is not None else None
        def _derive_syl(row):
            if row.get("MODALIDAD", "") == "Presencial": return "N/A"
            v = str(row.get(_syl_n_col, "—") if _syl_n_col else "—").strip()
            if v in ("—", "no aplica", "None", "nan", ""): return "NO"
            try:   return "Si" if float(v) > 0 else "NO"
            except Exception: return "Si"
        df["syl_val"] = df.apply(_derive_syl, axis=1)

    # periodo_propuesto
    def _proposed(row):
        per = str(row.get("PERIODO DE IMPLEMENTACIÓN", "")).strip()
        if "oferta" in per.lower():       return "Ya está en oferta"
        cf = str(row.get("cf_st", "nostart"))
        cf_done = cf in ("done", "inprog")
        pc_pct  = float(row.get("pc_pct", 0) or 0)
        pc_na   = str(row.get("pc_st", "nostart")) == "na"
        if cf_done:
            return "2026-2" if (not pc_na and pc_pct > 0) else "2027-1"
        return per if per else "2027-2"

    df["periodo_propuesto"] = df.apply(_proposed, axis=1)
    return df


def load_data():
    """Retorna DataFrame procesado, usando st.cache_data si Streamlit está disponible.
    El argumento _n_etapas fuerza la invalidación del caché cuando cambia ETAPAS_MAP."""
    try:
        import streamlit as st

        @st.cache_data
        def _cached(_n_etapas: int):
            return _build_df()

        return _cached(len(ETAPAS_MAP))
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
