"""Transport-only snapshot. Does not interact with inference or edit its checkpoint."""
import gzip,os
from pathlib import Path
src=Path('/content/puzzles/confirm.jsonl');dst=Path('/content/complete_checkpoint.jsonl.gz')
b=src.read_bytes();tmp=dst.with_suffix('.tmp');tmp.write_bytes(gzip.compress(b,compresslevel=1));tmp.replace(dst)
print('SNAPSHOT bytes',len(b),'compressed',dst.stat().st_size,'complete_lines',b.count(b'\n'))
