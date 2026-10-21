"""SSH fallback through the official Colab proxy, only to b9-118.
Install paramiko into experiment-local .local first. Keys are local and ignored.
"""
from pathlib import Path
import sys,shlex
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.local'))
import paramiko
keypath=ROOT/'.local/colab_rsa'
if not keypath.exists():
 key=paramiko.RSAKey.generate(2048);key.write_private_key_file(str(keypath));keypath.chmod(0o600)
 (keypath.with_suffix('.pub')).write_text(key.get_name()+' '+key.get_base64()+' experiment118\n')
key=paramiko.RSAKey.from_private_key_file(str(keypath))
proxy=paramiko.ProxyCommand('colab ssh --proxy-mode -s b9-118 -i '+shlex.quote(str(keypath)))
client=paramiko.SSHClient();client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
 client.connect('colab-runtime',username='root',pkey=key,sock=proxy,timeout=30,auth_timeout=30,banner_timeout=30)
 if len(sys.argv)>1 and sys.argv[1]=='download':
  with client.open_sftp() as s:s.get(sys.argv[2],sys.argv[3])
 elif len(sys.argv)>1 and sys.argv[1]=='upload':
  with client.open_sftp() as s:s.put(sys.argv[2],sys.argv[3])
 else:
  command=sys.stdin.read()
  _,stdout,stderr=client.exec_command(command,timeout=45)
  print(stdout.read().decode(),end='');print(stderr.read().decode(),end='',file=sys.stderr)
  sys.exit(stdout.channel.recv_exit_status())
finally:client.close();proxy.close()
