"""Small read-only checkpoint summary. Does not score incomplete cells."""
from pathlib import Path
from collections import Counter
import json,time
R=Path(__file__).resolve().parents[1];rows=[json.loads(l) for l in (R/'results/confirm.jsonl').read_text().splitlines()]
original=set(json.loads((R/'results/original_checkpoint_ids.json').read_text()))
new=[r for r in rows if r['id'] not in original]
counts=Counter((r['family'],r['n'],r['thinking'],r['arm']) for r in new)
print('Saved',len(rows),'/750; output tokens',sum(r['output_tokens'] for r in rows),'; cap hits',sum(r['truncated'] for r in rows))
for c,n in sorted(counts.items()):
 rs=[r for r in new if (r['family'],r['n'],r['thinking'],r['arm'])==c]
 print(c, f'{n}/25',f'correct={sum(r["correct"] for r in rs)} cap={sum(r["truncated"] for r in rs)}' if n==25 else 'incomplete, no accuracy estimate')
r=json.loads((R/'results/recovery.json').read_text());print('Upper cost so far',round(r['previous_cost_conservative_upper_CU']+r['guard_rate_CU_hr']*(time.time()-r['replacement_created_epoch'])/3600,3),'CU')
