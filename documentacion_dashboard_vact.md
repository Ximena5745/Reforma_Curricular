# Documentación del Dashboard Fase 2: Reforma Curricular (VACT)

## 📌 Descripción General
El archivo `app_act.py` implementa el **Dashboard Fase 2: Reforma Curricular por Etapas (VACT)**. Esta aplicación, desarrollada en **Streamlit**, tiene como objetivo principal realizar el seguimiento detallado del porcentaje de avance de la reforma curricular de los programas académicos de la institución (POLI), desglosado por sus diferentes etapas.

## ⚙️ Lógica del Proyecto
El proyecto está estructurado de manera modular y se apoya en scripts utilitarios:
1. **Carga y Procesamiento de Datos**: Utiliza `utils.data_loader_vact.py` para cargar los datos base (provenientes de la hoja *Etapas* del archivo Excel de Control Maestro), asegurando que se extraigan las etapas, metadatos de las actividades y el cálculo de los avances porcentuales.
2. **Estilos e Identidad Institucional**: Importa configuraciones visuales desde `utils.poli_theme.py`, incluyendo paletas de colores (`BRAND_PRIMARY`, `BRAND_SECONDARY`), formato de tablas y HTML customizado (badges, barras de progreso e íconos de estado).
3. **Filtros Dinámicos**: Permite filtrar los datos transversalmente por:
   - **Modalidad**
   - **Facultad**
   - **Período de Implementación**
   - **Nivel** (Pregrado / Posgrado)
4. **Tabla Maestra Interactiva**: Implementa una tabla en HTML/CSS inyectada directamente (`_master_activities_table_html`) con encabezados anclados (sticky) y funcionalidades de *toggle* (colapsar/expandir mediante JavaScript). Esto permite al usuario ver detalladamente las actividades específicas de cada etapa de reforma por programa.

## 🛤️ Etapas de la Reforma
El avance general de la reforma se compone de un promedio consolidado (`avance_general_vact`), y se divide internamente en cuatro fases clave del proceso (`ETAPAS_ORDEN`). Cada una de estas etapas se alimenta dinámicamente de una lista de actividades que determinan su porcentaje de progreso:

1. **Alistamiento Curricular** (`pct_alistamiento`):
   - Fase inicial donde se preparan las condiciones institucionales, financieras y normativas para la creación o modificación del programa.
2. **Diseño Curricular** (`pct_diseno`):
   - Etapa dedicada a la estructuración de competencias, propósitos de formación y perfil de egreso.
3. **Desarrollo Curricular** (`pct_desarrollo`):
   - Fase de construcción del plan de estudios detallado, diseño de sílabos, créditos y rutas de aprendizaje.
4. **Implementación Curricular** (`pct_implementacion`):
   - Fase final que abarca los trámites ante el Ministerio, radicación de documentos, renovaciones y la puesta en marcha oficial de la oferta académica.

### Lógica de Evaluación por Actividades
El progreso porcentual de cada etapa se calcula en función del estado de las actividades que la componen. El sistema asigna los siguientes valores de avance según el estado (`_cls_status`):
- **Finalizado (`done`)**: 100%
- **En proceso (`inprog`)**: 50% *(Incluye visitas, elaboración, evaluación)*
- **Devuelto (`devuelto`)**: 25%
- **Sin iniciar (`nostart`)**: 0%
- **Informativo / No aplica (`info`, `na`)**: No afectan el promedio de la etapa.

## 📊 Estructura y Navegación del Dashboard
La interfaz de usuario está dividida en un encabezado, una barra lateral y tres pestañas principales:

### 1. Barra Lateral (Sidebar)
Permite la navegación entre los módulos principales:
- **Fase 1: Producción** (`app.py`)
- **Fase 2: Etapas (VACT)** (`app_act.py` - vista actual)

### 2. Pestañas de Visualización (Tabs)
- **📊 Avance General**: 
  - Muestra tarjetas resumen con los promedios de avance por etapa y el avance general de la reforma.
  - Renderiza un diagrama estilo **Gantt** de progreso para un pantallazo ejecutivo.
  - Muestra la tabla maestra interactiva con todos los programas que coincidan con el filtro actual.
  - Opción de descargar un reporte consolidado en Excel.
- **📋 Detalle por Etapa**:
  - Contiene un resumen numérico rápido de los programas en el filtro.
  - Enfatiza el uso de la tabla maestra, invitando al usuario a hacer clic en el símbolo `+` para desglosar el estado de las micro-actividades por cada etapa.
- **🏛️ Por Programa**:
  - Vista filtrada enfocada en programas individuales.
  - Ofrece la visual interactiva completa con opción a descargar los datos en Excel.

## 💡 Información y Características Relevantes
- **Interactividad HTML/JavaScript**: Dado que las tablas nativas de Streamlit a veces quedan cortas para diseños complejos, el dashboard inyecta JS (`toggleEtapa`) y un montón de CSS (`_MASTER_TABLE_CSS`) para expandir/colapsar las columnas interactivas, manejando *colspans* dinámicos de forma altamente eficiente.
- **Estados Visuales**: Las tareas y actividades reportan varios estados (completado, en progreso, no iniciado, devuelto, NA) que se traducen a íconos definidos en la función `_vact_act_icon()`.
- **Exportación de Datos Liviana**: La función `_excel_export_bytes()` toma en memoria (`io.BytesIO()`) un subconjunto específico del `DataFrame` y renombra las columnas críticas (Programa, Facultad, Escuela, Modalidad, Nivel, Sede, Período y porcentajes de avance) para exportar un archivo `.xlsx` limpio.
- **Manejo Inteligente del Estado (Session State)**: La barra de filtros global (`_render_filter_bar`) se renderiza una sola vez y controla el DataFrame para las 3 pestañas, evitando problemas de rendimiento y colisión de variables (`DuplicateElementKey`) en la interfaz interactiva.
