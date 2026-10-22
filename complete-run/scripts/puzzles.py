"""Public, synthetic, constructively solvable puzzles and deterministic verifiers."""
import ast,json,random,re,subprocess,sys,tempfile,os

def instance(family,n,seed):
    r=random.Random(seed)
    labels=r.sample(['A','B','C','D','E','F','G','H','J','K','L','M'],3)
    return dict(family=family,n=n,seed=seed,labels=labels,nonce=r.randrange(10**8))

def prompt(x,arm):
    n=x['n']; a,b,c=x['labels']
    if x['family']=='hanoi':
        s=f"Tower of Hanoi. There are {n} disks, numbered 1 (smallest) to {n} (largest), stacked legally on peg {a}. Pegs {b} and {c} are empty. Move the entire tower to peg {b}, using {c} as auxiliary. Move one top disk at a time, never putting a larger disk on a smaller disk."
        if arm=='program':
            s+=" Output Python code only (optionally fenced), defining solve(n, source, target, auxiliary) returning a Python list of [from_peg,to_peg] pairs. No imports, input, print, or external dependencies. The evaluator calls your function with the puzzle's n and peg names. You may use recursion. Do not enumerate the move list in your answer."
        else:
            s+=f' Output the complete solution as a JSON list of [from_peg,to_peg] pairs, e.g. [["{a}","{b}"]]. No disk numbers. No abbreviations, ellipses, programs, or omitted moves. Only the final JSON list after your thinking. The answer budget comfortably fits all {2**n-1} required moves in this format.'
    else:
        s=f"Checker jumping puzzle. Positions are indexed 0 through {2*n}. Initial board is "+('R'*n+'_'+'B'*n)+'. Target is '+('B'*n+'_'+'R'*n)+'. R moves only right; B moves only left. A move slides one checker into an adjacent empty position, or jumps over exactly one checker of the OPPOSITE color into the empty position. No backwards moves. '
        s+='Output a complete solution as a JSON list of [from_index,to_index] integer pairs. No abbreviations, code, or omitted moves. Only the final JSON list after your thinking.'
    return s+f"\nInstance identifier: {x['nonce']} (irrelevant to rules)."

def canonical(n,a,b,c):
    if not n:return []
    return canonical(n-1,a,c,b)+[[a,b]]+canonical(n-1,c,b,a)

def extract(text):
    text=text.strip()
    for i,c in enumerate(text):
        if c=='[':
            try:
                obj,_=json.JSONDecoder().raw_decode(text[i:])
                if isinstance(obj,list) and (not obj or isinstance(obj[0],list)):return obj
            except (ValueError,TypeError):pass
    raise ValueError('no_json_move_list')

def verify(x,moves):
    if not isinstance(moves,list):return False,'not_list',0
    n=x['n']; count=0
    if len(moves)>20000:return False,'too_many_moves',0
    if x['family']=='hanoi':
        a,b,c=x['labels']; pegs={a:list(range(n,0,-1)),b:[],c:[]}
        for m in moves:
            if not isinstance(m,(list,tuple)) or len(m)!=2:return False,'bad_move_format',count
            u,v=m
            if not isinstance(u,str) or not isinstance(v,str) or u not in pegs or v not in pegs or u==v:return False,'bad_peg',count
            if not pegs[u]:return False,'empty_source',count
            if pegs[v] and pegs[u][-1]>pegs[v][-1]:return False,'larger_on_smaller',count
            pegs[v].append(pegs[u].pop());count+=1
        ok=pegs[b]==list(range(n,0,-1))
    else:
        board=list('R'*n+'_'+'B'*n)
        for m in moves:
            if not isinstance(m,(list,tuple)) or len(m)!=2 or any(type(z)!=int for z in m):return False,'bad_move_format',count
            u,v=m
            if not(0<=u<len(board) and 0<=v<len(board)) or board[v]!='_' or board[u]=='_':return False,'invalid_position',count
            d=v-u; piece=board[u]
            if (piece=='R' and d not in (1,2)) or (piece=='B' and d not in (-1,-2)):return False,'wrong_direction',count
            if abs(d)==2 and board[(u+v)//2] != ('B' if piece=='R' else 'R'):return False,'invalid_jump',count
            board[v],board[u]=board[u],'_';count+=1
        ok=''.join(board)=='B'*n+'_'+'R'*n
    return ok,'solved' if ok else 'incomplete_goal',count

def run_program(text,x):
    blocks=re.findall(r'```(?:python)?\s*\n(.*?)```',text,re.S)
    code=blocks[-1] if blocks else text.strip()
    tree=ast.parse(code)
    forbidden=(ast.Import,ast.ImportFrom,ast.ClassDef,ast.With,ast.AsyncFunctionDef)
    for z in ast.walk(tree):
        if isinstance(z,forbidden) or (isinstance(z,ast.Attribute) and z.attr not in ('append','extend','copy')) or (isinstance(z,ast.Name) and z.id.startswith('__')):raise ValueError('unsafe_or_unsupported_code')
    runner='''import json,resource,sys
resource.setrlimit(resource.RLIMIT_CPU,(2,2))
resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
d={"__builtins__":{k:__builtins__.__dict__[k] for k in ["range","len","list","tuple","min","max","abs","enumerate","zip","reversed","int","str","bool","sum"]}}
code,args=json.load(sys.stdin)
exec(compile(code,"<model>","exec"),d)
print(json.dumps(d["solve"](*args)))
'''
    p=subprocess.run([sys.executable,'-I','-c',runner],input=json.dumps([code,[x['n'],*x['labels']]]),text=True,capture_output=True,timeout=4)
    if p.returncode:raise ValueError('program_execution_error:'+p.stderr[-120:])
    return json.loads(p.stdout)

def grade(text,x,arm):
    try:return verify(x,run_program(text,x) if arm=='program' else extract(text))
    except Exception as e:return False,str(e)[:200],0

if __name__=='__main__':
    for n in range(3,11):
        x=instance('hanoi',n,n)
        assert verify(x,canonical(n,*x['labels']))[0]
        code='def solve(n,source,target,auxiliary):\n if n==0:return []\n return solve(n-1,source,auxiliary,target)+[[source,target]]+solve(n-1,auxiliary,target,source)'
        assert grade(code,x,'program')[0]
    assert not verify(instance('hanoi',3,1),[['Z','Q']])[0]
    # Exhaustive constructive BFS proves every checker level used is reachable.
    from collections import deque
    for n in range(2,6):
        start='R'*n+'_'+'B'*n;goal='B'*n+'_'+'R'*n
        q=deque([(start,[])]);seen={start}
        while q:
            state,path=q.popleft()
            if state==goal:
                assert verify(instance('checkers',n,n),path)[0];break
            v=state.index('_')
            for u in range(max(0,v-2),min(len(state),v+3)):
                d=v-u;p=state[u]
                if (p=='R' and d in (1,2)) or (p=='B' and d in (-1,-2)):
                    if abs(d)==2 and state[(u+v)//2] != ('B' if p=='R' else 'R'):continue
                    z=list(state);z[v],z[u]=z[u],'_';z=''.join(z)
                    if z not in seen:seen.add(z);q.append((z,path+[[u,v]]))
        else:raise AssertionError('unreachable')
    print('Verifier checks passed: Hanoi 3..10, checkers 2..5, programs and illegal moves')
