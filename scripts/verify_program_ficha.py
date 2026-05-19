"""Verifica get_etapas_by_programa incluye responsable y actividades por etapa."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.data_loader_vact import ETAPAS_ORDEN, load_etapas_data, get_etapas_by_programa

df = load_etapas_data()
prog = df["NOMBRE DEL PROGRAMA"].iloc[0]
data = get_etapas_by_programa(df, prog)
print("Programa:", prog)
for etapa in ETAPAS_ORDEN:
    acts = data["etapas"].get(etapa, {}).get("actividades", [])
    with_resp = sum(1 for a in acts if a.get("responsable") not in (None, "", "—"))
    print(f"  {etapa}: {len(acts)} actividades, {with_resp} con responsable")
    if acts:
        a0 = acts[0]
        assert "responsable" in a0, "falta clave responsable"
        assert "estado_key" in a0
print("OK")
