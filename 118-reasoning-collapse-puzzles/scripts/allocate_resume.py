"""Wait for an L4 slot, respecting the daily floor and other sessions."""
import subprocess,time,json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];end=time.time()+7200
next_try=datetime.datetime.fromisoformat('2026-10-18T19:29:10+00:00').timestamp()
def call(a):return subprocess.run(['colab',*a],capture_output=True,text=True,timeout=90)
while time.time()<end:
 if time.time()<next_try:time.sleep(min(30,next_try-time.time()));continue
 usage=call(['usage']);floor=float(Path('/workspace/work/tig/_batch9/cu_floor.txt').read_text().strip())
 import re
 m=re.search(r'Current balance:\s*([\d.]+)',usage.stdout)
 print(datetime.datetime.now(datetime.timezone.utc).isoformat(),usage.stdout,'floor',floor,flush=True)
 if not m or float(m.group(1))<=floor:next_try=time.time()+900;continue
 p=call(['new','--gpu','L4','-s','b9-118']);print(p.stdout,p.stderr,flush=True)
 if p.returncode==0:
  path=R/'results/recovery.json';r=json.loads(path.read_text());r['replacement_created_epoch']=time.time();r['replacement_created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();path.write_text(json.dumps(r,indent=2));break
 next_try=time.time()+300
else:
 (R/'results/resume_allocation_failed.json').write_text(json.dumps({'status':'two-hour allocation retry limit reached','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
