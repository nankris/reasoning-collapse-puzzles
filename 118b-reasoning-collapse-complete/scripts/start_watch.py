"""Start local polling independently of the shell. watch.py prevents duplicates."""
import subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
with (R/'results/watch_daemon.log').open('a') as log:
 p=subprocess.Popen(['/workspace/tools/mlenv/bin/python','-u',str(R/'scripts/watch.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print('Started watcher process',p.pid,'(duplicate watchers exit under the file lock)')
