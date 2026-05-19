"""Verifica responsables propagados y metadatos de ficha por programa."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from utils.data_loader_vact import (
    DATA_PATH,
    ETAPAS_ORDEN,
    _build_area_by_col,
    _detect_area_row,
    get_etapas_by_programa,
    load_etapas_data,
)

raw = pd.read_excel(DATA_PATH, sheet_name="Etapas", header=None, dtype=str).fillna("")
area_row = _detect_area_row(raw)
print(f"Fila areas detectada: Excel row {area_row + 1} (idx {area_row})")

area = _build_area_by_col(raw)
non_empty = [v for v in area.values() if v != "—"]
print(f"Columnas con responsable: {len(non_empty)}")
print("Muestra:", non_empty[:6])
assert len(non_empty) >= 5, f"esperado >=5 areas, got {len(non_empty)}"

df = load_etapas_data()
prog = df["NOMBRE DEL PROGRAMA"].iloc[0]
data = get_etapas_by_programa(df, prog)
print("Programa:", prog)

all_resp = []
for etapa in ETAPAS_ORDEN:
    acts = data["etapas"].get(etapa, {}).get("actividades", [])
    with_resp = [a for a in acts if a.get("responsable") not in (None, "", "—")]
    print(f"  {etapa}: {len(acts)} actividades, {len(with_resp)} con responsable")
    if with_resp:
        print(f"    ej: {with_resp[0]['nombre'][:40]} -> {with_resp[0].get('responsable')}")
    all_resp.extend(a.get("responsable", "") for a in with_resp)
    if etapa == "Alistamiento Curricular":
        assert len(with_resp) >= 4, f"Alistamiento >=4 responsables, got {len(with_resp)}"

joined = " ".join(all_resp).upper()
assert "CURR" in joined or "DECANATURA" in joined or "ESCUELA" in joined, (
    "ningun responsable conocido encontrado"
)
print("OK")
