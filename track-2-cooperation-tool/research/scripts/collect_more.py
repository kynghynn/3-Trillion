from collect import *
jobs={
'gpedc_global_2026.xlsx':'https://www.effectivecooperation.org/sites/default/files/2026-09/GPEDC_Global_Data_public_0.xlsx',
'gpedc_historical.xlsx':'https://www.effectivecooperation.org/sites/default/files/documents/GPEDC_Datasets_main-indicators-online.xlsx',
'wgi_2026.xlsx':'https://www.worldbank.org/content/dam/sites/govindicators/doc/wgidataset_with_sourcedata-2026.xlsx',
'koica_qhealth.html':'https://www.koica.go.kr/sites/evaluation_kr/article/view/1265',
'korea_iati.html':'https://www.oda.go.kr/opo/nnstat/opoNstatInfoOthBcIatiList.do',
'oecd_crs_structure.xml':'https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.DCD.FSD/DSD_CRS@DF_CRS/1.5?references=all',
'lowy_methodology.html':'https://pacificaidmap.lowyinstitute.org/methodology/',
'lowy_data.html':'https://pacificaidmap.lowyinstitute.org/data/',
'wb_projects_png.json':'https://search.worldbank.org/api/v2/projects?format=json&countrycode=PG&rows=500',
'wb_projects_vnm.json':'https://search.worldbank.org/api/v2/projects?format=json&countrycode=VN&rows=500',
'pefa.html':'https://www.pefa.org/assessments',
'obs_download.html':'https://internationalbudget.org/open-budget-survey/download',
'jica_vietnam.pdf':'https://www2.jica.go.jp/en/evaluation/pdf/2013_0601704_4_f.pdf',
'dfat_png.html':'https://www.dfat.gov.au/about-us/publications/Pages/medical-supply-reform-impact-evaluation-papua-new-guinea',
}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:out=list(pool.map(fetch,jobs.items()))
(B/'download_manifest_more.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
