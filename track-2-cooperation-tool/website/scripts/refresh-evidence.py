import json
from pathlib import Path
site=Path(__file__).resolve().parents[1];root=site.parents[1]
src=root/'outputs/track2_coverage_expansion_20261110/processed'
d=json.load(open(site/'dist/assets/data.json'))
d['gradeRegistry']=json.load(open(src/'country_grade_registry.json'))
d['chemistryRegistry']=json.load(open(src/'chemistry_registry.json'))
d['activities']=json.load(open(src/'additional_result_activity_index.json'))
d['coverage']=json.load(open(src/'coverage_summary.json'))
d['snapshot']='2026-11-10'
obs=json.load(open(src/'objective_observations.json'))
d['observations']=[{'activity':o['project_id'],'title':' / '.join(t['text'] for t in o['indicator_title']),'period':[o['period_start'],o['period_end']],'baseline':o['baseline'],'targets':o['targets'],'actuals':o['actuals'],'quality':o['quality']} for o in obs]
for name in ['data.json','data.js']:(site/'dist/assets'/name).write_text(('window.ATLAS_DATA=' if name.endswith('.js') else '')+json.dumps(d,ensure_ascii=False,separators=(',',':'))+(';' if name.endswith('.js') else ''))
(site/'dist/assets/new-observations.json').write_text(json.dumps(obs,ensure_ascii=False,separators=(',',':')))
