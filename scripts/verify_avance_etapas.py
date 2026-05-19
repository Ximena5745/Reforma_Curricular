"""Verificación rápida: conteos por actividad en Diseño deben sumar n programas."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.charts_vact import STATUS_STACK
from utils.data_loader_vact import _ensure_activities_meta, load_etapas_data

STATUS_KEYS = [k for k, _, _ in STATUS_STACK]

df = load_etapas_data()
meta = _ensure_activities_meta(df)
n = len(df)
diseno = [m for m in meta if m["phase"] == "Diseño Curricular"]
print(f"Programas: {n}, actividades Diseño: {len(diseno)}")
errors = []
for m in diseno:
    col = f"cl_act_{m['idx']}"
    counts = {k: int((df[col] == k).sum()) for k in STATUS_KEYS}
    total = sum(counts.values())
    name = m["name"][:55]
    flag = "OK" if total == n else "FAIL"
    if total != n:
        errors.append((name, total, counts))
    if "proyeccion" in m["name"].lower() or "formato ra" in m["name"].lower() or "cronograma" in m["name"].lower():
        print(f"  [{flag}] {name}: total={total} {counts}")
if errors:
    print(f"\n{len(errors)} actividades con total != {n}:")
    for name, total, counts in errors[:5]:
        print(f"  {name}: {total} {counts}")
    raise SystemExit(1)
print("\nTodas las actividades de Diseño suman correctamente.")
