import sys,json,time,datetime,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'results/timing.json';t=json.loads(p.read_text());now=time.time();start=datetime.datetime.fromisoformat(t['start_ist']).timestamp()
t['end_ist']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat();t['actual_minutes']=(now-start)/60;t['per_stage_minutes']['writeup']=(now-t['eval_end_epoch'])/60
p.write_text(json.dumps(t,indent=2));subprocess.run([sys.executable,str(R/'scripts/publish.py')],cwd=R,check=True)
r=R/'README.md';s=r.read_text().split('\n## Final results\n')[0];s=s.replace('actual pending; NVIDIA L4 planned, CU pending.',f"actual {t['actual_minutes']:.1f} minutes; NVIDIA L4, {t['CU_estimate']:.3f} estimated CU.");s+='\n## Final results\n\n```text\n'+(R/'results/final_stats.txt').read_text()+'\n```\n\n'+f"Timing: estimated 230 minutes; actual {t['actual_minutes']:.1f} minutes, NVIDIA L4, {t['CU_estimate']:.3f} estimated CU ({t['CU_upper']:.3f} conservative upper).\n\nSee writeup.md for results and intervals; blog.md is the publication draft. Screenshots listed above are real file/log renders. Source experiment remained read-only; its original raw checkpoint was recovered from Git. Only puzzles-l4-complete was allocated and stopped. The Excalidraw renderer was unavailable, so diagram.png uses the permitted matplotlib fallback; an editable diagram.excalidraw is also supplied.\n"
r.write_text(s)

(R/'results/publication_status.json').write_text(json.dumps({'state':'reviewed','records':json.loads((R/'results/hypothesis_results.json').read_text())['records'],'review_end_ist':t['end_ist']},indent=2))
