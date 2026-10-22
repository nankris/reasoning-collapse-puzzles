"""Restartable local polling daemon. Inference stays detached on Colab."""
from poll_once import main,R
import time,traceback,contextlib,fcntl,os
lock=(R/'results/watch.lock').open('w')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:raise SystemExit('Another watcher holds the lock')
(R/'results/watch.pid').write_text(str(os.getpid()))
while not (R/'results/session_stopped.json').exists():
 with (R/'results/watcher.log').open('a') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
  try:main()
  except Exception:traceback.print_exc()
 time.sleep(45)
