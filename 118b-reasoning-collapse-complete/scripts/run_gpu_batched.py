import argparse,json,os,time,sys,hashlib,subprocess
from pathlib import Path
from puzzles import instance,prompt,grade,canonical

def main():
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=['pilot','confirm'],required=True);args=p.parse_args()
 phase=args.phase;root=Path('/content/exp118');root.mkdir(exist_ok=True)
 out=root/(phase+'.jsonl');done={}
 if out.exists():
  for line in out.read_text().splitlines():
   try:r=json.loads(line);done[r['id']]=r
   except ValueError:pass
 model='Qwen/Qwen3-4B' if phase=='pilot' else 'Qwen/Qwen3-8B-AWQ'
 from vllm import LLM,SamplingParams
 print('START',phase,model,time.time(),flush=True)
 llm=LLM(model=model,dtype='bfloat16',max_model_len=20480,gpu_memory_utilization=.90,max_num_seqs=32,max_num_batched_tokens=8192,enable_prefix_caching=True,seed=118, enforce_eager=(phase=='pilot'))
 tok=llm.get_tokenizer()
 meta={'model':model,'phase':phase,'time':time.time(),'canonical_n10_tokens':len(tok.encode(json.dumps(canonical(10,'A','B','C'),separators=(',',':')))),'versions':subprocess.getoutput('pip show vllm torch transformers | head -45'),'gpu':subprocess.getoutput('nvidia-smi')}
 (root/(phase+'_meta.json')).write_text(json.dumps(meta,indent=2))
 print('META',json.dumps(meta),flush=True)
 cells=[]
 levels={'hanoi':[3,5,7,9,10] if phase=='pilot' else list(range(3,11)),'checkers':[2,4] if phase=='pilot' else list(range(2,6))}
 for family,ns in levels.items():
  for n in ns:
   for mode in (False,True):cells.append((family,n,mode,'moves'))
 for n in ([9,10] if phase=='pilot' else [8,9,10]):
  for mode in (False,True):cells.append(('hanoi',n,mode,'program'))
 # Complete entire cells; checkpoints after every generation batch.
 for ci,(family,n,mode,arm) in enumerate(cells):
  todo=[];prompts=[]
  for j in range(2 if phase=='pilot' else 25):
   ident=f'{phase}:{family}:{n}:{int(mode)}:{arm}:{j}'
   if ident in done:continue
   seed=(118000 if phase=='pilot' else 918000)+1000*(family=='checkers')+n*100+j
   x=instance(family,n,seed)
   messages=[{'role':'user','content':prompt(x,arm)}]
   rendered=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=mode)
   todo.append((ident,x,j,rendered));prompts.append(rendered)
  if not todo:continue
  t=time.monotonic()
  params=[SamplingParams(temperature=.6,top_p=.95,top_k=20,max_tokens=16384,seed=(118+ci*1000+z[2] if phase=='confirm' else 118+ci)) for z in todo]
  outputs=llm.generate(prompts,params,use_tqdm=False)
  elapsed=time.monotonic()-t
  with out.open('a') as f:
   for (ident,x,j,rendered),output in zip(todo,outputs):
    o=output.outputs[0];text=o.text;ids=list(o.token_ids)
    close=tok.convert_tokens_to_ids('</think>')
    think_tokens=ids.index(close) if mode and close in ids else (len(ids) if mode else 0)
    final=text.split('</think>',1)[-1] if '</think>' in text else ('' if mode else text)
    ok,reason,valid=grade(final,x,arm)
    row=dict(id=ident,phase=phase,model=model,family=family,n=n,thinking=mode,arm=arm,item=j,instance=x,prompt=rendered,prompt_tokens=len(output.prompt_token_ids),output=text,output_tokens=len(ids),thinking_tokens=think_tokens,final_tokens=len(ids)-think_tokens,finish_reason=o.finish_reason,truncated=o.finish_reason=='length',correct=ok,verifier_reason=reason,valid_moves=valid,batch_seconds=elapsed,batch_size=len(todo),seed=(118+ci*1000+j if phase=='confirm' else 118+ci))
    f.write(json.dumps(row)+'\n');done[ident]=row
   f.flush();os.fsync(f.fileno())
  print('CELL',ci,family,n,mode,arm,'correct',sum(done[z[0]]['correct'] for z in todo),'/',len(todo),'seconds',round(elapsed,2),'tokens',sum(done[z[0]]['output_tokens'] for z in todo),flush=True)
 print('DONE',phase,'records',len(done),'time',time.time(),flush=True)
 (root/(phase+'.done')).write_text(str(time.time()))
if __name__=='__main__':main()
