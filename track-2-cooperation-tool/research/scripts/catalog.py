from pathlib import Path
import json
B=Path(__file__).resolve().parents[1]
rows=[
('GPEDC-2026','OECD/UNDP GPEDC Global Database','https://www.effectivecooperation.org/resources/progressreport2026','core','raw/gpedc_global_2026.xlsx','국가·공여자·쌍별 협력관행 및 조사사업','발간라운드 2026과 실제 ReportingYear 구분; 표본선정·자기보고; 일부 원지수 결측을 0 처리'),
('GPEDC-HIST','GPEDC 2014/2016/2018','https://www.effectivecooperation.org/content/gpedc-monitoring-excel-database','historical','raw/gpedc_historical.xlsx','과거 협력관행','현재와 문항·모집단 차이; 현재 점수 대체 금지'),
('QUODA','CGD QuODA 2021','https://www.cgdev.org/topics/quoda','method_and_historical','raw/quoda_2021.xlsx','공여자 메타지표 설계·과거 비교','2021판을 현재 평가로 사용 금지; GPEDC·ATI와 중복'),
('ATI','Publish What You Fund ATI 2024','https://www.publishwhatyoufund.org/the-index/2024/','auxiliary_not_downloaded',None,'공여기관 공개 역량','기관 단위; 효과성 아님; 다운로드 시간초과'),
('CDI','CGD CDI 2025','https://www.cgdev.org/cdi-methodology','method_only','raw/cdi_method.pdf','개발금융 구성항목 검토','총점은 무역·이민 등 포함하여 범위 과대'),
('WGI','World Bank WGI 2026 revision','https://www.worldbank.org/en/publication/worldwide-governance-indicators','context','raw/wgi_2026.xlsx','행정·책무성·운영위험 배경','인지기반 추정; 90% 구간; 다른 지수와 원천중복; 기존 EST 코드는 조회오류'),
('SPI','World Bank SPI','https://www.worldbank.org/en/programs/statistical-performance-indicators','context','raw/wb_IQ.SPI.OVRL.json','국가 통계체계 역량','사업 모니터링 성과와 다름'),
('CPIA','World Bank CPIA','https://data.worldbank.org/indicator/IQ.CPA.PUBS.XQ','diagnostic','raw/wb_IQ.CPA.PUBS.XQ.json','공공행정 역량 참고','공개 국가군 제한; 누락국 0점 금지'),
('OBS','IBP Open Budget Survey 2025','https://internationalbudget.org/open-budget-survey/download','external_validation','raw/obs_2025.xlsx','예산참여·감시·공개','주민의 개별사업 참여를 직접 측정하지 않음'),
('PEFA','PEFA public finance assessments','https://www.pefa.org/node/5592','diagnostic_access_limited',None,'재정관리 체계의 심층 점검','평가연도/프레임워크/국가·지방 차이; 접근 403; D* 결측이 낮은 점수로 처리되는 원칙 주의'),
('CPI','Transparency International CPI 2025','https://www.transparency.org/en/cpi/2025','exclude_from_core',None,'부패 인식 참고','WGI CC와 중복; 국가 파트너십 자체가 아님'),
('VDEM','V-Dem civil society participation','https://www.v-dem.net/data/','optional_validation',None,'시민사회 환경 점검','정부 파트너십 참여의 직접 증거 아님; WGI 원천중복'),
('LTL','AidData Listening to Leaders 2025','https://www.aiddata.org/publications/listening-to-leaders-2025-development-cooperation-over-a-decade-of-disruption','external_validation','raw/aiddata_ltl_2025.pdf','협력국 리더의 유용성 인식','엘리트 조사; 영향력은 효과성 아님; 모든 쌍 미시자료 공개 확인 안 됨'),
('CRS','OECD Creditor Reporting System','https://data-explorer.oecd.org/vis?df[ag]=OECD.DCD.FSD&df[id]=DSD_CRS@DF_CRS','core_flows_pending','raw/oecd_crs_flow.xml','비교가능한 공여자-수원자-분야-연도 금액','메타데이터만 저장; bulk 403; 아직 전체 흐름자료 없음'),
('IATI','IATI Datastore','https://docs.datastore.iatistandard.org/en/latest/api/','core_discovery','raw/iati_api_docs.html','사업·거래·문서·성과 연결','공식 API 키 필요; 발행기관 직접 XML로 대체 가능; 부분포괄'),
('KOICA-IATI','KOICA IATI 2025 snapshot','https://www.oda.go.kr/opo/nnstat/opoNstatInfoOthBcIatiList.do','core','raw/koica_iati_2025.xml','2600 사업·115 수원국 코드 연결','2025-11-18 생성; 공개 목록 2026-03-06; period/actual 없음; 일반 포털 링크를 보고서 직접링크로 오인 금지'),
('KOICA-EVAL','KOICA Q-health evaluation 2024','https://www.koica.go.kr/sites/evaluation_kr/article/view/1265','core_case','raw/koica_qhealth.pdf','베트남 보건사업 실제 평가·이행교훈','300쪽; 지속가능성 준비도; C는 보고서 품질등급; 표지 금액 오기 의심'),
('JICA','JICA evaluation search','https://www2.jica.go.jp/en/evaluation/index.php?country1=Viet+Nam&search=Search','candidate',None,'일본-베트남 비교 평가','후보 보고서 검색 확인; 원문 직접 저장 시간초과; 점수 미산출'),
('DFAT','DFAT PNG Medical Supply Reform 2013 evaluation','https://www.dfat.gov.au/sites/default/files/png-burnet-institute-medical-supply-evaluation.pdf','historical_case',None,'호주-PNG 의약품 유통 경험','웹 원문 확인; 로컬 다운로드 시간초과; 오래된 결과를 현재로 사용 금지'),
('LOWY','Lowy Pacific Aid Map','https://pacificaidmap.lowyinstitute.org/methodology/','regional_crosscheck','raw/lowy_data.html','태평양 사업·공여기관 탐색','ODF=ODA+OOF; CRS와 중복; 전체 구조화 자료 미추출'),
('WBPROJECT','World Bank Projects API','https://search.worldbank.org/api/v2/projects?format=json&countrycode=PG&rows=500','multilateral_context','raw/wb_projects_png.json','PNG·베트남 다자기관 사업 탐색','한국 양자사업으로 계산 금지; 완료와 성과등급 다름'),
('WDI','World Bank WDI API','https://api.worldbank.org/v2/indicator?format=json&per_page=30000','context_similarity','raw/wb_indicators.json','UHC·농촌·소득·아동사망·의료비 맥락','국가 집계값을 마누스 기초선으로 대입 금지; 코드 변경 대응'),
('PNG-NHP','PNG National Health Plan 2021–2030','https://health.gov.pg/pdf/NHP_2A.pdf','policy_alignment','raw/png_health_plan.pdf','수원국 보건 우선순위','국가 계획 존재가 개별 제안 승인이나 실행 약속은 아님'),
('WHO-PNG','WHO medical supply strategic plan consultation 2026','https://www.who.int/papuanewguinea/news/detail/29-07-2026-strengthening-papua-new-guinea-s-medical-supply-system','policy_alignment','raw/who_png_2026.html','의약품 공급망 정책수요','MSSP 2027–31 초안 협의 소식; 확정 시행계획으로 표기 금지'),
('OECD-COMP','OECD/JRC composite indicators handbook','https://www.oecd.org/en/publications/handbook-on-constructing-composite-indicators-methodology-and-user-guide_9789264043466-en.html','method','raw/oecd_composite.pdf','가중치·정규화·불확실성 검토','동일가중도 가치판단'),
('OECD-EVAL','OECD Applying Evaluation Criteria Thoughtfully','https://www.oecd.org/en/publications/applying-evaluation-criteria-thoughtfully_543e84ed-en.html','method','raw/oecd_evaluation.pdf','적절성·일관성·효과성·효율성·영향·지속가능성','질문 틀이며 자동점수 산식 아님'),
]
out=[dict(zip(['id','title','url','decision','local_file','use','limitation'],r),reviewed_on='2026-11-04',redistribution='Verify source terms before republishing originals; link and attribute in website') for r in rows]
(B/'source_registry.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('source families',len(out))
