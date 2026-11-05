from pathlib import Path
import json,math,statistics,collections,hashlib
B=Path(__file__).resolve().parents[1];P=B/'processed';R=B/'raw'
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
def load(n):return json.loads((P/n).read_text())
obs=load('world_bank_observations.json');ids={x['id'] for x in load('countries.json')}
for name in ['wb_SH_UHC_SCI.json','wb_SH_UHC_SCI_CAPACITY.json']:
 p=R/name
 if p.exists():
  a=json.loads(p.read_text())
  if len(a)>1:
   for r in a[1]:
    if r.get('countryiso3code') in ids and r.get('value') is not None:obs.append({'iso3':r['countryiso3code'],'indicator':r['indicator']['id'],'name':r['indicator']['value'],'year':int(r['date']),'value':r['value'],'unit':r.get('unit'),'source_file':'raw/'+name})
obs=list({(r['iso3'],r['indicator'],r['year']):r for r in obs}.values());save('world_bank_observations.json',obs)
latest={}
for r in obs:
 k=(r['iso3'],r['indicator'])
 if k not in latest or latest[k]['year']<r['year']:latest[k]=r
save('world_bank_latest.json',list(latest.values()));save('demo_country_context.json',[r for r in latest.values() if r['iso3'] in ['KOR','VNM','PNG','JPN','AUS','LAO','KHM','IDN','PHL','SLB','TLS']])
# Similarity exploratory, never prognosis. Fixed 2023; no imputation.
features=['NY.GNP.PCAP.CD','SP.RUR.TOTL.ZS','SH.DYN.MORT','SH_UHC_SCI','SH.XPD.OOPC.CH.ZS']
iso2={c['iso2Code']:c['id'] for c in load('countries.json')};eligible={iso2[x['recipient_iso2']] for x in load('korea_partner_inventory.json') if x['recipient_iso2'] in iso2};by={}
for r in obs:
 if r['iso3'] in eligible and r['year']==2023 and r['indicator'] in features:by.setdefault(r['iso3'],{})[r['indicator']]=r['value']
complete={k:v for k,v in by.items() if all(f in v for f in features)}
for v in complete.values():v['NY.GNP.PCAP.CD']=math.log(v['NY.GNP.PCAP.CD'])
ranges={f:(min(v[f] for v in complete.values()),max(v[f] for v in complete.values())) for f in features};rank=[]
if 'VNM' in complete:
 for c,v in complete.items():
  if c=='VNM':continue
  diffs={f:abs(v[f]-complete['VNM'][f])/(ranges[f][1]-ranges[f][0]) for f in features};rank.append({'iso3':c,'similarity':100*(1-statistics.mean(diffs.values())),'feature_distances':diffs})
 rank.sort(key=lambda r:-r['similarity'])
 for i,r in enumerate(rank):r['rank']=i+1
save('vietnam_context_similarity_experiment.json',{'status':'exploratory_not_prediction','year':2023,'reference':'VNM','features':features,'method':'equal-weight Gower numeric distance; income log transformed; frozen observed cohort ranges','ranges':ranges,'cohort':'KOICA snapshot partner countries with complete 2023 observations','n':len(complete),'rankings':rank,'excluded_missing':sorted(eligible-set(complete)),'not_captured':['island logistics','subnational access','supply chain governance','donor operational expertise']})
print('similarity n',len(complete),'PNG',[r for r in rank if r['iso3']=='PNG'],'top',[(r['iso3'],round(r['similarity'],1)) for r in rank[:5]])
# Validation inventory with actual payload type; source retrieval failures are not datasets.
manifest=[]
for p in sorted(R.iterdir()):
 b=p.read_bytes();kind='other';valid=True
 if p.suffix=='.json':
  try:
   a=json.loads(b);kind='json';valid=not(isinstance(a,list) and a and isinstance(a[0],dict) and 'message'in a[0])
  except:valid=False
 elif p.suffix=='.xlsx':kind='xlsx';valid=b[:2]==b'PK'
 elif p.suffix=='.pdf':kind='pdf';valid=b[:4]==b'%PDF'
 elif p.suffix=='.xml':kind='xml';valid=b.lstrip().startswith((b'<?xml',b'<'))
 elif p.suffix=='.html':kind='html'
 manifest.append({'file':'raw/'+p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'format':kind,'payload_valid':valid})
save('file_inventory.json',manifest)
print('files',len(manifest),'valid',sum(x['payload_valid'] for x in manifest),'json observations',len(obs))
