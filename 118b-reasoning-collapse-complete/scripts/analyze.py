"""Resumable analysis of saved model outputs. No inference or network access."""
import json,csv,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];RES=ROOT/'results';FIG=ROOT/'figures'
plt.rcParams.update({'font.size':12,'axes.titlesize':15,'axes.labelsize':12,'figure.dpi':150,'savefig.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
RNG=np.random.default_rng(118)
def boot(v):
 v=np.asarray(v,dtype=float)
 if not len(v):return [float('nan')]*2
 return np.quantile(v[RNG.integers(0,len(v),(10000,len(v)))].mean(1),[.025,.975]).tolist()
def wilson(k,n):
 z=1.95996398454;p=k/n;d=1+z*z/n
 m=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [max(0,m-h),min(1,m+h)]
def rows():return [json.loads(l) for l in (RES/'confirm.jsonl').read_text().splitlines() if l.strip()]
def canvas(summary):
 has_checkers=any(s['N']==25 and s['family']=='checkers' for s in summary)
 fig,axs=plt.subplots(1,2 if has_checkers else 1,figsize=(12,4.8) if has_checkers else (8.5,5.3))
 if not has_checkers:fig.text(.5,.012,'Checker jumping: no complete 25-response cells; missing outputs are not failures.',ha='center',fontsize=10,color='#536572')
 return fig,np.atleast_1d(axs)

def format_axes(axs,summary,thinking_only=False):
 from matplotlib.ticker import MaxNLocator
 for ax,fam in zip(axs,['hanoi','checkers']):
  levels=list(range(3,11)) if fam=='hanoi' else list(range(2,6))
  ax.set_xlim(levels[0]-.4,levels[-1]+.4);ax.set_xticks(levels)
  has=any(s['N']==25 and s['family']==fam and s['arm']=='moves' and (s['thinking'] or not thinking_only) for s in summary)
  if not has:
   ax.text(.5,.5,'No complete move-list cells\nMissing responses are not failures',transform=ax.transAxes,ha='center',va='center',fontsize=13,color='#536572',bbox=dict(facecolor='white',edgecolor='#d5dce2',pad=12))
  ax.xaxis.set_major_locator(MaxNLocator(integer=True))

def main():
 data=rows();groups={}
 fields=['id','phase','model','family','n','arm','thinking','item','seed','correct','truncated','finish_reason','verifier_reason','valid_moves','prompt_tokens','output_tokens','thinking_tokens','final_tokens']
 with (RES/'raw_metrics.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(data)
 from collections import Counter
 (RES/'failure_reasons.json').write_text(json.dumps(dict(Counter(r['verifier_reason'] for r in data if not r['correct'])),indent=2))
 for r in data:groups.setdefault((r['family'],r['n'],r['arm'],r['thinking']),[]).append(r)
 summary=[]
 for (family,n,arm,thinking),rs in sorted(groups.items()):
  correct=sum(r['correct'] for r in rs);N=len(rs);ci=wilson(correct,N)
  t=[r['thinking_tokens'] for r in rs];ti=boot(t);aci=boot([r['correct'] for r in rs])
  summary.append(dict(family=family,n=n,arm=arm,thinking=thinking,N=N,complete=N==25,correct=correct,accuracy=correct/N,ci_low=ci[0],ci_high=ci[1],bootstrap_accuracy_low=aci[0],bootstrap_accuracy_high=aci[1],truncated=sum(r['truncated'] for r in rs),mean_thinking_tokens=np.mean(t),thinking_ci_low=ti[0],thinking_ci_high=ti[1],mean_output_tokens=np.mean([r['output_tokens'] for r in rs]),nontruncated_N=sum(not r['truncated'] for r in rs),nontruncated_correct=sum(r['correct'] and not r['truncated'] for r in rs)))
 with (RES/'summary.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
 (RES/'summary_note.txt').write_text('Only N=25 cells are confirmatory. Partial-cell summaries describe completed responses and may be biased by completion time; they are excluded from publication plots and accuracy table.\n')
 (RES/'summary.json').write_text(json.dumps(summary,indent=2))
 colors={False:'#c16b29',True:'#126782'}
 fig,axs=canvas(summary)
 for ax,fam in zip(axs,['hanoi','checkers']):
  for mode in (False,True):
   ss=[s for s in summary if s['N']==25 and s['family']==fam and s['arm']=='moves' and s['thinking']==mode]
   grid=list(range(3,11)) if fam=='hanoi' else list(range(2,6));by={s['n']:s for s in ss};xx=np.array(grid);yy=np.array([by[n]['accuracy'] if n in by else np.nan for n in grid]);lo=np.array([by[n]['ci_low'] if n in by else np.nan for n in grid]);hi=np.array([by[n]['ci_high'] if n in by else np.nan for n in grid])
   ax.errorbar(xx+(.04 if mode else -.04),yy*100,yerr=np.array([yy-lo,hi-yy])*100,marker='o',capsize=3,color=colors[mode],label='Moves, thinking ON' if mode else 'Moves, thinking OFF')
  if fam=='hanoi':
   for mode in (False,True):
    ss=[s for s in summary if s['N']==25 and s['family']==fam and s['arm']=='program' and s['thinking']==mode]
    grid=list(range(3,11)) if fam=='hanoi' else list(range(2,6));by={s['n']:s for s in ss};xx=np.array(grid);yy=np.array([by[n]['accuracy'] if n in by else np.nan for n in grid]);lo=np.array([by[n]['ci_low'] if n in by else np.nan for n in grid]);hi=np.array([by[n]['ci_high'] if n in by else np.nan for n in grid])
    ax.errorbar(xx+(.07 if mode else -.07),yy*100,yerr=np.array([yy-lo,hi-yy])*100,marker='s',linestyle='--',capsize=3,color=colors[mode],alpha=.7,label='Program, thinking ON' if mode else 'Program, thinking OFF')
  ax.set(title='Tower of Hanoi' if fam=='hanoi' else 'Checker jumping',xlabel='Disks' if fam=='hanoi' else 'Checkers per color',ylabel='Verified complete solutions (%)',ylim=(-4,104));ax.grid(alpha=.15);ax.legend(fontsize=10)
 format_axes(axs,summary)
 fig.suptitle('Qwen3-8B AWQ: move lists versus programs',fontsize=17);fig.tight_layout(rect=(0,.05,1,1));fig.savefig(FIG/'accuracy.png');plt.close(fig)
 fig,axs=canvas(summary)
 for ax,fam in zip(axs,['hanoi','checkers']):
  ss=[s for s in summary if s['N']==25 and s['family']==fam and s['arm']=='moves' and s['thinking']]
  grid=list(range(3,11)) if fam=='hanoi' else list(range(2,6));by={s['n']:s for s in ss};xx=grid;yy=np.array([by[n]['mean_thinking_tokens'] if n in by else np.nan for n in grid]);lo=np.array([by[n]['thinking_ci_low'] if n in by else np.nan for n in grid]);hi=np.array([by[n]['thinking_ci_high'] if n in by else np.nan for n in grid])
  ax.errorbar(xx,yy,yerr=[yy-lo,hi-yy],color=colors[True],marker='o',capsize=4,label='Move list, thinking ON')
  ps=[s for s in summary if s['N']==25 and s['family']==fam and s['arm']=='program' and s['thinking']]
  if ps:
   py=np.array([s['mean_thinking_tokens'] for s in ps]);pl=np.array([s['thinking_ci_low'] for s in ps]);ph=np.array([s['thinking_ci_high'] for s in ps])
   ax.errorbar([s['n'] for s in ps],py,yerr=[py-pl,ph-py],color='#608c42',marker='s',linestyle='--',capsize=4,label='Program, thinking ON')
  ax.legend(fontsize=10)
  ax.set(title='Tower of Hanoi' if fam=='hanoi' else 'Checker jumping',xlabel='Disks' if fam=='hanoi' else 'Checkers per color',ylabel='Mean tokens before </think>');ax.grid(alpha=.15)
 format_axes(axs,summary,True)
 fig.suptitle('Thinking tokens by size and output contract',fontsize=17);fig.tight_layout(rect=(0,.05,1,1));fig.savefig(FIG/'thinking_tokens.png');plt.close(fig)
 fig,axs=canvas(summary)
 for ax,fam in zip(axs,['hanoi','checkers']):
  for mode in (False,True):
   ss=[s for s in summary if s['N']==25 and s['family']==fam and s['arm']=='moves' and s['thinking']==mode]
   grid=list(range(3,11)) if fam=='hanoi' else list(range(2,6));by={s['n']:s for s in ss}
   ax.plot(grid,[100*by[n]['truncated']/by[n]['N'] if n in by else np.nan for n in grid],marker='o',color=colors[mode],label='Thinking ON' if mode else 'Thinking OFF')
  ax.set(title='Tower of Hanoi' if fam=='hanoi' else 'Checker jumping',xlabel='Disks' if fam=='hanoi' else 'Checkers per color',ylabel='Outputs hitting 16,384-token cap (%)',ylim=(-3,103));ax.grid(alpha=.15);ax.legend(fontsize=10)
 format_axes(axs,summary)
 fig.suptitle('How often did outputs reach the token cap?',fontsize=17);fig.tight_layout(rect=(0,.05,1,1));fig.savefig(FIG/'truncation.png');plt.close(fig)
 # Main publication table, Hanoi move-list modes and program arms.
 table=[]
 for n in range(3,11):
  row=[str(n),str(2**n-1)]
  for arm,mode in [('moves',False),('moves',True),('program',False),('program',True)]:
   ss=[s for s in summary if s['family']=='hanoi' and s['n']==n and s['arm']==arm and s['thinking']==mode]
   row.append('not tested' if arm=='program' and n<8 else ('not completed' if not ss else (f"incomplete ({ss[0]['N']}/25)" if ss[0]['N']!=25 else f"{ss[0]['correct']}/{ss[0]['N']}\n[{100*ss[0]['ci_low']:.0f}, {100*ss[0]['ci_high']:.0f}]%")))
  table.append(row)
 fig,ax=plt.subplots(figsize=(12,6));ax.axis('off');ax.set_title('Qwen3-8B AWQ Hanoi: exact success counts and 95% Wilson intervals',pad=25)
 tab=ax.table(cellText=table,colLabels=['Disks','Minimum moves','Move list\nOFF','Move list\nON','Program\nOFF','Program\nON'],loc='center',cellLoc='center');tab.auto_set_font_size(False);tab.set_fontsize(12);tab.scale(1,2.7)
 for (i,j),cell in tab.get_celld().items():
  cell.set_edgecolor('#d5dce2')
  if i==0:cell.set_facecolor('#153e52');cell.set_text_props(color='white',weight='bold')
  elif i%2==0:cell.set_facecolor('#eef4f7')
 fig.tight_layout();fig.savefig(FIG/'table.png',bbox_inches='tight');plt.close(fig)
 print('Analyzed',len(data),'records;',sum(r['output_tokens'] for r in data),'generated tokens')
if __name__=='__main__':main()
