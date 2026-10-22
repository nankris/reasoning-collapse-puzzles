"""Render real saved files with a terminal-screenshot helper (set TERMSHOT_HELPER to its path)."""
from pathlib import Path
import os,subprocess,sys
R=Path(__file__).resolve().parents[1];helper=os.environ.get('TERMSHOT_HELPER','termshot.py')
shots=[('01_original.png','Original run: 150/150 passed, but the test was incomplete','results/legacy/first_result_excerpt.txt','150/150|INCONCLUSIVE|97.5',None),('02_missing.png','The flaw: 465 planned answers were missing','results/legacy/audit.json','records|expected|missing|25|20','1:29'),('03_fixed.png','Complete run: resumed answers saved one at a time','results/fixed_run_excerpt.txt','RESULT|16384|length',None),('04_verdict.png','Complete run: final registered statistics and verdict','results/final_stats.txt','VERDICT|PROVEN|DISPROVEN|INCONCLUSIVE|Saved responses',None)]
for name,title,src,pattern,lines in shots:
 if not (R/src).exists():continue
 args=[sys.executable,helper,str(R/'figures/screenshots'/name),'--title',title,'--file',str(R/src),'--highlight',pattern,'--width','90','--max','45']
 if lines:args+=['--lines',lines]
 subprocess.run(args,check=True)
