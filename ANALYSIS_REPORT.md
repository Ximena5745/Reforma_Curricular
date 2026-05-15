# ANÁLISIS ESTRUCTURA: Excel y Mappings de Facultades

## 1. ESTRUCTURA DE LA HOJA "ETAPAS"

### Organización por filas
- **Row 8**: Fases principales de la reforma (merged cells)
- **Row 9**: Áreas involucradas (merged cells - sub-fases)
- **Row 10**: Información de programas (merged cells)
- **Row 11**: Headers de actividades (columnas específicas)
- **Row 12+**: Datos de programas

### Fases y su rango de columnas

| Fase | Columns | Descripción |
|------|---------|-------------|
| **FASES DE LA REFORMA CURRICULAR** | C:K | Información base de programas (FACULTAD, ESCUELA, PROGRAMA, MODALIDAD, NIVEL, etc.) |
| **ALISTAMIENTO CURRICULAR** | L:Q | L:P = Etapa 1, Q = % avance |
| **DISEÑO CURRICULAR** | R:AC | R:V = Diseño actividades, W:AB = Aseguramiento, AC = % avance |
| **IMPLEMENTACIÓN CURRICULAR** | AT:AU | Banner y operaciones |

### Columnas principales (Header Row 11)

```
C  = FACULTAD
D  = ESCUELA
E  = NOMBRE DEL PROGRAMA
F  = MODALIDAD
G  = NIVEL
H  = COMPARTIDAS /INSTITUCIONAL-
I  = SEDE
J  = SNIES VIGENTE
K  = PERIODO DE IMPLEMENTACIÓN

L  = Formato creación de programas Banner (Alistamiento)
M  = Syllabus Completos
N  = Actas/formato de homologación- convenios- articulación
O  = Syllabus de programa
P  = Vo Bo PPT
Q  = % de Avance Alistamiento Curricular (FÓRMULA)

R  = Formato creación de programas Banner (Diseño)
S  = Verificación curricular
T  = Formato RA
U  = Plan de virtualización
V  = Formato de proyecciones académicas y financieras
W  = Generar estudio de viabilidad financiera por plan de estudios
X  = 5.Formato de proyecciones académicas y financieras
Y  = Plan de Transición
Z  = Cronograma de trámites frente al MEN
AA = Cronograma de trámites frente al MEN
AB = ¿El plan de estudios es único y equivalente (MEN = Reforma)
AC = % de Avance Diseño curricular (FÓRMULA)
...
```

### Estructura de datos (Row 12 - ejemplo)

```
FACULTAD = "Facultad de Sociedad, Cultura y Creatividad"
ESCUELA = "Comunicación, Artes Visuales y Digitales"
PROGRAMA = "Comunicación Digital"
MODALIDAD = "Presencial"
NIVEL = "Profesional"
PERIODO = "2027-1"
Estatus = "Finalizado", "Sin Iniciar", "En proceso", "No aplica", "Devuelto", "Renovación de Registro Calificado"

Q  = FÓRMULA: =(COUNTIF(L12:P12,"Finalizado")*1 + COUNTIF(L12:P12,"En proceso")*0.5 + COUNTIF(L12:P12,"Sin Iniciar")*0 + COUNTIF(L12:P12,"No aplica")*1) / 5
AC = FÓRMULA: =(COUNTIF(R12:AB12,"Finalizado")*1 + COUNTIF(R12:AB12,"En proceso")*0.5 + COUNTIF(R12:AB12,"Sin Iniciar")*0 + COUNTIF(R12:AB12,"No aplica")*1) / 9
```

---

## 2. MAPEOS DE FACULTADES (CURRENT)

### Ubicaciones en el código

**app_act.py (líneas 224-237)** y **pages/1_Detalle_por_Etapa.py (líneas 147-157)**

```python
# FULL NAMES ↔ SHORT LABELS
fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}

# FULL NAMES ↔ ABBREVIATIONS
fac_abrev = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación":    "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
}

# INVERSE MAPPINGS
fac_inv       = {v: k for k, v in fac_labels.items()}         # Short label → Full name
fac_abrev_inv = {v: k for k, v in fac_abrev.items()}          # Abbreviation → Full name
```

### Color Palette por Facultad (pages/1_Detalle_por_Etapa.py líneas 475-478)

```python
FAC_PALETTE = {
    "FSCC": "#EC0677",    # MAGENTA/PINK (Sociedad, Cultura y Creatividad)
    "FIDI": "#1FB2DE",    # CYAN/BLUE (Ingeniería, Diseño e Innovación)
    "FNGS": "#A6CE38",    # GREEN/LIME (Negocios, Gestión y Sostenibilidad)
}
```

### Valores únicos en la hoja "Etapas"

```
Facultad de Sociedad, Cultura y Creatividad
Facultad de Ingeniería, Diseño e Innovación
Facultad de Negocios, Gestión y Sostenibilidad
```

---

## 3. FLUJO DE DATOS: Excel → Dashboard

### 1. **Carga de datos** (utils/data_loader.py, línea 184)
```python
df = pd.read_excel(DATA_PATH, sheet_name="Borrador", header=9, dtype=str)
```
- Lee sheet "Borrador" (NOT "Etapas")
- Header en fila 9 (row 10, 0-indexed)
- Todas las columnas como strings

