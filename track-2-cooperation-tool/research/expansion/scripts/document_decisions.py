from pathlib import Path
import json,hashlib,collections,datetime
B=Path(__file__).resolve().parents[1]; P=B/'processed';BASE=B.parent

def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
notes=[
 {'id':'DFAT-AIHSS-2023','url':'https://www.dfat.gov.au/sites/default/files/hdmes-aihss-evaluation-2023.pdf','title':'AIHSS Evaluation, June 2023','access':'web_fulltext_review; local PDF download failed','locator':'PDF pages 8–9, 22–24, 38, 52–53 (one-based PDF pages may differ from printed page numbers; web locator P37–38 for printed 32–33)','finding_ko':'일부 사업지역의 예방접종 개선과 함께 운영·조정 및 자료 신뢰성의 한계가 제시된다. 인구분모와 접종률 계산에 문제가 있어 지역 비교와 성과 해석에 주의해야 한다.','use':'PNG 보건체계 협력경험·위험·교훈','limits':['공동지원 사업이며 호주 단독 인과효과가 아님','초기 조건과 지역별 변화가 다름','마누스의 의약품 물류 효과에 직접 대입하지 않음'],'related_activity_ids':['AU-5-INN147']},
 {'id':'DFAT-SLB-HSSP-2019','url':'https://www.dfat.gov.au/sites/default/files/solomon-islands-health-sector-support-program-independent-performance-assessment-and-management-response-2019.pdf','title':'Independent Performance Assessment of HSSP 2018 Performance Indicators','access':'web_fulltext_review; local PDF download failed','locator':'PDF pages 5–6, Executive Summary and Development Partner Performance','finding_ko':'정부와 16개 개발파트너가 합의한 지표를 평가한다. 65%는 성과연계 지급 산정 비율이고, 개발파트너 78%도 파트너 전체에 대한 참고 평가다. 예측 가능한 집행과 다년도 약속에 한계가 보고된다.','use':'공동 이행·상호책무성의 사례','limits':['65 또는 78을 호주–솔로몬제도 케미 점수로 쓰지 않음','2018 성과를 현재 성과로 표시하지 않음'],'related_activity_ids':['AU-5-INL121']},
 {'id':'DFAT-IPR-DEFINITION','url':'https://adp.dfat.gov.au/faqs','title':'AusDevPortal FAQs: How are performance ratings calculated?','access':'web_fulltext_review; local HTML timeout','locator':'performance ratings and reporting exemptions questions','finding_ko':'DFAT 담당자가 연차 투자성과를 1–6으로 평가한다. 4 이상은 만족 범주다. 소규모·초기 단계·일부 유형은 평가대상이 아니므로 결측은 무작위가 아니다.','use':'호주 원평가의 척도 해석','limits':['자체 관리평가를 독립평가로 표시하지 않음','다른 기관 척도와 자동 선형 통합하지 않음']},
 {'id':'SLB-HEALTH-2025','url':'https://solomons.gov.sb/launch-of-150-million-solomon-islands-australia-health-partnership/','title':'Launch of Solomon Islands Australia Health Partnership','access':'web_review; local HTML is a challenge page, not content','locator':'2025-03-13 announcement; cross-check local TOR PDF','finding_ko':'2025–2028 보건협력은 AUD 28 million 규모로 소개되며 지방 보건서비스 전달을 지원한다. 기존 HSSP3과 후속 사업의 시기를 구분한다.','use':'현재 사업의 기간·정책목표 확인','limits':['성과평가가 아닌 사업 설명','AUD와 SBD 금액을 중복합산하지 않음'],'corroborating_local_file':'expansion/raw/solomon_health_tor_2025.pdf'},
 {'id':'PWYF-ATI-2024','url':'https://www.publishwhatyoufund.org/the-index/2024/','download_url':'https://www.publishwhatyoufund.org/download/index-results-data/','title':'2024 Aid Transparency Index Results Data','access':'official XLSX downloaded and parsed','local_file':'expansion/raw/ati_2024.xlsx','finding_ko':'51개 기관의 공개성 평가 자료를 확보했다. 기관 범위이며 개발성과나 국가 전체의 협력 적합성은 아니다.','use':'기관 공개성 프로필, 대체 자료경로 확보 사례'},
 {'id':'IATI-TRANSACTION-TYPE','url':'https://azure.iatistandard.org/en/iati-standard/203/codelists/transactiontype/','title':'IATI Transaction Type codelist','access':'web_review','finding_ko':'자금이전 disbursement와 재화·서비스 지출 expenditure는 다른 거래유형이다. 중복 여부와 보고 경계를 확인해 집계한다.','use':'재정자료 처리 규칙'},
 {'id':'JICA-PNG-WASH','title':'Port Moresby Sewerage System Upgrading Project and associated technical assistance','local_file':'expansion/raw/jica_png_health.pdf','access':'PDF downloaded and title checked','finding_ko':'파일명은 health지만 실제 내용은 하수도 사업 관련 평가다. 임상보건 성과 근거에서 제외하고 WASH·인프라 사례로 분류한다.','use':'문서 분야 오분류 방지'}
]
for n in notes:n['reviewed_on']='2026-11-04'
save('web_review_notes.json',notes)
config=json.loads((BASE/'processed/methodology_config.json').read_text());config['version']='0.2-research-prototype';config['scope']='multi-donor and multi-recipient; 10 donor and 24 recipient demo scope; eventual open-ended coverage';config['source_reuse']='allowed across views and constructs with explicit lineage; same observation not double weighted';config['agency_country_mapping']='retain agency identity; no blind country attribution of agency score';config['comparison']='criterion-oriented scores + optional peer percentile, never enforced equal-size grade groups';config['chemistry']['current_full_scores']=0;config['chemistry']['components_can_be_shown_without_total']=True;config['chemistry']['current_preview']='DFAT health effectiveness distributions are descriptive evidence, not chemistry';config['country_role_inputs']='See source raw indicator IDs retained in country_ratings.json';config['freshness']='Separate edition year and observed reporting periods; country_ratings.json contains observed_periods; old editions never silently backfilled';config['financial_total_status']='transactions preserved; cross-source national totals not yet reconciled';save('methodology_v0.2.json',config)
save('demo_storyboard.json',{'status':'research-backed editorial route, not validated ranking','primary':['AUS','SLB','PNG','Track1 Manus medicine supply chain'],'alternative':['NZL','SLB or VUT','PNG','Track1 Manus medicine supply chain'],'donor_change_supported':True,'intermediate_recipient_not_required':True,'selection_reason':'relevant Pacific health-service delivery experience and accessible evidence','recommendation_type':'editorial_shared_problem_candidate','predicted_chemistry':None,'nearest_neighbor_rank':None,'png_fixed_in_algorithm':False,'steps':['Select Australia and health','Inspect Solomon Islands HSSP3 evidence and distinguish successor program','Review relevant implementation lessons and shortcomings','Open PNG as a candidate sharing the policy problem, not claimed highest similarity','Review PATH/AIHSS evidence and country plan, then identify Manus-specific information gaps','Move to Track1 proposed project design and its own validation plan'],'demo_activity_ids':['AU-5-INL121','AU-5-INN147','NZ-1-ACT-0100478','NZ-1-ACT-0101394','NZ-1-ACT-0102626']})
# Post-download semantic validation separates successful transport from valid content.
manifest=[]
for f in sorted(B.glob('jobs*_manifest.json')):
 for row in json.loads(f.read_text()):
  r=dict(row); r['manifest']=f.name;p=B/r['file']
  if r['status']=='downloaded' and p.exists():
   content=p.read_bytes();valid=True;why='downloaded; content type-specific checks see xml_audit and validation_summary'
   if p.suffix=='.html' and b'You are being redirected' in content:valid=False;why='JavaScript challenge; article not downloaded'
   if p.suffix=='.pdf' and not content.startswith(b'%PDF-'):valid=False;why='not PDF signature'
   if p.suffix=='.xml' and not any(x in content[:200] for x in [b'<?xml',b'<iati-activities']):valid=False;why='XML signature not recognized'
   r.update(content_usable=valid,validation_note=why)
  else:r['content_usable']=False
  manifest.append(r)
save('acquisition_audit.json',manifest)
inv=[]
for f in sorted(B.rglob('*')):
 if not f.is_file() or f.name in ['inventory.json']:continue
 inv.append({'path':str(f.relative_to(BASE)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
save('inventory.json',inv)
summary={'activity_count':len(json.loads((P/'activities.json').read_text())),'result_actual_count':len(json.loads((P/'result_observations.json').read_text())),'ati_agency_count':len(json.loads((P/'ati_2024_agencies.json').read_text())),'acquisition_records':len(manifest),'content_usable_download_records':sum(r['content_usable'] for r in manifest),'source_families_total':len(json.loads((BASE/'source_registry.json').read_text())),'expansion_bytes':sum(r['bytes'] for r in inv),'all_full_chemistry_scores_null':True}
save('package_summary.json',summary)
print(summary)
