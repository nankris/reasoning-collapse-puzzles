#!/usr/bin/env bash
# File downloads remain usable when the Colab execution websocket is unstable.
# Run from this experiment directory. Never creates a VM.
set -eu
phase="${1:-confirm}"
logphase="$phase"
if [ "$phase" = "pilot" ]; then logphase="pilot_stream"; fi
colab usage | tee -a results/usage.log
colab download -s puzzles-l4 "/content/puzzles/${phase}.jsonl" "results/${phase}.jsonl.partial"
mv "results/${phase}.jsonl.partial" "results/${phase}.jsonl"
colab download -s puzzles-l4 "/content/${logphase}.log" "figures/${phase}_run.txt.partial"
mv "figures/${phase}_run.txt.partial" "figures/${phase}_run.txt"
tail -8 "figures/${phase}_run.txt"
