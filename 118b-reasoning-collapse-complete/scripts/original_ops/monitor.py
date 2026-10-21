"""Copy detached VM checkpoints; stop ONLY b9-118 when all outputs are saved.

Run in a foreground exec session after setup.sh. Restart after sandbox reboot.
The independent conservative account-budget watcher must also be running.
"""
import datetime, json, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT/'results'

def command(args, timeout=45):
    return subprocess.run(['colab', *args], capture_output=True, text=True, timeout=timeout)

while not (RES/'session_stopped.json').exists():
    try:
        p = command(['usage'])
        with (RES/'usage_monitor.log').open('a') as f:
            f.write(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n'+p.stdout+'\n')
        for remote, local in [('/content/exp118/confirm.jsonl', RES/'confirm.jsonl'),
                              ('/content/confirm.log', ROOT/'figures/confirm_run.txt')]:
            tmp = local.with_suffix(local.suffix+'.partial')
            d = command(['download', '-s', 'b9-118', remote, str(tmp)])
            if d.returncode == 0:
                # Ignore a torn final line; never replace a good checkpoint with it.
                if local.suffix == '.jsonl':
                    for line in tmp.read_text().splitlines():
                        json.loads(line)
                tmp.replace(local)
        rows = [json.loads(s) for s in (RES/'confirm.jsonl').read_text().splitlines()]
        print(datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'saved',len(rows),'tokens',sum(r['output_tokens'] for r in rows),flush=True)
        if len(rows) == 750 and len({r['id'] for r in rows}) == 750:
            before = command(['usage']).stdout
            stop = command(['stop', '-s', 'b9-118'])
            if stop.returncode != 0:
                print('Stop failed; will retry:',stop.stderr[-300:],flush=True)
                time.sleep(10)
                continue
            after = command(['usage']).stdout
            record = dict(reason='all 750 planned outputs checkpointed locally',
                          time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                          stop_returncode=stop.returncode, stop_output=stop.stdout,
                          usage_before=before, usage_after=after)
            (RES/'session_stopped.json').write_text(json.dumps(record,indent=2))
            print(json.dumps(record),flush=True)
            break
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError) as e:
        print(type(e).__name__,str(e)[:200],flush=True)
    time.sleep(45)
