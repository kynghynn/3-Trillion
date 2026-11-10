import json
from pathlib import Path
d=json.load(open(Path(__file__).resolve().parents[1]/'dist/assets/data.json'))
assert len(d['countries'])==249
assert len(d['gradeRegistry'])==100
assert sum(g['version']=='v03' for g in d['gradeRegistry'])==33
assert sum(p['partner_type']=='Bilateral' for p in d['chemistryRegistry'])==503
assert sum(p['version']=='process-posterior-v1' for p in d['chemistryRegistry'])==230
assert len(d['activities'])==777 and len(d['observations'])==3215
assert len({(p['donor_iso3'],p['recipient_iso3']) for p in d['chemistryRegistry'] if p['partner_type']=='Bilateral'})==503
png=[p for p in d['chemistryRegistry'] if p['recipient_iso3']=='PNG' and p['partner_type']=='Bilateral']
assert len(png)==3 and all(p['source_year']==2017 for p in png)
assert round(next(p['chemistry'] for p in png if p['donor_iso3']=='AUS'),2)==66.06
print('Validated strict latest grades, separate historical registries, unique bilateral pairs, PNG provenance, UNICEF observations.')
