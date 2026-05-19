"""Verifica get_etapas_by_programa incluye responsable propagado y actividades por etapa."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.data_loader_vact import ETAPAS_ORDEN, load_etapas_data, get_etapas_by_programa
from utils.data_loader_vact import _build_area_by_col
import pandas as pd
from utils.data_loader_vact import DATA_PATH, AREA_ROW

df = load_etapas_data()
raw = pd.read_excel(DATA_PATH, sheet_name="Etapas", header=None, dtype=str).fillna("")
area = _build_area_by_col(raw)
non_empty = [v for v in area.values() if v != "—"]
print(f"Columnas con responsable (forward-fill): {len(non_empty)}")
assert len(non_empty) >= 5, f"esperado >=5 areas, got {len(non_empty)}: {non_empty[:8]}"

prog = df["NOMBRE DEL PROGRAMA"].iloc[0]
data = get_etapas_by_programa(df, prog)
print("Programa:", prog)
for etapa in ETAPAS_ORDEN:
    acts = data["etapas"].get(etapa, {}).get("actividades", [])
    with_resp = sum(1 for a in acts if a.get("responsable") not in (None, "", "—"))
    print(f"  {etapa}: {len(acts)} actividades, {with_resp} con responsable")
    if acts:
        print(f"    ej: {acts[0]['nombre'][:40]} -> {acts[0].get('responsable')}")
    if etapa == "Alistamiento Curricular":
        assert with_resp >= 4, f"Alistamiento debe tener >=4 responsables, got {with_resp}"
print("OK")
