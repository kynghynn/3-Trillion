from pathlib import Path
import json, re, hashlib, collections, gzip
import openpyxl
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]; P=R/'processed'
def load(n): return json.loads((P/n).read_text())
def dump(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
ps={x['id']:x for x in load('projects.json')}; obs=load('objective_observations.json'); edges=load('explicit_project_links.json'); anchors=load('common_indicator_candidates.json')
# Keep workbook row coordinates and raw fields rather than inferred code definitions.
w=openpyxl.load_workbook(R/'raw/nlmfa_indicator_codes.xlsx',data_only=True)
codebook=[]
for rowno,row in enumerate(w.worksheets[1].values,1):
    if rowno>2 and row[3]:
        codebook.append(dict(zip(['theme','framework_reference','definition','code','disaggregation','reporting_basis','methodological_notes','bhos_indicator'],row[:8]))|{'source_sheet':w.worksheets[1].title,'source_row':rowno})
disaggregates=[{'row':i,'values':list(r)} for i,r in enumerate(w.worksheets[2].values,1) if any(x is not None for x in r)]
dump('nlmfa_indicator_dictionary.json',{'source':'https://helpdesk-opendata-minbuza.nl/indicator-codelist/','version_date':'2023-07-06','indicators':codebook,'disaggregation_rows':disaggregates})

def scalar(v):
    if v is None:return {'raw':v,'numeric':None,'year':None}
    m=re.fullmatch(r'\s*((?:19|20)\d{2}):\s*([-+]?\d+(?:\.\d+)?)\s*',v)
    if m:return {'raw':v,'numeric':float(m[2]),'year':int(m[1]),'encoding':'source_year_colon_value'}
    try:return {'raw':v,'numeric':float(v),'year':None,'encoding':'plain_numeric'}
    except (TypeError,ValueError):return {'raw':v,'numeric':None,'year':None,'encoding':'unparsed'}
def dim(n):
    # Empty exporter placeholders carry no disaggregation, retain them in the raw row.
    c=n['children']; return tuple(sorted((tag,tuple(sorted(x['attributes'].items()))) for tag in ('dimension','location') for x in c.get(tag,[]) if any(x['attributes'].values())))
flat=[]
for o in obs:
    targets=collections.defaultdict(list)
    for t in o['targets']:targets[dim(t)].append(t)
    for idx,a in enumerate(o['actuals']):
        av=scalar(a['attributes'].get('value')); candidates=targets[dim(a)]; tv=scalar(candidates[0]['attributes'].get('value')) if len(candidates)==1 else scalar(None)
        b=o['baseline']; bv=scalar(b['attributes'].get('value')) if b else scalar(None)
        q={'id':o['id']+'::a'+str(idx),'parent_observation_id':o['id'],'project_id':o['project_id'],'source_file':o['source_file'],'actual':av,'target':tv,'baseline':bv,'dimensions':dim(a),'target_matches':len(candidates),'same_reported_year':av['year']==tv['year'] if av['year'] is not None or tv['year'] is not None else None,'actual_not_future':av['year']<=2026 if av['year'] else o['quality']['past_period'],'baseline_dimension_match':b is not None and dim(b)==dim(a),'measure':o['measure'],'direction':o['ascending']}
        q['direction_conflicts_with_target_change']=bool(tv['numeric'] is not None and bv['numeric'] is not None and ((o['ascending']=='0' and tv['numeric']>bv['numeric']) or (o['ascending']=='1' and tv['numeric']<bv['numeric'])))
        q['comparison_candidate']=av['numeric'] is not None and tv['numeric'] is not None and len(candidates)==1 and q['same_reported_year'] is not False and q['actual_not_future'] and o['measure'] in ('1','2') and o['ascending'] in ('0','1') and not q['direction_conflicts_with_target_change']
        q['publishable_chemistry_input']=False
        flat.append(q)
dump('dimension_matched_measurements.json',flat)

# Funding paths use explicit incoming provider references, never mere co-occurrence.
adj=collections.defaultdict(set)
for e in edges:
    if e['target_resolved'] and (e['relation_field']=='transaction/provider-org' or (e['relation_field']=='participating-org' and e.get('role')=='1')):adj[e['from']].add(e['to'])
paths=[]
for pid in {o['project_id'] for o in obs}:
    queue=[(pid,[pid])]; seen={pid}
    while queue:
        v,path=queue.pop(0)
        if len(path)>8:continue
        if ps[v]['reporting_org_ref']=='XM-DAC-7' and len(path)>1:
            paths.append({'result_project_id':pid,'funder_country':'NLD','funder_project_id':v,'path':path,'interpretation':'funding provenance only; does not attribute the whole result to one donor'}); continue
        for nxt in sorted(adj[v]):
            if nxt not in seen:seen.add(nxt);queue.append((nxt,path+[nxt]))
dump('netherlands_funding_paths.json',paths)

oid={o['id']:o for o in obs}
anchor_audits=[]
for a in anchors:
    buckets=collections.defaultdict(list)
    for ident in a['observation_ids']:
        o=oid[ident]; country=tuple(sorted(c['code'] for c in ps[o['project_id']]['countries']))
        sig=(country,o['period_start'],o['period_end'],json.dumps(o['targets'],sort_keys=True),json.dumps(o['actuals'],sort_keys=True))
        buckets[sig].append(o)
    duplicates=[{'projects':sorted({o['project_id'] for o in rows}),'orgs':sorted({o['reporting_org_ref'] for o in rows}),'observations':[o['id'] for o in rows]} for rows in buckets.values() if len({o['reporting_org_ref'] for o in rows})>1]
    anchor_audits.append({'key':a['key'],'exact_definition_variants':a['exact_definition_variants'],'same_country_period_values_cross_org':duplicates,'status':'possible repeated consortium reporting; never count as independent replicates'})
dump('anchor_dependence_audit.json',anchor_audits)

cohorts=collections.defaultdict(lambda: {'projects':set(),'rows':0})
for o in obs:
    if o['structural_candidate']:
        p=ps[o['project_id']]; country=p['countries'][0]['code'];codes=sorted({s['code'] for s in p['sectors'] if s.get('vocabulary','1')=='1'})
        health=bool(codes) and all(c.startswith(('121','122','123','130')) for c in codes)
        key=(p['reporting_org_ref'],country,'pure_health_activity' if health else 'mixed_or_other_sector')
        cohorts[key]['projects'].add(p['id']);cohorts[key]['rows']+=1
dump('structural_candidate_cohorts.json',[{'reporting_org':k[0],'country':k[1],'sector_scope':k[2],'project_count':len(v['projects']),'project_ids':sorted(v['projects']),'indicator_period_rows':v['rows'],'public_score_allowed':False} for k,v in sorted(cohorts.items())])

# A page-verified case preserves changed geographical and conceptual definitions.
case=[]
records=[('PDO1','People receiving guideline-concordant TB treatment, NCD','number',6169,7100,7717,6169,7100,'unchanged',41),('PDO2','People receiving guideline-concordant TB treatment, Daru','number',480,612,661,1659,1900,'South Fly district removed; baseline and target population changed',41),('PDO3','New/relapse TB patients tested using WHO-recommended rapid test, NCD','percent',10,90,62,20,80,'DST measure replaced by rapid-test measure; not same indicator',41),('PDO4','New/relapse TB patients tested using WHO-recommended rapid test, Daru','percent',10,90,74,41,80,'DST measure and geographical population changed',41),('PDO5','DS-TB treatment success rate, NCD','percent',56,85,90,56,85,'unchanged',42),('PDO6','DR-TB treatment success rate, NCD','percent',44,75,75,44,75,'regimen wording changed; cohort timing must be reviewed',42),('PDO7','DR-TB treatment success rate, females, NCD','percent',0,75,60,0,75,'unchanged; zero baseline is reported, not established as meaningful absence',42)]
for ident,title,unit,b,t,a,ob,ot,change,page in records:
    case.append({'project_id':'P160947','indicator_local_id':ident,'definition':title,'unit':unit,'baseline':b,'baseline_date':'2016-08','target':t,'target_date':'2024-03','actual':a,'actual_date_as_labeled':'2023-12','original_baseline':ob,'original_target':ot,'original_target_source':'ICR Annex 8 retrospective record, not separately downloaded original PAD','revision_month':'2022-06','revision_note':change,'source_pdf':'raw/wb_P160947_icr.pdf','results_pdf_page':page,'revision_pdf_page':69,'source_document_url':'https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099022825093514594','subjective_rating_used':False,'validation_note':'Result table and comments contain cohort/date/denominator inconsistencies. Retain separately, do not auto-rank.'})
dump('wb_png_tb_target_history.json',case)
for f in (R/'raw').glob('*.pdf'):
    reader=PdfReader(f)
    (P/(f.stem+'.txt')).write_text('\n'.join(f'\n=== PDF PAGE {n+1} ===\n'+p.extract_text() for n,p in enumerate(reader.pages)))

summary=load('collection_summary.json')
summary.update({'standard_indicator_codes':len(codebook),'flattened_actual_rows':len(flat),'explicit_year_numeric_actuals':sum(x['actual']['year'] is not None for x in flat),'matched_comparison_candidates':sum(x['comparison_candidate'] for x in flat),'direction_conflict_rows':sum(x['direction_conflicts_with_target_change'] for x in flat),'result_projects_linked_to_netherlands':len({x['result_project_id'] for x in paths}),'verified_funding_paths':len(paths),'anchor_groups_with_exact_definition':sum(x['exact_definition_variants']==1 for x in anchors),'anchor_groups_with_possible_duplicate_reports':sum(bool(x['same_country_period_values_cross_org']) for x in anchor_audits),'structural_candidate_projects':len({o['project_id'] for o in obs if o['structural_candidate']}),'structural_candidate_countries':sorted({ps[o['project_id']]['countries'][0]['code'] for o in obs if o['structural_candidate']}),'wb_target_revision_records':len(case)})
summary['unique_cross_org_directed_project_pairs']=len({(e['from'],e['to']) for e in edges if e['cross_reporting_org']})
summary['reporting_orgs_in_anchor_candidates']=sorted({org for a in anchors for org in a['reporting_orgs']})
summary['pure_health_candidate_projects']=len({pid for k,v in cohorts.items() if k[2]=='pure_health_activity' and k[1]!='NL' for pid in v['projects']})
summary['all_country_codes_count']=len(summary['recipient_country_codes'])
dump('collection_summary.json',summary)
jobs=json.loads((R/'source_download_jobs.json').read_text())
manual=[('wb_P160947_icr.pdf','https://documents1.worldbank.org/curated/en/099022825093514594/pdf/BOSIB-d40598d5-542e-4b1e-b8ef-4336b55b9c5d.pdf'),('wb_P160947_iegreview.pdf','https://documents1.worldbank.org/curated/en/099060925144090421/pdf/P160947-9723d848-1c30-4438-b2ee-c2df1a5fae71.pdf'),('nlmfa_indicator_codes.xlsx','https://helpdesk-opendata-minbuza.nl/wp-content/uploads/2023/07/IATI-Indicator-and-disaggregates-reference-code-list-webversion.xlsx'),('nlmfa_publication_guidelines.pdf','https://helpdesk-opendata-minbuza.nl/wp-content/uploads/2021/07/how-to-use-the-iati-standard-2.pdf')]
jobs +=[{'file':f,'url':u,'method':'Chrome_browser_download'} for f,u in manual]
for j in jobs:
    f=R/'raw'/j['file'];j.update({'retrieved_local_date':'2026-11-06','saved':f.exists(),'bytes':f.stat().st_size if f.exists() else None,'sha256':hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None})
dump('source_manifest.json',jobs)
assert not summary['source_errors'],summary['source_errors']
assert len(obs)==len({o['id'] for o in obs})
assert len(flat)==sum(len(o['actuals']) for o in obs)
assert all(o['project_id'] in ps for o in obs)
assert all(e['target_resolved']==(e['to'] in ps) for e in edges)
assert all(j['saved'] for j in jobs)
assert {j['file'] for j in jobs}=={f.name for f in (R/'raw').iterdir()}
dump('validation.json',{'all_xml_parse':True,'unique_observation_keys':True,'measurement_count_reconciles':True,'project_foreign_keys':True,'explicit_links_reconciled':True,'raw_sources_manifest_complete':True,'no_subjective_rating_in_scoring':True,'no_new_chemistry_scores':True,'warnings':['source-reported direction may be unreliable','same indicator code alone is not equivalence','country and sex disaggregates must not be added twice','cofinancing is not independent replication','year-only actuals are not end-of-programme outcomes']})
for name in ['projects.json','objective_observations.json','dimension_matched_measurements.json']:
    with gzip.open(P/(name+'.gz'),'wb') as g:g.write((P/name).read_bytes())
print(json.dumps({k:v for k,v in summary.items() if k not in ['per_file','recipient_country_codes']},ensure_ascii=False,indent=2))
