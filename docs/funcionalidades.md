# Funcionalidades y Lógica — Reforma Curricular

> **Fecha:** 2026-04-06  
> **Proyecto:** Dashboard Streamlit de seguimiento de la Reforma Curricular POLI  
> **Fuente canónica:** `data/raw/CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx`

---

## Resumen ejecutivo

El proyecto es un dashboard web construido con **Streamlit** que permite hacer seguimiento integral del proceso de reforma curricular de la institución. Se estructura en **9 procesos**, **20 etapas** de trabajo y un conjunto de reglas de negocio que transforman los datos crudos del Excel en indicadores visuales (KPIs, gráficos, tablas, exportaciones).

**Funcionalidades principales:**
- Dashboard general con métricas clave (avance global, promedios por proceso, conteo de urgentes)
- 6 páginas temáticas: Detalle por Etapa, Programa, Riesgos, Gestión Académica, Periodo Propuesto, Plan de Trabajo
- Generación y descarga de reportes en Excel desde la UI
- Script CLI para exportar el Excel maestro a CSV

---

## Cómo ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py

# Regenerar CSV desde el Excel (opcional)
python exportar_csv.py
```

---

## Punto(s) de entrada

| Archivo | Rol |
|---------|-----|
| `app.py` | Punto de entrada principal. Monta la app Streamlit, define el layout global, CSS institucional, sidebar y orquestación de KPIs. |
| `exportar_csv.py` | Script CLI. Lee la hoja `Borrador` del Excel y escribe `data/raw/control_maestro.csv`. No requiere Streamlit. |
| `pages/*.py` | Módulos de página Streamlit (1–6). Se acceden como rutas dentro de la app. |

---

## Flujo de datos

```
CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx
  ├── Hoja: "Borrador"  →  exportar_csv.py  →  control_maestro.csv
  └── Hoja: "Borrador"  →  utils/data_loader.py (lectura directa XLSX)
                                                 │
                                          load_data() + enrich_df()
                                                 │
                                   ┌──────────────┴──────────────┐
                                   │   DataFrame enriquecido     │
                                   │   cl_{i}, val_{i},         │
                                   │   proc_{Proceso},          │
                                   │   avance_general           │
                                   └──────────────┬──────────────┘
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                    app.py (KPIs)                              pages/*.py
```

**Decisión (confirmada):** la fuente canónica es el XLSX en `data/raw/`. `exportar_csv.py` es opcional como backup/audit trail.

---

## Archivos y lógica

### `app.py` — Dashboard principal

- **Rol:** Página de inicio "Resumen General". Carga datos, calcula KPIs, renderiza gráficos Plotly y tablas.
- **Dependencias internas:** `utils.data_loader` (`load_data`, `enrich_df`, `apply_filters`, `ETAPAS_MAP`, `PROCESOS`, `PROCESO_COLOR`, `STATUS_LABEL`, `STATUS_COLOR`, `color_for_pct`)
- **Funciones propias:**
  - `_arc(...)` — formateador de porcentajes
  - `_kpi(...)` — renderizador de caja KPI
  - `clasificar_programa(...)` — clasifica en "Crítico / En riesgo / En curso / Saludable" según `conv_pct`, `pc_pct`, `avance_general`
- **CSS:** degrade azul `#0F385A → #1A5276 → #1FB2DE`, colores de proceso, estilos de tabs, selectbox y DataFrame
- **Sidebar:** filtros globales por `MODALIDAD`, `FACULTAD` y `PERIODO`

### `exportar_csv.py` — Exportador CSV

- **Rol:** convierte la hoja `Borrador` del Excel en un CSV estático
- **Dependencias:** `openpyxl`, `csv`, `pathlib`
- **Parámetros hardcoded:**
  - `EXCEL_PATH = Path("CONTROL_MAESTRO_DE_REFORMA_CURRICULAR.xlsx")` ← en **raíz**
  - `OUT_PATH = Path("data/raw/control_maestro.csv")`
  - `SHEET_NAME = "Borrador"`, `HEADER_ROW = 10`, `DATA_START = 11`, `ID_COL = 2`
- **Lógica:** abre el workbook con `openpyxl`, extrae headers de fila 10, itera desde fila 11 omitiendo filas con `FACULTAD` vacía, convierte fechas a `YYYY-MM-DD`, escribe CSV UTF-8

### `utils/data_loader.py` — Núcleo de transformación

Este es el archivo con mayor lógica del proyecto. Toda la clasificación y enriquecimiento de datos ocurre aquí.

#### Constantes

**`ETAPAS_MAP`** — 22 tuplas `(proceso, nombre_etapa, columna_excel, tipo_clasificacion)`:

| Proceso | Etapa | Columna Excel | Tipo |
|---------|-------|---------------|------|
| Gestión Académica | Formato creación de programas Banner | `Formato creación de programas Banner` | `status` |
| Gestión Académica | La reforma cumple con la política curricular | `LA REFORMA CUMPLE CON LA POLITICA CURRICULAR` | `status` |
| Gestión Financiera | Concepto financiero | `CONCEPTO FINANCIERO` | `status` |
| Aseguramiento de la Calidad | Tipo de trámite | `Tipo de trámite de aseguramiento de la calidad` | `info` |
| Aseguramiento de la Calidad | Estado del trámite | `Estado del trámite` | `estado_tramite` |
| Ger. Planeación y Gestión Institucional | Correo para implementación | `CORREO PARA IMPLEMENTACIÓN` | `status` |
| Producción de Contenidos | Número de syllabus | `Número de syllabus` | `info` |
| Producción de Contenidos | Total módulos con cambios | `TOTAL MÓDULOS CON CAMBIOS` | `info` |
| Producción de Contenidos | % avance contenidos virtuales | `% avance contenidos virtuales` | `pct` |
| Convenios Institucionales | Acta de homologación | `Acta de homologación` | `status` |
| Convenios Institucionales | Ruta sugerida homologación/articulación | `Ruta sugerida programa homologación/articulación convenio` | `status` |
| Convenios Institucionales | % avance | `% avance` | `pct` |
| Parametrizar Reforma en Banner | Total aulas master | `Total Aulas Master` | `num` |
| Parametrizar Reforma en Banner | Avance de aulas master | `Avance de Aulas Master` | `num` |
| Parametrizar Reforma en Banner | % de avance | `% de Avance` | `pct` |
| Parametrizar Reforma en Banner | Configurar plan de estudios en Banner | `Configurar plan de estudios en Banner` | `status` |
| Publicación en Página Web | Publicar plan de estudios en web | `Publicar plan de estudios en Web` | `status` |
| Publicación en Página Web | Fecha fin | `FECHA FIN` | `date` |
| Publicación en Página Web | Periodo de implementación | `PERIODO DE IMPLEMENTACIÓN` | `info` |
| Publicación en Página Web | % de avance web | `% de Avance.1` | `pct_nostart` |
| Syllabus | Syllabus completos | `SYLLABUS COMPLETOS.1` | `syllabus` |

**`PROCESOS`** — 9 procesos ordenados.

**`PROCESO_COLOR`** — mapa proceso → color hex institucional.

**`STATUS_LABEL` / `STATUS_COLOR`** — `done`/#A6CE38, `inprog`/#1FB2DE, `nostart`/#EC0677, `info`/#FBAF17, `na`/#9aabb5.

#### Clasificadores

| Función | Lógica |
|---------|--------|
| `_cls_status(v)` | `done` si "finalizado"/"sí"/"aprobado por el men"; `nostart` si "sin iniciar"/"no"; `inprog` si "en proceso" o keywords ("visita de pares", "evaluación de sala", "pendiente"...); `na` si vacío/"no aplica" |
| `_cls_pct(v)` | Reemplaza `%` y `,`; si >= 100 → `done`, > 0 → `inprog`, = 0 → `nostart` |
| `_cls_num(v)` | > 0 → `inprog`, = 0 → `nostart` |
| `_cls_syllabus(v)` | Special: si `syl_val==1` y `_cls_pct` → `inprog`, fuerza `done` |
| `_classify(value, tipo)` | Dispatcher que elige el clasificador según `tipo` |

#### Parsing de fechas

**`_parse_fecha_es(fecha_str)`** — Convierte `dd Month yyyy` en español (ej. "12 enero 2024"). Retorna `datetime` o `None`.

#### `_build_df()` — Construcción del DataFrame

Pasos:
1. Lee Excel desde `DATA_PATH`, hoja `Borrador`, header fila 9 (0-based), dtype str.
2. Para cada tupla en `ETAPAS_MAP`: busca columna con `_find_col`, crea `cl_{i}` (clasificación) y `val_{i}` (valor original).
3. Calcula `proc_{Proceso}` = promedio de clasificaciones convertidas a numérico (done=1, inprog=0.5, nostart=0, na=0, info=0.5).
4. Calcula `avance_general` = promedio de los 9 `proc_{Proceso}`.
5. Deriva `pc_pct`, `conv_pct`, `ban_pct` como promedios de grupos de columnas.
6. Aplica **overrides por `MODALIDAD`**: ciertos procesos se forzanz a `na` según la modalidad del registro.
7. Aplica **override MEN**: si el valor contiene "aprobado por el men" → `done`.
8. Deriva `syl_val` desde `SYLLABUS COMPLETOS`.
9. Calcula `periodo_propuesto` desde `PERIODO DE IMPLEMENTACIÓN`.

**`enrich_df(df)`** — Añade columnas auxiliares si no existen.

**`load_data(path=None)`** — Función de alto nivel con cache (`st.cache_data` en contexto Streamlit, fallback directo otherwise).

**`apply_filters(df, modalidad, facultad, periodo)`** — Filtra por las columnas indicadas.

**`color_for_pct(p)`** — Retorna color hex: >75% verde, >50% amarillo, >25% naranja, ≤25% rojo.

### Páginas (`pages/`)

| Archivo | Propósito | Funciones clave |
|---------|-----------|-----------------|
| `1_Detalle_por_Etapa.py` | Consolidado por etapa y proceso; gráficos de barras y distribución por estado | `_render_etapa`, `_render_proceso` |
| `2_Programa.py` | Tabla maestra de programas + ficha detallada con selección | `_fit_columns`, radar chart |
| `3_Riesgos.py` | Evaluación cualitativa por 5 criterios de riesgo | `_crag`, `_table_risk` |
| `4_Gestion_Academica.py` | Tabla completa con exportación a Excel estilizado | `_gen_excel` (openpyxl Workbook con colores) |
| `5_Periodo_Propuesto.py` | Cálculo y visualización del periodo propuesto | `_periodo_table` |
| `6_Plan_de_Trabajo.py` | Plan de trabajo sugerido por programa; descarga Excel | `_gen_excel_plan`, `WORK_DATES` |

---

## Reglas de negocio embebidas

### Reglas generales

1. **Clasificación de estado:** texto "finalizado" o que contenga "sí" → `done`; "en proceso" o keywords ("visita de pares", "evaluación de sala", "pendiente") → `inprog`; "sin iniciar" o "no" → `nostart`.
2. **Overrides por modalidad:** ciertos procesos se forzanz a `na` cuando la modalidad es "profesional" o similar.
3. **Override MEN:** si el valor contiene "aprobado por el men" → `done`.
4. **Syllabus especiales:** si `syl_val=1` y porcentaje está `inprog` → se fuerza a `done`.
5. **Cálculo de periodo:** se toma `PERIODO DE IMPLEMENTACIÓN` y se aplica lógica de fallback si está vacío.
6. **Avance global:** promedio simple de los 9 `proc_{Proceso}`.

### Reglas de negocio — Análisis de Riesgos (`pages/3_Riesgos.py`)

El módulo de Riesgos aplica **5 reglas de filtrado** independientes. Cada una identifica programas que requieren atención prioritaria según combinaciones específicas de columnas derivadas (`pc_pct`, `ban_pct`, `conv_pct`, `syl_val`) y variables de estado (`cf_st`, `pc_st`, `val_12`).

| Riesgo | Nombre | Condición SQL equivalente | Columnas involucradas | Orden |
|--------|--------|--------------------------|----------------------|-------|
| R1 | Producción virtual sin aval financiero | `pc_pct > 0` AND `cf_st == "nostart"` | `pc_pct` (AK), `cf_st` (Concepto Financiero) | `periodo_propuesto` ASC: 2026-2 → 2027-1 → 2027-2 |
| R2 | Lanzamiento en 2026-2 con contenidos incompletos | `periodo_propuesto == "2026-2"` AND `pc_st != "na"` AND `pc_pct < 100` | `periodo_propuesto`, `pc_st`, `pc_pct` | `pc_pct` ASC (peores primero) |
| R3 | Avance en Banner sin producción de contenidos | `ban_pct > 0` AND `pc_pct < 100` | `ban_pct` (BB), `pc_pct` (AK) | `ban_pct` DESC |
| R4 | Syllabus incompleto en Virtual/Híbrido | `MODALIDAD` ∈ {virtual, híbrido} AND `syl_val == "NO"` | `MODALIDAD`, `syl_val`, `pc_pct` | `pc_pct` DESC |
| R5 | Parametrización en Banner sin trámite de convenios | `ban_pct > 0` AND `conv_pct < 100` AND `val_12 != "no aplica"` | `ban_pct` (BB), `conv_pct` (AS), `val_12` (Acta de homologación) | `conv_pct` ASC |

**Detalles por riesgo:**

- **Riesgo 1 — Producción virtual sin aval financiero**  
  Filtra programas con `% contenidos virtuales (PC/AK) > 0` pero cuyo `Concepto Financiero (CF)` está en estado `nostart` ("Sin iniciar"). Muestra: Programa, Periodo propuesto, % PC (AK), % Avance general. Prioriza por periodo (2026-2 primero).

- **Riesgo 2 — Lanzamiento en 2026-2 con contenidos incompletos**  
  Filtra programas con `periodo_propuesto == "2026-2"` cuyo `% de Producción de Contenidos (PC/AK) < 100%` (excluye registros donde PC = "No aplica"). Muestra: Programa, % PC (AK), % Avance. Ordena ascendente por % PC (los más incompletos primero).

- **Riesgo 3 — Avance en Banner sin producción de contenidos virtuales**  
  Filtra programas con `Parametrización Banner (BB) > 0%` pero `% Producción de Contenidos (AK) < 100%`. Muestra: Programa, % Banner (BB), % PC (AK), % Avance. Ordena DESC por % Banner.

- **Riesgo 4 — Syllabus incompleto en Virtual/Híbrido**  
  Filtra programas con `MODALIDAD` en {virtual, híbrido, hibrido} y `syl_val == "NO"` (Syllabus sin completar). Muestra: Programa, Estado Syllabus (AD), % PC (AK), % Avance. Ordena DESC por % PC.

- **Riesgo 5 — Parametrización en Banner sin trámite de convenios**  
  Filtra programas con `ban_pct > 0` Y `conv_pct < 100` Y `val_12 != "no aplica"` (excluye los que tienen acta de homologación marcada como "no aplica"). Muestra: Programa, % Convenios (AS), % Banner (BB), % Avance. Ordena ASC por % Convenios.

**Helpers de estilos aplicados a las tablas de riesgo:**

| Función | Umbrales |
|---------|----------|
| `_style_avance(val)` | ≥90% → verde `#f0f8e8`; ≥70% → amarillo `#fef9e8`; <70% → rojo `#fce8f2` |
| `_style_pc(val)` | ≥90% → verde; ≥70% → amarillo; <70% → rojo |
| `_style_ban(val)` | ≥100% → azul oscuro `#f0f0fa`; ≥50% → violeta `#ece8fc`; <50% → violeta claro `#f5f0fe` |
| `_style_conv(val)` | =0% → rojo `#fce8f2`; <50% → amarillo `#fdf8e8`; ≥50% → default |
| `_style_syl(val)` | `"NO"` → rojo `#fce8f2`; `"Si"` → verde `#f0f8e8` |

---

## Observaciones e inconsistencias

### 🔴 Inconsistencia de rutas (ALTA)
- `exportar_csv.py` espera el Excel en **raíz** (`CONTROL_MAESTRO_DE_REFORMA_CURRICULAR.xlsx`).
- `utils/data_loader.py` espera en **`data/raw/CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx`** (note: sin guiones bajos, con espacios).
- **Acción:** unificar hacia `data/raw/`.

### 🔴 Búsqueda de columnas frágil (ALTA)
- `_find_col` usa coincidencia parcial/case-insensitive. Cambios de formato en el Excel rompen la búsqueda silenciosamente.
- **Acción:** añadir validación post-búsqueda con `difflib.get_close_matches` y error claro.

### 🟡 Parsing de fechas (MEDIA)
- `_parse_fecha_es` asume `dd Month yyyy` en español. Formatos diferentes producen `None` sin advertencia.
- **Acción:** regex flexible y `logging.warning` para fechas no reconocidas.

### 🟡 Duplicación de código CSS (MEDIA)
- CSS institucional embebido en `app.py` y replicado en cada `pages/*.py`.
- **Acción:** extraer a `utils/styles.py` como constante compartida.

### 🔴 Sin tests (ALTA)
- No existen tests para `_classify`, `_cls_pct`, `_build_df`, `apply_filters`, `_parse_fecha_es`.
- **Acción:** añadir `pytest` con fixtures representativos.

### 🟡 Sin logging (MEDIA)
- `exportar_csv.py` usa `print`/`sys.exit`; `data_loader.py` no tiene logging.
- **Acción:** reemplazar por `logging` con niveles INFO/WARNING/ERROR.

---

## Recomendaciones priorizadas

### Prioridad Alta

| # | Recomendación | Archivos |
|---|--------------|----------|
| 1 | Unificar ruta del Excel en `exportar_csv.py` hacia `data/raw/CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx`. Añadir `--input`/`--output` opcionales. | `exportar_csv.py` |
| 2 | Añadir validación de columnas en `_build_df()`: si `_find_col` retorna `None`, usar `difflib.get_close_matches` para sugerir la columna más cercana y fallar con mensaje claro. | `utils/data_loader.py` |
| 3 | Reemplazar `print`/`sys.exit` en `exportar_csv.py` por `logging`. | `exportar_csv.py` |

### Prioridad Media

| # | Recomendación | Archivos |
|---|--------------|----------|
| 4 | Extraer CSS a `utils/styles.py` como constante multilínea compartida. Importar en `app.py` y cada página. | `utils/styles.py`, `pages/*.py` |
| 5 | Tests unitarios con `pytest`: `_classify`, `_cls_pct`, `_cls_status`, `_cls_num`, `_build_df`, `apply_filters`. Fixtures con filas representativas. | `tests/test_data_loader.py` |
| 6 | Robustecer `_parse_fecha_es`: regex para `dd/mm/yyyy`, `yyyy-mm-dd`, `Month dd, yyyy`. Registrar no reconocidos con `logging.warning`. | `utils/data_loader.py` |

### Prioridad Baja

| # | Recomendación | Archivos |
|---|--------------|----------|
| 7 | Crear `scripts/validate_data.py` que ejecute `load_data()` y verifique columnas esperadas. | `scripts/validate_data.py` |
| 8 | GitHub Actions CI que ejecute validación de carga básica. | `.github/workflows/ci.yml` |
| 9 | Considerar lectura chunked si el Excel crece >10k filas (`pandas.read_excel(chunksize=...)`). | `utils/data_loader.py` |

---

## Pasos de implementación — primera mejora (unificar XLSX)

```python
# 1. exportar_csv.py — actualizar rutas
EXCEL_PATH = ROOT / "data" / "raw" / "CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx"
# Añadir argparse: --input (-i), --output (-o)
# logging.info() en lugar de print()

# 2. utils/data_loader.py — validar columnas
from difflib import get_close_matches
# Tras _find_col, si col is None:
#    close = get_close_matches(col_name, df.columns, n=3)
#    raise ValueError(f"Columna no encontrada: {col_name}. ¿Quisiste decir: {close}?")

# 3. tests/test_data_loader.py
# Fixture: 3 filas, 5 columnas clave
# Test: load_data() no falla, 'avance_general' existe
```

---

## Verificación recomendada

1. `streamlit run app.py` → confirmar carga sin errores y dashboard con datos
2. `python exportar_csv.py` → confirmar que genera `data/raw/control_maestro.csv`
3. `pytest -q` → si hay tests, verificar que pasan
4. Abrir cada página (1–6) y confirmar datos visibles

---

## Arquitectura de referencia rápida

```
app.py
├── CSS institucional
├── st.set_page_config()
├── load_data() + enrich_df()          ← utils/data_loader.py
├── Filtros sidebar: MODALIDAD, FACULTAD, PERIODO
├── apply_filters()
├── KPIs: avg_av, proc_avgs, cnt_urgente, cnt_saludable
├── Gráficos: Plotly (bar, radar)
└── Tablas: st.dataframe

utils/data_loader.py
├── ETAPAS_MAP, PROCESOS, PROCESO_COLOR, STATUS_*
├── _cls_status, _cls_pct, _cls_num, _cls_syllabus, _classify
├── _find_col, _parse_fecha_es
├── _build_df()           ← mayor complejidad: reglas de negocio
├── enrich_df()
├── load_data()           ← punto de entrada (cacheado)
├── apply_filters()
└── color_for_pct()

exportar_csv.py
├── export()
└── CLI: python exportar_csv.py

pages/*.py
├── CSS duplicado por página
├── load_data() + enrich_df()
├── Filtros específicos
├── Visualizaciones (Plotly, DataFrame)
└── Descargas Excel (_gen_excel)
```
