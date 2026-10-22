from colab_cli.common import state
import requests,json
s=state.get_session('puzzles-l4')
params={'authuser':'0','colab-runtime-proxy-token':s.token}
for path in ['/api/kernels','/api/terminals']:
 r=requests.get(s.url.rstrip('/')+path,params=params,timeout=20)
 print(path,r.status_code,r.text[:1200])
