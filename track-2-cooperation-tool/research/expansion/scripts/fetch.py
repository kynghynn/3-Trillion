from pathlib import Path
import subprocess,json,hashlib,concurrent.futures,datetime
B=Path(__file__).resolve().parents[1]
def fetch(job):
 name,url=job;p=B/'raw'/name;tmp=p.with_suffix(p.suffix+'.part')
 r=subprocess.run(['curl','--http1.1','-L','--fail','--max-time','90','--connect-timeout','15','-A','Mozilla/5.0','-sS',url,'-o',str(tmp)],capture_output=True)
 rec={'file':'raw/'+name,'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'failed'}
 if r.returncode==0:
  tmp.replace(p);rec.update(status='downloaded',bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 else:rec['error']=r.stderr.decode()[:400];tmp.unlink(missing_ok=True)
 print(name,rec['status'],rec.get('bytes',0),flush=True);return rec
if __name__=='__main__':
 import sys
 jobs=json.loads(Path(sys.argv[1]).read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:out=list(ex.map(fetch,jobs.items()))
 (B/(Path(sys.argv[1]).stem+'_manifest.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2))
