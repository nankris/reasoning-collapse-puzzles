"""Read-only progress, coverage and runtime-staleness snapshot."""
import json,time,re
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1];res=R/'results';now=time.time()
try:
 p=json.loads((res/'progress.json').read_text());a=json.loads((res/'allocation.json').read_text());rows=[json.loads(l) for l in (res/'confirm.jsonl').read_text().splitlines()]
 cells=Counter((r['family'],r['n'],r['thinking'],r['arm']) for r in rows)
 summary=json.loads((res/'summary.json').read_text()) if (res/'summary.json').exists() else []
 old={(r['family'],r['n'],r['thinking'],r['arm']) for r in summary if r['N']==25};new={c for c,n in cells.items() if n==25}
 hb=[]
 for line in (R/'figures/colab_run.txt').read_text().splitlines():
  if line.startswith(('HEARTBEAT','RESULT')):
   m=re.search(r'elapsed ([0-9.]+)$',line)
   if m:hb.append(float(m.group(1)))
 meta=json.loads((res/'resume_meta.json').read_text());age=now-meta['time']-max(hb) if hb and meta['time']>=a['start_epoch'] else None
 poll_age=now-(res/'progress.json').stat().st_mtime
 stopped=(res/'session_stopped.json').exists()
 event='stopped' if stopped else ('runtime_stale' if poll_age>180 or (age is not None and age>240) else ('cell_complete' if new-old else 'running'))
 out=dict(event=event,records=len(rows),planned=750,complete_cells=len(new),analyzed_complete_cells=len(old),new_complete_cells=[list(c) for c in sorted(new-old)],CU_upper_live=a.get('base_CU_upper',0)+(now-a['start_epoch'])/3600*a['rate_upper'],poll_age_seconds=round(poll_age),heartbeat_age_seconds=round(age) if age is not None else None,allocation=a.get('allocation_number',1),utc=time.strftime('%Y-%m-%d %H:%M:%S UTC',time.gmtime()))
 print(json.dumps(out))
except Exception as e:print(json.dumps({'event':'local_read_error','error':type(e).__name__+': '+str(e)}))
