Raw model answers: confirm.jsonl and pilot.jsonl, each including rendered prompt,
instance, output text, model-reported token counts, finish reason and verifier score.
Preregistration: preregistration.json plus committed README.md (ba49376).
summary.csv/json: complete and partial cells, marked explicitly; partial-cell scores
are completion-time-selected and excluded from publication accuracy charts.
hypothesis_results.json: only fixed, complete-sample confirmatory tests.
audit.json: independent replay of saved answers through the deterministic verifier.
usage*.log, recovery*.json/log, colab_history.jsonl: operations and cost provenance.
Never infer missing model answers or scores from the expected sample size.
