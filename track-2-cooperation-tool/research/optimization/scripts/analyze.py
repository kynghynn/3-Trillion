from pathlib import Path
import json,math,collections,numpy as np
B=Path(__file__).resolve().parents[1];O=B.parent/'track2_research_20261104';O=O if O.exists() else B.parent;P=B/'processed';rng=np.random.default_rng(20261105)
def load(n):return json.loads((O/'processed'/n).read_text())
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
models=load('methodology_config.json')['models'];rows=[];audits=[];recoveries=[];summaries={};corrs=[]
subs={'D1_1_comp':['D1_1_1','D1_1_2','D1_1_3'],'D4_1_comp':['D4_1_1','D4_1_2','D4_1_3'],'D3_1_1':['D3_1_A1','D3_1_A2','D3_1_A3','D3_1_A4']}
def valid(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def rank(v):
 v=np.asarray(v);return np.array([np.sum(v<x)+(np.sum(v==x)+1)/2 for x in v])
def rho(a,b):
 if len(a)<3 or np.std(a)==0 or np.std(b)==0:return None
 return float(np.corrcoef(rank(a),rank(b))[0,1])
def grade(s):return ['D-','D0','D+','C-','C0','C+','B-','B0','B+','A-','A0','A+'][min(11,int(s*12/100))]
w=[]
while len(w)<10000:
 z=rng.dirichlet(np.ones(4),size=50000);w.extend(z[((z>=.15)&(z<=.35)).all(axis=1)].tolist())
w=np.array(w[:10000]);save('weight_scenarios.json',{'seed':20261105,'n':10000,'sampling':'Dirichlet(1,1,1,1) conditional on each weight in [0.15,0.35]','weights':w.tolist()})
for role,fn in [('recipient','gpedc_core_results.json'),('donor','gpedc_core_results_dp.json')]:
 source=[r for r in load(fn) if r.get('year')==2026 and (role!='donor' or r.get('Bilateral')==1)]
 keys=sum(list(models[role].values()),[]); matrices=[];rr=[]
 for r in source:
  name=r.get('recipient',r.get('provider')); values={};intervals={};flags=[]
  for k in keys:
   v=r.get(k); v=(v/5 if k=='D2_6_1' else v) if valid(v) else None
   
   if v is not None and (v<0 or v>1):
    if -1e-6<=v<=1+1e-6:
     recoveries.append({'country':name,'indicator':k,'raw_value':v,'value':min(1,max(0,v)),'method':'floating-point tolerance 1e-6; boundary clipping only'});v=min(1,max(0,v))
    else:v=None
   values[k]=v; intervals[k]=[v,v] if v is not None else [0,1]
   if role=='recipient' and k in subs:
    ss=[r.get(c) for c in subs[k]]; known=[v for v in ss if valid(v)];missing=len(ss)-len(known)
    if missing:
     intervals[k]=[sum(known)/len(ss),(sum(known)+missing)/len(ss)]
     flags.append({'indicator':k,'missing_components':missing,'total_components':len(ss),'published_value':v,'component_values':dict(zip(subs[k],ss))})
    elif v is None:
     v=sum(known)/len(ss);values[k]=v;intervals[k]=[v,v];recoveries.append({'country':name,'indicator':k,'value':v,'method':'same-source exact component mean'})
  dims={d:(float(np.mean([values[k] for k in kk]))*100 if all(values[k] is not None for k in kk) else None) for d,kk in models[role].items()}
  bounds=[sum(np.mean([intervals[k][side] for k in kk])*25 for kk in models[role].values()) for side in [0,1]]
  complete=all(v is not None for v in dims.values());score=float(np.mean(list(dims.values()))) if complete else None
  row={'country':name,'role':role,'round':2026,'dimensions':dims,'published_inputs':values,'published_score':score,'published_grade':grade(score) if complete else None,'missing_component_flags':flags,'missingness_bounds':bounds,'v03_status':'complete_inputs_provisional' if complete and not flags else 'partially_identified','v03_point_score':score if complete and not flags else None,'bounds_same_grade':grade(bounds[0])==grade(bounds[1])}
  if complete:
   x=np.array(list(dims.values()));s=w@x
   row.update(weight_scenario_p05_p95=np.quantile(s,[.05,.95]).tolist(),same_grade_fraction=float(np.mean([grade(v)==grade(score) for v in s])),possible_grades=sorted(set(grade(v) for v in s)),geometric_score=float(np.prod(x)**.25),leave_one_pillar_out_range=[float(min((x.sum()-v)/3 for v in x)),float(max((x.sum()-v)/3 for v in x))])
   matrices.append(x);rr.append(row)
  rows.append(row)
 for k in keys:audits.append({'role':role,'indicator':k,'n':len(source),'missing':sum(not valid(r.get(k)) for r in source),'zero':sum(r.get(k)==0 for r in source)})
 # Pairwise correlations with actual per-pair n, not imputed population.
 for i,k in enumerate(keys):
  for l in keys[i+1:]:
   pairs=[(r.get(k),r.get(l)) for r in source if valid(r.get(k)) and valid(r.get(l))]
   corrs.append({'role':role,'a':k,'b':l,'n':len(pairs),'spearman':rho([p[0] for p in pairs],[p[1] for p in pairs])})
 X=np.array(matrices);base=X.mean(axis=1);geo=np.prod(X,axis=1)**.25
 # PCA variance diagnostic only; not proposed normative weights.
 sd=X.std(axis=0);Z=(X-X.mean(axis=0))/np.where(sd==0,1,sd);eig=np.linalg.eigvalsh(np.cov(Z.T))[::-1]
 rankcorr=[rho(base,X@v) for v in w[::10]]
 summaries[role]={'n_total':len(source),'complete_published':len(rr),'complete_without_hidden_missing':sum(r['v03_point_score'] is not None for r in rows if r['role']==role),'hidden_missing_countries':sum(bool(r['missing_component_flags']) for r in rows if r['role']==role),'median_same_grade_fraction':float(np.median([r['same_grade_fraction'] for r in rr])),'countries_grade_stability_below_80pct':sum(r['same_grade_fraction']<.8 for r in rr),'weight_rank_correlation_p05_p95':np.quantile(rankcorr,[.05,.95]).tolist(),'arithmetic_geometric_rank_rho':rho(base,geo),'arithmetic_geometric_grade_changes':sum(grade(x)!=grade(y) for x,y in zip(base,geo)),'pca_first_component_explained':float(eig[0]/sum(eig))}

pc=load('gpedc_pc_data.json');dp=load('gpedc_dp_data.json')
for x in rows:
 source_periods=pc if x['role']=='recipient' else dp;identity_key='recipient' if x['role']=='recipient' else 'provider'
 x['observed_periods']=sorted({v['reporting_year'] for v in source_periods if v.get(identity_key)==x['country'] and v.get('year')==2026 and v.get('reporting_year')})
save('country_scores_v03.json',rows);save('country_missingness.json',audits);save('exact_recoveries.json',recoveries);save('indicator_correlations.json',corrs);save('country_robustness_summary.json',summaries)
# Actual repeated investment observations; no pooling across donors, countries, years or raters.
h=json.loads((O/'expansion/processed/australia_health_rating_observations.json').read_text());h=[r for r in h if r['criterion']=='Effectiveness'];out=[]
for rec in sorted(set(r['recipient'] for r in h)):
 rows1=[r for r in h if r['recipient']==rec];latest=max(r['period_end'] for r in rows1);cur={r['activity_id']:r for r in rows1 if r['period_end']==latest};n=len(cur);s=sum(r['satisfactory'] for r in cur.values());ph=s/n;z=1.959963984540054;den=1+z*z/n;center=(ph+z*z/(2*n))/den;half=z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/den
 out.append({'donor':'AUS','recipient':rec,'period_end':latest,'candidate_activity_ids':list(cur),'independence_verified':False,'n':n,'satisfactory':s,'share':ph,'wilson_95':[center-half,center+half],'interval_width':2*half,'publication':'show descriptive counts, do not rank when intervals overlap','interval_assumption':'binomial independent activity outcomes; does not cover selection bias, reporting error or program clustering','chemistry_score':None,'repeated_observations_removed':len(rows1)-n})
save('chemistry_evidence_uncertainty.json',out)
# Masking experiment assesses numerical imputation error, not validity under real MNAR missingness.
exper=[]
for role in models:
 full=[r for r in rows if r['role']==role and r['v03_point_score'] is not None];X=np.array([list(r['dimensions'].values()) for r in full]);errors=[];gradechanges=[]
 for i,x in enumerate(X):
  for j in range(4):
   pred=x.copy();pred[j]=np.median(np.delete(X,i,axis=0)[:,j]);errors.append(float(abs(pred.mean()-x.mean())));gradechanges.append(grade(pred.mean())!=grade(x.mean()))
 exper.append({'role':role,'n_countries':len(X),'masked_cases':len(errors),'method':'leave-one-country-out pillar median, one pillar masked at a time','mae_score':float(np.mean(errors)),'p95_absolute_error':float(np.quantile(errors,.95)),'grade_change_fraction':float(np.mean(gradechanges)),'decision':'diagnostic only; do not deploy imputation; real missingness may be nonrandom'})
save('imputation_masking_experiment.json',exper)
print(json.dumps(summaries,ensure_ascii=False,indent=2));print('exactrecoveries',len(recoveries));print(json.dumps(exper,indent=2));print('highcorr',[(r['role'],r['a'],r['b'],round(r['spearman'],3)) for r in corrs if r['spearman'] is not None and abs(r['spearman'])>.8])
