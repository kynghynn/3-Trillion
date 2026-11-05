from pathlib import Path
import json,xml.etree.ElementTree as E,collections,hashlib,datetime,statistics
B=Path(__file__).resolve().parents[1]; P=B/'processed'; BASE=B.parent

def load(n):return json.loads((P/n).read_text())
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
a=load('activities.json'); byid={x['id']:x for x in a}
# Preserve weighted ATI subindicator scores, not percentages inferred from their values.
sheet=next(iter(load('ati_2024_cells.json').values())); headers=sheet[1]
ati=[]
for row in sheet[2:]:
 if not row[0]:continue
 ati.append({'publisher':row[0],'edition':2024,'unit_of_analysis':'agency','total_score':row[1],'category':row[2],'weighted_component_scores':{headers[i]:row[i] for i in range(3,len(headers))},'source':'expansion/raw/ati_2024.xlsx','national_score':None})
save('ati_2024_agencies.json',ati)
# Record every actual with provenance. IATI actual is not itself verified impact.
obs=[]
for x in a:
 for ri,r in enumerate(x['results']):
  for ii,i in enumerate(r['indicators']):
   for pi,xml in enumerate(i['periods']):
    p=E.fromstring(xml)
    for ai,v in enumerate(p.findall('actual')):
     st=p.find('period-start');en=p.find('period-end')
     obs.append({'observation_id':f"{x['id']}/result/{ri}/indicator/{ii}/period/{pi}/actual/{ai}",'activity_id':x['id'],'provider_country':x['provider_country'],'recipient_iso3_candidates':[z['iso3'] for z in x['recipients']],'recipient_specific':len(x['recipients'])==1,'result_type':r['type'],'result_title':r['title'],'indicator_title':i['title'],'measure_code':i['measure'],'period_start':st.get('iso-date') if st is not None else None,'period_end':en.get('iso-date') if en is not None else None,'actual_attributes':dict(v.attrib),'dimensions':[dict(d.attrib) for d in v.findall('dimension')],'comments':[' '.join(t.itertext()).strip() for t in v.findall('comment')],'source_files':x['source_files'],'interpretation':'publisher_reported; not automatically independent evaluation or causal impact'})
save('result_observations.json',obs)
# Strict country-specific health subset: broad multi-country investment ratings are not duplicated into country scores.
def health(x,iso3):
 direct=[s for s in x['sectors'] if s.get('allocation_level')=='activity']
 if direct:return any(s.get('vocabulary','1')=='1' and s.get('code','').startswith(('121','122','123','130')) for s in direct)
 iso2=next((r['iso2'] for r in x['recipients'] if r['iso3']==iso3),None)
 return any(any(r.get('code')==iso2 for r in t['recipient_countries']) and any(s.get('vocabulary','1')=='1' and s.get('code','').startswith(('121','122','123','130')) for s in t['sectors']) for t in x['transactions'])
ratings=[]
for o in obs:
 x=byid[o['activity_id']]
 if o['provider_country']!='AUS' or o['indicator_title']!='Investment Performance Ratings' or not o['recipient_specific']:continue
 rec=x['recipients'][0]['iso3']
 if not health(x,rec):continue
 for d in o['dimensions']:
  if d.get('name') not in ['Effectiveness','Efficiency','Gender equality','Disability equity']:continue
  try:v=int(o['actual_attributes']['value'])
  except (ValueError,KeyError):continue
  if not 1<=v<=6:continue
  ratings.append({'observation_id':o['observation_id'],'activity_id':x['id'],'title':x['title'],'donor':'AUS','recipient':rec,'sector':'health_including_population_reproductive_health','criterion':d['name'],'period_start':o['period_start'],'period_end':o['period_end'],'ordinal_rating':v,'satisfactory':v>=4,'assessment_type':'DFAT investment manager annual assessment','scale_min':1,'scale_max':6,'scale_source':'https://adp.dfat.gov.au/faqs','chemistry_score':None})
