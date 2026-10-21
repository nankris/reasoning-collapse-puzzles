# 01: the registered verdict was locked INCONCLUSIVE whether or not the run completed
- H2 needs ≤5% cap hits in every n≥7 cell, and H3 needs ≤5% truncation at n=10. The observed n=8/9/10 cells are 100% capped, so H2 and H3 can never resolve, and the combined verdict stays INCONCLUSIVE whatever the missing cells show.
- The gate assumes that cap hits mean budget censoring. The move-level analysis (`RESULTS_move_level.md`) shows they are runaway loops after an early illegal move. So the gate mislabels an execution failure as censoring.
- Status: documented. Spending ~24 T4 CU to fill n=6/7 is not recommended.
