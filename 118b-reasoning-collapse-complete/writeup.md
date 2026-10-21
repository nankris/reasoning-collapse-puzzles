# 118b: completing the reasoning-collapse responses

**Three-regime verdict: INCONCLUSIVE. H4 representation verdict: INCONCLUSIVE.**

**Headline: 100/100 hit the token cap**, nine- and ten-disk move-list responses; descriptive 95% Wilson 96.3 to 100.0%, with 380/750 responses retained overall.

Plain-English takeaway: Qwen3's saved Hanoi programs can produce complete, checked solutions. We couldn't establish reasoning collapse under the original rules.

| Disks | Minimum moves | Moves OFF | Moves ON | Program OFF | Program ON |
|---|---:|---|---|---|---|
| 3 | 7 | 0/25 [0.0, 13.3]% | 25/25 [86.7, 100.0]% | not planned | not planned |
| 4 | 15 | 0/25 [0.0, 13.3]% | 25/25 [86.7, 100.0]% | not planned | not planned |
| 5 | 31 | 0/25 [0.0, 13.3]% | partial 5/25 | not planned | not planned |
| 6 | 63 | missing | missing | not planned | not planned |
| 7 | 127 | missing | missing | not planned | not planned |
| 8 | 255 | missing | missing | 25/25 [86.7, 100.0]% | 25/25 [86.7, 100.0]% |
| 9 | 511 | 0/25 [0.0, 13.3]% | 0/25 [0.0, 13.3]% | 25/25 [86.7, 100.0]% | 25/25 [86.7, 100.0]% |
| 10 | 1023 | 0/25 [0.0, 13.3]% | 0/25 [0.0, 13.3]% | 25/25 [86.7, 100.0]% | 25/25 [86.7, 100.0]% |

Descriptive censoring endpoint: 100/100 nine- and ten-disk move-list responses hit the ceiling (95% Wilson 96.3 to 100.0%). This does not replace the registered H1-H4 tests. Coverage is 380/750.

At ten disks, the completed move-list cells scored OFF 0/25 (95% Wilson 0.0–13.3%), ON 0/25 (95% Wilson 0.0–13.3%). 50/50 move-list responses hit the output ceiling. The retained ten-disk programs passed 50/50. This level-specific description does not replace H4’s registered eight-to-ten-disk comparison.

Table brackets are nominal 95% Wilson accuracy intervals. Per-cell bootstrap intervals, checker results, nontruncated counts and token measurements are in results/summary.csv. figures/table.png renders the main table for Substack.

- **H1: INCONCLUSIVE**. not estimable under the full-sample rule
- **H2: INCONCLUSIVE**. Planned sample incomplete; missing requests were not scored as failures and no partial-sample hypothesis test was performed
- **H3: INCONCLUSIVE**. Planned sample incomplete; missing requests were not scored as failures and no partial-sample hypothesis test was performed
- **H4: INCONCLUSIVE**. not estimable under the full-sample rule; The planned 150-pair program-versus-moves comparison remains incomplete.

The original result was 285/750 responses, 11/30 complete cells, all four hypotheses INCONCLUSIVE; its descriptive endpoint was 150/150 programs passed (95% Wilson 97.5–100.0%). This completion preserves all 285 original records and requests only absent IDs. Final coverage: 380/750; 15/30 complete cells. Saved outputs contain 64,732 prompt tokens and 2,105,756 generated tokens, with 105 cap hits. These are model-tokenizer measurements for saved 8B confirmation responses. They exclude unsaved/in-flight work and the separate 4B pilot. Checker jumping has 0/200 saved responses; incomplete cells do not supply accuracy estimates. New-run totals are 1,556,480 generated and 16,166 prompt tokens, excluding the 549,276 generated and 48,566 prompt tokens already saved by 118.

CIs use the frozen 10,000-resample analysis, paired within strata for H1/H4. H2 uses Wilson bounds, H3 independent bootstrap ratios. These are four nominal tests, without multiplicity correction. Percentile bootstrap intervals can degenerate at boundary outcomes; the registered calculation is retained and per-endpoint Wilson intervals expose remaining uncertainty. The full machine-readable application is results/hypothesis_results.json.

Caveats: one quantized model; renamed/nonce-varied isomorphic puzzles; original OFF decoding was not separately optimized; OFF already failed the easy baseline; program-plus-interpreter changes the output contract. Completion is not independent replication. GPU batch composition and restart timing can change floating-point samples. Original model/prompt/settings remain fixed. The censoring gate applies to the entire output, including the final answer. Our 16,384-token ceiling is smaller than the [source paper’s 64,000-token setup](https://arxiv.org/html/2506.06941v1). Censoring prevents causal claims of voluntary shortening; missing responses are never counted as failures.

Timing: estimated 230 minutes; actual duration and final CU pending; NVIDIA L4; inference is still running.

Cost counts only b10-118b across its allocations, including setup and conservatively counting a lost VM through CLI prune detection. Earlier allocation records are in results/allocations.json. The rate is attributed from the 1.54 CU/hour change on allocation, with a 1.56 CU/hour upper rate. Account totals include other work. Original 118's 4.484 estimated CU is historical and excluded from this follow-up's eight-CU cap. Evidence: results/allocation.json, results/session_stopped.json, results/usage.log and figures/colab_run.txt.

Reproduce offline: source /workspace/tools/setup.sh; run scripts/puzzles.py, scripts/audit.py, scripts/analyze.py, scripts/hypotheses.py using /workspace/tools/mlenv/bin/python. Source protocol and results are in results/legacy/. Preregistration commit: 7307a3b. For remote recovery inspect b10-118b and /content/118b.log before launching; scripts/poll_once.py copies checkpoints and enforces completion/budget stop.

Sources: [Shojaee et al.](https://arxiv.org/abs/2506.06941v1), [Lawsen corrected v2](https://arxiv.org/abs/2506.09250v2).