save('australia_health_rating_observations.json',ratings)
summaries=[]
for rec in load('scope.json')['target_recipients']:
 rows=[r for r in ratings if r['recipient']==rec and r['criterion']=='Effectiveness']
 if not rows:continue
 year=max(r['period_end'] for r in rows if r['period_end']); rr=[r for r in rows if r['period_end']==year]
 unique={r['activity_id']:r for r in rr}; rr=list(unique.values());n=len(rr)
 summaries.append({'donor':'AUS','recipient':rec,'period_end':year,'label':'관측 보건투자의 효과성 평가 분포','n_distinct_activities':n,'satisfactory_count':sum(r['satisfactory'] for r in rr),'satisfactory_share':sum(r['satisfactory'] for r in rr)/n,'ordinal_distribution':{str(k):sum(r['ordinal_rating']==k for r in rr) for k in range(1,7)},'display_percent':n>=3,'activity_ids':list(unique),'comparability':'same publisher scale, selected rated investments only; years may differ across recipients','chemistry_score':None,'caution':'3 cases is an editorial display threshold, not statistical reliability; excludes multi-country investments and unassessed small investments'})
save('australia_health_performance_preview.json',summaries)
selected=['AU-5-INL121','AU-5-INN147','AU-5-INM480','AU-5-INO262','NZ-1-ACT-0100478','NZ-1-ACT-0101394','NZ-1-ACT-0102626']
save('demo_project_evidence.json',[dict(byid[id],result_observation_ids=[o['observation_id'] for o in obs if o['activity_id']==id],evidence_scope='annual program/investment or shared intervention; not independent country-pair effect') for id in selected if id in byid])
# Minimal website contract. Distinguish source evidence, experimental composite and prediction.
save('data_contract.json',{'version':'0.2','entity_keys':{'country':'ISO3; sovereign status and territory metadata must be explicit','organisation':'IATI reporting-org ref; do not equate organisation with nation','activity':'IATI identifier + reporting entity provenance','pair':'donor ISO3 + recipient ISO3 + DAC sector + observation period'},'required_evidence_fields':['source_id','raw_file','source_url','retrieved_at','observation_period','edition','unit_of_analysis','sector_scope','assessment_type','missing_reason'],'missing_reasons':['not_collected','not_reported','not_applicable','too_old','insufficient_evidence','incomparable_scale'],'financial_rules':['Keep transaction types 2 commitment, 3 disbursement, 4 expenditure separate','Keep currency and value-date; no mixed-currency sum','Use transaction-level country/sector where present; otherwise declared activity allocations','Do not divide equally when published shares are missing; mark unallocated','Do not sum IATI, CRS and Lowy as independent money','IATI identifier count is activity count, not necessarily unique development project count','Resolve parent-child and cofunding overlaps before portfolio totals'],'map_states':['country_role_rating_prototype','pair_process_evidence','sector_performance_evidence','full_chemistry_not_yet_available','no_observed_relationship_in_subset','relationship_observed_but_insufficient_evidence'],'colors':{'country':'separate donor/recipient legend; no grade for missing','chemistry':'shared fixed scale only for comparable observed scores; red/blue does not encode missing','missing':'hatched/light grey with reason; allow click for available records','uncertainty':'separate opacity/icon with explicit legend'},'role_selection':'Either donor-first or recipient-first; a country may have both roles; multilaterals in separate entity layer','publication_policy':'Do not show experimental grades as externally validated rankings; predictions require separate validation and visual label'})
save('source_reuse_matrix.json',[
 {'source':'GPEDC','use':['country_role_practice_rating','bilateral_process_evidence','institutional_context','qualitative_sector_evaluation_background'],'rule':'Same observation may appear in multiple panels. Do not add node aggregate and its constituent edge observation to one final score. For incremental predictive value use leave-one-partner-out donor/recipient aggregates and temporal holdout. All-sector rows cannot stand in for health-specific outcomes.'},
 {'source':'IATI','use':['activity_inventory','sector_experience','funding_history','document_discovery','publisher_reported_results','data_completeness_diagnostics'],'rule':'Separate publication completeness from outcome quality. One shared project is one intervention cluster. API/XML reporting is not independent corroboration of an evaluation it republishes.'},
 {'source':'ATI2024','use':['agency_disclosure_profile','donor_rating_disclosure_subdimension_candidate','IATI_availability_diagnostic'],'rule':'Agency-level and 2024 edition. No national average without matched agency coverage and defensible weights; do not count ATI publication and IATI completeness as two independent achievements.'},
 {'source':'WGI_SPI_OBS_CPIA','use':['recipient_operational_context','similarity_features','external_convergent_validation','alternative_capacity_composite_candidate'],'rule':'Changing from cooperation practice to capacity changes construct. Do not add total indices and shared constituent variables. Overlap source check, correlations and sensitivity required; fragility/need is not lack of cooperation willingness.'},
 {'source':'QuODA_CDI','use':['construct_design','external_comparison','historical_benchmark'],'rule':'Inspect components and years. QuODA may already reuse GPEDC/ATI. CDI total includes policy domains outside aid, so use relevant components only.'},
 {'source':'OECD_CRS_Lowy_AidData','use':['portfolio_denominator','sector_specialisation','recipient_exposure','financial_crosscheck'],'rule':'Definitions differ: ODA vs OOF, commitments vs disbursements, current vs constant prices. Mirrors are alternative access routes to same observations, not extra evidence.'},
 {'source':'independent_evaluation_national_strategy','use':['priority_fit','joint_delivery','outcomes','sustainability','project_risk_lessons'],'rule':'Record page, evaluator, financing and coverage. Priority statements demonstrate alignment, not success; pre-completion sustainability readiness differs from post-completion persistence.'}
])
# Source catalog update is additive and retains historical research.
reg=json.loads((BASE/'source_registry.json').read_text())
for r in reg:
 if r['id']=='ATI':r.update(decision='downloaded_agency_auxiliary',local_file='expansion/raw/ati_2024.xlsx',limitation='51 agency observations, edition 2024; not country effectiveness; 2026 methodology not applied retrospectively')
