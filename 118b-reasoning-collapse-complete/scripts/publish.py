"""Build publication artifacts from measured results, never from planned counts."""
import json,datetime,re
from analyze import wilson
from pathlib import Path
R=Path(__file__).resolve().parents[1];H=json.loads((R/'results/hypothesis_results.json').read_text());A=json.loads((R/'results/audit.json').read_text());T=json.loads((R/'results/timing.json').read_text())
S=json.loads((R/'results/summary.json').read_text());N=H['records'];complete=N==750
v=H['overall_three_regime_verdict'];h4=H['H4'];h1=H['H1'];h3=H['H3'];h2=H['H2']
def pct(x):return f'{100*x:.1f}%'
def pp(x):return f'{100*x:.1f}'
def interval(ci,scale=100):return f'{ci[0]:.3f} to {ci[1]:.3f}' if scale==1 else f'{scale*ci[0]:.1f} to {scale*ci[1]:.1f}'
def result(h):
 if 'estimate' in h:return f"{pp(h['estimate'])} percentage points (95% CI {interval(h['ci'])})"
 return 'not estimable under the full-sample rule'
headline=f"{pp(h4['estimate'])} percentage points" if 'estimate' in h4 else f'{N}/750 saved responses'
headline_explain='program advantage over complete move lists at 8–10 disks' if 'estimate' in h4 else 'coverage achieved before the stop'
high_complete=[x for x in S if x['family']=='hanoi' and x['n'] in [9,10] and x['arm']=='moves' and x['N']==25]
cap_statement=''
if len(high_complete)==4:
 cap_n=sum(x['N'] for x in high_complete);cap_k=sum(x['truncated'] for x in high_complete);cap_interval=wilson(cap_k,cap_n)
 cap_statement=f"Descriptive censoring endpoint: {cap_k}/{cap_n} nine- and ten-disk move-list responses hit the ceiling (95% Wilson {interval(cap_interval)}%). This does not replace the registered H1-H4 tests. Coverage is {N}/750."
 if 'estimate' not in h4:
  headline=f'{cap_k}/{cap_n} hit the token cap';headline_explain=f'nine- and ten-disk move-list responses; descriptive 95% Wilson {interval(cap_interval)}%, with {N}/750 responses retained overall'
timing=f"Timing: estimated 230 minutes; actual {T.get('actual_minutes',0):.1f} minutes; NVIDIA L4; {T.get('CU_estimate',0):.3f} estimated CU ({T.get('CU_upper',0):.3f} conservative upper)."
if 'actual_minutes' not in T:timing='Timing: estimated 230 minutes; actual duration and final CU pending; NVIDIA L4; inference is still running.'
main=[]
for n in range(3,11):
 row=[str(n),str(2**n-1)]
 for arm,mode in [('moves',False),('moves',True),('program',False),('program',True)]:
  s=next((s for s in S if s['family']=='hanoi' and s['n']==n and s['arm']==arm and s['thinking']==mode),None)
  row.append('not planned' if arm=='program' and n<8 else ('missing' if s is None else (f"partial {s['N']}/25" if s['N']<25 else f"{s['correct']}/25 [{100*s['ci_low']:.1f}, {100*s['ci_high']:.1f}]%")))
 main.append('| '+' | '.join(row)+' |')
table='| Disks | Minimum moves | Moves OFF | Moves ON | Program OFF | Program ON |\n|---|---:|---|---|---|---|\n'+'\n'.join(main)
h2_detail='; '.join(f"{'ON' if m['thinking'] else 'OFF'} {m['correct']}/{m['n']}, 95% Wilson {interval(m['ci'])}%" for m in h2.get('modes',[]))
counts=(f"Programs passed {h4['program_correct']}/{h4['program_N']}; move lists passed {h4['moves_correct']}/{h4['moves_N']}, on the same paired instances." if 'program_N' in h4 else 'The planned 150-pair program-versus-moves comparison remains incomplete.')
n10=[x for x in S if x['family']=='hanoi' and x['n']==10 and x['arm']=='moves' and x['N']==25]
n10_statement=''
if len(n10)==2:
 bits=[f"{'ON' if x['thinking'] else 'OFF'} {x['correct']}/25 (95% Wilson {100*x['ci_low']:.1f}–{100*x['ci_high']:.1f}%)" for x in sorted(n10,key=lambda x:x['thinking'])]
 caps=sum(x['truncated'] for x in n10);progs=[x for x in S if x['family']=='hanoi' and x['n']==10 and x['arm']=='program'];pc=sum(x['correct'] for x in progs);pn=sum(x['N'] for x in progs)
 n10_statement='At ten disks, the completed move-list cells scored '+', '.join(bits)+f'. {caps}/50 move-list responses hit the output ceiling. The retained ten-disk programs passed {pc}/{pn}. This level-specific description does not replace H4’s registered eight-to-ten-disk comparison.'
