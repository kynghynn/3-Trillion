from collect import *
from urllib.parse import urlencode
out=[]
u='https://webfs-dcd.oecd.org/files/dotStat/DSD_CRS/CRS-reduced.parquet'
try:
 req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
 with urllib.request.urlopen(req,timeout=60) as r:
  p=R/'crs_reduced.parquet'; n=0
  with p.open('wb') as f:
   while True:
    b=r.read(1024*1024)
    if not b:break
    f.write(b);n+=len(b)
  out.append({'url':u,'file':'raw/crs_reduced.parquet','bytes':n,'status':'downloaded','sha256':hashlib.sha256(p.read_bytes()).hexdigest()});print('CRS',n,flush=True)
except Exception as e:out.append({'url':u,'status':'failed','error':str(e)});print(e,flush=True)
u='https://www.oda.go.kr/opo/nnstat/filedownload.do'
try:
 data=urlencode({'P_INDX_NO':'403','P_DOWN_FILE':'KR-GOV-051_KOICA IATI ACT_Report_FINAL_251118.xml','OPEN_POPUP_ID':'activ_403'}).encode()
 req=urllib.request.Request(u,data=data,headers={'Referer':jobs.get('korea_iati.html','https://www.oda.go.kr/'),'User-Agent':'Mozilla/5.0'})
 with urllib.request.urlopen(req,timeout=60) as r:b=r.read()
 (R/'koica_iati_2025.xml').write_bytes(b);out.append({'url':u,'file':'raw/koica_iati_2025.xml','bytes':len(b),'status':'downloaded','sha256':hashlib.sha256(b).hexdigest()});print('IATI',len(b),b[:70],flush=True)
except Exception as e:out.append({'url':u,'status':'failed','error':str(e)});print(e,flush=True)
(B/'download_manifest_crs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
