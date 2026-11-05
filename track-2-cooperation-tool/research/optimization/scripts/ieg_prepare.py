from pathlib import Path
import json,collections
B=Path(__file__).resolve().parents[1];P=B/'processed';A=json.loads((B/'raw/ieg_ratings.json').read_text())
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2))
scale={'Highly Unsatisfactory':1,'Unsatisfactory':2,'Moderately Unsatisfactory':3,'Moderately Satisfactory':4,'Satisfactory':5,'Highly Satisfactory':6}
health=[r for r in A if r.get('global_practice')=='Health, Nutrition & Population']
print('practices',collections.Counter(r.get('global_practice') for r in A).most_common(20))
# Keep evaluation records; latest evaluation FY then PPAR, flag ties instead of silently selecting contradictory ratings.
groups=collections.defaultdict(list)
for r in A:groups[r['project_id']].append(r)
latest=[];conflicts=[]
for id,rs in groups.items():
 yr=max((r.get('evaluation_fy') or 0) for r in rs);z=[r for r in rs if (r.get('evaluation_fy') or 0)==yr];zz=[r for r in z if r.get('evaluation_type')=='PPAR'];z=zz or z
 if len({r.get('outcome') for r in z})>1:conflicts.append({'project_id':id,'records':z});continue
 r=dict(z[0]);r.update(provider_entity='World Bank IBRD/IDA',provider_entity_type='multilateral',outcome_ordinal=scale.get(r.get('outcome')),source='raw/ieg_ratings.json',assessment_scope='project; cannot substitute bilateral donor recipient chemistry');latest.append(r)
health=[r for r in latest if 'health' in str(r.get('global_practice','')).lower()];recent=[r for r in health if isinstance(r.get('final_closing_fy'),int) and 2016<=r['final_closing_fy']<=2025];save('ieg_latest_projects.json',latest);save('ieg_health_recent.json',recent);save('ieg_conflicting_latest.json',conflicts)
summary={'raw_rows':len(A),'unique_project_ids':len(groups),'resolved_latest_rows':len(latest),'ambiguous_latest_projects':len(conflicts),'snapshot_dates':sorted(set(r['as_of_date'] for r in A)),'health_latest':len(health),'health_closed_2016_2025':len(recent),'health_recent_countries':len(set(r['country'] for r in recent)),'png_latest':[r for r in health if r['country']=='Papua New Guinea'],'use':'independent multilateral evaluation evidence and harmonization research; not a bilateral score replacement'}
save('ieg_summary.json',summary);print({k:v for k,v in summary.items() if k!='png_latest'})
