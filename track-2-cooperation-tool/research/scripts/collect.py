import json,urllib.request,concurrent.futures,hashlib,datetime
from pathlib import Path
B=Path(__file__).resolve().parents[1]; R=B/'raw'
jobs={
'quoda_2021.xlsx':'https://www.cgdev.org/sites/default/files/quoda-2021-results.xlsx',
'quoda_method.pdf':'https://www.cgdev.org/sites/default/files/QuODA-2021-methodology-paper.pdf',
'gpedc_archive.html':'https://www.effectivecooperation.org/content/gpedc-monitoring-excel-database',
'gpedc_2026.html':'https://www.effectivecooperation.org/resources/progressreport2026',
'gpedc_guide.pdf':'https://www.effectivecooperation.org/system/files/2024-02/Main%20Guide%20%28ENG%29.pdf',
'ati_2024.xlsx':'https://www.publishwhatyoufund.org/download/index-results-data/',
'obs_download.html':'https://internationalbudget.org/open-budget-survey/download',
'koica_qhealth.html':'https://koica.go.kr/sites/evaluation_kr/article/view/1265',
'dfat_png.html':'https://www.dfat.gov.au/about-us/publications/Pages/medical-supply-reform-impact-evaluation-papua-new-guinea',
'jica_vietnam.pdf':'https://www2.jica.go.jp/en/evaluation/pdf/2013_0601704_4_f.pdf',
'png_health_plan.pdf':'https://health.gov.pg/pdf/NHP_2A.pdf',
'who_png_2026.html':'https://www.who.int/papuanewguinea/news/detail/29-07-2026-strengthening-papua-new-guinea-s-medical-supply-system',
'aiddata_ltl_2025.pdf':'https://docs.aiddata.org/reports/ltl-2025/Listening_to_Leaders_2025.pdf',
'oecd_composite.pdf':'https://www.oecd.org/content/dam/oecd/en/publications/reports/2008/08/handbook-on-constructing-composite-indicators-methodology-and-user-guide_g1gh9301/9789264043466-en.pdf',
'oecd_evaluation.pdf':'https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/03/applying-evaluation-criteria-thoughtfully_45a54ea7/543e84ed-en.pdf',
'wb_countries.json':'https://api.worldbank.org/v2/country?format=json&per_page=400',
'wb_indicators.json':'https://api.worldbank.org/v2/indicator?format=json&per_page=30000',
'wgi_home.html':'https://www.worldbank.org/en/publication/worldwide-governance-indicators',
'spi_home.html':'https://www.worldbank.org/en/programs/statistical-performance-indicators/explore-data',
}
for code in ['GE.EST','CC.EST','VA.EST','IQ.SPI.OVRL','IQ.CPA.PUBS.XQ','SH.UHC.SRVS.CV.XD','SH.UHC.SRVS.CV','SH.DYN.MORT','SH.XPD.OOPC.CH.ZS','SP.RUR.TOTL.ZS','NY.GNP.PCAP.CD','SP.POP.TOTL','SH.MED.PHYS.ZS']:
 jobs['wb_'+code+'.json']='https://api.worldbank.org/v2/country/all/indicator/'+code+'?format=json&per_page=20000&date=2015:2025'
def fetch(kv):
 name,url=kv; rec={'file':'raw/'+name,'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 Research data collection'})
  with urllib.request.urlopen(req,timeout=50) as r: b=r.read(); rec.update(http_status=r.status,content_type=r.headers.get('Content-Type'),final_url=r.url)
  (R/name).write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),status='downloaded')
  if name.endswith('.json'):
   x=json.loads(b)
   if isinstance(x,list) and x and isinstance(x[0],dict) and 'message' in x[0]:rec.update(status='api_error',error=x)
 except Exception as e:rec.update(status='failed',error=str(e))
 print(name,rec['status'],rec.get('bytes',0),flush=True);return rec
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: out=list(pool.map(fetch,jobs.items()))
 (B/'download_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
