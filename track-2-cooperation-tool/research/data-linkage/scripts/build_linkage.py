"""Preserve objective IATI measurements and explicit relationships; no score imputation."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json, hashlib, collections, math, re
from datetime import date
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'processed'
CUTOFF = '2026-11-06'
def dump(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False))
def narr(e):
    return [] if e is None else [{'lang': n.get('{http://www.w3.org/XML/1998/namespace}lang'), 'text': ''.join(n.itertext()).strip()} for n in e.findall('narrative')]
def node(e):
    if e is None: return None
    return {'attributes': dict(e.attrib), 'narratives': narr(e), 'children': {tag: [node(n) for n in e.findall(tag)] for tag in sorted({c.tag for c in e if c.tag != 'narrative'})}}
def number(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError): return None
projects, observations, edges, file_stats, errors = {}, [], [], [], []
for f in sorted((ROOT/'raw').glob('*.xml')):
    try: root=ET.parse(f).getroot()
    except Exception as exc:
        errors.append({'file':f.name,'error':str(exc)}); continue
    acts=root.findall('iati-activity')
    file_stats.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'activities':len(acts),'generated':root.get('generated-datetime')})
    for a in acts:
        pid=(a.findtext('iati-identifier') or '').strip()
        if not pid: errors.append({'file':f.name,'error':'missing project id'}); continue
        org=a.find('reporting-org'); orgref=org.get('ref') if org is not None else None
        if pid in projects:
            errors.append({'file':f.name,'id':pid,'error':'duplicate project id; first record retained'}); continue
        countries=[dict(e.attrib) for e in a.findall('recipient-country')]
        sectors=[dict(e.attrib) for e in a.findall('sector')]
        p={'id':pid,'reporting_org':node(org),'reporting_org_ref':orgref,'title':narr(a.find('title')),'source_file':f.name,'last_updated':a.get('last-updated-datetime'),'status':a.find('activity-status').get('code') if a.find('activity-status') is not None else None,'countries':countries,'regions':[dict(e.attrib) for e in a.findall('recipient-region')],'sectors':sectors,'dates':[dict(e.attrib) for e in a.findall('activity-date')],'participating_orgs':[node(e) for e in a.findall('participating-org')],'other_identifiers':[node(e) for e in a.findall('other-identifier')],'documents':[node(e) for e in a.findall('document-link')],'transaction_country_sector_context':[]}
        projects[pid]=p
        for tag, attr in [('related-activity','ref'),('participating-org','activity-id'),('transaction/provider-org','provider-activity-id'),('transaction/receiver-org','receiver-activity-id')]:
            for e in a.findall(tag):
                if e.get(attr): edges.append({'from':pid,'to':e.get(attr).strip(),'relation_field':tag,'role':e.get('role'),'relation_type':e.get('type') if tag=='related-activity' else None,'org_ref':e.get('ref') if tag!='related-activity' else None})
        for t in a.findall('transaction'):
            if t.find('recipient-country') is not None or t.find('sector') is not None:
                p['transaction_country_sector_context'].append({'countries':[dict(x.attrib) for x in t.findall('recipient-country')],'sectors':[dict(x.attrib) for x in t.findall('sector')],'date':node(t.find('transaction-date'))})
        for ri,r in enumerate(a.findall('result')):
            for ii,i in enumerate(r.findall('indicator')):
                refs=[dict(e.attrib) for e in i.findall('reference')]
                for ti,t in enumerate(i.findall('period')):
                    if not t.findall('actual'): continue
                    start=t.find('period-start'); end=t.find('period-end')
                    row={'id':f'{pid}::r{ri}i{ii}p{ti}','project_id':pid,'reporting_org_ref':orgref,'source_file':f.name,'result_type':r.get('type'),'result_title':narr(r.find('title')),'result_aggregation':r.get('aggregation-status'),'indicator_title':narr(i.find('title')),'indicator_description':narr(i.find('description')),'measure':i.get('measure'),'ascending':i.get('ascending'),'indicator_aggregation':i.get('aggregation-status'),'references':refs,'baseline':node(i.find('baseline')),'period_start':start.get('iso-date') if start is not None else None,'period_end':end.get('iso-date') if end is not None else None,'targets':[node(e) for e in t.findall('target')],'actuals':[node(e) for e in t.findall('actual')],'indicator_documents':[node(e) for e in i.findall('document-link')]}
                    av=number(row['actuals'][0]['attributes'].get('value')) if len(row['actuals'])==1 else None
                    tv=number(row['targets'][0]['attributes'].get('value')) if len(row['targets'])==1 else None
                    bv=number(row['baseline']['attributes'].get('value')) if row['baseline'] else None
                    dimensions=any(n['children'].get('dimension') or n['children'].get('location') for n in row['targets']+row['actuals'])
                    row['quality']={'one_numeric_target_and_actual':av is not None and tv is not None,'numeric_baseline':bv is not None,'explicit_direction':row['ascending'] in ('0','1'),'past_period':bool(row['period_end'] and row['period_end']<=CUTOFF),'single_activity_country':len(countries)==1,'dimension_or_location_present':bool(dimensions),'has_external_indicator_uri':any(x.get('indicator-uri') for x in refs),'original_target_verified':False,'target_revision_history_verified':False,'independent_verification_established':False}
                    row['numeric_values']={'actual':av,'target':tv,'baseline':bv}
                    # This is a structural diagnostic, not an authorization to aggregate or rank.
                    row['structural_candidate']=all(row['quality'][k] for k in ['one_numeric_target_and_actual','numeric_baseline','explicit_direction','past_period','single_activity_country']) and not dimensions
                    observations.append(row)
edge_unique={json.dumps(e,sort_keys=True):e for e in edges}
edges=list(edge_unique.values())
for e in edges:
    e['target_resolved']=e['to'] in projects
    e['cross_reporting_org']=e['target_resolved'] and projects[e['from']]['reporting_org_ref'] != projects[e['to']]['reporting_org_ref']
    e['interpretation']='explicit project/funding relation; not independent measurement or additive effect'
groups=collections.defaultdict(list)
for o in observations:
    for r in o['references']:
        if r.get('indicator-uri') and r.get('code'):
            # URI is not normalized across hosts or versions without equivalence evidence.
            key=(r.get('vocabulary'),r['indicator-uri'],r['code'],o['measure'],o['ascending'])
            groups[key].append(o)
anchors=[]
for key, rows in groups.items():
    orgs=sorted({x['reporting_org_ref'] or '' for x in rows})
    if len(orgs)<2: continue
    definitions={json.dumps([x['indicator_title'],x['indicator_description']],sort_keys=True,ensure_ascii=False) for x in rows}
    anchors.append({'key':list(key),'reporting_orgs':orgs,'project_ids':sorted({x['project_id'] for x in rows}),'observation_ids':[x['id'] for x in rows],'exact_definition_variants':len(definitions),'status':'candidate_only_review_scope_units_disaggregation_and_source_dependence','independent_anchor_established':False})
summary={'as_of':CUTOFF,'projects':len(projects),'reporting_orgs':len({p['reporting_org_ref'] for p in projects.values()}),'recipient_country_codes':sorted({c['code'] for p in projects.values() for c in p['countries']}),'indicator_period_records':len(observations),'actual_elements':sum(len(o['actuals']) for o in observations),'structural_candidates':sum(o['structural_candidate'] for o in observations),'quality_counts':{k:sum(o['quality'][k] for o in observations) for k in observations[0]['quality']} if observations else {},'explicit_edges':len(edges),'resolved_edges':sum(e['target_resolved'] for e in edges),'cross_reporting_org_edges':sum(e['cross_reporting_org'] for e in edges),'cross_org_indicator_uri_candidates':len(anchors),'public_chemistry_scores_emitted':0,'source_errors':errors,'per_file':file_stats}
dump('projects.json',list(projects.values())); dump('objective_observations.json',observations); dump('explicit_project_links.json',edges); dump('common_indicator_candidates.json',anchors); dump('collection_summary.json',summary)
print(json.dumps({k:v for k,v in summary.items() if k not in ['per_file','recipient_country_codes']},ensure_ascii=False,indent=2))
