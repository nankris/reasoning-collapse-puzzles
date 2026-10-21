"""Execute only on b10-118b after uploads. No inference-setting changes."""
from pathlib import Path
import subprocess,json,time,shutil
root=Path('/content/exp118');root.mkdir(exist_ok=True)
checkpoint=Path('/content/confirm_checkpoint.jsonl')
rows=[json.loads(l) for l in checkpoint.read_text().splitlines()]
assert 285<=len(rows)<=750 and len({r['id'] for r in rows})==len(rows)
assert not Path('/content/118b_launch.json').exists(),'Inspect existing job before resuming'
shutil.copyfile(checkpoint,root/'confirm.jsonl')
log=open('/content/118b.log','a')
p=subprocess.Popen(['nohup','bash','-c','pip install vllm==0.32.0 transformers==5.18.0 > /content/118b_install.log 2>&1 && python -u /content/run_gpu.py --phase confirm'],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
record={'pid':p.pid,'launch_epoch':time.time(),'session':'b10-118b'}
Path('/content/118b_launch.json').write_text(json.dumps(record))
print(json.dumps(record))
