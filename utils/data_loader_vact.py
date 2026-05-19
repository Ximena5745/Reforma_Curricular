"""
utils/data_loader_vact.py
Carga y procesa la hoja 'Etapas' del archivo VACT (Fase 2).
Fuente: data/raw/CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "raw" / "CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx"

PHASE_ROW = 7   # fila 8 Excel: fases
HEADER_ROW = 10  # fila 11 Excel: encabezados actividades
DATA_START_ROW = 11  # fila 12 Excel: primer programa

INFO_COLS = [
    "FACULTAD",
    "ESCUELA",
    "NOMBRE DEL PROGRAMA",
    "MODALIDAD",
    "NIVEL",
    "SEDE",
    "PERIODO DE IMPLEMENTACIÓN",
]

FAC_ABREV = {
    "Facultad de Sociedad, Cultura y Creatividad": "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación": "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
}

from utils.poli_theme import (
    ETAPA_CLR,
    FACULTAD_CLR,
    STATUS_CLR,
    color_for_pct,
)

FAC_COLORS = FACULTAD_CLR
FAC_ABREV_INV = {v: k for k, v in FAC_ABREV.items()}

STATUS_LABEL = {
    "done": "Finalizado",
    "inprog": "En proceso",
    "nostart": "Sin iniciar",
    "devuelto": "Devuelto",
    "info": "Informativo",
    "na": "No aplica",
}

STATUS_COLOR = STATUS_CLR

# Etapas canónicas (orden de visualización)
ETAPAS_ORDEN = [
    "Alistamiento Curricular",
    "Diseño Curricular",
    "Desarrollo Curricular",
    "Implementación Curricular",
]

ETAPA_PCT_COL = {
    "Alistamiento Curricular": "pct_alistamiento",
    "Diseño Curricular": "pct_diseno",
    "Desarrollo Curricular": "pct_desarrollo",
    "Implementación Curricular": "pct_implementacion",
}

ETAPA_SLUG = {
    "Alistamiento Curricular": "alistamiento",
    "Diseño Curricular": "diseno",
    "Desarrollo Curricular": "desarrollo",
    "Implementación Curricular": "implementacion",
}

ETAPA_HEADER_CLR = ETAPA_CLR


def _norm(s) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _norm_phase_name(s: str) -> str:
    """Normaliza nombres de fase del Excel."""
    t = _norm(s)
    if "alistamiento" in t:
        return "Alistamiento Curricular"
    if "dise" in t and "curricular" in t:
        return "Diseño Curricular"
    if "desarr" in t or "desarrollo" in t:
        return "Desarrollo Curricular"
    if "implement" in t:
        return "Implementación Curricular"
    if "fases de la reforma" in t:
        return "Info Programa"
    return str(s).strip()


def homologar_nivel(val) -> str:
    v = str(val).strip().lower()
    if any(v.startswith(p) for p in ("profesional", "tecnico", "técnico", "tecnologico", "tecnológico", "tecn")):
        return "Pregrado"
    if any(v.startswith(p) for p in ("maestria", "maestría", "especializacion", "especialización", "maest", "espec")):
        return "Posgrado"
    return ""


def _cls_status(v) -> str:
    s = str(v).strip().lower()
    if not s or s in ("none", "nan", ""):
        return "na"
    if "no aplica" in s:
        return "na"
    if s in ("finalizado", "si", "sí"):
        return "done"
    if "sin iniciar" in s or s == "no":
        return "nostart"
    if s == "devuelto":
        return "devuelto"
    if s == "en proceso":
        return "inprog"
    if "aprobado" in s or "renovación" in s or "renovacion" in s:
        return "inprog"
    keywords_inprog = [
        "visita", "evaluación", "elaboración", "completitud", "resolución",
        "notificado", "pendiente",
    ]
    if any(k in s for k in keywords_inprog):
        return "inprog"
    if s == "informativo" or "informativo" in s:
        return "info"
    return "inprog" if s else "na"


def _cls_pct_value(v) -> float | None:
    """Convierte valor de celda a porcentaje 0-100."""
    s = str(v).strip().lower()
    if not s or s in ("none", "nan", "no aplica", "—", ""):
        return None
    try:
        f = float(s.replace("%", "").replace(",", "."))
        return round(f * 100 if 0 <= f <= 1 else f, 1)
    except Exception:
        return None


def _activity_score(cl: str) -> float | None:
    if cl == "done":
        return 100.0
    if cl == "inprog":
        return 50.0
    if cl == "nostart":
        return 0.0
    if cl == "devuelto":
        return 25.0
    return None  # na / info no cuentan


def _build_phase_column_map(raw: pd.DataFrame) -> tuple[dict, list[dict]]:
    """
    Retorna (phase_by_col_index, activities_list).
    activities_list: [{phase, name, col_idx, is_pct}, ...]
    """
    phase_row = raw.iloc[PHASE_ROW]
    header_row = raw.iloc[HEADER_ROW]

    phase_by_col: dict[int, str] = {}
    current_phase = "Info Programa"
    for j in range(raw.shape[1]):
        pv = phase_row.iloc[j]
        if pd.notna(pv) and str(pv).strip():
            current_phase = _norm_phase_name(str(pv))
        phase_by_col[j] = current_phase

    activities: list[dict] = []
    for j in range(raw.shape[1]):
        hv = header_row.iloc[j]
        if pd.isna(hv) or not str(hv).strip():
            continue
        hname = str(hv).strip()
        phase = phase_by_col.get(j, "Info Programa")

        is_pct = "% de avance" in _norm(hname) or hname.startswith("%")
        is_general = "general de reforma" in _norm(hname)

        if phase == "Info Programa" and not is_pct:
            continue

        if is_general:
            activities.append({
                "phase": "General",
                "name": hname,
                "col_idx": j,
                "is_pct": True,
                "is_general": True,
            })
            continue

        if is_pct:
            activities.append({
                "phase": phase,
                "name": hname,
                "col_idx": j,
                "is_pct": True,
                "is_general": False,
            })
        elif phase in ETAPAS_ORDEN:
            activities.append({
                "phase": phase,
                "name": hname,
                "col_idx": j,
                "is_pct": False,
                "is_general": False,
            })

    return phase_by_col, activities


def _build_etapas_df() -> pd.DataFrame:
    raw = pd.read_excel(DATA_PATH, sheet_name="Etapas", header=None, dtype=str)
    raw = raw.fillna("")

    _, activities_meta = _build_phase_column_map(raw)
    header_row = raw.iloc[HEADER_ROW]

    # Índices fijos de columnas info (según fila 11 del Excel)
    info_idx = {
        "FACULTAD": 2,
        "ESCUELA": 3,
        "NOMBRE DEL PROGRAMA": 4,
        "MODALIDAD": 5,
        "NIVEL": 6,
        "SEDE": 8,
        "PERIODO DE IMPLEMENTACIÓN": 10,
    }

    data_raw = raw.iloc[DATA_START_ROW:].reset_index(drop=True)
    n_rows = len(data_raw)

    prog_idx = info_idx["NOMBRE DEL PROGRAMA"]
    mask = data_raw.iloc[:, prog_idx].astype(str).str.strip() != ""
    data_raw = data_raw[mask].reset_index(drop=True)
    n_rows = len(data_raw)

    df = pd.DataFrame()
    for col_name, idx in info_idx.items():
        if idx < data_raw.shape[1]:
            df[col_name] = data_raw.iloc[:, idx].astype(str).str.strip().values

    # Normalizar periodo
    if "PERIODO DE IMPLEMENTACIÓN" in df.columns:
        df["PERIODO DE IMPLEMENTACIÓN"] = (
            df["PERIODO DE IMPLEMENTACIÓN"].astype(str).str.split("\n").str[0].str.strip()
        )

    # Nivel homologado
    if "NIVEL" in df.columns:
        df["NIVEL_HOMOLOGADO"] = df["NIVEL"].apply(homologar_nivel)
    else:
        df["NIVEL_HOMOLOGADO"] = ""

    # Facultad abreviada
    if "FACULTAD" in df.columns:
        df["FACULTAD_ABREV"] = df["FACULTAD"].map(FAC_ABREV).fillna("—")
        df["FACULTAD_COLOR"] = df["FACULTAD_ABREV"].map(FAC_COLORS).fillna("#6e7681")
    else:
        df["FACULTAD_ABREV"] = "—"
        df["FACULTAD_COLOR"] = "#6e7681"

    # Procesar actividades por etapa (por índice de columna, evita duplicados de nombre)
    act_idx = 0
    for meta in activities_meta:
        col_idx = meta["col_idx"]
        series = data_raw.iloc[:n_rows, col_idx].astype(str).str.strip()
        series.index = range(n_rows)

        if meta.get("is_general"):
            df["avance_general_vact"] = series.apply(
                lambda v: _cls_pct_value(v) if _cls_pct_value(v) is not None else 0.0
            )
            continue

        if meta["is_pct"]:
            pct_key = ETAPA_PCT_COL.get(meta["phase"])
            if pct_key:
                df[pct_key] = series.apply(
                    lambda v: _cls_pct_value(v) if _cls_pct_value(v) is not None else np.nan
                )
            continue

        # Actividad individual
        cl_col = f"cl_act_{act_idx}"
        val_col = f"val_act_{act_idx}"
        df[cl_col] = series.apply(_cls_status)
        df[val_col] = series.apply(
            lambda v: str(v).strip() if str(v).strip() not in ("", "None", "nan") else "—"
        )
        df[f"act_phase_{act_idx}"] = meta["phase"]
        df[f"act_name_{act_idx}"] = meta["name"]
        act_idx += 1

    df["_n_activities"] = act_idx

    # Calcular % por etapa si no viene del Excel o para validar
    for etapa in ETAPAS_ORDEN:
        pct_key = ETAPA_PCT_COL[etapa]
        if pct_key not in df.columns:
            df[pct_key] = np.nan

        # Recalcular desde actividades si faltan valores
        mask_missing = df[pct_key].isna()
        if mask_missing.any():
            scores = []
            for i in range(act_idx):
                if df[f"act_phase_{i}"].iloc[0] != etapa:
                    continue
                cl_col = f"cl_act_{i}"
                row_scores = df[cl_col].apply(_activity_score)
                scores.append(row_scores)

            if scores:
                mat = pd.concat(scores, axis=1)
                calc = mat.mean(axis=1, skipna=True).round(1)
                df.loc[mask_missing, pct_key] = calc[mask_missing]

        # Rellenar NaN con 0
        df[pct_key] = df[pct_key].fillna(0).astype(float)

    if "avance_general_vact" not in df.columns:
        pct_cols = [ETAPA_PCT_COL[e] for e in ETAPAS_ORDEN]
        df["avance_general_vact"] = df[pct_cols].mean(axis=1).round(1)
    else:
        df["avance_general_vact"] = df["avance_general_vact"].fillna(0).astype(float)

    # Si avance general viene como decimal 0-1
    if df["avance_general_vact"].max() <= 1.0:
        df["avance_general_vact"] = (df["avance_general_vact"] * 100).round(1)

    for etapa in ETAPAS_ORDEN:
        pk = ETAPA_PCT_COL[etapa]
        if df[pk].max() <= 1.0:
            df[pk] = (df[pk] * 100).round(1)

    return df


# Metadatos de actividades (se construyen al cargar)
_ACTIVITIES_META: list[dict] = []


def _ensure_activities_meta(df: pd.DataFrame) -> list[dict]:
    global _ACTIVITIES_META
    if _ACTIVITIES_META:
        return _ACTIVITIES_META
    n = int(df.get("_n_activities", pd.Series([0])).iloc[0]) if len(df) else 0
    meta = []
    for i in range(n):
        if f"act_phase_{i}" not in df.columns:
            break
        meta.append({
            "idx": i,
            "phase": df[f"act_phase_{i}"].iloc[0],
            "name": df[f"act_name_{i}"].iloc[0],
        })
    _ACTIVITIES_META = meta
    return meta


# Alias para reglas de riesgo / alertas (nombres normalizados del Excel)
ACTIVITY_ALIASES: dict[str, list[str]] = {
    "proyecciones_fin": [
        "5.formato de proyecciones",
        "formato de proyecciones académicas y financieras",
        "formato de proyecciones academicas y financieras",
        "estudio de viabilidad financiera",
    ],
    "produccion_contenido": [
        "producción del contenido",
        "produccion del contenido",
        "% avance contenidos",
        "contenidos virtuales",
    ],
    "banner_convenios": [
        "parametrización en banner",
        "parametrizacion en banner",
        "convenios y homologaciones",
    ],
    "syllabus": ["syllabus aprobado", "syllabus"],
    "convenios": ["formato maestro de convenios", "maestro de convenios"],
    "cronograma_men": [
        "cronograma de trámites frente al men",
        "cronograma de tramites frente al men",
        "trámites frente al men",
    ],
}

_ACTIVITY_IDX_CACHE: dict[str, int | None] = {}


def _resolve_activity_idx(df: pd.DataFrame, key: str) -> int | None:
    if key in _ACTIVITY_IDX_CACHE:
        return _ACTIVITY_IDX_CACHE[key]
    patterns = ACTIVITY_ALIASES.get(key, [])
    if not patterns:
        _ACTIVITY_IDX_CACHE[key] = None
        return None
    meta = _ensure_activities_meta(df)
    for m in meta:
        name_n = _norm(m["name"])
        for pat in patterns:
            if pat in name_n or name_n in pat:
                _ACTIVITY_IDX_CACHE[key] = m["idx"]
                return m["idx"]
    _ACTIVITY_IDX_CACHE[key] = None
    return None


def activity_cl(df: pd.DataFrame, key: str) -> pd.Series:
    """Serie de clasificación (done/inprog/...) para una actividad por alias."""
    idx = _resolve_activity_idx(df, key)
    if idx is None:
        return pd.Series("na", index=df.index)
    col = f"cl_act_{idx}"
    if col not in df.columns:
        return pd.Series("na", index=df.index)
    return df[col]


def activity_val(df: pd.DataFrame, key: str) -> pd.Series:
    """Serie de valor crudo de actividad por alias."""
    idx = _resolve_activity_idx(df, key)
    if idx is None:
        return pd.Series("—", index=df.index)
    col = f"val_act_{idx}"
    if col not in df.columns:
        return pd.Series("—", index=df.index)
    return df[col]


def activity_not_done(df: pd.DataFrame, key: str) -> pd.Series:
    """True si la actividad no está finalizada."""
    cl = activity_cl(df, key)
    return cl != "done"


def activity_in_progress(df: pd.DataFrame, key: str) -> pd.Series:
    cl = activity_cl(df, key)
    return cl == "inprog"


def activity_val_contains(df: pd.DataFrame, key: str, substring: str) -> pd.Series:
    vals = activity_val(df, key).astype(str).str.lower()
    return vals.str.contains(substring.lower(), na=False)


def load_etapas_data() -> pd.DataFrame:
    """Retorna DataFrame procesado de la hoja Etapas."""
    global _ACTIVITIES_META, _ACTIVITY_IDX_CACHE
    _ACTIVITIES_META = []
    _ACTIVITY_IDX_CACHE = {}
    try:
        import streamlit as st

        @st.cache_data
        def _cached(_v: int = 3):
            return _build_etapas_df()

        return _cached()
    except Exception:
        return _build_etapas_df()


def apply_filters_vact(
    df: pd.DataFrame,
    modalidad=None,
    facultad=None,
    periodo=None,
    nivel=None,
) -> pd.DataFrame:
    """Filtros para Fase 2. facultad acepta nombres completos o abreviaturas."""

    def _to_list(v):
        if not v:
            return []
        return list(v) if not isinstance(v, str) else [v]

    mods = _to_list(modalidad)
    facs = _to_list(facultad)
    pers = _to_list(periodo)
    nivs = _to_list(nivel)

    out = df.copy()
    if mods and "MODALIDAD" in out.columns:
        out = out[out["MODALIDAD"].isin(mods)]
    if facs and "FACULTAD" in out.columns:
        full_facs = [FAC_ABREV_INV.get(f, f) for f in facs]
        out = out[out["FACULTAD"].isin(full_facs)]
    if pers and "PERIODO DE IMPLEMENTACIÓN" in out.columns:
        mask = out["PERIODO DE IMPLEMENTACIÓN"].isin(pers)
        if "2027-1" in pers:
            mask = mask | out["PERIODO DE IMPLEMENTACIÓN"].str.contains("2027-1", na=False)
        if any("oferta" in str(p).lower() for p in pers):
            mask = mask | out["PERIODO DE IMPLEMENTACIÓN"].str.contains("oferta", case=False, na=False)
        out = out[mask]
    if nivs and "NIVEL_HOMOLOGADO" in out.columns:
        out = out[out["NIVEL_HOMOLOGADO"].isin(nivs)]
    return out.reset_index(drop=True)


def get_etapas_by_programa(df: pd.DataFrame, nombre_programa: str) -> dict:
    """Actividades + estados de un programa."""
    meta = _ensure_activities_meta(df)
    row = df[df["NOMBRE DEL PROGRAMA"].astype(str).str.strip() == str(nombre_programa).strip()]
    if row.empty:
        return {"programa": nombre_programa, "etapas": {}}
    row = row.iloc[0]
    result: dict = {"programa": nombre_programa, "etapas": {}}
    for etapa in ETAPAS_ORDEN:
        acts = []
        for m in meta:
            if m["phase"] != etapa:
                continue
            i = m["idx"]
            cl = row.get(f"cl_act_{i}", "na")
            val = row.get(f"val_act_{i}", "—")
            score = _activity_score(cl)
            acts.append({
                "nombre": m["name"],
                "estado": STATUS_LABEL.get(cl, cl),
                "estado_key": cl,
                "valor": val,
                "pct": score if score is not None else "—",
            })
        pct_col = ETAPA_PCT_COL[etapa]
        result["etapas"][etapa] = {
            "pct": float(row.get(pct_col, 0) or 0),
            "actividades": acts,
        }
    result["avance_general"] = float(row.get("avance_general_vact", 0) or 0)
    result["info"] = {
        "FACULTAD": row.get("FACULTAD", "—"),
        "FACULTAD_ABREV": row.get("FACULTAD_ABREV", "—"),
        "FACULTAD_COLOR": row.get("FACULTAD_COLOR", "#6e7681"),
        "ESCUELA": row.get("ESCUELA", "—"),
        "MODALIDAD": row.get("MODALIDAD", "—"),
        "NIVEL": row.get("NIVEL", "—"),
        "NIVEL_HOMOLOGADO": row.get("NIVEL_HOMOLOGADO", "—"),
        "SEDE": row.get("SEDE", "—"),
        "PERIODO DE IMPLEMENTACIÓN": row.get("PERIODO DE IMPLEMENTACIÓN", "—"),
    }
    return result


def get_estadisticas_etapa(df: pd.DataFrame, etapa_name: str) -> dict:
    """Estadísticas agregadas de una etapa sobre el df filtrado."""
    pct_col = ETAPA_PCT_COL.get(etapa_name)
    if not pct_col or pct_col not in df.columns or len(df) == 0:
        return {"pct_promedio": 0, "done": 0, "inprog": 0, "nostart": 0, "na": 0, "total_act": 0}

    meta = _ensure_activities_meta(df)
    acts_meta = [m for m in meta if m["phase"] == etapa_name]
    done = inprog = nostart = na = 0
    for m in acts_meta:
        col = f"cl_act_{m['idx']}"
        if col not in df.columns:
            continue
        for cl in df[col]:
            if cl == "done":
                done += 1
            elif cl == "inprog":
                inprog += 1
            elif cl == "nostart":
                nostart += 1
            else:
                na += 1

    return {
        "pct_promedio": round(float(df[pct_col].mean()), 1),
        "done": done,
        "inprog": inprog,
        "nostart": nostart,
        "na": na,
        "total_act": len(acts_meta) * len(df) if acts_meta else 0,
        "n_programas": len(df),
    }


def count_actividades_completadas(row, etapa_name: str, df: pd.DataFrame) -> tuple[int, int]:
    """Retorna (completadas, total) para una fila y etapa."""
    meta = _ensure_activities_meta(df)
    acts = [m for m in meta if m["phase"] == etapa_name]
    total = len(acts)
    done = sum(1 for m in acts if row.get(f"cl_act_{m['idx']}") == "done")
    return done, total
