"""Detached, streaming vLLM runner. Checkpoints every completed request."""
import argparse,json,os,time,subprocess
from pathlib import Path
from puzzles import instance,prompt,grade,canonical

def main():
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=['pilot','confirm'],required=True);args=p.parse_args()
 phase=args.phase;root=Path('/content/exp118');root.mkdir(exist_ok=True)
 out=root/(phase+'.jsonl');done={}
 if out.exists():
  valid_lines=[];torn_lines=[]
  for line in out.read_text().splitlines():
   try:
    r=json.loads(line);done[r['id']]=r;valid_lines.append(line)
   except ValueError:torn_lines.append(line)
  if torn_lines:
   (root/(phase+'.torn_lines.json')).write_text(json.dumps(torn_lines))
   tmp=out.with_suffix('.repaired');tmp.write_text('\n'.join(valid_lines)+'\n');tmp.replace(out)
 if len(done)==(36 if phase=='pilot' else 750):
  print('Already complete:',phase,len(done),'saved outputs; no model loaded',flush=True)
  (root/(phase+'.done')).touch();return
 model='Qwen/Qwen3-4B' if phase=='pilot' else 'Qwen/Qwen3-8B-AWQ'
 from vllm import LLM,SamplingParams
 print('START',phase,model,time.time(),'resuming',len(done),flush=True)
 llm=LLM(model=model,dtype='bfloat16',max_model_len=20480,gpu_memory_utilization=.90,max_num_seqs=32,max_num_batched_tokens=8192,enable_prefix_caching=True,seed=118,enforce_eager=(phase=='pilot'))
 tok=llm.get_tokenizer()
 meta={'model':model,'phase':phase,'time':time.time(),'canonical_n10_tokens':len(tok.encode(json.dumps(canonical(10,'A','B','C'),separators=(',',':')))),'versions':subprocess.getoutput('pip show vllm torch transformers | head -45'),'gpu':subprocess.getoutput('nvidia-smi'),'runner':'streaming engine; request-level checkpoints'}
 (root/(phase+'_meta.json')).write_text(json.dumps(meta,indent=2))
 print('META',json.dumps(meta),flush=True)
 cells=[]
 levels={'hanoi':[3,5,7,9,10] if phase=='pilot' else list(range(3,11)),'checkers':[2,4] if phase=='pilot' else list(range(2,6))}
 for family,ns in levels.items():
  for n in ns:
   for mode in (False,True):cells.append((family,n,mode,'moves'))
 for n in ([9,10] if phase=='pilot' else [8,9,10]):
  for mode in (False,True):cells.append(('hanoi',n,mode,'program'))
 requests={}
 for ci,(family,n,mode,arm) in enumerate(cells):
  for j in range(2 if phase=='pilot' else 25):
   ident=f'{phase}:{family}:{n}:{int(mode)}:{arm}:{j}'
   if ident in done:continue
   seed=(118000 if phase=='pilot' else 918000)+1000*(family=='checkers')+n*100+j
   x=instance(family,n,seed)
   rendered=tok.apply_chat_template([{'role':'user','content':prompt(x,arm)}],tokenize=False,add_generation_prompt=True,enable_thinking=mode)
   generation_seed=118+ci*1000+j if phase=='confirm' else 118+ci
   requests[ident]=(x,mode,arm,j,rendered,generation_seed,ci)
 # Keep stable cell indices for seeds, but schedule short program arms first.
 order=sorted(requests,key=lambda k:(0 if requests[k][2]=='program' else (1 if requests[k][0]['family']=='hanoi' and requests[k][0]['n']>=8 else 2), -requests[k][0]['n'] if requests[k][0]['family']=='hanoi' and requests[k][0]['n']>=8 else requests[k][6], requests[k][6], requests[k][3]))
 engine=llm.llm_engine
 for ident in order:
  rendered=requests[ident][4];seed=requests[ident][5]
  engine.add_request(ident,rendered,SamplingParams(temperature=.6,top_p=.95,top_k=20,max_tokens=16384,seed=seed))
 t=time.monotonic();lastprint=t
 with out.open('a') as f:
  while engine.has_unfinished_requests():
   for output in engine.step():
    if not output.finished:continue
    ident=output.request_id
    if ident in done:continue
    x,mode,arm,j,rendered,seed,ci=requests[ident]
    o=output.outputs[0];text=o.text;ids=list(o.token_ids);close=tok.convert_tokens_to_ids('</think>')
    think_tokens=ids.index(close) if mode and close in ids else (len(ids) if mode else 0)
    final=text.split('</think>',1)[-1] if '</think>' in text else ('' if mode else text)
    ok,reason,valid=grade(final,x,arm)
    row=dict(id=ident,phase=phase,model=model,family=x['family'],n=x['n'],thinking=mode,arm=arm,item=j,instance=x,prompt=rendered,prompt_tokens=len(output.prompt_token_ids),output=text,output_tokens=len(ids),thinking_tokens=think_tokens,final_tokens=len(ids)-think_tokens,finish_reason=o.finish_reason,truncated=o.finish_reason=='length',correct=ok,verifier_reason=reason,valid_moves=valid,phase_elapsed_seconds=time.monotonic()-t,seed=seed)
    f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno());done[ident]=row
    print('RESULT',ident,'correct',int(ok),'tokens',len(ids),'reason',reason,'finish',o.finish_reason,'elapsed',round(time.monotonic()-t,2),flush=True)
   if time.monotonic()-lastprint>60:
    print('HEARTBEAT',phase,'completed',len(done),'elapsed',round(time.monotonic()-t,2),flush=True);lastprint=time.monotonic()
 print('DONE',phase,'records',len(done),'time',time.time(),flush=True)
 (root/(phase+'.done')).write_text(str(time.time()))
if __name__=='__main__':main()