### 2. **Filtrado inicial** (data_loader.py, línea 194)
```python
df = df[df["NOMBRE DEL PROGRAMA"].str.strip() != ""].copy()
```
- Solo mantiene filas con nombre de programa

### 3. **Aplicación de filtros** (data_loader.py, líneas 500-520)
```python
def apply_filters(df, modalidad=None, facultad=None, periodo=None):
    # facultad parameter acepta lista de FULL NAMES
    if facs:
        df = df[df["FACULTAD"].isin(facs)]  # Filtra por FULL NAME
```

### 4. **UI - Conversión de labels** (pages/1_Detalle_por_Etapa.py)

**Lectura:**
```python
fac_ops = sorted([fac_abrev.get(f, f) for f in df_raw["FACULTAD"].dropna().unique()])
# Convierte: Full name → Abbreviation (FSCC, FIDI, FNGS)
```

**Aplicación de filtro:**
```python
sel_fac = st.pills("fac", fac_ops, selection_mode="multi")  # Usuario selecciona abbreviations
facultad_f = [fac_abrev_inv.get(f, f) for f in sel_fac]     # Convierte back a FULL NAMES
df = apply_filters(df_filt, modalidad_f, facultad_f, periodo_f)
```

**Mostrar en tabla:**
```python
df_det["Facultad"] = df["FACULTAD"].map(fac_abrev).fillna("—")
# Convierte FULL NAME a abbreviation para mostrar
```

---

## 4. INSTITUCIONALES COLORS (data_loader.py, líneas 51-61)

```python
# Procesos (8 líneas de color principal)
PROCESO_COLOR = {
    "Gestión Académica":                       "#0F385A",    # Dark blue
    "Gestión Financiera":                      "#FBAF17",    # Orange/Amber
    "Aseguramiento de la Calidad":             "#EC0677",    # Pink/Magenta
    "Syllabus":                                "#9333ea",    # Purple
    "Producción de Contenidos":                "#A6CE38",    # Green/Lime
    "Convenios Institucionales":               "#42B0B5",    # Teal
    "Parametrizar Reforma en Banner":          "#5C89B5",    # Steel blue
    "Publicación en Página Web":               "#F47B20",    # Orange
}

# Status colors (6 valores)
STATUS_COLOR = {
    "done":      "#A6CE38",    # Green - Finalizado
    "inprog":    "#1FB2DE",    # Cyan - En proceso
    "nostart":   "#EC0677",    # Pink - Sin iniciar
    "devuelto":  "#F47B20",    # Orange - Devuelto
    "info":      "#FBAF17",    # Amber - Informativo
    "na":        "#9aabb5",    # Gray - N/A
}

# Palette for progress % (data_loader.py, líneas 523-532)
color_for_pct(p):
    >= 70%  → "#3ecf8e"  (green)
    >= 45%  → "#4f8ef7"  (blue)
    >= 25%  → "#f97316"  (orange)
    < 25%   → "#ef4444"  (red)
```

---

## 5. INSIGHTS SOBRE EL FLUJO DE DATOS

### A. Dos versiones del Excel
- **"Borrador"** sheet: Usada para procesar y cargar datos en la app
- **"Etapas"** sheet: Parece ser la estructura/template original

### B. Transformación de nombres
- **Almacenado**: FULL NAME (ej. "Facultad de Sociedad, Cultura y Creatividad")
- **UI (Filtros)**: ABBREVIATION (ej. "FSCC")
- **Conversión**: `fac_abrev` y `fac_abrev_inv` dictionaries

### C. Esquema de clasificación de estado
Cada celda de actividad se clasifica automáticamente en:
- `done` (Finalizado, Si, 100%)
- `inprog` (En proceso, Visita de pares, etc.)
- `nostart` (Sin iniciar, No)
- `devuelto` (Devuelto)
- `na` (No aplica)
- `info` (Informativo)

### D. Cálculo de avance
- Por etapa (cl_N)
- Por proceso (proc_[PROCESS_NAME])
- General (avance_general)
- Específicos: pc_pct, conv_pct, ban_pct, web_pct

### E. Filtros disponibles
1. **MODALIDAD**: Presencial, Virtual, Híbrido
2. **FACULTAD**: FSCC, FIDI, FNGS (internamente stored as full names)
3. **PERIODO**: "2026-2", "2027-1", "2027-2", "Ya está en oferta"
4. **NIVEL**: Pregrado, Posgrado (homologado desde NIVEL column)

---

## 6. SUMMARY TABLE

| Aspecto | Details |
|---------|---------|
| **Excel Main Sheet** | "Borrador" (no "Etapas") |
| **Data Path** | `data/raw/CONTROL MAESTRO DE REFORMA CURRICULAR.xlsx` |
| **Header Row** | Row 9 (0-indexed from pandas) = Row 10 (Excel) |
| **Main Phases** | Alistamiento (L:Q), Diseño (R:AC), Implementación (AT:AU) |
| **Faculty Count** | 3 facultades |
| **Faculty Abbreviations** | FSCC, FIDI, FNGS |
| **Faculty Colors** | Pink (#EC0677), Cyan (#1FB2DE), Green (#A6CE38) |
| **Status Values** | 6 estados (done, inprog, nostart, devuelto, info, na) |
| **Process Count** | 8 procesos principales |
| **Data Mappings** | `fac_labels`, `fac_abrev`, `fac_inv`, `fac_abrev_inv` |
| **UI Implementation** | Pills (abbreviations) → Filters (full names) |
