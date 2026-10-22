"""Local checkpoint/budget monitor. Never creates or touches other sessions."""
import json,time,datetime,subprocess,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];res=R/'results'
def call(args,timeout=35):return subprocess.run(['colab',*args],capture_output=True,text=True,timeout=timeout)
state=json.loads((res/'recovery.json').read_text());start=state['replacement_created_epoch'];deadline=start+3.19/1.6*3600
while not (res/'session_stopped.json').exists():
 try:
  state=json.loads((res/'recovery.json').read_text())
  usage=call(['usage'],20).stdout
  with (res/'recovery_usage.log').open('a') as f:f.write(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n'+usage+'\n')
  for remote,local in [('/content/puzzles/confirm.jsonl',res/'confirm.jsonl'),(state.get('remote_log','/content/resume.log'),R/state.get('local_log','figures/resume_run.txt')),('/content/puzzles/confirm_meta.json',res/'resume_meta.json')]:
   tmp=local.with_suffix(local.suffix+'.partial');p=call(['download','-s','puzzles-l4',remote,str(tmp)])
   if p.returncode==0:
    if local.suffix=='.jsonl':
     rs=[json.loads(l) for l in tmp.read_text().splitlines()]
     old=[json.loads(l) for l in local.read_text().splitlines()]
     assert {r['id'] for r in old}<={r['id'] for r in rs}
    tmp.replace(local)
  rows=[json.loads(l) for l in (res/'confirm.jsonl').read_text().splitlines()]
  n=len(rows);now=time.time();state=json.loads((res/'recovery.json').read_text());deadline=start+state['remaining_upper_budget_CU']/state['guard_rate_CU_hr']*3600;print(datetime.datetime.now(datetime.timezone.utc).isoformat(),'saved',n,'remaining_budget_minutes',round((deadline-now)/60,1),flush=True)
  rate=re.search(r'Usage rate:\s*([\d.]+)',usage)
  rate_alarm=bool(rate and float(rate.group(1))>3.2)
  if n==750 or now>=deadline or rate_alarm:
   before=call(['usage'],20).stdout;p=call(['stop','-s','puzzles-l4'],30)
   if p.returncode==0:
    stop=time.time();after=call(['usage'],20).stdout
    (res/'session_stopped.json').write_text(json.dumps({'reason':'all 750 saved' if n==750 else ('aggregate rate unexpectedly increased; conservative stop' if rate_alarm else 'conservative 5.8 total-CU guard'),'records':n,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stop_epoch':stop,'stop_output':p.stdout,'stop_returncode':p.returncode,'usage_before':before,'usage_after':after,'estimated_CU':state['previous_cost_estimate_CU']+1.54*(stop-start)/3600,'conservative_upper_CU':2.61+1.6*(stop-start)/3600},indent=2));break
 except Exception as e:print(type(e).__name__,str(e)[:200],flush=True)
 time.sleep(40)