new=[{'id':'CODEFORIATI-REGISTRY','title':'Code for IATI registry metadata mirror','url':'https://registry.codeforiati.org/','local_file':'expansion/raw/registry_datasets.json','use':'discover official publisher XML URLs','limitation':'third-party metadata mirror; underlying activity data downloaded from listed publisher URLs; not a CRS copy'}, {'id':'DFAT-PERFORMANCE','title':'AusDevPortal performance definitions','url':'https://adp.dfat.gov.au/faqs','use':'interpret annual investment performance ratings','limitation':'manager assessment, exemptions and reporting selection; not independent causal effect'}]
for provider in ['ausgov','mfat','jica','fcdo','gac-amc','afd','sida']:
 new.append({'id':'IATI-'+provider.upper(),'title':provider+' IATI publisher XML sample','url':'https://registry.codeforiati.org/','local_files':[r['file'] for r in load('xml_audit.json') if Path(r['file']).name.startswith(provider)],'use':'activities, transactions, documents and reported results','limitation':'selected files and agencies; partial national coverage; actual publisher URLs in expansion/jobs2_manifest.json'})
for r in new:
 r.update(reviewed_on='2026-11-04',decision='core_expansion',redistribution='Check publisher terms before publishing original files')
 if not any(x['id']==r['id'] for x in reg):reg.append(r)
(BASE/'source_registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2))
print(json.dumps({'ati_agencies':len(ati),'result_actual_observations':len(obs),'health_rating_observations':len(ratings),'australia_health_recipient_previews':len(summaries),'demo_projects':len([i for i in selected if i in byid])},indent=2))
for r in summaries:
 if r['recipient'] in ['SLB','PNG','VUT','FJI']:print(r)
