"""Conservative named-session wall-time budget guard; no other VM is modified."""
import subprocess,re,time,json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
START=datetime.datetime.fromisoformat('2026-10-18T17:45:18.795755+00:00')
def call(args,timeout=25):
 return subprocess.run(['colab',*args],capture_output=True,text=True,timeout=timeout)
while not (R/'results/session_stopped.json').exists():
 now=datetime.datetime.now(datetime.timezone.utc)
 elapsed_hours=(now-START).total_seconds()/3600
 try:usage=call(['usage'],15).stdout
 except subprocess.TimeoutExpired:usage='usage query timed out\n'
 with (R/'results/usage_watch.log').open('a') as f:f.write(now.isoformat()+'\n'+usage+'\n')
 m=re.search(r'Current balance:\s*([\d.]+)',usage)
 rate=re.search(r'Usage rate:\s*([\d.]+)',usage)
 if elapsed_hours*2>=5.5 or (rate and float(rate.group(1))>3.10):
  for remote,local in [('/content/puzzles/confirm.jsonl','results/confirm.jsonl'),('/content/puzzles/pilot.jsonl','results/pilot.jsonl'),('/content/confirm.log','figures/confirm_run.txt'),('/content/pilot_stream.log','figures/pilot_stream_run.txt')]:
   dest=R/local;tmp=dest.with_suffix(dest.suffix+'.budget_partial')
   try:
    p=call(['download','-s','puzzles-l4',remote,str(tmp)],15)
    if p.returncode==0:
     if dest.suffix=='.jsonl':
      for line in tmp.read_text().splitlines():json.loads(line)
     tmp.replace(dest)
   except (subprocess.TimeoutExpired,ValueError):pass
  try:p=call(['stop','-s','puzzles-l4'],30)
  except subprocess.TimeoutExpired:
   time.sleep(5);continue
  if p.returncode:
   time.sleep(5);continue
  try:after=call(['usage'],15).stdout
  except subprocess.TimeoutExpired:after='usage query timed out\n'
  (R/'results/session_stopped.json').write_text(json.dumps({'reason':'conservative 2-CU/hour named-session guard: 5.5 CU or aggregate rate increase','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'balance_at_trigger':float(m.group(1)) if m else None,'stop_output':p.stdout,'stop_returncode':p.returncode,'usage_before':usage,'usage_after':after},indent=2));break
 time.sleep(45)
