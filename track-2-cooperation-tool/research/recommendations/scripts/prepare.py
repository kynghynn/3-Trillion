from pathlib import Path
import json,math,collections,statistics
B=Path(__file__).resolve().parents[1];OLD=B.parent/'track2_research_20261104'
if not OLD.exists():OLD=B.parent
P=B/'processed'
def old(n):return json.loads((OLD/n).read_text())
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False))
scope=old('expansion/processed/scope.json');donors=list(scope['target_donors'].values());recips=scope['target_recipients'];obs=old('processed/world_bank_observations.json');new=[]
for f in (B/'raw').glob('wb_*.json'):
 a=json.loads(f.read_text());assert isinstance(a,list) and len(a)>1 and isinstance(a[1],list)
 for r in a[1]:
  if r['value'] is not None:new.append({'iso3':r['countryiso3code'],'indicator':r['indicator']['id'],'name':r['indicator']['value'],'year':int(r['date']),'value':r['value'],'unit':'percent','source_file':'raw/'+f.name})
save('new_world_bank_observations.json',new);obs+=new
features={'gni':('NY.GNP.PCAP.CD','log','所得水準'),'rural':('SP.RUR.TOTL.ZS','identity','농촌 인구 비율'),'population':('SP.POP.TOTL','log','인구 규모'),'electricity':('EG.ELC.ACCS.ZS','identity','전력 접근성'),'uhc':('SH_UHC_SCI','identity','보건서비스 접근'),'child_mortality':('SH.DYN.MORT','identity','아동사망 수준'),'water':('SH.H2O.BASW.ZS','identity','기초 식수 접근성'),'internet':('IT.NET.USER.ZS','identity','인터넷 이용률')}
features['gni']=(features['gni'][0],'log','소득 수준')
profiles=[]
for c in recips:
 vals={}
 for k,(code,tr,label) in features.items():
  z=[r for r in obs if r['iso3']==c and r['indicator']==code and r['year']==2023]
  r=z[-1] if z else None;v=r['value'] if r else None
  vals[k]={'value':v,'transformed':math.log(v) if v is not None and tr=='log' and v>0 else v,'year':2023,'indicator':code,'label':label,'source_file':r['source_file'] if r else None,'missing_reason':None if r else 'no_2023_observation'}
 profiles.append({'iso3':c,'features':vals})
scales={}
for k in features:
 vs=[p['features'][k]['transformed'] for p in profiles if p['features'][k]['transformed'] is not None];vs.sort();lo=vs[round((len(vs)-1)*.1)];hi=vs[round((len(vs)-1)*.9)];scales[k]={'p10':lo,'p90':hi,'n':len(vs),'rule':'clip at p10/p90 of frozen 24-recipient demo reference; not refit on selected donor'}
 for p in profiles:
  v=p['features'][k]['transformed'];p['features'][k]['normalized']=max(0,min(1,(v-lo)/(hi-lo))) if v is not None and hi>lo else None
save('recipient_profiles.json',profiles);save('recipient_feature_scales.json',scales)
ratings=old('expansion/processed/country_ratings.json');dp=[{'iso3':r['iso3'],'dimensions':r['dimensions'],'observed_periods':r['observed_periods'],'source':'GPEDC 2026 donor Core Results DP','national_practice_not_sector_skill':True} for r in ratings if r['role']=='donor'];save('donor_profiles.json',dp)
# Join sectors to the matching recipient at transaction level. Counts represent exposure, not impact or national specialisation.
acts=old('expansion/processed/activities.json');sector_ids=collections.defaultdict(set)
def group(code):
 if str(code).startswith(('121','122','123','130')):return 'health'
 if str(code).startswith('140'):return 'water'
 if str(code).startswith('220'):return 'digital'
 return None
for a in acts:
 for r in a['recipients']:
  if r['iso3'] not in recips:continue
  key=(a['provider_country'],r['iso3']);sector_ids[key+('all',)].add(a['id'])
  direct=[s for s in a['sectors'] if s.get('allocation_level')=='activity']
  ss=direct if direct else [s for t in a['transactions'] if any(z.get('code')==r['iso2'] for z in t['recipient_countries']) for s in t['sectors']]
  for s in ss:
   if s.get('vocabulary','1')!='1':continue
   g=group(s.get('code',''))
   if g:sector_ids[key+(g,)].add(a['id'])
ex=[]
for d in donors:
 for r in recips:
  for sector in ['all','health','water','digital']:
   ids=sorted(sector_ids[(d,r,sector)]);ex.append({'donor':d,'recipient':r,'sector':sector,'activity_count':len(ids),'activity_ids':ids,'status':'observed' if ids else 'not_observed_in_subset','sample_scope':'selected publisher files; not national sector finance shares','causal_or_success_measure':False})
