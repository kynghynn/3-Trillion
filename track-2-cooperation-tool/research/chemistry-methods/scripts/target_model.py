from pathlib import Path
import json,collections,numpy as np
from scipy.special import expit
from scipy.optimize import minimize
B=Path(__file__).resolve().parents[1];P=B/'processed';A=json.loads((P/'target_actual_candidates.json').read_text());rng=np.random.default_rng(20261106)
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False))
def key(r):return r['indicator']+' | '+r['unit']
def fit(rows,groups,items,projects,lam,pa):
 gi={g:i for i,g in enumerate(groups)};ji={j:i for i,j in enumerate(items)};pi={p:i for i,p in enumerate(projects)}
 X=np.zeros((len(rows),1+len(gi)+len(ji)+len(pi)))
 for i,r in enumerate(rows):X[i,0]=1;X[i,1+gi[r['recipient']]]=1;X[i,1+len(gi)+ji[key(r)]]=1;X[i,1+len(gi)+len(ji)+pi[r['project_id']]]=1
 y=np.array([r['target_attained'] for r in rows]);pen=np.r_[0,np.repeat(lam,len(gi)+len(ji)),np.repeat(pa,len(pi))]
 def obj(v):
  eta=X@v;pr=expit(eta);return float(np.sum(np.logaddexp(0,eta)-y*eta)+.5*np.sum(pen*v*v)),X.T@(pr-y)+pen*v
 res=minimize(obj,np.zeros(X.shape[1]),jac=True,method='L-BFGS-B',options={'maxiter':500,'ftol':1e-11})
 pr=expit(X@res.x);H=X.T@((pr*(1-pr))[:,None]*X)+np.diag(pen);return res, np.linalg.pinv(H),gi,ji,pi
