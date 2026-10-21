"""Run after setup.sh. Downloads only b10-118b, never touches other sessions."""
import subprocess,json,time,datetime,gzip
from pathlib import Path
R=Path(__file__).resolve().parents[1];res=R/'results'
def cmd(args,timeout=55,input=None):
 return subprocess.run(['colab',*args],text=True,capture_output=True,timeout=timeout,input=input)
def main():
 a=json.loads((res/'allocation.json').read_text());usage=cmd(['usage'])
 with (res/'usage.log').open('a') as f:f.write(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n'+usage.stdout+usage.stderr+'\n')
 for remote,local in [('/content/exp118/confirm.jsonl',res/'confirm.jsonl'),('/content/118b.log',R/'figures/colab_run.txt'),('/content/exp118/confirm_meta.json',res/'resume_meta.json')]:
  tmp=local.with_suffix('.partial');p=cmd(['download','-s','b10-118b',remote,str(tmp)])
  if p.returncode!=0:
   print('DOWNLOAD_FAILED',remote,'returncode',p.returncode,flush=True)
   if local.name=='confirm.jsonl':raise RuntimeError('Checkpoint download failed; check named session before resuming')
  if p.returncode==0:
   if local.suffix=='.jsonl':
    lines=tmp.read_text().splitlines();rows=[]
    for line in lines:
     try:rows.append(json.loads(line))
     except ValueError:break
    old=[json.loads(l) for l in local.read_text().splitlines()]
    new={r['id']:r for r in rows}
    assert len(new)==len(rows)<=750 and all(0<=r['item']<25 for r in rows),'Duplicate/unexpected rows'
    assert all(new.get(r['id'])==r for r in old),'Would lose/change saved answers'
    tmp.write_text(''.join(json.dumps(r)+'\n' for r in rows))
   tmp.replace(local)
 rows=[json.loads(l) for l in (res/'confirm.jsonl').read_text().splitlines()]
 status={'records':len(rows),'missing':750-len(rows),'generated_tokens':sum(r['output_tokens'] for r in rows),'elapsed_GPU_minutes':(time.time()-a['start_epoch'])/60+a.get('base_GPU_minutes',0),'allocation_elapsed_GPU_minutes':(time.time()-a['start_epoch'])/60,'CU_estimate':(time.time()-a['start_epoch'])/3600*a['rate_attributed']+a.get('base_CU_estimate',0),'CU_upper':(time.time()-a['start_epoch'])/3600*a['rate_upper']+a.get('base_CU_upper',0),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (res/'progress.json').write_text(json.dumps(status,indent=2));print(json.dumps(status),flush=True)
 reason='complete' if len(rows)==750 else ('budget upper bound reached' if status['CU_upper']>=a['stop_at_upper_CU'] else None)
 if reason and not (res/'session_stopped.json').exists():
  if reason=='budget upper bound reached':
   terminate="from pathlib import Path\nimport os,json,signal,time\npid=json.loads(Path('/content/118b_launch.json').read_text())['pid']\ntry:\n assert os.getpgid(pid)==pid, 'Unexpected runner process group'\n os.killpg(pid,signal.SIGTERM)\n print('BUDGET_STOP_SENT',pid,time.time())\nexcept ProcessLookupError: print('RUNNER_ALREADY_EXITED',pid)\n"
   try:
    q=cmd(['exec','-s','b10-118b','--timeout','15'],input=terminate)
    (res/'budget_job_stop.txt').write_text(q.stdout+'\nreturncode='+str(q.returncode))
   except Exception as e:print('Budget runner-stop request:',type(e).__name__,flush=True)
   try:
    tmp=res/'final_checkpoint.partial';q=cmd(['download','-s','b10-118b','/content/exp118/confirm.jsonl',str(tmp)])
    if q.returncode==0:
     final=[]
     for line in tmp.read_text().splitlines():
      try:final.append(json.loads(line))
      except ValueError:break
     by={r['id']:r for r in final}
     assert len(by)==len(final)<=750 and all(by.get(r['id'])==r for r in rows)
     tmp.write_text(''.join(json.dumps(r)+'\n' for r in final));tmp.replace(res/'confirm.jsonl');rows=final
     status.update(records=len(rows),missing=750-len(rows),generated_tokens=sum(r['output_tokens'] for r in rows))
     if len(rows)==750:reason='complete'
   except Exception as e:print('Final sync retained prior validated snapshot:',type(e).__name__,flush=True)
  stop=cmd(['stop','-s','b10-118b'])
  if stop.returncode==0:
   stopped=time.time();status.update(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_GPU_minutes=(stopped-a['start_epoch'])/60+a.get('base_GPU_minutes',0),allocation_elapsed_GPU_minutes=(stopped-a['start_epoch'])/60,CU_estimate=(stopped-a['start_epoch'])/3600*a['rate_attributed']+a.get('base_CU_estimate',0),CU_upper=(stopped-a['start_epoch'])/3600*a['rate_upper']+a.get('base_CU_upper',0))
   (res/'session_stopped.json').write_text(json.dumps(dict(status,reason=reason,stop_output=stop.stdout,usage_before=usage.stdout,usage_after=cmd(['usage']).stdout),indent=2))
   (res/'progress.json').write_text(json.dumps(dict(status,run_state='stopped',reason=reason),indent=2))
 if not reason:
  checkfile=res/'last_remote_check.json'
  last=json.loads(checkfile.read_text()).get('epoch',0) if checkfile.exists() else 0
  if time.time()-last>=180:
   code="from pathlib import Path\nimport os,json,time,subprocess\npid=json.loads(Path('/content/118b_launch.json').read_text())['pid']\ntry: os.kill(pid,0); alive=True\nexcept ProcessLookupError: alive=False\nprint('REMOTE_CHECK',time.time(),'runner_alive',alive,'checkpoint_lines',len(Path('/content/exp118/confirm.jsonl').read_bytes().splitlines()))\nprint(subprocess.getoutput('nvidia-smi --query-gpu=name,utilization.gpu,memory.used --format=csv'))\nprint(subprocess.getoutput('tail -2 /content/118b.log'))\n"
   q=cmd(['exec','-s','b10-118b','--timeout','15'],input=code)
   with (res/'remote_heartbeat.log').open('a') as f:f.write(datetime.datetime.now(datetime.timezone.utc).isoformat()+' returncode='+str(q.returncode)+'\n'+q.stdout+'\n')
   checkfile.write_text(json.dumps({'epoch':time.time(),'returncode':q.returncode}))
 return status
if __name__=='__main__':main()