save('bilateral_sector_experience.json',ex)
# Complete-case within each declared feature panel: no pair-specific reweighting to reward missingness.
byc={p['iso3']:p for p in profiles};byd={p['iso3']:p for p in dp};panels={'all':['gni','rural','population','electricity'],'health':['gni','rural','population','electricity','uhc','child_mortality'],'water':['gni','rural','population','electricity','water'],'digital':['gni','rural','population','electricity','internet']};sims=[]
for sector,ks in panels.items():
 for a in recips:
  for b in recips:
   if a==b:continue
   gaps=[abs(byc[a]['features'][k]['normalized']-byc[b]['features'][k]['normalized']) if byc[a]['features'][k]['normalized'] is not None and byc[b]['features'][k]['normalized'] is not None else None for k in ks]
   complete=all(g is not None for g in gaps)
   if sector=='all':weights=[1/4]*4
   else:weights=[.5/4]*4+[.5/(len(ks)-4)]*(len(ks)-4)
   sims.append({'role':'recipient','anchor':a,'candidate':b,'sector':sector,'similarity':100*(1-sum(g*w for g,w in zip(gaps,weights))) if complete else None,'comparable_features':sum(g is not None for g in gaps),'required_features':len(ks),'closest_features':[features[k][2] for k,g in sorted(zip(ks,gaps),key=lambda x:x[1] if x[1] is not None else 2)[:2]] if complete else [],'interpretation':'environment similarity only; not need priority or predicted chemistry'})
for a in donors:
 for b in donors:
  if a==b:continue
  common=set(byd[a]['dimensions'])&set(byd[b]['dimensions']);gaps=[abs(byd[a]['dimensions'][k]-byd[b]['dimensions'][k]) for k in common if byd[a]['dimensions'][k] is not None and byd[b]['dimensions'][k] is not None];sims.append({'role':'donor','anchor':a,'candidate':b,'sector':'all','similarity':100-statistics.mean(gaps) if len(gaps)==4 else None,'comparable_features':len(gaps),'required_features':4,'closest_features':sorted(common,key=lambda k:abs(byd[a]['dimensions'][k]-byd[b]['dimensions'][k]))[:2],'interpretation':'GPEDC cooperation practice similarity; not sector expertise'})
save('similarity_pairs.json',sims)
exp={(x['donor'],x['recipient'],x['sector']):x for x in ex};examples=[]
for d in donors:
 for r in recips:
  for sector in ['all','health']:
   for direction,role,anchor,fixed in [('donor_first','recipient',r,d),('recipient_first','donor',d,r)]:
    pool=[s for s in sims if s['role']==role and s['anchor']==anchor and s['sector']==(sector if role=='recipient' else 'all') and s['similarity'] is not None];out=[]
    for s in pool:
     key=(fixed,s['candidate'],sector) if role=='recipient' else (s['candidate'],fixed,sector);e=exp[key]
     # Anchor and candidate must be different; experience is an eligibility filter, not a bonus score.
     if e['status']!='observed':continue
     out.append({'iso3':s['candidate'],'similarity':s['similarity'],'reason_features':s['closest_features'],'activity_count_in_subset':e['activity_count'],'predicted_chemistry':None,'recommendation_type':'similar_environment' if role=='recipient' else 'similar_cooperation_practice'})
    out.sort(key=lambda s:(-s['similarity'],s['iso3']));examples.append({'direction':direction,'selected_donor':d,'selected_recipient':r,'sector':sector,'candidates':out[:3],'no_candidate_reason':None if out else 'insufficient_comparable_profile_or_no_observed_sector_experience_in_subset'})
save('recommendation_previews.json',examples)
save('recommendation_rules.json',{'version':'0.1-lightweight','reference_year':2023,'scope':scope,'panels':panels,'recipient_formula':'100*(1-weighted mean absolute difference of frozen normalized features)','weights':'general panel equal 0.25; sector panels general context 0.5 plus sector needs 0.5','donor_formula':'100-mean absolute difference of four 0..100 GPEDC donor practice dimensions','candidate_rule':'fix first selected country; exclude second selected country; require observed sector exposure in collected subset for suggestions; show additional profile matches separately if needed','missing':'complete selected panel required; no mean imputation or missing as zero','ranking_tie':'ISO3 stable tie-break, not substantive preference','predicted_chemistry':{'enabled':False,'reason':'no validated outcome training labels; schema reserves nullable field'},'limits':['donor practice similarity is not sector specialisation','higher activity counts show experience, not success','national averages omit island and subnational logistics','no fixed PNG recommendation or donor nationality preference','2023 is common comparison year, not current state','health combines health/population/reproductive-health DAC codes; digital telecom exposure does not imply all digital capability','recommendation direction controls candidate entity; observed chemistry itself is not reversed or recalculated']})
assert all(c['iso3'] not in [r['selected_recipient'] if r['direction']=='donor_first' else r['selected_donor']] and c['predicted_chemistry'] is None for r in examples for c in r['candidates'])
assert len(profiles)==24 and len(dp)==10 and len(examples)==960
summary={'new_observations':len(new),'recipient_profiles':len(profiles),'donor_profiles':len(dp),'pair_sector_records':len(ex),'similarity_rows':len(sims),'recommendation_contexts':len(examples),'nonempty_contexts':sum(bool(r['candidates']) for r in examples),'feature_coverage_2023':{k:sum(p['features'][k]['value'] is not None for p in profiles) for k in features},'role_exclusion_and_null_prediction_checks':'passed'};save('validation_summary.json',summary);print(json.dumps(summary,indent=2))