checker_N=sum(x['N'] for x in S if x['family']=='checkers')
checker_summary=f'Checker jumping has {checker_N}/200 saved responses; incomplete cells do not supply accuracy estimates.'
if checker_N==200:
 from analyze import wilson
 bits=[]
 for mode in [False,True]:
  cells=[x for x in S if x['family']=='checkers' and x['thinking']==mode];n=sum(x['N'] for x in cells);k=sum(x['correct'] for x in cells)
  bits.append(f"{'ON' if mode else 'OFF'} {k}/{n} (95% Wilson {interval(wilson(k,n))}%)")
 checker_summary='Checker jumping, descriptively pooled over its four levels: '+', '.join(bits)+'. These are supplementary results, outside H1-H4.'
def hyp_line(k):
 x=H[k]
 if k=='H1':body=result(x)
 elif k=='H4':body=result(x)+'; '+counts
 elif k=='H2':body=(h2_detail+'; ' if h2_detail else '')+x.get('note','Planned sample incomplete.')
 elif 'late_over_peak' in x:body=f"Peak/low thinking-token ratio {x['peak_over_low']:.3f}, 95% CI {interval(x['rise_ratio_ci'],1)}; late/peak {x['late_over_peak']:.3f}, 95% CI {interval(x['ratio_ci'],1)}; maximum relevant truncation {pct(x['truncation'])}."
 else:body=x.get('note','Planned sample incomplete.')
 return f"- **{k}: {x['verdict']}**. "+body
hyp='\n'.join(hyp_line(k) for k in ['H1','H2','H3','H4'])
takeaway="Qwen3's saved Hanoi programs can produce complete, checked solutions. "+({'INCONCLUSIVE':"We couldn't establish reasoning collapse under the original rules.",'DISPROVEN':'The registered three-part collapse prediction did not hold in this setup.','PROVEN':'All three parts of the registered collapse prediction passed in this setup.'}[v])

