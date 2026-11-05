from pathlib import Path
import json,xml.etree.ElementTree as E,collections,re,statistics
B=Path(__file__).resolve().parents[1];P=B/'processed';BASE=B.parent
D={'Australia':'AUS','New Zealand':'NZL','Japan':'JPN','Korea':'KOR','United Kingdom':'GBR','Canada':'CAN','France':'FRA','Sweden':'SWE','Germany':'DEU','United States':'USA'}
R=['PNG','SLB','VUT','FJI','WSM','TON','TLS','VNM','KHM','LAO','IDN','PHL','BGD','NPL','PAK','LKA','KEN','TZA','UGA','RWA','GHA','SEN','ETH','MMR']
country=json.loads((BASE/'processed/countries.json').read_text());i2={x['iso2Code']:x['id'] for x in country};names={x['id']:x['name'] for x in country}
def load(n):return json.loads((BASE/'processed'/n).read_text())
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str,allow_nan=False))
def txt(e,path):return ' '.join((x.text or '').strip() for x in e.findall(path)).strip()
pub={'ausgov':'AUS','mfat':'NZL','jica':'JPN','fcdo':'GBR','gac-amc':'CAN','afd':'FRA','sida':'SWE','koica':'KOR'}
files=[*sorted((B/'raw').glob('*.xml')),BASE/'raw/koica_iati_2025.xml'];acts={};audits=[];conflicts=[]
for p in files:
 donor=next((v for k,v in pub.items() if p.name.startswith(k)),None)
 if donor is None:continue
 try:rt=E.parse(p).getroot()
 except Exception as e:audits.append({'file':str(p.relative_to(BASE)),'error':str(e)});continue
 aa=rt.findall('iati-activity');n=0
 for x in aa:
  direct=x.findall('recipient-country'); nodes=direct or x.findall('transaction/recipient-country')
  recs=list({e.get('code'):{'iso2':e.get('code'),'iso3':i2.get(e.get('code')),'percentage':e.get('percentage') if direct else None,'allocation_level':'activity' if direct else 'transaction'} for e in nodes}.values())
  if not any(e['iso3'] in R for e in recs):continue
  id=(x.findtext('iati-identifier') or '').strip()
  if not id:continue
  row={'id':id,'provider_country':donor,'reporting_org_ref':x.find('reporting-org').get('ref') if x.find('reporting-org') is not None else None,'reporting_org_name':txt(x,'reporting-org/narrative'),'title':txt(x,'title/narrative'),'description':txt(x,'description/narrative'),'recipients':recs,'sectors':[dict(e.attrib, allocation_level='activity' if x.findall('sector') else 'transaction') for e in (x.findall('sector') or x.findall('transaction/sector'))],'status':x.find('activity-status').get('code') if x.find('activity-status') is not None else None,'dates':[dict(e.attrib) for e in x.findall('activity-date')],'participating_orgs':[{'ref':e.get('ref'),'role':e.get('role'),'name':txt(e,'narrative')} for e in x.findall('participating-org')],'documents':[{'url':e.get('url'),'title':txt(e,'title/narrative'),'categories':[c.get('code') for c in e.findall('category')]} for e in x.findall('document-link')],'results':[{'type':e.get('type'),'title':txt(e,'title/narrative'),'indicators':[{'title':txt(z,'title/narrative'),'measure':z.get('measure'),'periods':[E.tostring(q,encoding='unicode') for q in z.findall('period')]} for z in e.findall('indicator')]} for e in x.findall('result')],'transactions':[],'source_files':[str(p.relative_to(BASE))],'generated_at':rt.get('generated-datetime'),'chemistry_score':None}
  for t in x.findall('transaction'):
   v=t.find('value');dt=t.find('transaction-date');tt=t.find('transaction-type')
   row['transactions'].append({'type':tt.get('code') if tt is not None else None,'date':dt.get('iso-date') if dt is not None else None,'value':v.text if v is not None else None,'currency':v.get('currency',x.get('default-currency')) if v is not None else None,'value_date':v.get('value-date') if v is not None else None,'recipient_countries':[dict(z.attrib) for z in t.findall('recipient-country')],'sectors':[dict(z.attrib) for z in t.findall('sector')]})
  if id in acts:
   if acts[id]['provider_country']!=donor:conflicts.append({'id':id,'countries':[acts[id]['provider_country'],donor]})
   acts[id]['source_files']+=row['source_files']
  else:acts[id]=row
  n+=1
 audits.append({'file':str(p.relative_to(BASE)),'provider':donor,'total_activities':len(aa),'selected_occurrences':n,'generated_at':rt.get('generated-datetime')})
