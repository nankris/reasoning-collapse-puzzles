"""Execute only on puzzles-l4-complete after uploads. No inference-setting changes."""
from pathlib import Path
import subprocess,json,time,shutil
root=Path('/content/puzzles');root.mkdir(exist_ok=True)
checkpoint=Path('/content/confirm_checkpoint.jsonl')
rows=[json.loads(l) for l in checkpoint.read_text().splitlines()]
assert 285<=len(rows)<=750 and len({r['id'] for r in rows})==len(rows)
assert not Path('/content/complete_launch.json').exists(),'Inspect existing job before resuming'
shutil.copyfile(checkpoint,root/'confirm.jsonl')
log=open('/content/complete.log','a')
p=subprocess.Popen(['nohup','bash','-c','pip install vllm==0.32.0 transformers==5.18.0 > /content/complete_install.log 2>&1 && python -u /content/run_gpu.py --phase confirm'],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
record={'pid':p.pid,'launch_epoch':time.time(),'session':'puzzles-l4-complete'}
Path('/content/complete_launch.json').write_text(json.dumps(record))
print(json.dumps(record))
