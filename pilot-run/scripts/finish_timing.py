"""Record non-overlapping wall stages, preserving original estimate and start."""
import datetime,json,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('stage',choices=['eval_start','eval_end','done']);a=p.parse_args()
R=Path(__file__).resolve().parents[1];path=R/'results/timing.json';r=json.loads(path.read_text());now=datetime.datetime.now(datetime.timezone.utc)
if a.stage!='done':r.setdefault('final_'+a.stage+'_utc',now.isoformat())
else:
 r['end_ist']=now.astimezone(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat()
 start=datetime.datetime.fromisoformat(r['start_ist']);ready=datetime.datetime.fromisoformat(r['first_pilot_engine_ready_utc']);es=datetime.datetime.fromisoformat(r['final_eval_start_utc']);ee=datetime.datetime.fromisoformat(r['final_eval_end_utc'])
 r['actual_minutes']=round((now-start).total_seconds()/60,2)
 r['per_stage_minutes']={k:round((b-a).total_seconds()/60,2) for k,a,b in [('setup',start,ready),('GPU_run',ready,es),('eval',es,ee),('writeup',ee,now)]}
 r['stage_definitions']='Exclusive wall intervals: setup through first pilot engine ready; GPU_run through final evaluation start (includes model changes, recovery pauses, queue waits and overlapping drafting); eval through final audit/analysis completion; writeup through final artifact checks. These are elapsed stages, not GPU kernel timers.'
 stop=json.loads((R/'results/session_stopped.json').read_text());r['CU_estimated']=stop['estimated_CU'];r['CU_conservative_upper']=stop['conservative_upper_CU'];r['GPU']='NVIDIA L4 (23,034 MiB)'
path.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
