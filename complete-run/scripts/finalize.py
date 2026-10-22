"""Run after the named session is stopped, then review all generated artifacts."""
import sys,json,time,subprocess,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];res=R/'results';py=sys.executable
assert (res/'session_stopped.json').exists(),'Save final checkpoint and stop our GPU session first'
stop=json.loads((res/'session_stopped.json').read_text());t=json.loads((res/'timing.json').read_text());alloc=json.loads((res/'allocation.json').read_text())
for script,log in [('puzzles.py','verifier_checks.txt'),('audit.py','audit_latest.txt'),('analyze.py','analysis_latest.txt'),('hypotheses.py','hypothesis_latest.txt'),('final_stats.py','final_stats.txt')]:
 p=subprocess.run([py,str(R/'scripts'/script)],cwd=R,capture_output=True,text=True)
 (res/log).write_text(p.stdout+p.stderr)
 assert p.returncode==0,(script,p.stderr)
evalend=time.time()
meta=json.loads((res/'resume_meta.json').read_text());first_meta=min([meta['time']]+[json.loads(f.read_text())['time'] for f in res.glob('allocation*_meta.json')]);start=datetime.datetime.fromisoformat(t['start_ist']).timestamp();stop_epoch=datetime.datetime.fromisoformat(stop['utc']).timestamp()
ledger_path=res/'allocations.json';ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else []
if not any(x['start_epoch']==alloc['start_epoch'] for x in ledger):
 ledger.append({'allocation_number':alloc.get('allocation_number',1),'creation_event':alloc['creation_event'],'start_epoch':alloc['start_epoch'],'stop_epoch':stop_epoch,'reason':stop['reason'],'CU_estimate':stop['CU_estimate']-alloc.get('base_CU_estimate',0),'CU_upper':stop['CU_upper']-alloc.get('base_CU_upper',0),'records_saved':stop['records']})
 ledger_path.write_text(json.dumps(ledger,indent=2))
t.update({'allocated_GPU_minutes_estimated':stop.get('elapsed_GPU_minutes'),'GPU':'NVIDIA L4','CU_estimate':stop['CU_estimate'],'CU_upper':stop['CU_upper'],'eval_end_epoch':evalend,'per_stage_minutes':{'setup':(first_meta-start)/60,'GPU run':(stop_epoch-first_meta)/60,'eval':max(0,(evalend-stop_epoch)/60),'writeup':0},'stage_definition':'Disjoint wall intervals; GPU-run stage includes overlapping article preparation, checkpoint polling and later-allocation recovery/setup gaps. Allocation CU excludes gaps without a GPU. Eval begins when GPU is stopped. Final review updates writeup stage.'})
t['end_ist']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat();t['actual_minutes']=(time.time()-start)/60
(res/'timing.json').write_text(json.dumps(t,indent=2))
subprocess.run([py,str(R/'scripts/publish.py')],cwd=R,check=True)
