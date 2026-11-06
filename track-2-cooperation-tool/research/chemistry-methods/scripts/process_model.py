from pathlib import Path
import json,math,collections,numpy as np
from scipy.special import expit,logsumexp,gammaln,betaln,logit
from scipy.optimize import minimize
from numpy.polynomial.hermite import hermgauss
B=Path(__file__).resolve().parents[1];P=B/'processed';A=json.loads((P/'process_projects.json').read_text());C=['ownership','results_alignment','government_data'];rng=np.random.default_rng(20261106)
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False))
def pair(r):return (r['provider'],r['recipient'])
def packed(rows,c):
 r=sorted([x for x in rows if x['components'][c]['k'] is not None],key=pair);groups=list(dict.fromkeys(pair(x) for x in r));gmap={g:i for i,g in enumerate(groups)}
 return {'rows':r,'groups':groups,'k':np.array([x['components'][c]['k'] for x in r],float),'n':np.array([x['components'][c]['n'] for x in r],float),'g':np.array([gmap[pair(x)] for x in r])}
def ll(k,n,theta,kappa=None):
 # Output shape observations x grid points; all binomial constants retained.
 mu=np.clip(expit(theta),1e-12,1-1e-12);k=np.asarray(k)[:,None];n=np.asarray(n)[:,None];const=gammaln(n+1)-gammaln(k+1)-gammaln(n-k+1)
 if kappa is None:return const-k*np.logaddexp(0.,-theta)-(n-k)*np.logaddexp(0.,theta)
 aa=mu*kappa;bb=(1-mu)*kappa
 return const+betaln(k+aa,n-k+bb)-betaln(aa,bb)
def fit(rows,c,mode='bb',q=81):
 data=packed(rows,c);bb=c!='ownership' and mode=='bb';z,w=hermgauss(q);z=np.sqrt(2)*z;lw=np.log(w)-.5*np.log(np.pi)
 def objective(par):
  m=par[0];tau=np.exp(par[1]) if mode!='pooled' else 0;kap=np.exp(par[-1]) if bb else None
  th=m+tau*z;L=ll(data['k'],data['n'],th,kap);S=np.zeros((len(data['groups']),q));np.add.at(S,data['g'],L)
  return -float(np.sum(logsumexp(S+lw,axis=1)))
 avg=np.mean(data['k']/data['n']);initial=[float(logit(np.clip(avg,.001,.999))),0]+([0.] if bb else []);bounds=[(-7,7),(-3,2)]+([(-4,6)] if bb else [])
 if mode=='pooled':initial[1]=-3;bounds[1]=(-3,-3)
 fits=[minimize(objective,initial,method='L-BFGS-B',bounds=bounds,options={'maxiter':250,'ftol':1e-10})]
 initial2=initial.copy();initial2[1]=.7
 if mode!='pooled':fits.append(minimize(objective,initial2,method='L-BFGS-B',bounds=bounds,options={'maxiter':250,'ftol':1e-10}))
 opt=min(fits,key=lambda r:r.fun);m=float(opt.x[0]);tau=float(np.exp(opt.x[1])) if mode!='pooled' else 0.;kap=float(np.exp(opt.x[-1])) if bb else None
 return {'m':m,'tau':tau,'kappa':kap,'nll':float(opt.fun),'optimizer_success':bool(opt.success),'message':str(opt.message),'q':q,'mode':mode,'data':data,'parameter_at_bound':any(abs(v-a)<1e-4 or abs(v-b)<1e-4 for v,(a,b) in zip(opt.x,bounds) if a!=b)}
def posterior(fit,rows,c,tau_factor=1.):
 theta=np.linspace(-15,15,2001);tau=max(fit['tau']*tau_factor,.01);lp=-.5*((theta-fit['m'])/tau)**2
 if rows:
  L=ll([r['components'][c]['k'] for r in rows],[r['components'][c]['n'] for r in rows],theta,fit['kappa']);lp+=L.sum(axis=0)
 w=np.exp(lp-logsumexp(lp));mu=expit(theta);cum=np.cumsum(w)
 def quant(q):return float(np.interp(q,cum,mu))
 return {'mean':float(w@mu),'interval_95':[quant(.025),quant(.975)],'bonferroni_component_interval':[quant(.05/6),quant(1-.05/6)],'conditional_variance':float(w@((mu-w@mu)**2))}
fits={};diag={};pred={};allgroups=sorted(set(pair(r) for r in A));groups={g:[r for r in A if pair(r)==g] for g in allgroups}
for c in C:
 f=fit(A,c);fits[c]=f;diag[c]={k:v for k,v in f.items() if k!='data'};diag[c]['rho_within_project']=1/(1+f['kappa']) if f['kappa'] else None
 # Numerical integration check at final parameters using doubled quadrature.
 f2=fit(A,c,q=121);diag[c]['q121_parameters']={k:v for k,v in f2.items() if k!='data'}
 print('fit',c,{k:v for k,v in diag[c].items() if k!='q121_parameters'},flush=True)
 for g,rs in groups.items():
  rr=[r for r in rs if r['components'][c]['k'] is not None];pred[(g,c)]=posterior(f,rr,c) if rr else None
