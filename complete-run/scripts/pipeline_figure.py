from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
R=Path(__file__).resolve().parents[1]
boxes=[(0.4,2.1,3.1,1.25,'Recover original checkpoint\n285 saved responses\nPreserve every record'),(4.3,2.1,3.1,1.25,'Resume Qwen3-8B-AWQ\n465 missing IDs only\nSame seeds and settings'),(8.2,2.1,3.1,1.25,'Append each answer\nfsync on Colab VM\nCopy checkpoints locally'),(4.3,.1,3.1,1.25,'Verify saved responses\nFrozen H1-H4 rules\nReport coverage and verdict')]
fig,ax=plt.subplots(figsize=(12,4.5),dpi=150);ax.set(xlim=(0,11.8),ylim=(-.3,4));ax.axis('off')
elements=[]
for i,(x,y,w,h,t) in enumerate(boxes):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.06',fc='#edf5f7',ec='#22566c',lw=1.8));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=12,linespacing=1.6,color='#173b4b')
 # Editable Excalidraw fallback source. Coordinates use a separate 1200x500 canvas.
 xx=x*100;yy=(3.7-y-h)*100
 base=dict(angle=0,strokeColor='#22566c',backgroundColor='#edf5f7',fillStyle='solid',strokeWidth=2,strokeStyle='solid',roughness=1,opacity=100,groupIds=[],frameId=None,index=None,roundness={'type':3},seed=118+i,version=1,versionNonce=118+i,isDeleted=False,boundElements=None,updated=1,link=None,locked=False)
 elements.append(dict(base,id=f'box{i}',type='rectangle',x=xx,y=yy,width=w*100,height=h*100))
 tb=dict(base);tb.update(backgroundColor='transparent',roundness=None)
 elements.append(dict(tb,id=f'text{i}',type='text',x=xx+15,y=yy+22,width=w*100-30,height=84,text=t,fontSize=18,fontFamily=1,textAlign='center',verticalAlign='middle',containerId=None,originalText=t,autoResize=False,lineHeight=1.5))
for x1,y1,x2,y2 in [(3.6,2.72,4.2,2.72),(7.5,2.72,8.1,2.72),(9.75,2,7.5,.75)]:
 ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',lw=2,color='#22566c'))
 arrow=dict(base);arrow.pop('index',None);arrow.update(id=f'arrow{len(elements)}',type='arrow',x=x1*100,y=(3.7-y1)*100,width=abs(x2-x1)*100,height=abs(y2-y1)*100,points=[[0,0],[(x2-x1)*100,(y1-y2)*100]],startBinding=None,endBinding=None,lastCommittedPoint=None,startArrowhead=None,endArrowhead='arrow',elbowed=False,backgroundColor='transparent',roundness=None)
 elements.append(arrow)
ax.set_title('Completion, not a new replication: 285 preserved + 465 missing',fontsize=17,pad=15)
fig.tight_layout();fig.savefig(R/'figures/diagram.png',dpi=150,bbox_inches='tight')
for e in elements:e.pop('index',None)
(R/'figures/diagram.excalidraw').write_text(json.dumps({'type':'excalidraw','version':2,'source':'https://excalidraw.com','elements':elements,'appState':{'viewBackgroundColor':'#ffffff','gridSize':None},'files':{}},indent=2))
