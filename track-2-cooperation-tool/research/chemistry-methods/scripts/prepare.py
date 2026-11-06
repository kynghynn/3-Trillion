from pathlib import Path
import json,math,re,collections,unicodedata,xml.etree.ElementTree as E
B=Path(__file__).resolve().parents[1];O=B.parent/'track2_research_20261104';P=B/'processed'
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False))
def load(n):return json.loads((O/n).read_text())
A=load('processed/gpedc_projects_data.json');I=load('expansion/processed/activities.json');D=load('expansion/processed/scope.json')['target_donors']
def norm(t):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',str(t)).encode('ascii','ignore').decode().lower())
def sectors(x,iso2):
 ss=[z for z in x['sectors'] if z.get('allocation_level')=='activity']
 if not ss:ss=[z for t in x['transactions'] if any(v.get('code')==iso2 for v in t['recipient_countries']) for z in t['sectors']]
 return sorted(set(z.get('code','')[:3] for z in ss if z.get('vocabulary','1')=='1' and len(z.get('code',''))>=3))
lookup=collections.defaultdict(list)
for x in I:
 for r in x['recipients']:lookup[(x['provider_country'],r['iso3'],norm(x['title']))].append((x,r))
rows=[];issues=[];seen=set();matches=[]
for r in A:
 if r.get('Bilateral')!=1:continue
 id='|'.join(str(r.get(k)) for k in ['provider','recipient','project_id']);assert id not in seen;seen.add(id)
 govkeys=['B2Q06_'+k for k in 'abcdef']+(['B2Q06_'+k for k in 'ghij'] if r.get('adapted_quest')=='Y' else [])
 gov=any(r.get(k)=='Y' for k in govkeys);notgov=r.get('B2Q06_k')=='Y';ownership=int(gov) if gov or notgov else None
 if gov and notgov:ownership=None;issues.append({'id':id,'issue':'conflicting government and not-government objectives'})
 comp={'ownership':{'k':ownership,'n':1 if ownership is not None else None,'source_fields':govkeys+['B2Q06_k']}}
 for c,key in [('results_alignment','B2Q10x1'),('government_data','B2Q10x2')]:
  n=r.get('B2Q10');k=r.get(key);valid=all(isinstance(v,(int,float)) and math.isfinite(v) and abs(v-round(v))<1e-8 for v in [n,k]) and n>0 and 0<=k<=n
  if not valid and n is not None and k is not None and n>0:issues.append({'id':id,'issue':'invalid count','component':c,'n':n,'k':k})
  comp[c]={'k':int(k) if valid else None,'n':int(n) if valid else None,'source_fields':['B2Q10',key],'missing_reason':None if valid else 'missing_invalid_or_zero_denominator'}
 z=lookup.get((D.get(r['provider']),r.get('alpha3code'),norm(r.get('B2Q01'))),[]);sector=None
 if len(z)==1:
  x,rec=z[0];sector=sectors(x,rec['iso2']);matches.append({'project_id':id,'iati_id':x['id'],'dac3':sector,'match_method':'unique exact normalized title + provider + recipient'})
 rows.append({'project_id':id,'provider':r['provider'],'recipient':r['recipient'],'recipient_iso3':r.get('alpha3code'),'title':r.get('B2Q01'),'reporting_period':r['ReportingYear'],'approval_date':r.get('B2Q03'),'components':comp,'sector_dac3':sector,'sample_scope':'GPEDC largest interventions; source survey, not random sample; measures design/process, not impact'})
save('process_projects.json',rows);save('process_data_issues.json',issues);save('exact_sector_links.json',matches)
# Objective target/actual candidates, retaining exclusions and source semantics.
def number(v):
 if v is None:return None
 v=str(v).strip().replace('\u202f','').replace('\u00a0','')
 if ',' in v and '.' not in v:v=v.replace(',','.')
 try:return float(v)
 except:return None
cand=[]
for x in I:
 for ri,r in enumerate(x['results']):
  for ii,i in enumerate(r['indicators']):
   for pi,st in enumerate(i['periods']):
    z=E.fromstring(st);acts=z.findall('actual');tars=z.findall('target')
    if not acts or not tars:continue
    act=number(acts[0].get('value'));tar=number(tars[0].get('value'));end=z.find('period-end');date=end.get('iso-date') if end is not None else None;ex=[]
    if x['status']!='4':ex.append('not_closed')
    if len(x['recipients'])!=1:ex.append('not_single_recipient')
    if not date or date>'2026-11-06':ex.append('future_or_unknown_period')
    if act is None or tar is None or act<0 or tar<=0:ex.append('invalid_or_nonpositive_target')
    if 'ex-ante' in (r['title'] or '').lower() or 'prévisions' in (r['title'] or '').lower():ex.append('forecast_not_realized_output')
    if len(acts)!=1 or len(tars)!=1:ex.append('multiple_dimensions_not_matched')
    iso=x['recipients'][0]['iso3'];iso2=x['recipients'][0]['iso2']
    cand.append({'row_id':f"{x['id']}/{ri}/{ii}/{pi}",'project_id':x['id'],'provider':x['provider_country'],'recipient':iso,'sector_dac3':sectors(x,iso2),'indicator':r['title'],'unit':i['title'],'result_type':r['type'],'actual':act,'target':tar,'period_end':date,'target_attained':int(act>=tar) if not ex else None,'eligible_numeric':not ex,'exclusions':ex,'direction':'counts of reported outputs; higher attainment conditional on target; semantic direction must be verified before wider use','baseline_available_in_normalized_snapshot':False,'source_files':x['source_files']})
save('target_actual_candidates.json',cand)
save('data_inventory.json',{'process_projects':len(rows),'providers':len(set(r['provider'] for r in rows)),'recipients':len(set(r['recipient'] for r in rows)),'pairs':len(set((r['provider'],r['recipient']) for r in rows)),'components_observed':{c:sum(r['components'][c]['k'] is not None for r in rows) for c in ['ownership','results_alignment','government_data']},'exact_sector_links':len(matches),'target_actual_pairs':len(cand),'eligible_closed_numeric_pairs':sum(r['eligible_numeric'] for r in cand),'eligible_target_projects':len(set(r['project_id'] for r in cand if r['eligible_numeric'])),'eligible_target_countries':len(set(r['recipient'] for r in cand if r['eligible_numeric'])),'gpedc_sector_warning':'sdg_1..8 and sdgL* are geographic dummy fields, not SDG3 or DAC sector; do not use for health tagging','sdg_3_geography':dict(collections.Counter(r['SDGRegions'] for r in A if r.get('sdg_3')==1))})
print((P/'data_inventory.json').read_text())
print('eligible bysector',collections.Counter(tuple(r['sector_dac3']) for r in cand if r['eligible_numeric']))