out=[];diagnostics=[];cvrecords=[]
for sector,codes in {'health':{'121','122','123','130'},'water':{'140'},'agriculture':{'311'}}.items():
 rows=[r for r in A if r['eligible_numeric'] and set(r['sector_dac3'])<=codes and set(r['sector_dac3'])]
 # Only common exact indicators/units spanning >=2 recipient countries. No forced equivalence.
 gs=collections.defaultdict(set)
 for r in rows:gs[key(r)].add(r['recipient'])
 items=sorted(j for j,v in gs.items() if len(v)>=2);rows=[r for r in rows if key(r) in items];groups=sorted(set(r['recipient'] for r in rows));projects=sorted(set(r['project_id'] for r in rows))
 # Graph connectedness is required before within-cohort common-basket comparison.
 nodes={('g',g):set() for g in groups};nodes.update({('j',j):set() for j in items})
 for r in rows:nodes[('g',r['recipient'])].add(('j',key(r)));nodes[('j',key(r))].add(('g',r['recipient']))
 seen=set();components=[]
 for n in nodes:
  if n in seen:continue
  visit={n};todo=[n]
  while todo:
   for z in nodes[todo.pop()]-visit:visit.add(z);todo.append(z)
  seen|=visit;components.append(len(visit))
 if len(components)!=1:diagnostics.append({'sector':sector,'status':'disconnected_no_combined_score','components':components});continue
 candidates=[]
 for lam in [.5,2.,8.]:
  for pa in [1.,4.,16.]:
   losses=[]
   for held in projects:
    train=[r for r in rows if r['project_id']!=held];test=[r for r in rows if r['project_id']==held]
    res,cov,gi,ji,pi=fit(train,groups,items,projects,lam,pa)
    # Integrate a held-out project effect from its N(0, 1/pa) prior by fixed Gauss-Hermite quadrature.
    z,w=np.polynomial.hermite.hermgauss(21);z=z*np.sqrt(2/pa);w=w/np.sqrt(np.pi)
    for r in test:
     eta=res.x[0]+res.x[1+gi[r['recipient']]]+res.x[1+len(gi)+ji[key(r)]];prob=float(w@expit(eta+z));y=r['target_attained'];losses.append((y-prob)**2)
   candidates.append({'lambda_country_item':lam,'lambda_project':pa,'brier':float(np.mean(losses)),'n_heldout_rows':len(losses)})
 # Nested leave-project-out evaluation avoids reusing tuning errors as validation.
 outer=[]
 for held in projects:
  train0=[r for r in rows if r['project_id']!=held];test0=[r for r in rows if r['project_id']==held];inner=[]
  for lc in [.5,2.,8.]:
   for lp in [1.,4.,16.]:
    losses=[]
    for h2 in sorted(set(r['project_id'] for r in train0)):
     tr=[r for r in train0 if r['project_id']!=h2];te=[r for r in train0 if r['project_id']==h2];rr,_,gg,jj,pp=fit(tr,groups,items,projects,lc,lp);zz,ww=np.polynomial.hermite.hermgauss(21);zz=zz*np.sqrt(2/lp);ww=ww/np.sqrt(np.pi)
     for r in te:
      eta=rr.x[0]+rr.x[1+gg[r['recipient']]]+rr.x[1+len(gg)+jj[key(r)]];prob=float(ww@expit(eta+zz));losses.append((r['target_attained']-prob)**2)
    inner.append((np.mean(losses),lc,lp))
  _,lc,lp=min(inner);rr,_,gg,jj,pp=fit(train0,groups,items,projects,lc,lp);zz,ww=np.polynomial.hermite.hermgauss(21);zz=zz*np.sqrt(2/lp);ww=ww/np.sqrt(np.pi);baseline=(.5+sum(r['target_attained'] for r in train0))/(1+len(train0))
  for r in test0:
   eta=rr.x[0]+rr.x[1+gg[r['recipient']]]+rr.x[1+len(gg)+jj[key(r)]];prob=float(ww@expit(eta+zz));outer.append({'project_id':held,'y':r['target_attained'],'probability':prob,'squared_error':float((r['target_attained']-prob)**2),'pooled_squared_error':float((r['target_attained']-baseline)**2)})
 cvrecords.append({'sector':sector,'nested_project_holdout':outer,'brier_model':float(np.mean([r['squared_error'] for r in outer])),'brier_pooled':float(np.mean([r['pooled_squared_error'] for r in outer])),'n_projects':len(projects),'caution':'very small selected sample; not external or prospective validation'})
 best=min(candidates,key=lambda z:z['brier']);lam=best['lambda_country_item'];pa=best['lambda_project'];res,cov,gi,ji,pi=fit(rows,groups,items,projects,lam,pa)
 samples=rng.multivariate_normal(res.x,cov,size=4000,check_valid='raise');z,w=np.polynomial.hermite.hermgauss(21);z=z*np.sqrt(2/pa);w=w/np.sqrt(np.pi)
 for g in groups:
  ss=np.zeros(len(samples))
  for j in items:
   eta=samples[:,0]+samples[:,1+gi[g]]+samples[:,1+len(gi)+ji[j]];ss+=(expit(eta[:,None]+z)@w)/len(items)
  rr=[r for r in rows if r['recipient']==g]
  out.append({'provider':'FRA','agency':'AFD','recipient':g,'sector':sector,'n_independent_activity_candidates':len(set(r['project_id'] for r in rr)),'n_target_records':len(rr),'common_basket_indicator_count':len(items),'target_attainment_common_basket_score':float(np.mean(ss)*100),'conditional_laplace_95':(np.quantile(ss,[.025,.975])*100).tolist(),'raw_attainment_share':float(np.mean([r['target_attained'] for r in rr])),'source_output_type':'IATI type 1 outputs, not impact','human_rating_used':False,'interpretation':'model-standardized attainment of agency targets for shared output indicators; not bilateral causal chemistry or cross-agency comparable','status':'research_pilot_not_validated_for_public_ranking','uncertainty':'conditional on CV-selected penalties and normal approximation; ignores target difficulty gaming, source errors, selection bias and model selection uncertainty'})
 diagnostics.append({'sector':sector,'rows':len(rows),'countries':groups,'projects':len(projects),'common_indicator_units':items,'connected':True,'optimizer_success':bool(res.success),'selected_penalty':best,'validation_type':'LOPO tuning only; not an unbiased nested validation estimate','penalty_grid':candidates})
save('target_nested_validation.json',cvrecords);save('target_standardized_scores.json',out);save('target_model_diagnostics.json',diagnostics);print(json.dumps([{k:v for k,v in r.items() if k not in ['penalty_grid','common_indicator_units']} for r in diagnostics],indent=2))