write=f'''# 118b: completing the reasoning-collapse responses

**Three-regime verdict: {v}. H4 representation verdict: {h4['verdict']}.**

**Headline: {headline}**, {headline_explain}.

Plain-English takeaway: {takeaway}

{table}

{cap_statement}

{n10_statement}

Table brackets are nominal 95% Wilson accuracy intervals. Per-cell bootstrap intervals, checker results, nontruncated counts and token measurements are in results/summary.csv. figures/table.png renders the main table for Substack.

{hyp}

The original result was 285/750 responses, 11/30 complete cells, all four hypotheses INCONCLUSIVE; its descriptive endpoint was 150/150 programs passed (95% Wilson 97.5–100.0%). This completion preserves all 285 original records and requests only absent IDs. Final coverage: {N}/750; {sum(s['N']==25 for s in S)}/30 complete cells. Saved outputs contain {H['total_prompt_tokens']:,} prompt tokens and {H['total_output_tokens']:,} generated tokens, with {H['truncations']} cap hits. These are model-tokenizer measurements for saved 8B confirmation responses. They exclude unsaved/in-flight work and the separate 4B pilot. {checker_summary} New-run totals are {H['total_output_tokens']-549276:,} generated and {H['total_prompt_tokens']-48566:,} prompt tokens, excluding the 549,276 generated and 48,566 prompt tokens already saved by 118.

CIs use the frozen 10,000-resample analysis, paired within strata for H1/H4. H2 uses Wilson bounds, H3 independent bootstrap ratios. These are four nominal tests, without multiplicity correction. Percentile bootstrap intervals can degenerate at boundary outcomes; the registered calculation is retained and per-endpoint Wilson intervals expose remaining uncertainty. The full machine-readable application is results/hypothesis_results.json.

Caveats: one quantized model; renamed/nonce-varied isomorphic puzzles; original OFF decoding was not separately optimized; OFF already failed the easy baseline; program-plus-interpreter changes the output contract. Completion is not independent replication. GPU batch composition and restart timing can change floating-point samples. Original model/prompt/settings remain fixed. The censoring gate applies to the entire output, including the final answer. Our 16,384-token ceiling is smaller than the [source paper’s 64,000-token setup](https://arxiv.org/html/2506.06941v1). Censoring prevents causal claims of voluntary shortening; missing responses are never counted as failures.

{timing}

Cost counts only b10-118b across its allocations, including setup and conservatively counting a lost VM through CLI prune detection. Earlier allocation records are in results/allocations.json. The rate is attributed from the 1.54 CU/hour change on allocation, with a 1.56 CU/hour upper rate. Account totals include other work. Original 118's 4.484 estimated CU is historical and excluded from this follow-up's eight-CU cap. Evidence: results/allocation.json, results/session_stopped.json, results/usage.log and figures/colab_run.txt.

Reproduce offline: source /workspace/tools/setup.sh; run scripts/puzzles.py, scripts/audit.py, scripts/analyze.py, scripts/hypotheses.py using /workspace/tools/mlenv/bin/python. Source protocol and results are in results/legacy/. Preregistration commit: 7307a3b. For remote recovery inspect b10-118b and /content/118b.log before launching; scripts/poll_once.py copies checkpoints and enforces completion/budget stop.

Sources: [Shojaee et al.](https://arxiv.org/abs/2506.06941v1), [Lawsen corrected v2](https://arxiv.org/abs/2506.09250v2).
'''
(R/'writeup.md').write_text(write)
if 'estimate' in h4:
 finding=f"Qwen3's Hanoi programs gained {pp(h4['estimate'])} points at eight to ten disks"
elif len(high_complete)==4:
 finding=f"{cap_k}/{cap_n} nine- and ten-disk move lists hit Qwen3's token cap"
else:
 finding='The puzzle continuation still cannot establish reasoning collapse'
if complete:completion='I generated the 465 absent responses and reached all 750 planned answers.'
else:completion=f"The follow-up saved {N-285} additional responses, reaching {N}/750; the registered sample remains incomplete."

