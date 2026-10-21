# Experiment 118b: complete the registered reasoning-collapse test

Question: Does the original Qwen3 puzzle test show the registered three-regime pattern when all 750 planned responses are available?

This is completion of experiment 118, not a new independent replication. The original writeup reported **285/750** saved responses, **11/30** complete cells, and all four hypotheses INCONCLUSIVE. Its descriptive program result was **150/150** successes (95% Wilson 97.5–100.0%). No original answer is regenerated.

## Frozen protocol and decision rule

The full original preregistration is preserved in results/legacy/README.md and results/preregistration.json. Copy its model, puzzles, prompts, generation seeds, item IDs, settings and analysis exactly. Qwen/Qwen3-8B-AWQ, BF16 activations/KV, vLLM 0.32.0, 20,480 context, 16,384 output tokens; temperature .6, top_p .95, top_k 20; thinking ON/OFF; 25 instances per cell, 30 cells, 750 total. Public synthetic Hanoi n=3..10 and checker jumping n=2..5, no private data or paid APIs. This task explicitly requires the original synthetic data rather than substituting an HF benchmark.

H1: ON minus OFF Hanoi n=4,5,6 accuracy >10 pp, 75 pairs. H2: both move modes Hanoi n>=7 accuracy <10%, 100 responses/mode, both 95% Wilson upper bounds <10%, and <=5% truncation in every relevant cell. H3: thinking-token ratio n5/n3 >=1.2 and n10/n5 <=.8, both bootstrap CIs clear their margins, <=5% truncation at each level. H4: program minus moves accuracy >50 pp at Hanoi n=8,9,10, 150 pairs. Paired stratified 10,000-resample percentile bootstrap for H1/H4, independent bootstrap ratios for H3. PROVEN when the registered bounds clear the margin, DISPROVEN when opposite bounds exclude it, otherwise INCONCLUSIVE. Censoring gates override H2/H3. Combined pattern PROVEN only if H1-H3 all pass, DISPROVEN if any is disproven, otherwise INCONCLUSIVE. No new hypotheses or pilot.

Margins and sample sizes come from 118's frozen pilot-based protocol, retained unchanged even if they miss. Missing items are fresh relative to the saved pilot and confirmation outputs; 285 old outputs remain in the planned sample. This is not a fresh 750-item replication.

## Decisions

- The source working tree lacked confirm.jsonl. Recover its exact committed HEAD blob read-only into THIS folder, preserve a second immutable copy, and hash it. Do not restore or edit the source folder.
- Generate only 465 absent IDs. Preserve original runner and analysis before any operational edits. Use /content/exp118 on our own b10-118b VM, never any other VM.
- Resume original 32-request engine settings; no model, prompt, decoding or verifier changes. New VM batching can affect floating-point samples. Preserve that limitation.
- Detached remote process, per-response fsync; poll and download often. Stop our session at completion, failure, or the cumulative 7.85 CU upper guard, retaining 0.15 CU of shutdown headroom. Hard cap 8 CU. Do not stop b10-ctl.
- Account aggregate balances include other experiments. Attribute rate from allocation change and conservatively use >=2 CU/hour if unavailable; record uncertainty.
- Missing Excalidraw tools: use matplotlib pipeline diagram as explicitly allowed.

## Planned artifacts

README.md, writeup.md, blog.md, scripts, raw results, 150-dpi accuracy/thinking/truncation charts, table.png, pipeline diagram. Real screenshots: figures/screenshots/01_original.png (earlier output), 02_missing.png (coverage audit), 03_fixed.png (resumed runner), 04_verdict.png (final fixed-rule output).

Timing: estimated 230 minutes (setup 15, GPU run 180, eval 10, writeup 25), actual pending; NVIDIA L4 planned, CU pending. results/timing.json records wall clock and stages.

Sources: https://arxiv.org/abs/2506.06941 and https://arxiv.org/abs/2506.09250 (corrected v2).

## Recovery without changing the experiment

After source /workspace/tools/setup.sh, run colab sessions and inspect b10-118b with a short colab exec. Check /content/118b.log, /content/118b_launch.json and the runner process before launching anything. If it is running, resume scripts/watch.py locally. scripts/run_gpu.py automatically skips every saved ID. Do not allocate another VM while this session exists.

