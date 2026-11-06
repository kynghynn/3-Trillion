from pathlib import Path
import json,collections,numpy as np
B=Path(__file__).resolve().parents[1];P=B/'processed';rng=np.random.default_rng(20261106)
def load(n):return json.loads((P/n).read_text())
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False))
# Bootstrap paired validation errors at the provider-recipient cluster level, preserving dependence across projects.
projects={r['project_id']:r for r in load('process_projects.json')};out=[];a=load('process_heldout_predictions.json')
for component in ['ownership','results_alignment','government_data']:
 rows=[r for r in a if r['component']==component];lookup={(r['project_id'],r['model']):r for r in rows}
 for other in ['pooled_project_mean','pair_smoothed_project_mean']:
  vals=collections.defaultdict(list)
  for r in rows:
   if r['model']!='hierarchical_bb':continue
   z=lookup.get((r['project_id'],other))
   if z:
    p=projects[r['project_id']];vals[(p['provider'],p['recipient'])].append(r['squared_error']-z['squared_error'])
  sums=np.array([sum(v) for v in vals.values()]);ns=np.array([len(v) for v in vals.values()]);idx=rng.integers(0,len(sums),size=(2000,len(sums)));boot=sums[idx].sum(axis=1)/ns[idx].sum(axis=1)
  out.append({'component':component,'comparison':'hierarchical_bb minus '+other,'n_clusters':len(vals),'mse_difference':float(sums.sum()/ns.sum()),'cluster_bootstrap_95':np.quantile(boot,[.025,.975]).tolist(),'negative_favors_hierarchical':True,'conditional_on_fitted_CV_models':True})
save('process_cv_comparisons.json',out)
# The sector result pilot is not approved for ranking if nested validation does not beat the pooled comparator.
v=load('target_nested_validation.json');gate=[]
for r in v:gate.append({'sector':r['sector'],'model_brier':r['brier_model'],'pooled_brier':r['brier_pooled'],'passes_pooled_baseline':r['brier_model']<r['brier_pooled'],'public_ranking_enabled':False,'reason':'small sample and no nested predictive gain over pooled baseline' if r['brier_model']>=r['brier_pooled'] else 'small sample; external validation still needed'})
save('model_adoption_decisions.json',{'process':'research-use provisional estimation of planning/results/data alignment only; no full sector or causal success claim','outcome':gate,'human_scoring':'no investigator judgement scores or source ordinal ratings used in fitted models','universal_source_linking':'not identified without shared projects/items and construct invariance; no global universal score emitted'})
# Identity, source and scoring invariants.
s=load('process_scores.json');t=load('target_standardized_scores.json');assert len(s)==253 and len(t)==19
assert all(r['process_chemistry'] is None or 0<=r['process_chemistry']<=100 for r in s)
assert all(0<=r['target_attainment_common_basket_score']<=100 and r['conditional_laplace_95'][0]<=r['target_attainment_common_basket_score']<=r['conditional_laplace_95'][1] for r in t)
assert all(not r['human_rating_used'] for r in s+t)
assert not any(r['sector'].startswith('health') for r in s)
# Compare analytically computed n=1 Bernoulli marginal against stable binomial PMF identities.
from scipy.special import expit,gammaln,betaln
for p in [.01,.3,.8,.99]:
 for kappa in [.1,1,10]:
  got=np.exp(betaln(1+kappa*p,kappa*(1-p))-betaln(kappa*p,kappa*(1-p)));assert abs(got-p)<1e-10
# 81 and 121-node fits must agree sufficiently for final reported parameters.
for c,r in load('process_hyperparameters.json').items():assert abs(r['nll']-r['q121_parameters']['nll'])<.01
save('validation.json',{'process_pairs':len(s),'complete_process_scores':sum(r['process_chemistry'] is not None for r in s),'target_pilot_scores':len(t),'target_public_scores':0,'probability_and_interval_bounds':'passed','no_human_rating_inputs':'passed','binary_beta_binomial_identity':'passed','quadrature_convergence':'passed','sector_scope_not_fabricated':'passed','validation_is_not_external_causal_validation':True})
print(json.dumps(out,indent=2));print('all checks passed')
