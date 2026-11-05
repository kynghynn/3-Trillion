from pathlib import Path
import json,collections,statistics,math,xml.etree.ElementTree as E
B=Path(__file__).resolve().parents[1];P=B/'processed';D=B/'docs'
def load(n):return json.loads((P/n).read_text())
def save(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
# Explicit normative design, not an externally validated model.
models={'recipient':{'strategy':['D2_1_1'],'inclusion':['D1_1_comp','D4_1_comp'],'mutual_accountability':['D2_6_1'],'information_system':['D2_7_1','D3_1_1']},'donor':{'ownership':['D2_2_1','D2_3_3'],'predictability':['D2_4_1_1','D2_4_1_2'],'inclusion':['D1_1_4','D4_1_4'],'accountability':['D2_7_2','D3_2_2']}}
config={'version':'0.1-research-prototype','validation_status':'not_validated','models':models,'pillar_weights':'equal 0.25','normalization':'GPEDC 0..1 times 100; D2_6_1 divide by 5 then times 100','missing':'require all selected indicators; never substitute other-source proxies','grade_policy':'12 equal-width display bins, provisional only; not empirical thresholds','grades_low_to_high':['D-','D0','D+','C-','C0','C+','B-','B0','B+','A-','A0','A+'],'freshness':'2023-26 round rows labelled 2026; retain actual ReportingYear separately; older rounds historical only','chemistry':{'fit':0.3,'joint_delivery':0.3,'outcomes':0.25,'sustainability':0.15,'gate':'all four components; >=3 independent evaluated projects in same sector, >=2 completion years; coverage and selection bias shown; proposed quality gate, not statistical guarantee'},'map':{'unknown':'hatched neutral','historical':'outlined neutral, clickable','no_observed_relationship':'light gray, explorable','unsupported_high_chemistry_prediction':False}}
save('methodology_config.json',config)
out=[]
for role,fn in [('recipient','gpedc_core_results.json'),('donor','gpedc_core_results_dp.json')]:
 for r in load(fn):
  if r.get('year')!=2026 or (role=='donor' and r.get('Bilateral')!=1):continue
  dims={};raw={}
  for dim,keys in models[role].items():
   vals=[]
   for k in keys:
    v=r.get(k);raw[k]=v
    if isinstance(v,(int,float)) and not isinstance(v,bool):
     z=v/5 if k=='D2_6_1' else v
     if 0<=z<=1:vals.append(z*100)
   dims[dim]=statistics.mean(vals) if len(vals)==len(keys) else None
  complete=all(v is not None for v in dims.values());score=statistics.mean(dims.values()) if complete else None
  sensitivity=[]
  if complete:
   for dim in dims:
    for weight in [0.15,0.35]:sensitivity.append(sum(v*(weight if k==dim else (1-weight)/3) for k,v in dims.items()))
  out.append({'country':r.get('recipient',r.get('provider')),'iso3':r.get('alpha3code'),'role':role,'round_year':2026,'observed_year':'see GPEDC PC/DP Data.ReportingYear','dimensions':dims,'raw_indicators':raw,'score':score,'experimental_grade':config['grades_low_to_high'][min(11,int(score*12/100))] if complete else None,'publication_status':'prototype_not_validated' if complete else 'insufficient_data','weight_sensitivity_range':[min(sensitivity),max(sensitivity)] if sensitivity else None,'source':'gpedc_global_2026.xlsx'})
save('country_rating_prototypes.json',out)
# Preserve actual fiscal reporting year, never call survey round year the observation year.
pairs=load('gpedc_korea_pairs.json');dp=load('gpedc_dp_data.json'); projects=load('gpedc_projects_data.json')
for p in pairs:
 p['reporting_periods']=sorted({str(x['ReportingYear']) for x in dp if x.get('provider')==p['provider'] and x.get('recipient')==p['recipient'] and x.get('year')==p['year'] and x.get('ReportingYear')})
 p['health_specific']=False;p['chemistry_score']=None;p['reason']='Cross-sector process measures; not health outcome evidence'
save('korea_pair_evidence.json',pairs)
acts=load('koica_activities.json'); summary=[]
for country in sorted({r['code'] for x in acts for r in x['recipients']}):
 aa=[x for x in acts if any(r['code']==country for r in x['recipients'])]
 summary.append({'recipient_iso2':country,'activity_count_in_snapshot':len(aa),'health_activity_ids':[x['iati_identifier'] for x in aa if any(s.get('code','').startswith(('121','122','123','130')) for s in x['sectors'])],'scope':'KOICA publisher snapshot generated 2025-11-18; not complete Korea ODA','chemistry':None})
save('korea_partner_inventory.json',summary)
root=E.parse(B/'raw/koica_iati_2025.xml').getroot(); results=[]
for a in root.findall('iati-activity'):
 for r in a.findall('result'): results.append({'activity_id':a.findtext('iati-identifier'),'type':r.get('type'),'title':' '.join(n.text or '' for n in r.findall('title/narrative')),'description':' '.join(n.text or '' for n in r.findall('description/narrative')),'actual_values':[v.text for v in r.findall('.//period/actual')],'status':'descriptive_output_only' if not r.findall('.//period/actual') else 'actual_available'})
save('koica_results.json',results)
save('evaluation_evidence.json',[{'id':'KOICA-QHEALTH-2024','donor':'KOR','recipient':'VNM','sector':'health','title':'베트남 중부지역병원 사후관리 기술협력(Q-health)','source_file':'raw/koica_qhealth.pdf','source_url':'https://www.koica.go.kr/sites/evaluation_kr/common/filedownload/1927','pdf_page':5,'evaluation_completed':'2023-10-31','quality_review_completed':'2024-05-09','scores_as_published':{'relevance':3,'coherence':3.5,'effectiveness':2.6,'sustainability_readiness':3.6,'total':14.7},'scale_max':4,'total_max':20,'published_overall_label':'성공적','report_quality_grade':'C','important':'C is report quality grade, not national/project success grade. Sustainability is readiness, not longitudinal measured persistence. Published rounding retained.','budget_conflict':{'cover':'400백만불','summary_pdf_page_6':'400만불','use':'USD 4 million only with discrepancy note; not silently repaired'},'interpretation':'다낭과 후에의 이행·성과 차이를 분리하여 설명. 단일 사업으로 국가쌍 케미 산출 금지.','chemistry_score':None}])
print('ratings',len(out),'complete',sum(x['score'] is not None for x in out),'partners',len(summary),'iati',len(acts))
for x in out:
 if x['country'] in ['Korea','Viet Nam [VN]']:print(x['country'],x['dimensions'],x['publication_status'])
