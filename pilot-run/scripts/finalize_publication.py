"""Finalize prose from saved results without changing the preregistration."""
import json
import sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'blog.md';s=p.read_text()
if '{{RESULTS}}' not in s:
 print('Publication already finalized; no changes made.');sys.exit(0)
s=s.replace('{{RESULTS}}','''The collapse experiment is **INCONCLUSIVE**. Only 285 of the planned 750 confirmation responses survived locally. Both Colab allocations were pruned, and the second interruption left too little of the six-CU allowance to finish the remaining sample after another setup. All four registered hypotheses remain inconclusive, including the claim that programs beat move lists. A completed program arm cannot supply the missing paired baseline.

![Verified accuracy and missing coverage](figures/accuracy.png)

Thinking ON solved 25/25 instances at both three and four disks; OFF solved 0/25 at three, four and five. At each individual level, the 95% Wilson interval is 86.7–100% for 25/25 and 0–13.3% for 0/25. Blank regions are missing measurements, not zero accuracy. The high-complexity move-list comparison is unavailable.

![Measured thinking tokens](figures/thinking_tokens.png)

For complete move-list cells, mean thinking tokens rose from 2,036 at three disks to 5,606 at four. That does not test the registered five-disk peak or ten-disk decline: both needed complete cells that I don't have. Program answers used about 1,839–1,987 thinking tokens across eight to ten disks.

![Length-limited outputs](figures/truncation.png)

OFF move lists hit the ceiling in 0/25, 1/25 and 3/25 responses at three, four and five disks. Every saved program answer finished below the ceiling. The five-disk OFF rate already exceeds the registered five-percent gate, although that level is outside H2's high-complexity range. Neither the plot nor the ten cap hits across all 285 saved outputs estimates truncation among missing requests.

The run saved 549,276 generated tokens and 48,566 prompt tokens, excluding the pilot and any lost in-flight work. Eleven of thirty cells are complete. Checker jumping has no saved confirmation outputs, so its generator validation is not a model result. The full count-and-interval table is supplied separately as `figures/table.png`.''')
s=s.replace('{{SURPRISES}}','''I got the execution budget wrong. Long generations and cache pressure made the planned 750-response matrix much more expensive than the short program answers suggested. The pilot itself stopped early. Losing two VMs then exposed a gap in recovery: detached GPU work survived a local interruption only until the remote allocation disappeared, and answers after the last local copy could not be recovered.

I also assumed that making the literal ten-disk answer fit would keep truncation a minor issue. Five saved ten-disk OFF answers all hit the ceiling. They are an incomplete, scheduling-selected slice, so I won't report their accuracy as a level estimate. They do show that a token-fit calculation alone cannot guarantee an uncensored experiment.

The predicted peak-and-fall pattern was not established. There is no license to rename four disks the peak or treat missing high levels as evidence of decline. The clean result is narrower: all six planned program cells completed successfully.''')
s=s.replace('{{CLOSING}}','''Timing: estimated 115 minutes; actual {{ACTUAL_MINUTES}} minutes including recovery gaps, on NVIDIA L4, at an estimated 4.484 CU (conservative bookkeeping upper estimate 4.665 CU).

The next test needs fewer cells or a better throughput pilot, durable remote checkpoints, and a budget validated against the longest responses. This run leaves the collapse debate open while documenting a useful capability: this model consistently wrote executable Hanoi procedures under the tested conditions.''')
p.write_text(s)
meta=json.loads((R/'results/confirm_meta.json').read_text())
with (R/'figures/colab_run.txt').open('a') as f:f.write('\nSAVED NVIDIA-SMI\n'+str(meta['gpu'])+'\n')
read=R/'README.md';s=read.read_text();s+='''

## Final outcome and second allocation loss

Final audit: **285/750** saved confirmation responses, **11/30** complete cells. All original 280 responses remain byte-for-byte equivalent as JSON records; all 285 grades, seeds and instances were reverified. No missing output is scored as a failure. **H1, H2, H3 and H4 are INCONCLUSIVE** under the frozen rules. The descriptive program endpoint is 150/150 verified successes (95% Wilson 97.5–100%), without the completed paired move-list baseline required by H4. Checker jumping has no saved confirmation outputs. Saved confirmation totals: 549,276 generated tokens, 48,566 prompt tokens, 10 cap hits; these exclude lost work and the pilot.

Final history records the replacement session pruned at 20:46:18 UTC. At final resume, `colab sessions` returned no active session and `colab stop -s puzzles-l4` reported session not found. No third allocation was made: the remaining budget could not support another setup and 465 missing responses at observed throughput. Local polling had last copied results at 20:09 UTC, so later unsaved work is unavailable. Remote nohup protects against local process loss, not VM pruning. This is an incomplete confirmatory experiment, not a demonstrated collapse or a disproven source paper.

GPU: NVIDIA L4 (23,034 MiB); estimated **4.484 CU**, conservative bookkeeping upper estimate **4.665 CU**, counting both full allocations through prune events. Rate attribution is 1.54 CU/hour from before/after allocation observations; this is not a per-experiment invoice. Exact timestamps and estimates: results/session_stopped.json. Hardware and runtime proof: figures/colab_run.txt. Final artifacts: writeup.md, blog.md, three analysis charts, table.png and reviewed Excalidraw diagram.

Timing: estimated 115 minutes; actual {{ACTUAL_MINUTES}} minutes, NVIDIA L4, 4.484 estimated CU (4.665 conservative upper). Stages and included recovery gaps: results/timing.json. The original estimate and start timestamp have been preserved.
''';read.write_text(s)
