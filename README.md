# Reasoning collapse on puzzles: Qwen3-8B on Tower of Hanoi and checker jumping (pilot and complete run)

A two-part series testing the "reasoning models collapse past a complexity threshold" claim on one open model (Qwen/Qwen3-8B-AWQ, thinking ON vs OFF), with synthetic Tower of Hanoi (n = 3-10) and checker-jumping puzzles.

| folder | what it is | verdict |
|---|---|---|
| [`pilot-run/`](pilot-run/) | First pre-registered run (pilot + partial confirmation, 285/750 responses before the Colab VM ended) | All four hypotheses INCONCLUSIVE (incomplete) |
| [`complete-run/`](complete-run/) | Completion attempt plus a post-hoc move-level re-analysis of the 417 saved responses ([RESULTS_move_level.md](complete-run/RESULTS_move_level.md)) | Registered H1-H4: INCONCLUSIVE (H2/H3 are locked by the truncation/censoring gate). Post-hoc, descriptive: 0/137 solved at n = 8-10. The first illegal move comes at a median of move 4 (max 11). After that the model loops and emits 3-4k moves against the 255-1,023 needed. Programs: 150/150 |

**What it shows, modestly.** For this model and this answer format, failure at large n is an execution failure at the very start followed by looping. It is not "ran out of tokens". The move-level finding is a post-hoc description of saved outputs, not a pre-registered test. It covers one quantized 8B model, one sample per item, and 25 relabelled copies of each puzzle per cell.

A ready-to-run T4 notebook for completing the missing cells would cost about 24 CU, but I don't recommend running it: it cannot change the registered verdict.

Issues found during review are in [`issues-found/`](issues-found/). Times in the folders are IST unless marked UTC.
