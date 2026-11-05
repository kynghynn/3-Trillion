from pathlib import Path
import json,openpyxl,datetime,re,collections
B=Path(__file__).resolve().parents[1];R=B/'raw';P=B/'processed'
def dump(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str,allow_nan=False))
def table(s):
 rows=list(s.values); h=[str(v) if v is not None else 'unnamed_'+str(i) for i,v in enumerate(rows[0])]
 return [dict(zip(h,[None if v=='' else v for v in r])) for r in rows[1:] if any(v is not None for v in r)]
w=openpyxl.load_workbook(R/'gpedc_global_2026.xlsx',read_only=True,data_only=True)
for sn in ['Core Results','Core Results PC_DP','Core Results DP','Projects Data','PC Data','DP Data','Untied aid','Global Transparency','Dictionary Variables']:
 rows=table(w[sn]);dump('gpedc_'+sn.lower().replace(' ','_')+'.json',rows)
 print(sn,len(rows))
 if sn=='Core Results PC_DP':
  dump('gpedc_korea_pairs.json',[r for r in rows if r.get('provider')=='Korea'])
  print('Korea recent partners',[(r['recipient'],r['year']) for r in rows if r.get('provider')=='Korea' and r.get('year',0)>=2023])
dump('gpedc_interpretation_cells.json',[list(r) for r in w['Results interpretation'].values])
q=openpyxl.load_workbook(R/'quoda_2021.xlsx',read_only=True,data_only=True)
dump('quoda_workbook_cells.json',{s.title:[list(r) for r in s.values] for s in q})
w=openpyxl.load_workbook(R/'wgi_2026.xlsx',read_only=True,data_only=True)
a=[]
for sn in ['ge','cc','va','pv','rq','rl']:
 for r in list(w[sn].values)[1:]:
  if isinstance(r[5],(int,float)) and r[5]>=2015:a.append({'iso3':r[2],'country':r[1],'year':r[5],'dimension':sn,'score':r[12],'lower90':r[14],'upper90':r[15],'sources':r[7],'source_file':'raw/wgi_2026.xlsx','sheet':sn})
dump('wgi_2015_2025.json',a)
cs=json.loads((R/'wb_countries.json').read_text())[1];cs=[r for r in cs if r['region']['id']!='NA'];dump('countries.json',cs);ids={r['id'] for r in cs}
obs=[]
for p in R.glob('wb_*.json'):
 try:x=json.loads(p.read_text())
 except:continue
 if not isinstance(x,list) or len(x)<2 or not isinstance(x[1],list):continue
 for r in x[1]:
  if not isinstance(r,dict) or 'indicator' not in r or r.get('countryiso3code') not in ids:continue
  if r.get('value') is not None:obs.append({'iso3':r['countryiso3code'],'indicator':r['indicator']['id'],'name':r['indicator']['value'],'year':int(r['date']),'value':r['value'],'unit':r.get('unit'),'source_file':'raw/'+p.name})
dump('world_bank_observations.json',obs)
latest={}
for r in obs:
 key=(r['iso3'],r['indicator'])
 if key not in latest or latest[key]['year']<r['year']:latest[key]=r
dump('world_bank_latest.json',list(latest.values()))
dump('demo_country_context.json',[r for r in latest.values() if r['iso3'] in ['KOR','VNM','PNG','JPN','AUS','LAO','KHM','IDN','PHL','SLB','TLS']])
# Copy source text for evidence coding, preserving PDF page positions.
from pypdf import PdfReader
for p in R.glob('*.pdf'):
 try:
  pdf=PdfReader(p);t='\n\n'.join('=== PDF PAGE '+str(i+1)+' ===\n'+(pg.extract_text() or '') for i,pg in enumerate(pdf.pages));(P/(p.stem+'_text.txt')).write_text(t)
 except Exception as e: print('PDF error',p.name,str(e)[:100])
print('context observations',len(obs),'countries',len(cs),'wgi',len(a))