# Hold out entire interventions, simultaneously across components. Singleton pairs are excluded from validation.
folds={}
for g,rs in groups.items():
 if len(rs)<2:continue
 inds=rng.permutation(len(rs))
 for pos,i in enumerate(inds):folds[rs[i]['project_id']]=pos%5
scores=[];fold_models=[]
for fold in range(5):
 train=[r for r in A if folds.get(r['project_id'])!=fold];test=[r for r in A if folds.get(r['project_id'])==fold]
 for c in C:
  for mode in ['bb','binomial'] if c!='ownership' else ['bb']:
   f=fit(train,c,mode=mode,q=61);lookup=collections.defaultdict(list)
   for r in train:
    if r['components'][c]['k'] is not None:lookup[pair(r)].append(r)
   pool=float(np.mean([r['components'][c]['k']/r['components'][c]['n'] for r in train if r['components'][c]['k'] is not None]));post={}
   for r in test:
    x=r['components'][c]
    if x['k'] is None:continue
    g=pair(r)
    if g not in post:post[g]=posterior(f,lookup[g],c)['mean']
    actual=x['k']/x['n'];no_pool=(.5+sum(z['components'][c]['k']/z['components'][c]['n'] for z in lookup[g]))/(1+len(lookup[g]));p=post[g]
    for model,prob in [('hierarchical_'+mode,p),('pooled_project_mean',pool),('pair_smoothed_project_mean',no_pool)]:
     if mode=='binomial' and model!='hierarchical_binomial':continue
     scores.append({'project_id':r['project_id'],'component':c,'fold':fold,'model':model,'actual_fraction':actual,'predicted_fraction':prob,'squared_error':float((actual-prob)**2)})
 print('validated fold',fold,flush=True)
metrics=[]
for c in C:
 for model in sorted(set(r['model'] for r in scores)):
  ss=[r for r in scores if r['component']==c and r['model']==model]
  if ss:metrics.append({'component':c,'model':model,'n':len(ss),'mean_squared_error':float(np.mean([r['squared_error'] for r in ss])),'mae':float(np.mean([abs(r['actual_fraction']-r['predicted_fraction']) for r in ss]))})
out=[]
for g,rs in groups.items():
 comps={c:pred[(g,c)] for c in C};complete=all(comps[c] is not None for c in C);known=sum(comps[c]['mean'] for c in C if comps[c] is not None)
 row={'provider':g[0],'recipient':g[1],'sector':'all_sectors_survey_sample','n_projects':len(rs),'reporting_periods':sorted(set(r['reporting_period'] for r in rs)),'components':{},'process_chemistry':100*known/3 if complete else None,'missing_component_bounds':[100*known/3,100*(known+sum(comps[c] is None for c in C))/3],'score_construct':'country-owned planning/results/data alignment; not outcome, sustainability, causal synergy or success probability','status':'model_estimate_provisional' if complete else 'incomplete_no_total','human_rating_used':False,'source_self_reported':True}
 for c in C:
  rr=[r for r in rs if r['components'][c]['k'] is not None]
  row['components'][c]={'n_projects':len(rr),'raw_project_mean':float(np.mean([r['components'][c]['k']/r['components'][c]['n'] for r in rr])) if rr else None,'posterior':comps[c]}
 if complete:
  row['conditional_95_union_bound']=[100*sum(comps[c]['bonferroni_component_interval'][i] for c in C)/3 for i in [0,1]]
  row['tau_half_double_sensitivity']=[100*sum(posterior(fits[c],[r for r in rs if r['components'][c]['k'] is not None],c,f)['mean'] for c in C)/3 for f in [.5,2.]]
 out.append(row)
save('process_hyperparameters.json',diag);save('process_scores.json',out);save('process_cross_validation.json',metrics);save('process_heldout_predictions.json',scores)
save('process_model_summary.json',{'n_projects':len(A),'n_pairs':len(out),'n_complete_score_pairs':sum(r['process_chemistry'] is not None for r in out),'n_validation_pairs':len(set(pair(r) for r in A if r['project_id'] in folds)),'validation_design':'5-fold entire-project holdout within pairs with >=2 projects; singleton pairs not validated; no prospective or causal validation','score_interval':'Bonferroni union bounds of marginal component posteriors conditional on fitted empirical-Bayes hyperparameters; excludes hyperparameter uncertainty, selection bias and reporting errors','all_optimizers_success':all(f['optimizer_success'] for f in fits.values()),'large_point_shifts_over_10':int(sum(abs(r['process_chemistry']-100*np.mean([r['components'][c]['raw_project_mean'] for c in C]))>10 for r in out if r['process_chemistry'] is not None))})
print(json.dumps(metrics,indent=2),flush=True);print((P/'process_model_summary.json').read_text(),flush=True)
