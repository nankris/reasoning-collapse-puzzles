"""Audit saved confirmation without regenerating any model output."""
import json, subprocess
from pathlib import Path
from collections import Counter
from puzzles import grade, instance, prompt

ROOT = Path(__file__).resolve().parents[1]
rows = [json.loads(s) for s in (ROOT/'results/confirm.jsonl').read_text().splitlines()]
assert len({r['id'] for r in rows}) == len(rows), 'duplicate IDs'
# Prove that recovery preserved all previously committed responses verbatim.
original=[json.loads(l) for l in subprocess.check_output(['git','show','d3a1768:results/confirm.jsonl'],cwd=ROOT,text=True).splitlines()]
by_id={r['id']:r for r in rows}
assert len(original)==280 and all(by_id.get(r['id'])==r for r in original), 'original saved outputs changed'
cells = []
for family, levels in [('hanoi', range(3, 11)), ('checkers', range(2, 6))]:
    for n in levels:
        for mode in (False, True):
            cells.append((family, n, mode, 'moves'))
for n in (8, 9, 10):
    for mode in (False, True):
        cells.append(('hanoi', n, mode, 'program'))
counts = Counter()
for r in rows:
    cell = (r['family'], r['n'], r['thinking'], r['arm'])
    ci = cells.index(cell)
    assert r['seed'] == 118 + ci*1000 + r['item']
    seed = 918000 + 1000*(r['family'] == 'checkers') + r['n']*100 + r['item']
    x = instance(r['family'], r['n'], seed)
    assert x == r['instance']
    assert prompt(x, r['arm']) in r['prompt']
    assert r['model'] == 'Qwen/Qwen3-8B-AWQ'
    assert 0 <= r['thinking_tokens'] <= r['output_tokens'] <= 16384
    assert r['truncated'] == (r['finish_reason'] == 'length')
    final = r['output'].split('</think>', 1)[-1] if '</think>' in r['output'] else ('' if r['thinking'] else r['output'])
    ok, reason, valid = grade(final, x, r['arm'])
    assert ok == r['correct'], (r['id'], reason, r['verifier_reason'])
    assert valid == r['valid_moves']
    counts[cell] += 1
missing = {str(c):25-counts[c] for c in cells if counts[c] != 25}
audit = dict(records=len(rows), expected=750, complete=not missing, missing=missing,
             all_saved_outputs_reverified=True, seeds_and_instances_match=True, original_280_outputs_preserved_verbatim=True,
             total_output_tokens=sum(r['output_tokens'] for r in rows),
             total_prompt_tokens=sum(r['prompt_tokens'] for r in rows),
             truncations=sum(r['truncated'] for r in rows))
(ROOT/'results/audit.json').write_text(json.dumps(audit, indent=2))
print(json.dumps(audit, indent=2))
