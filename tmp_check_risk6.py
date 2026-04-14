import pandas as pd
from utils.data_loader import load_data, enrich_df

df = enrich_df(load_data())
cols = [c for c in df.columns if 'estado del tr' in c.lower() or 'trámite' in c.lower() or 'tramite' in c.lower()]
print('maybe columns:', cols)
from itertools import islice
for c in cols:
    vals = df[c].dropna().astype(str)
    print('--- col:', c)
    print('unique count', vals.nunique())
    sample = list(islice(sorted(set(vals.str.lower().tolist())), 30))
    print('sample values', sample)
    print('contains aprobado por el men', vals.str.lower().str.contains('aprobado por el men', na=False).sum())
    print('contains aprobado', vals.str.lower().str.contains('aprobado', na=False).sum())
    print('contains men', vals.str.lower().str.contains('men', na=False).sum())
    print('')
    
if cols:
    m = pd.Series(False, index=df.index)
    for c in cols:
        m = m | df[c].astype(str).str.lower().str.contains('aprobado', na=False)
    print('rows matching aprobado count', m.sum())
    for idx, row in df[m].head(10).iterrows():
        print('row', idx, {c: row[c] for c in cols})
