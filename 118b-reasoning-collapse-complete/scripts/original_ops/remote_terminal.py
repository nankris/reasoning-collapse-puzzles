"""Fallback: temporary Jupyter terminal on this experiment's existing Colab VM."""
from colab_cli.common import state
import requests,websocket,json,sys,time
from urllib.parse import urlencode
s=state.get_session('b9-118');base=s.url.rstrip('/')
params={'authuser':'0','colab-runtime-proxy-token':s.token}
r=requests.post(base+'/api/terminals',params=params,timeout=20);r.raise_for_status();name=r.json()['name']
ws=None
try:
 url=base.replace('https://','wss://').replace('http://','ws://')+'/terminals/websocket/'+name+'?'+urlencode(params)
 ws=websocket.create_connection(url,timeout=20,suppress_origin=True)
 ws.send(json.dumps(['stdin',sys.stdin.read()+"\necho EXP118_DONE\n"]))
 text='';start=time.time()
 while time.time()-start<45:
  msg=json.loads(ws.recv())
  if msg[0]=='stdout':
   print(msg[1],end='',flush=True);text+=msg[1]
   if '\r\nEXP118_DONE\r\n' in text:break
finally:
 if ws:ws.close()
 requests.delete(base+'/api/terminals/'+name,params=params,timeout=15)