late=(f"The middle-to-low thinking-token ratio was {h3['peak_over_low']:.3f}, with a 95% interval of {interval(h3['rise_ratio_ci'],1)}. The late-to-middle thinking-token ratio was {h3['late_over_peak']:.3f}, with a 95% interval of {interval(h3['ratio_ci'],1)}. The maximum truncation rate across its compared levels was {pct(h3['truncation'])}." if 'late_over_peak' in h3 else 'The full-sample token-ratio test could not be estimated from the saved coverage.')
runtime_sentence=f"The measured duration was {T['actual_minutes']:.1f} minutes." if 'actual_minutes' in T else 'The run is still in progress; its final duration is pending.'
result_heading='The result, with the missing denominator restored' if complete else 'The result, and the remaining missing answers'
blog=f'''# {finding}

A continuation of one interrupted Qwen3 evaluation, with the original predictions left intact.

A model writes a recursive Hanoi solver, the interpreter runs it, and every disk reaches the right peg. Ask the same model to spell out every move, and the story can look very different. That difference matters whenever an engineer must choose between generating a long action sequence and generating a small program that produces it.

The popular claim behind this test comes from [The Illusion of Thinking](https://arxiv.org/abs/2506.06941v1): reasoning models face a “complete accuracy collapse beyond certain complexities.” That is a consequential claim about deploying models on long workflows. I wanted to know which part our own experiment could actually establish.

My expectation, registered before confirmation in experiment 118, was specific: thinking would help in the middle, both modes would fail at larger Hanoi puzzles, and measured thinking would first rise and then fall. A separate prediction said executable programs would recover more than 50 percentage points of accuracy on the largest puzzles. Those predictions survived into this follow-up unchanged.

## The first result looked cleaner than the experiment was

The earlier writeup's headline was **“150/150 executable Hanoi answers passed”**, with **“95% Wilson interval 97.5–100.0%.”** That is an excellent-looking endpoint. It is also only one side of a planned comparison.

The same writeup reported **“285/750”** saved confirmation responses and **“11/30”** complete cells. All four registered hypotheses were **INCONCLUSIVE**. Checker jumping had no saved confirmation responses. For ten-disk move lists, only five OFF answers had finished, and that partial cell was excluded from publication accuracy estimates.

![The original program output](figures/screenshots/01_original.png)
*Screenshot 1: the original writeup reported 150/150 program successes while keeping the registered verdict INCONCLUSIVE.*

I got suspicious because the attractive program number was available while its paired move-list baseline was largely absent. Short programs finish quickly. Long enumerations can sit in flight when a runtime disappears. Looking only at finished answers can therefore select by response length before anyone calculates an accuracy rate.

The flaw was coverage. The earlier writeup correctly kept the verdict inconclusive. What would have been misleading was treating the successful program endpoint as a completed demonstration of the whole collapse story.

![Coverage audit](figures/screenshots/02_missing.png)
*Screenshot 2: the verifier audit lists the missing cells. There were 465 absent responses, rather than 465 observed failures.*

## What I tested

This is a continuation, not an independent replication. The raw checkpoint was missing from the old working tree, but Git still held its committed copy. I recovered that exact 285-response checkpoint into a new experiment folder, checked that every recovered answer retained its original record, and committed the protocol before new inference. {completion} The newly requested items were previously unobserved planned items, separate from the old pilot; the final analysis deliberately retains the old responses.

The confirmation model was **Qwen/Qwen3-8B-AWQ**, with four-bit AWQ weights and BF16 activations and cache. It ran on an **NVIDIA L4** through vLLM 0.32.0. The original pilot used Qwen/Qwen3-4B; I did not rerun or expand that pilot to improve the predictions.

The public synthetic tasks were Tower of Hanoi at three through ten disks and checker jumping at two through five checkers per color. Every cell planned 25 responses. Thinking ON and OFF shared temperature 0.6, top-p 0.95, top-k 20, a 20,480-token context, and a 16,384-token output ceiling. Programs were requested only for Hanoi at eight through ten disks, in both modes.

![Completion pipeline](figures/diagram.png)
*The pipeline preserves old answers, requests missing IDs, and applies the same deterministic checks and registered tests to saved responses.*

A state simulator replayed moves and checked the final board. Generated programs ran in a restricted, resource-limited subprocess, then went through that same simulator. This measures a model-plus-interpreter system in the program arm. It does not give the model credit for mentally executing its own recursion.

The runner saved each finished response immediately, including the rendered prompt, generation seed, actual token counts, finish reason, and verifier result. It ran detached on the GPU VM, while local polling copied checkpoints. That protects against losing a terminal connection, although it cannot guarantee survival if the GPU VM itself is pruned.

## {result_heading}

**The headline is {headline}: {headline_explain}.** The registered three-regime verdict is **{v}**, and the separate representation verdict is **{h4['verdict']}**.

{n10_statement}

![Exact accuracy](figures/accuracy.png)
*Exact success rates by puzzle size and output contract. Error bars are 95% Wilson intervals; incomplete cells are excluded.*

![Main results table](figures/table.png)
*Exact counts and Wilson intervals for Hanoi; incomplete cells are labelled explicitly.*

The medium-complexity thinking advantage was {result(h1)}. Its frozen target was more than ten percentage points. The high-complexity program comparison was {result(h4)}, against a target above fifty points. {counts} {checker_summary}

The analysis resampled paired items within fixed strata 10,000 times, rather than treating the two output contracts as unrelated samples.

![Thinking length](figures/thinking_tokens.png)
*Measured tokens before the thinking delimiter, with bootstrap uncertainty. These are observed lengths, not a direct measurement of reasoning quality.*

{late} The original rule required at least a 20% early rise and at least a 20% late fall. Moving the peak after seeing the graph would answer a different, easier question.

![Token-cap hits](figures/truncation.png)
*The cap-hit chart identifies cells whose apparent failures or token lengths cannot support an uncensored collapse claim.*

That gate matters. The compact canonical ten-disk answer was measured at 4,094 tokens in the original setup, but fitting the answer does not guarantee that thinking plus the answer fits. A response stopped by the ceiling is a task failure under this output contract. It does not establish that the model freely chose to stop thinking. A separate higher-budget test would be needed to learn whether additional tokens improve the answer.

![Resumed run output](figures/screenshots/03_fixed.png)
*Screenshot 3: real RESULT lines from the resumed runner, with token counts and termination reasons.*

![Final registered statistics](figures/screenshots/04_verdict.png)
*Screenshot 4: the frozen hypothesis program's final output. The raw JSON accompanies the post.*

## What surprised me, and what I got wrong

The original expectation tried to connect several different measurements into one story. Completing coverage tests that story; it does not entitle me to simplify it. The individual verdicts are H1 **{h1['verdict']}**, H2 **{h2['verdict']}**, H3 **{h3['verdict']}**, and H4 **{h4['verdict']}**. A missed threshold stays missed, and a censoring gate stays binding.

I also underestimated the runtime. My plan was 230 minutes. {runtime_sentence} Coverage reached {N}/750 under the eight-CU ceiling. The original sample sizes and decoding settings stayed fixed. Long responses and runtime recovery consumed the available compute, and the remaining missing answers remain missing.

The other warning was already present at three disks: OFF failed all 25 answers while ON passed all 25. That weak OFF baseline limits any narrative about falling from competence. It also cautions against treating this exact prompt and shared sampling recipe as the best possible non-thinking configuration.

## What I would do in production

1. Use a tested deterministic solver when one already exists. For model-generated plans, prefer a small executable program when the task is naturally algorithmic. Validate its output against domain rules before applying actions.
2. Save each request independently, including failures, finish reasons, and tokenizer counts. Build the denominator from planned IDs, not whatever files happen to arrive first.
3. Separate invalid actions, unfinished goals, and token-cap failures in dashboards. They suggest different interventions.
4. Freeze the comparison and its stopping rules before paying for the full evaluation. Replotting a more convenient peak is exploration and deserves a new test.

5. Measure long-response throughput and check easy baselines before funding a full evaluation. Include recovery time in the budget.

## Limits worth keeping

This is one quantized model on renamed, nonce-varied versions of the same mathematical structures. Those are repeated sampling trials, not hundreds of unrelated reasoning problems. Restarted batching can change floating-point samples even with unchanged seeds. The intervals are nominal per hypothesis, without a familywise correction. Percentile bootstrap intervals can have zero width at all-success or all-failure endpoints. I retained the registered calculation and show Wilson accuracy intervals in the table.

Our 16,384-token ceiling is also smaller than the [original paper’s 64,000-token setup](https://arxiv.org/html/2506.06941v1). The censoring gate applies to the whole response, including the final answer, even if its thinking delimiter appeared earlier.

The [corrected rebuttal](https://arxiv.org/abs/2506.09250v2) motivates checking output contracts and token limits, but this experiment does not adjudicate all models or puzzles in either paper. It also does not convert a model-plus-interpreter result into proof of unaided reasoning ability.

{timing} The earlier run's cost is historical and excluded from this follow-up's cap. Full measurements, the original protocol, preserved answers, logs, and the table image live beside the post.

Before trusting a collapse chart, check what finished, what was missing, and what the runtime stopped. Those distinctions can change what the same failure rate means.

Code: <repo link placeholder>
'''
assert '—' not in blog
(R/'blog.md').write_text(blog)
print('Blog words:',len(blog.split()));print('Verdict:',v);print('Headline:',headline,headline_explain)
