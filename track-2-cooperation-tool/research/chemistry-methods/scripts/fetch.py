from pathlib import Path
import subprocess,json,hashlib,concurrent.futures,datetime,re
B=Path(__file__).resolve().parents[1]
def get(job):
 n,u=job;p=B/'raw'/n
 r=subprocess.run(['curl','-L','--fail','--max-time','45','--connect-timeout','12','-sS',u,'-o',str(p)],capture_output=True)
 z={'file':n,'url':u,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':r.returncode==0,'error':r.stderr.decode()[:180]}
 if p.exists():z.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 return z
if __name__=='__main__':
 import sys
 jobs=json.loads(Path(sys.argv[1]).read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as e:out=list(e.map(get,jobs.items()))
 (B/(Path(sys.argv[1]).stem+'_manifest.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
