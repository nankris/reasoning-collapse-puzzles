import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];h=json.loads((R/'results/hypothesis_results.json').read_text());a=json.loads((R/'results/audit.json').read_text())
print('EXPERIMENT 118b: FIXED PREREGISTERED RULES')
print('Saved responses:',h['records'],'/ 750')
print('Original 285 preserved:',a['original_285_outputs_preserved_verbatim'])
for key in ['H1','H2','H3','H4']:
 x=h[key];print(key,x['verdict'])
 if 'estimate' in x:print('  Accuracy difference: %.2f pp; 95%% CI [%.2f, %.2f] pp'%(100*x['estimate'],100*x['ci'][0],100*x['ci'][1]))
 if key=='H2' and 'modes' in x:
  for m in x['modes']:print('  %s: %s/%s; 95%% Wilson [%.2f, %.2f]%%'%('ON' if m['thinking'] else 'OFF',m['correct'],m['n'],100*m['ci'][0],100*m['ci'][1]))
  print('  Maximum cell truncation:',max(x['cell_truncation'].values()))
 if key=='H3' and 'late_over_peak' in x:
  print('  Late/peak tokens: %.3f; 95%% CI [%.3f, %.3f]'%(x['late_over_peak'],*x['ratio_ci']))
  print('  Peak/low tokens: %.3f; 95%% CI [%.3f, %.3f]'%(x['peak_over_low'],*x['rise_ratio_ci']))
  print('  Maximum relevant truncation:',x['truncation'])
print('THREE-REGIME VERDICT:',h['overall_three_regime_verdict'])
print('Prompt tokens:',h['total_prompt_tokens'])
print('Generated tokens:',h['total_output_tokens'])
print('Token-cap hits:',h['truncations'])

rows=[json.loads(l) for l in (R/'results/confirm.jsonl').read_text().splitlines()]
high=[r for r in rows if r['family']=='hanoi' and r['n'] in [9,10] and r['arm']=='moves']
if len(high)==100:
 from analyze import wilson
 k=sum(r['truncated'] for r in high);ci=wilson(k,len(high))
 print('DESCRIPTIVE nine/ten-disk cap hits:',str(k)+'/'+str(len(high)))
 print('  95% Wilson cap-rate interval: [%.2f, %.2f]%%'%(100*ci[0],100*ci[1]))
