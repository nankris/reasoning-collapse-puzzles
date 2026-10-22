"""Recovery command, to be executed only on this experiment's VM."""
import os,signal,subprocess,time
try:os.kill(4330,signal.SIGKILL)
except ProcessLookupError:pass
print('orphan cleanup attempted',flush=True)
subprocess.Popen('nohup python -u /content/run_gpu.py --phase pilot > /content/pilot_stream.log 2>&1 < /dev/null &',shell=True,start_new_session=True)
print('pilot relaunched',flush=True)