a=list(acts.values());save('activities.json',a);save('xml_audit.json',audits);save('identity_conflicts.json',conflicts)
# GPEDC donor-agnostic network, entity type retained.
core=load('gpedc_core_results_pc_dp.json');dp=load('gpedc_dp_data.json');look={(r.get('recipient'),r.get('provider'),r.get('year')):r.get('reporting_year') for r in dp}
pairs=[]
for r in core:
 m=re.search(r'\[([A-Z]{2})\]',r['recipient']);iso=i2.get(m.group(1)) if m else None
 if r['provider'] not in D or iso not in R:continue
 z=dict(r);z.update(donor_iso3=D[r['provider']],recipient_iso3=iso,reporting_period=look.get((r['recipient'],r['provider'],r['year'])),scope='all_sectors',chemistry_score=None);pairs.append(z)
save('pair_process_observations.json',pairs)
latest={}
for r in pairs:
 key=(r['donor_iso3'],r['recipient_iso3'])
 if key not in latest or latest[key]['year']<r['year']:latest[key]=r
coverage=[]
for donor in D.values():
 for rec in R:
  aa=[x for x in a if x['provider_country']==donor and any(z['iso3']==rec for z in x['recipients'])];g=latest.get((donor,rec));health=[x for x in aa if any(s.get('allocation_level')=='activity' and s.get('vocabulary','1')=='1' and s.get('code','').startswith(('121','122','123','130')) for s in x['sectors']) or any(any(z.get('code') in i2 and i2[z['code']]==rec for z in t['recipient_countries']) and any(s.get('vocabulary','1')=='1' and s.get('code','').startswith(('121','122','123','130')) for s in t['sectors']) for t in x['transactions'])]
  coverage.append({'donor':donor,'recipient':rec,'iati_activity_count':len(aa),'health_activity_count':len(health),'activities_with_period_actual':sum(any('<actual' in t for q in x['results'] for z in q['indicators'] for t in z['periods']) for x in aa),'evaluation_link_activity_count':sum(any('A07' in d['categories'] for d in x['documents']) for x in aa),'gpedc_latest_round':g['year'] if g else None,'gpedc_reporting_period':g.get('reporting_period') if g else None,'relationship_status':'observed_in_sources' if aa or g else 'not_observed_in_collected_subset','chemistry_status':'not_scored','sample_scope':'selected publisher files; not national portfolio census'})
save('coverage_matrix.json',coverage)
save('countries.json',[{'iso3':c,'name':names.get(c,c),'roles':(['donor'] if c in D.values() else [])+(['recipient'] if c in R else [])} for c in sorted(set(D.values())|set(R))])
ratings=[x for x in load('country_rating_prototypes.json') if x['country'] in D or x.get('iso3') in R]
for x in ratings:
 if not x.get('iso3'):x['iso3']=D.get(x['country'])
pc=load('gpedc_pc_data.json')
for x in ratings:
 if x['role']=='recipient':
  periods=sorted(set(str(r['reporting_year']) for r in pc if r.get('recipient')==x['country'] and r.get('year')==x['round_year'] and r.get('reporting_year')))
 else:
  periods=sorted(set(str(r['reporting_year']) for r in dp if r.get('provider')==x['country'] and r.get('year')==x['round_year'] and r.get('reporting_year')))
 x['observed_periods']=periods
 x['observed_year']='multiple reporting periods' if len(periods)>1 else periods[0] if periods else 'not available'
save('country_ratings.json',ratings)
save('country_context.json',[r for r in load('world_bank_latest.json') if r['iso3'] in set(D.values())|set(R)])
save('scope.json',{'target_donors':D,'target_recipients':R,'eventual_scope':'open ended all observed countries; same country may be donor and recipient; multilaterals typed separately','collected_activity_count':len(a),'activity_donor_counts':dict(collections.Counter(x['provider_country'] for x in a)),'pair_round_rows':len(pairs),'observed_pairs':sum(x['relationship_status']=='observed_in_sources' for x in coverage),'full_chemistry_scores':0})
print('ACTS',len(a),'DONORS',dict(collections.Counter(x['provider_country'] for x in a)),'PAIRS',sum(x['relationship_status']=='observed_in_sources' for x in coverage))
for c in coverage:
 if c['donor'] in ['AUS','NZL','JPN'] and c['recipient'] in ['PNG','SLB','VUT']: print(c['donor'],c['recipient'],c['iati_activity_count'],c['health_activity_count'],c['gpedc_latest_round'])
