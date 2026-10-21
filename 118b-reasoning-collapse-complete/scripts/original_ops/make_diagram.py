import json,random
from pathlib import Path
root=Path(__file__).resolve().parents[1];els=[];r=random.Random(118)
def base(kind,x,y,w,h):
 return dict(id=f'e{len(els)}',type=kind,x=x,y=y,width=w,height=h,angle=0,strokeColor='#183d50',backgroundColor='transparent',fillStyle='hachure',strokeWidth=2,strokeStyle='solid',roughness=1,opacity=100,groupIds=[],frameId=None,roundness={'type':3} if kind=='rectangle' else None,seed=r.randrange(1000000),version=1,versionNonce=r.randrange(1000000),isDeleted=False,boundElements=None,updated=1,link=None,locked=False)
def text(s,x,y,w,h,size=20):
 h=len(s.split('\n'))*size*1.25
 e=base('text',x,y,w,h);e.update(text=s,originalText=s,fontSize=size,fontFamily=1,textAlign='center',verticalAlign='top',baseline=h-size*.25,lineHeight=1.25,containerId=None,autoResize=True);els.append(e)
def box(s,x,y,w=300,h=115,color='#e5f4f7'):
 e=base('rectangle',x,y,w,h);e['backgroundColor']=color;els.append(e);text(s,x+12,y+20,w-24,h-30)
def arrow(x,y,dx,dy):
 e=base('arrow',x,y,abs(dx),abs(dy));e.update(points=[[0,0],[dx,dy]],lastCommittedPoint=None,startBinding=None,endBinding=None,startArrowhead=None,endArrowhead='arrow',elbowed=False);els.append(e)
text('What does a failed puzzle answer actually measure?',30,20,1080,40,20)
box('Solvable synthetic puzzles\nHanoi + checker jumping',30,115)
box('Pilot: Qwen3-4B\nFreeze hypotheses',420,115)
box('Confirm: Qwen3-8B AWQ\nFresh random variants',810,115)
arrow(340,173,65,0);arrow(730,173,65,0)
box('Same 16,384-token ceiling\nThinking ON / OFF\nMoves or Hanoi programs',810,340,h=150,color='#fff0da')
arrow(960,240,0,80)
box('Deterministic simulator\nExecute code, check moves\nCheck the final goal',420,340,h=150)
arrow(795,410,-65,0)
box('Save every raw answer\nAccuracy + uncertainty\nToken counts + truncation',30,340,h=150)
arrow(405,410,-65,0)
text('Representation changes what the model must do; verification stays the same.',45,550,1060,60,20)
out={'type':'excalidraw','version':2,'source':'https://excalidraw.com','elements':els,'appState':{'viewBackgroundColor':'#ffffff','gridSize':None},'files':{}}
(root/'figures/diagram.excalidraw').write_text(json.dumps(out,indent=2))
