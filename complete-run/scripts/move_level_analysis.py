#!/usr/bin/env python3
"""POST-HOC, DESCRIPTIVE move-level failure analysis of Hanoi move-list responses (21 Oct 2026 IST).
Not part of the registered H1-H4 tests. For each move-list response: extract the [from,to] pairs from the final answer
(the text after </think> if present; else whole output), simulate from the start state, and record the first illegal move,
the length of the valid prefix, whether the valid prefix matches the optimal solution, and repetition (looping)."""
import json,re,collections
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results/move_level'; FIG=ROOT/'figures/move_level'
OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
PAIR=re.compile(r'\[\s*"([A-Za-z])"\s*,\s*"([A-Za-z])"\s*\]')
def optimal(n,s,t,a):
    if n==0: return []
    return optimal(n-1,s,a,t)+[(s,t)]+optimal(n-1,a,t,s)
def simulate(n,labels,moves):
    src,tgt,aux=labels; pegs={src:list(range(n,0,-1)),tgt:[],aux:[]}
    for i,(f,t) in enumerate(moves):
        if f not in pegs or t not in pegs: return i,'unknown_peg'
        if not pegs[f]: return i,'empty_source'
        if pegs[t] and pegs[t][-1]<pegs[f][-1]: return i,'larger_on_smaller'
        pegs[t].append(pegs[f].pop())
    done=len(pegs[tgt])==n
    return len(moves),('solved' if done else 'ran_out')
def loop_period(moves,window=60):
    tail=moves[-window:] if len(moves)>=window else moves
    for p in range(1,13):
        if len(tail)>=3*p and all(tail[i]==tail[i-p] for i in range(p,len(tail))): return p
    return None
rows=[]
for l in (ROOT/'results/confirm.jsonl').read_text().splitlines():
    r=json.loads(l)
    if r['arm']!='moves': continue
    out=r['output']; ans=out.split('</think>')[-1] if '</think>' in out else (out if not r['thinking'] else '')
    in_think=r['thinking'] and '</think>' not in out
    mv=[(a.upper(),b.upper()) for a,b in PAIR.findall(ans)]
    n=r['n']; labels=r['instance']['labels']  # labels = [source, target, auxiliary] per prompt wording
    opt=optimal(n,*labels); valid,why=simulate(n,labels,mv)
    pref_opt=0
    for a,b in zip(mv,opt):
        if a!=b: break
        pref_opt+=1
    rows.append(dict(id=r['id'],n=n,thinking=r['thinking'],correct=r['correct'],truncated=r['truncated'],output_tokens=r['output_tokens'],
        thinking_tokens=r.get('thinking_tokens'),cap_in_thinking=bool(in_think),n_moves_emitted=len(mv),required=2**n-1,
        valid_prefix=valid,stop_reason=why if mv else ('no_answer_cap_in_thinking' if in_think else 'no_moves'),
        optimal_prefix=pref_opt,loop_period=loop_period(mv) if len(mv)>=30 else None))
(OUT/'per_response.jsonl').write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
summ=[]
for (n,th),g in sorted(collections.defaultdict(list,{k:[x for x in rows if (x['n'],x['thinking'])==k] for k in {(x['n'],x['thinking']) for x in rows}}).items()):
    vp=np.array([x['valid_prefix'] for x in g]); op=np.array([x['optimal_prefix'] for x in g])
    summ.append(dict(n=n,thinking=th,responses=len(g),correct=sum(x['correct'] for x in g),capped=sum(bool(x['truncated']) for x in g),
        cap_in_thinking=sum(x['cap_in_thinking'] for x in g),required_moves=2**n-1,
        median_moves_emitted=float(np.median([x['n_moves_emitted'] for x in g])),
        median_valid_prefix=float(np.median(vp)),max_valid_prefix=int(vp.max()),median_optimal_prefix=float(np.median(op)),
        median_valid_fraction=float(np.median(vp/(2**n-1))),
        stop_reasons=dict(collections.Counter(x['stop_reason'] for x in g)),
        looping=sum(1 for x in g if x['loop_period']),loop_periods=dict(collections.Counter(x['loop_period'] for x in g if x['loop_period']))))
(OUT/'summary.json').write_text(json.dumps(summ,indent=2)); print(json.dumps(summ,indent=1))
# figure: valid prefix vs required
fig,ax=plt.subplots(figsize=(8,4.8))
for th,c,mk in [(False,'#c0392b','o'),(True,'#20639b','s')]:
    g=[x for x in rows if x['thinking']==th]
    xs=np.array([x['n'] for x in g])+(0.12 if th else -0.12)+np.random.default_rng(0).uniform(-.05,.05,len(g))
    ax.scatter(xs,[max(x['valid_prefix'],0.8) for x in g],s=14,alpha=.55,color=c,marker=mk,label=f"thinking {'ON' if th else 'OFF'}: legal moves before first error")
ns=sorted({x['n'] for x in rows}); ax.plot(ns,[2**n-1 for n in ns],'k--',label='moves required (2^n − 1)')
ax.set_yscale('log'); ax.set_xlabel('disks (n)'); ax.set_ylabel('moves (log scale)'); ax.set_xticks(ns)
ax.set_title('Qwen3-8B on Tower of Hanoi: how far does a move list get before the first illegal move?',fontsize=10); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(FIG/'valid_prefix_vs_required.png',dpi=170)
