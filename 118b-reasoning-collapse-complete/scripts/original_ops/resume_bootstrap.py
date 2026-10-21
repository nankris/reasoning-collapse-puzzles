"""Run ON the replacement b9-118 VM after uploading checkpoint and scripts."""
import subprocess,time,json
from pathlib import Path
print(subprocess.getoutput('nvidia-smi'))
checkpoint=Path('/content/exp118/confirm.jsonl')
assert checkpoint.exists() and len(checkpoint.read_text().splitlines())>=280, 'Restore and validate checkpoint before launching'
marker=Path('/content/resume_launch.json')
if marker.exists():
 print('Launch marker exists; inspect processes/logs before doing anything else:',marker.read_text())
else:
 log=open('/content/resume.log','a')
 p=subprocess.Popen(['nohup','bash','-c','pip install vllm==0.32.0 > /content/resume_install.log 2>&1 && python -u /content/run_gpu.py --phase confirm'],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
 marker.write_text(json.dumps({'pid':p.pid,'start_epoch':time.time()}))
 print(marker.read_text())
