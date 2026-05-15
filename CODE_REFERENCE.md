# CODE REFERENCE: Facultad Mappings & Colors

## Files with Faculty Mappings

### 1. app_act.py (líneas 224-237)

```python
fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}

fac_abrev = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación":    "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
}

fac_inv       = {v: k for k, v in fac_labels.items()}
fac_abrev_inv = {v: k for k, v in fac_abrev.items()}
FAC_LIST  = list(fac_labels.values())
FAC_PALETTE = {
    "FSCC": "#EC0677",
    "FIDI": "#1FB2DE",
    "FNGS": "#A6CE38",
}
```

**Usage in app_act.py:**
- Line 256: `FAC_LIST` usado en sidebar para mostrar opciones
- Line 235: `FAC_PALETTE` para colorear cards

### 2. pages/1_Detalle_por_Etapa.py (líneas 147-478)

**Faculty Definitions:**
```python
fac_labels = {
    "Facultad de Sociedad, Cultura y Creatividad":    "Sociedad, Cultura y Creatividad",
    "Facultad de Ingeniería, Diseño e Innovación":    "Ingeniería, Diseño e Innovación",
    "Facultad de Negocios, Gestión y Sostenibilidad": "Negocios, Gestión y Sostenibilidad",
}

fac_abrev = {
    "Facultad de Sociedad, Cultura y Creatividad":    "FSCC",
    "Facultad de Ingeniería, Diseño e Innovación":    "FIDI",
    "Facultad de Negocios, Gestión y Sostenibilidad": "FNGS",
}

fac_inv       = {v: k for k, v in fac_labels.items()}
fac_abrev_inv = {v: k for k, v in fac_abrev.items()}
```

**Faculty Palette:**
```python
FAC_PALETTE = {
    "FSCC": "#EC0677",    # Line 476
    "FIDI": "#1FB2DE",    # Line 477
    "FNGS": "#A6CE38",    # Line 478
}
```

**Usage:**
- Line 196: `fac_ops = sorted([fac_abrev.get(f, f) for f in df_raw["FACULTAD"].dropna().unique()])`
  → Convierte full names a abbreviations para mostrar en UI

- Line 233-236: Selectbox/Pills de facultad (muestra FSCC, FIDI, FNGS)

- Line 270: `facultad_f = [fac_abrev_inv.get(f, f) for f in sel_fac] if sel_fac else []`
  → Convierte abbreviations seleccionadas back a full names para filtro

- Line 542: `df_det["Facultad"] = df["FACULTAD"].map(fac_abrev).fillna("—")`
  → En tabla, muestra abbreviation

- Line 763-770: Función `_fac_col()` para colorear células por facultad
  ```python
  def _fac_col(s):
      val = str(s).strip() if isinstance(s, str) else "—"
      if val != "—":
          c = FAC_PALETTE.get(str(val), "#1FB2DE")
          # Usa color para background y border
  ```

- Line 784: `sel_fac_filt = st.pills("fac_filt", fac_ops, selection_mode="multi")`
  → Filtro por facultad en Detalle page

- Line 804-809: Aplica filtro seleccionado a dataframe

### 3. utils/data_loader.py

**Usado:**
- Line 500-520: `apply_filters()` - acepta full names para facultad parameter
- Line 514: `df[df["FACULTAD"].isin(facs)]` - filtra por column FACULTAD (full names)

---

## Color Palettes Summary

### Faculty Colors (FAC_PALETTE)
```
FSCC = "#EC0677"     (Pink/Magenta)
FIDI = "#1FB2DE"     (Cyan/Sky Blue)
FNGS = "#A6CE38"     (Lime Green)
```

### Process Colors (PROCESO_COLOR)
```
Gestión Académica               #0F385A  (Dark Navy)
Gestión Financiera              #FBAF17  (Amber/Orange)
Aseguramiento de la Calidad     #EC0677  (Pink) ← Same as FSCC!
Syllabus                        #9333ea  (Purple)
Producción de Contenidos        #A6CE38  (Lime) ← Same as FNGS!
Convenios Institucionales       #42B0B5  (Teal)
Parametrizar Reforma en Banner  #5C89B5  (Steel Blue)
Publicación en Página Web       #F47B20  (Orange)
```

### Status Colors (STATUS_COLOR)
```
done      #A6CE38  (Green - Lime, same as FNGS!)
inprog    #1FB2DE  (Cyan - same as FIDI!)
nostart   #EC0677  (Pink - same as FSCC!)
devuelto  #F47B20  (Orange)
info      #FBAF17  (Amber)
na        #9aabb5  (Gray)
```

**Note:** Status colors intentionally match faculty colors for consistency:
- FSCC (Pink) = Not Started
- FIDI (Cyan) = In Progress
- FNGS (Green) = Done

---

## Data Flow Diagram

```
Excel Sheet "Borrador" (Row 9 = header)
    ↓
load_data() in data_loader.py
    ↓
df["FACULTAD"] = "Facultad de Sociedad, Cultura y Creatividad" [FULL NAME]
    ↓
app_act.py / pages/1_Detalle_por_Etapa.py
    ├─ fac_abrev.get(full_name) → "FSCC" (for display)
    │   ├─ Show in UI pills/select
    │   └─ Store in session_state
    │
    └─ User selects abbreviation
        ├─ fac_abrev_inv.get("FSCC") → full_name
        └─ apply_filters(df, facultad=[full_name])
            └─ df[df["FACULTAD"].isin([full_name])] ← Backend filter
```

---

## Key Implementation Details

### 1. **Inverse Mappings**
Both `fac_inv` and `fac_abrev_inv` are computed dynamically:
```python
fac_abrev_inv = {v: k for k, v in fac_abrev.items()}
# Result: {"FSCC": "Facultad de Sociedad...", ...}
```

### 2. **Fallback Logic**
When mapping might fail:
```python
df["Facultad"] = df["FACULTAD"].map(fac_abrev).fillna("—")
# If mapping fails, shows "—" instead of NaN
```

### 3. **Color Retrieval with Default**
```python
c = FAC_PALETTE.get(str(val), "#1FB2DE")  # Default to FIDI cyan
```

### 4. **Filter Conversion Pattern**
```
UI Selection (abbrev) → Backend Filter (full name)
    sel_fac = ["FSCC", "FIDI"]  # User chooses
    ↓
    facultad_f = [fac_abrev_inv.get(f, f) for f in sel_fac]
    # facultad_f = ["Facultad de Sociedad...", "Facultad de Ingeniería..."]
    ↓
    apply_filters(df, facultad=facultad_f)
    # Filters df["FACULTAD"].isin(facultad_f)
```

---

## Integration Points

| Component | Purpose | Mapping Used |
|-----------|---------|--------------|
| Sidebar Faculty Select | Show options to user | `fac_abrev` |
| DataFrame Display | Show faculty column | `fac_abrev` |
| Filter Backend | Query database | `fac_abrev_inv` |
| Cell Styling | Color by faculty | `FAC_PALETTE` |
| Session State | Store user selection | `fac_abrev_inv` |
| Download/Export | Include full name | Original `FACULTAD` column |
