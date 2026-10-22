# Addendum: move-level failure analysis (post-hoc, descriptive), 21 Oct 2026 IST
**This is not one of the registered H1-H4 tests.** It re-reads the 417 saved responses in `results/confirm.jsonl`; no new inference. Script: `scripts/move_level_analysis.py`. Outputs: `results/move_level/{per_response.jsonl,summary.json}`, `figures/move_level/valid_prefix_vs_required.png`.

Method: extract every `["X","Y"]` pair from the final answer (the text after `</think>`), simulate it from the start state, and record the first illegal move, the valid-prefix length, agreement with the optimal solution, and the repetition period in the last 60 moves.

| n | thinking | responses | solved | capped (16k) | median moves emitted | median legal moves before 1st error | max | looping |
|---|---|---|---|---|---|---|---|---|
| 3 | OFF | 25 | 0 | 0 | 7 | 7 (legal, but 14/25 end on the wrong peg) | 7 | 0 |
| 3 | ON | 25 | 25 | 0 | 7 | 7 | 7 | 0 |
| 4 | OFF | 25 | 0 | 1 | 15 | 4 | 13 | 1 |
| 4 | ON | 25 | 25 | 0 | 15 | 15 | 15 | 0 |
| 5 | OFF | 25 | 0 | 3 | 30 | 4 | 13 | 19 |
| 5 | ON | 5 (partial cell) | 2 | 1 | 31 | 20 | 31 | 0 |
| 8 | OFF | 25 | 0 | 25 | 4,095 | 4 | 10 | 25 |
| 8 | ON | 12 (partial) | 0 | 12 | 3,158 | 4 | 7 | 10 |
| 9 | OFF | 25 | 0 | 25 | 4,095 | 4 | 9 | 25 |
| 9 | ON | 25 | 0 | 25 | 3,231 | 4 | 11 | 22 |
| 10 | OFF | 25 | 0 | 25 | 4,095 | 4 | 7 | 25 |
| 10 | ON | 25 | 0 | 25 | 3,245 | 4 | 9 | 24 |

**Finding.** At n ≥ 8 the cap hits are *not* "ran out of room". The model emits 3,000-4,000 moves, which is far more than the 255-1,023 required. Its first illegal move comes at a median of move 4 (never later than move 11), and it then repeats a short cycle (period 3 in most responses) until the 16k-token cap. With thinking ON, 58/62 responses at n = 8-10 *finished thinking* and still made an illegal move by about move 4. This is execution failure followed by degenerate looping. It is not the token-budget censoring that the H2/H3 gates were designed to detect. It supports reading the collapse as real for this model and format, and argues against the "just out of tokens" explanation. The caveat: one quantized 8B model, one sample per item, and 25 relabelled copies of the same puzzle per cell.

**Implication for the remaining GPU work.** Completing the missing moves cells (n = 6/7) would cost about 24 CU on a T4 by the Colab-job estimate, because every response runs to the 16k cap. It cannot change the registered verdict: H2/H3 are locked INCONCLUSIVE by the censoring gate. It is not recommended.
