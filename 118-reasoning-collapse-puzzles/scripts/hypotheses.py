"""Apply frozen preregistration to confirmation, without fitting thresholds."""
import json
from pathlib import Path
import numpy as np
from analyze import boot,wilson
R=Path(__file__).resolve().parents[1];rng=np.random.default_rng(118118)
def classify(ci,margin,greater=True):
 if greater:
  return 'PROVEN' if ci[0]>margin else ('DISPROVEN' if ci[1]<margin else 'INCONCLUSIVE')
 return 'PROVEN' if ci[1]<margin else ('DISPROVEN' if ci[0]>margin else 'INCONCLUSIVE')
def paired_difference(a,b,keys):
 aa={tuple(r[k] for k in keys):r for r in a};bb={tuple(r[k] for k in keys):r for r in b}
 assert set(aa)==set(bb),'unmatched rows'
 # Resample instances within each fixed level/mode stratum, keeping pairs intact.
 strata={}
 for k in aa:strata.setdefault(k[:-1],[]).append(float(aa[k]['correct'])-float(bb[k]['correct']))
 samples=[]
 for vals in strata.values():
  v=np.asarray(vals);samples.append(v[rng.integers(0,len(v),(10000,len(v)))].mean(1))
 distr=np.mean(samples,axis=0)
 return float(np.mean([np.mean(v) for v in strata.values()])),np.quantile(distr,[.025,.975]).tolist()
def main():
 reg=json.loads((R/'results/preregistration.json').read_text());data=[json.loads(l) for l in (R/'results/confirm.jsonl').read_text().splitlines()]
 assert len(data)<=750 and len({r['id'] for r in data})==len(data),'Duplicate or unexpected records'
 moves=[r for r in data if r['arm']=='moves'];ha=[r for r in moves if r['family']=='hanoi'];out={}
 medium=[r for r in ha if r['n'] in reg['H1']['levels']]
 if len(medium)==150:
  est,ci=paired_difference([r for r in medium if r['thinking']],[r for r in medium if not r['thinking']],['n','item'])
  out['H1']={'estimate':est,'ci':ci,'margin':reg['H1']['margin'],'verdict':classify(ci,reg['H1']['margin'])}
 else:
  out['H1']={'verdict':'INCONCLUSIVE','complete':False,'note':'Planned sample incomplete; missing requests were not scored as failures and no partial-sample hypothesis test was performed'}
 if len([r for r in ha if r['n']>=reg['H2']['threshold']])==200:
  hard=[r for r in ha if r['n']>=reg['H2']['threshold']];checks=[]
  for mode in (False,True):
   rs=[r for r in hard if r['thinking']==mode];k=sum(r['correct'] for r in rs);ci=wilson(k,len(rs));tr=np.mean([r['truncated'] for r in rs])
   checks.append(dict(thinking=mode,n=len(rs),correct=k,accuracy=k/len(rs),ci=ci,truncation=tr))
  near=reg['H2']['near_zero'];v='PROVEN' if all(c['ci'][1]<near for c in checks) else ('DISPROVEN' if any(c['ci'][0]>near for c in checks) else 'INCONCLUSIVE')
  cell_truncation={f'{n}:{int(mode)}':float(np.mean([r['truncated'] for r in hard if r['n']==n and r['thinking']==mode])) for n in range(reg['H2']['threshold'],11) for mode in (False,True)}
  if max(cell_truncation.values())>.05:v='INCONCLUSIVE'
  out['H2']={'threshold':reg['H2']['threshold'],'near_zero':near,'modes':checks,'cell_truncation':cell_truncation,'verdict':v,'note':'Truncation gate prevents attribution to uncensored collapse'}
 else:
  out['H2']={'verdict':'INCONCLUSIVE','complete':False,'note':'Planned sample incomplete; missing requests were not scored as failures and no partial-sample hypothesis test was performed'}
 if all(len([r for r in ha if r['thinking'] and r['n']==n])==25 for n in [3,reg['H3']['peak_level'],reg['H3']['late_level']]):
  think=[r for r in ha if r['thinking']];peak=reg['H3']['peak_level'];late=reg['H3']['late_level']
  arrays={n:np.asarray([r['thinking_tokens'] for r in think if r['n']==n],float) for n in [3,peak,late]}
  ds={n:v[rng.integers(0,len(v),(10000,len(v)))].mean(1) for n,v in arrays.items()}
  ratio=np.mean(arrays[late])/np.mean(arrays[peak]);ci=np.quantile(ds[late]/ds[peak],[.025,.975]).tolist();rise=np.mean(arrays[peak])/np.mean(arrays[3]);rise_ci=np.quantile(ds[peak]/ds[3],[.025,.975]).tolist()
  fallver=classify(ci,reg['H3']['max_late_ratio'],False);risever=classify(rise_ci,reg['H3']['min_rise_ratio'])
  v='PROVEN' if fallver==risever=='PROVEN' else ('DISPROVEN' if 'DISPROVEN' in [fallver,risever] else 'INCONCLUSIVE')
  trunc=max(np.mean([r['truncated'] for r in think if r['n']==n]) for n in {3,peak,late})
  if trunc>.05:v='INCONCLUSIVE'
  out['H3']={'peak_level':peak,'late_level':late,'late_over_peak':ratio,'ratio_ci':ci,'peak_over_low':rise,'rise_ratio_ci':rise_ci,'truncation':trunc,'verdict':v,'fall_comparison_verdict_before_censoring_gate':fallver}
 else:
  out['H3']={'verdict':'INCONCLUSIVE','complete':False,'note':'Planned sample incomplete; missing requests were not scored as failures and no partial-sample hypothesis test was performed'}
 if len([r for r in data if r['family']=='hanoi' and r['n'] in reg['H4']['levels']])==300:
  highlevels=reg['H4']['levels'];a=[r for r in data if r['family']=='hanoi' and r['arm']=='program' and r['n'] in highlevels];b=[r for r in ha if r['n'] in highlevels]
  est,ci=paired_difference(a,b,['n','thinking','item'])
  out['H4']={'estimate':est,'ci':ci,'margin':reg['H4']['margin'],'program_correct':sum(r['correct'] for r in a),'program_N':len(a),'moves_correct':sum(r['correct'] for r in b),'moves_N':len(b),'verdict':classify(ci,reg['H4']['margin'])}
 else:
  out['H4']={'verdict':'INCONCLUSIVE','complete':False,'note':'Planned sample incomplete; missing requests were not scored as failures and no partial-sample hypothesis test was performed'}
 out['records']=len(data);out['planned_records']=750
 out['total_output_tokens']=sum(r['output_tokens'] for r in data);out['total_prompt_tokens']=sum(r['prompt_tokens'] for r in data);out['truncations']=sum(r['truncated'] for r in data)
 pattern=[out[h]['verdict'] for h in ['H1','H2','H3']]
 out['overall_three_regime_verdict']='PROVEN' if all(v=='PROVEN' for v in pattern) else ('DISPROVEN' if 'DISPROVEN' in pattern else 'INCONCLUSIVE')
 (R/'results/hypothesis_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
