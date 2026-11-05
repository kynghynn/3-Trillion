from collect import *
jobs={
'koica_qhealth.pdf':'https://www.koica.go.kr/sites/evaluation_kr/common/filedownload/1927',
'dfat_png_evaluation.pdf':'https://www.dfat.gov.au/sites/default/files/png-burnet-institute-medical-supply-evaluation.pdf',
'obs_2025.xlsx':'https://internationalbudget.org/sites/default/files/2026-09/IBP_OBS2025_Global_Data_Launch.xlsx',
'korea_iati_script.js':'https://www.oda.go.kr/opo/statics/js/views/nnstat/opoNstatInfoOthBcList.js',
'oecd_crs_flow.xml':'https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.DCD.FSD/DSD_CRS@DF_CRS/?references=none',
'cdi_method.pdf':'https://www.cgdev.org/sites/default/files/cdi-2025-methodology.pdf',
'pefa_guidance.html':'https://www.pefa.org/node/5592',
'iati_api_docs.html':'https://docs.datastore.iatistandard.org/en/latest/api/',
'lowy_methodology.html':'https://pacificaidmap.lowyinstitute.org/methodology/',
}
for code in ['SH_UHC_SCI','SH_UHC_SCI_CAPACITY']:
 jobs['wb_'+code+'.json']='https://api.worldbank.org/v2/country/all/indicator/'+code+'?format=json&per_page=20000&date=2015:2025'
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:out=list(pool.map(fetch,jobs.items()))
(B/'download_manifest_final.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