If our VM is pruned, first preserve all local results and usage. Recheck the daily floor and remaining eight-CU budget before considering a replacement. Upload the current results/confirm.jsonl as /content/confirm_checkpoint.jsonl, plus run_gpu.py and puzzles.py. launch_remote.py accepts an intact 285–750-row checkpoint on a fresh VM and refuses a duplicate launch marker. Existing VM restarts need process inspection before any marker cleanup. Accumulate allocation costs rather than resetting the eight-CU cap.

Historical operational scripts under scripts/original_ops are provenance only and must not be executed: they address the original b9-118 session.

Checkpoint transport refinement during inference: compress a read-only snapshot of the VM JSONL before download. Long raw answers otherwise make repeated transfers slow. This does not edit the runner, live checkpoint, requests or measurements; local preservation checks still reject missing or changed old records.

Cost refinement during inference: observed allocation delta 3.16 minus 1.62 = 1.54 CU/hour; departures/arrivals of the other L4 reproduce those account rates. Two-decimal display implies at most .01 CU/hour rounding uncertainty on the difference. Use 1.56 CU/hour upper instead of the initial 1.62, and stop at 7.85 upper CU, reserving .15 CU for polling/shutdown. This operational change gives the unchanged test more completion time and remains below eight CU. See results/allocation.json for the initial guard and refinement timestamp.

Local watcher recovery at 00:26 UTC: the polling command had exited with status 143. The remote runner was still busy at 100% GPU utilization and had continued to 307 responses. Restarted only local polling as a separate process session with a single-watcher file lock. No GPU job or request was restarted, and all allocation time remains counted.

Transport recovery: repeated file-based remote snapshot execution timed out while direct raw checkpoint downloads succeeded. Reverted polling to direct downloads and validated/promoted the recovered 307-row checkpoint. This changes transport only; the GPU runner continued throughout.

Recovery note: colab status reports the Jupyter kernel as IDLE while detached inference runs. Use the live runner log, process list and nvidia-smi to determine GPU activity; do not start another runner based on that kernel status.

Allocation timestamp audit: the CLI session_created event is 2026-10-19 23:27:09.662407 UTC. Replace the provisional 23:26:40 anchor, which was 29.7 seconds early, with this exact creation event for elapsed allocation time and CU bookkeeping. Both point and upper estimates still count the entire allocation. Evidence: results/session_created.json.

## Replacement allocation after confirmed session loss

At 00:53:06 UTC the CLI recorded session_terminated with reason pruned; the VM was absent and the account rate fell by 1.54 CU/hour. The stop attempt reported session not found. Only 317 locally retained answers exist; later in-flight work cannot be reconstructed. Preserve these and resume only the 433 missing IDs on a replacement b10-118b L4. Count the entire first allocation through the CLI detection timestamp, conservatively, and carry its cost forward. The original runner, sampling, prompts, seeds, puzzle generator and analysis remain unchanged. The local poller now raises on failed checkpoint download rather than labelling an old file a fresh successful snapshot.

Story decision: 118 correctly reported INCONCLUSIVE. This follow-up addresses its missing coverage and the potential over-reading of its 150/150 program endpoint; it does not invent an earlier claim that collapse had been proven.

Runtime monitoring: supplement direct checkpoint downloads with a short stdin-based colab exec every three minutes. Record the actual runner PID status, checkpoint line count and GPU utilization in results/remote_heartbeat.log. File-based snapshot execution had timed out; these read-only stdin checks use the working interface. They do not alter inference.

Budget-stop cleanup: if the cumulative upper CU guard is reached, signal only this VM’s detached runner process group, copy a final validated checkpoint, then stop b10-118b. All cleanup time is included in allocation accounting. This captures durable answers that finished after the preceding regular poll; unfinished answers remain missing.

Reporting decision after partial results: if the registered H4 sample remains incomplete, use the observed cap-hit count from the fully completed nine/ten-disk cells as a clearly labelled descriptive headline. This does not alter any hypothesis, margin, threshold, sample size or formal verdict, and does not substitute a new hypothesis test for H4. Report total coverage beside it.
