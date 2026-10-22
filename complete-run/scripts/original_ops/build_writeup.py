"""Build publication summary from final, audited checkpoints only."""
import json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];res=R/'results'
assert (res/'session_stopped.json').exists(),'Stop and record GPU before final reporting'
summ=json.loads((res/'summary.json').read_text());h=json.loads((res/'hypothesis_results.json').read_text());audit=json.loads((res/'audit.json').read_text());stop=json.loads((res/'session_stopped.json').read_text());recovery=json.loads((res/'recovery.json').read_text())
assert audit['records']==h['records']
rows=[json.loads(l) for l in (res/'confirm.jsonl').read_text().splitlines()]
programs=[r for r in rows if r['arm']=='program'];pk=sum(r['correct'] for r in programs)
from analyze import wilson
pci=wilson(pk,len(programs))
timing=json.loads((res/'timing.json').read_text())
def cell(n,arm,mode):
 ss=[s for s in summ if s['family']=='hanoi' and s['n']==n and s['arm']==arm and s['thinking']==mode]
 if not ss:return 'not planned' if arm=='program' and n<8 else 'not completed'
 s=ss[0]
 if not s['complete']:return f"incomplete ({s['N']}/25), not scored here"
 return f"{s['correct']}/25 ({100*s['accuracy']:.0f}%; {100*s['ci_low']:.1f}–{100*s['ci_high']:.1f}%)"
text=f'''# Qwen3 puzzle execution and the limits of this test

**Verdict: {h['overall_three_regime_verdict']}** for the registered three-regime collapse pattern. H4 representation verdict: **{h['H4']['verdict']}**.

**Headline number: {pk}/{len(programs)} executable Hanoi answers passed** at eight to ten disks, pooling both modes (95% Wilson interval {100*pci[0]:.1f}–{100*pci[1]:.1f}%). This descriptive endpoint does not replace the registered paired representation test.

Plain-English takeaway: Qwen3 can produce compact Hanoi programs that a deterministic interpreter executes successfully. This experiment's collapse conclusion is limited by incomplete samples and/or length censoring, so exact move-list failures cannot by themselves establish that the model stopped reasoning.

## Main results

All scored table cells contain 25 responses. Brackets are nominal 95% Wilson accuracy intervals; per-level percentile bootstrap intervals are also in `results/summary.csv`. An ordinary bootstrap is degenerate at 0/25 and 25/25, so Wilson intervals display the remaining uncertainty. Missing requests are never failures, and partial cells are excluded because completion order selects for shorter answers.

| Disks | Minimum moves | Moves OFF | Moves ON | Program OFF | Program ON |
|---|---:|---|---|---|---|
'''
for n in range(3,11):text+=f"| {n} | {2**n-1} | {cell(n,'moves',False)} | {cell(n,'moves',True)} | {cell(n,'program',False)} | {cell(n,'program',True)} |\n"
text+='\nTable image: `figures/table.png`.\n\n## Fixed hypotheses\n\n'
labels={'H1':'ON minus OFF accuracy, Hanoi 4–6, >10 percentage points','H2':'Both move-list modes below 10% at Hanoi 7–10; per-cell censoring gate','H3':'Thinking tokens 5/3 >=1.2 and 10/5 <=0.8; per-cell censoring gate','H4':'Program minus moves accuracy, Hanoi 8–10, >50 percentage points'}
for k,label in labels.items():text+=f"- **{k}: {h[k]['verdict']}**, {label}. Full estimates, CIs and gating reasons: `results/hypothesis_results.json`.\n"
text+=f'''
## Coverage, tokens and operational limits

Saved **{len(rows)}/750** planned confirmation responses. {sum(s['complete'] for s in summ)}/30 cells are complete. Completed outputs used {h['total_prompt_tokens']:,} prompt tokens and **{h['total_output_tokens']:,} generated tokens**, with {h['truncations']} length-limited responses. These totals exclude unsaved/in-flight generation and the separate pilot. The 4B pilot saved 18/36 planned responses; unfinished pilot work was not scored.

The confirmation uses Qwen/Qwen3-8B-AWQ, vLLM 0.32.0, BF16 activations/KV, a 20,480-token context and the same 16,384-token generation ceiling in both modes. Sampling is temperature 0.6, top-p 0.95, top-k 20. The cap includes thinking plus final output. The compact ten-disk canonical answer measured 4,094 tokenizer tokens, but this did not guarantee enough allowance for a model's reasoning. Cap hits are an experimental limitation, not evidence of voluntary shortening. Non-truncated counts and successes are recorded separately per cell in the raw summary.

Public synthetic puzzle generators, no private data or paid APIs. Hanoi peg names and irrelevant nonces vary; the mathematical structures remain isomorphic. Checker levels 2–5 are constructively solvable, but their inference coverage is reported in the raw summaries rather than assumed complete. This is one quantized open model, not a replication of every model in either source paper. The OFF mode was not separately sampling-tuned and already failed the three-disk baseline. Programs add an interpreter and test a different output contract. No causal claim about general reasoning ability follows from this comparison.

The original VM was pruned; 280 intact responses were restored. Resumed scheduling prioritizes high Hanoi move cells. A five-request concurrency phase saved five cap-limited answers in 757.6 seconds; all were retained, then the original 32-request configuration was restored for throughput. This can change batching-dependent samples; no saved output was regenerated. All IDs, prompts, instance seeds, generation seeds, samples, token limits, metrics and margins stayed fixed. Preregistration commit: `ba49376`.

GPU: NVIDIA L4, 23,034 MiB. Cost: **{stop['estimated_CU']:.3f} CU estimated**, conservative upper bookkeeping **{stop['conservative_upper_CU']:.3f} CU**, below the hard six-CU cap. The rate was attributed from the change in account aggregate usage when this L4 was allocated; Colab does not expose a per-experiment invoice here. The first allocation is conservatively counted through the CLI prune timestamp. Both allocations were pruned (19:22:58 and 20:46:18 UTC); the final stop command found no session. The last local checkpoint was at 20:09 UTC. No third allocation was made because the remaining budget could not complete 465 missing outputs after another setup. Final session evidence: `results/session_stopped.json`; hardware/timing logs: `figures/colab_run.txt` and full phase logs.

Timing: estimated 115 minutes; actual {timing.get('actual_minutes','pending')} minutes, NVIDIA L4, {stop['estimated_CU']:.3f} estimated CU. Stage durations and wall-time definitions are in `results/timing.json`. Queue waits and recovery pauses are included in elapsed time; drafting the write-up overlapped inference.

## Figures and reproduction

- `figures/accuracy.png`: complete-cell accuracy versus puzzle size, with 95% Wilson intervals.
- `figures/thinking_tokens.png`: mean measured thinking tokens with 10,000-resample bootstrap intervals. Missing levels are not connected.
- `figures/truncation.png`: complete-cell cap-hit rates, separately by thinking mode.
- `figures/table.png`: main results table as an image.
- `figures/diagram.excalidraw` and `figures/diagram.png`: editable setup diagram and rendered version.

Run `python scripts/puzzles.py`, `scripts/audit.py`, `scripts/analyze.py`, `scripts/hypotheses.py`, and `scripts/build_writeup.py` in that order. Analysis uses saved outputs and does not start a GPU. The GPU runner checks completed IDs and checkpoints each answer; inspect sessions and restore the result file before launching it on puzzles-l4 only.

Sources: [Shojaee et al., 2025](https://arxiv.org/abs/2506.06941), [Lawsen, corrected v2](https://arxiv.org/abs/2506.09250).
'''
(R/'writeup.md').write_text(text)
print('Built writeup from',len(rows),'audited outputs')
