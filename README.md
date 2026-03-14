# Control Maestro · Reforma Curricular
Dashboard de seguimiento del proceso de reforma curricular.

## Estructura del proyecto

```
proyecto_streamlit/
├── app.py                        # Página principal — Resumen General
├── requirements.txt              # Dependencias para Streamlit Cloud
├── .streamlit/
│   └── config.toml               # Tema oscuro y configuración del servidor
├── data/
│   └── raw/
│       └── control_maestro.csv   # Datos exportados del Excel (Borrador)
├── utils/
│   ├── __init__.py
│   └── data_loader.py            # Carga, mapeo y clasificación de etapas
└── pages/
    ├── 1_Detalle_por_Etapa.py    # Vista detallada de las 20 etapas × programa
    └── 2_Programa.py             # Ficha individual por programa
```

## Páginas

| Página | Descripción |
|--------|-------------|
| **Resumen General** (`app.py`) | KPIs globales, avance por proceso, barras por etapa, tabla resumen |
| **Detalle por Etapa** | Totales por cada etapa (col B Estructura), tabla matricial programa × etapa, mapa de calor |
| **Ficha de Programa** | Radar de procesos, detalle de todos los campos del Excel por programa |

## Fuente de datos

El archivo `data/raw/control_maestro.csv` es una exportación de la hoja **Borrador** del Excel
`CONTROL_MAESTRO_DE_REFORMA_CURRICULAR.xlsx`.

Las etapas se mapean desde la **columna B de la hoja Estructura**:

| Proceso | Etapas |
|---------|--------|
| Gestión Académica | Formato creación Banner · Política curricular · Proyecciones financieras |
| Gestión Financiera | Concepto financiero |
| Aseguramiento de la Calidad | Tipo de trámite · Estado del trámite |
| Ger. Planeación y Gestión Institucional | Correo para implementación |
| Producción de Contenidos | Núm. syllabus · Total módulos · % avance contenidos |
| Convenios Institucionales | Acta homologación · Ruta homologación · % avance |
| Parametrizar Reforma en Banner | Total aulas · Avance aulas · % avance · Config. Banner |
| Publicación en Página Web | Publicar plan web · Fecha fin · Periodo implementación |

## Despliegue en Streamlit Cloud

1. Subir este repositorio a **GitHub** (repositorio público o privado).

2. Ir a [share.streamlit.io](https://share.streamlit.io) e iniciar sesión con GitHub.

3. Hacer clic en **"New app"** y configurar:
   - **Repository:** `tu-usuario/tu-repositorio`
   - **Branch:** `main`
   - **Main file path:** `app.py`

4. Hacer clic en **Deploy**.

> El archivo `requirements.txt` instala automáticamente todas las dependencias.
> El archivo `.streamlit/config.toml` aplica el tema oscuro automáticamente.

## Actualización de datos

Para actualizar los datos con una nueva versión del Excel, ejecutar:

```bash
python3 exportar_csv.py
```

Esto regenera `data/raw/control_maestro.csv` desde el Excel original.
Luego hacer commit y push del nuevo CSV para que Streamlit Cloud lo tome.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```
