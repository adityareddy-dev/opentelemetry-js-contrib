import os,socket,struct,subprocess,threading
print('host uid:',os.getuid(),flush=True)
print('host range:',open('/proc/sys/net/ipv4/ip_local_port_range').read().strip(),flush=True)
print('host reserved:',repr(open('/proc/sys/net/ipv4/ip_local_reserved_ports').read().strip()),flush=True)
print('host reserved sysctl writable:',os.access('/proc/sys/net/ipv4/ip_local_reserved_ports',os.W_OK),flush=True)
srv=socket.socket();srv.bind(('127.0.0.1',15432));srv.listen()
client=socket.socket();client.setsockopt(socket.SOL_IP,51,struct.pack('I',54320|(54320<<16)))
client.connect(srv.getsockname());peer,_=srv.accept()
print('automatically allocated outgoing socket:',client.getsockname(),'->',client.getpeername(),flush=True)
cmd=['docker','compose','-p','ar888-local-proof','-f','test/docker-compose.yaml','up','-d','--wait','postgres']
print('$',' '.join(cmd),flush=True)
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);print(r.stdout,flush=True);print('exit:',r.returncode,flush=True)
assert r.returncode!=0 and ('address already in use' in r.stdout or 'port is already allocated' in r.stdout)
client.setsockopt(socket.SOL_SOCKET,socket.SO_LINGER,struct.pack('ii',1,0));client.close();peer.close();srv.close()
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);print('after closing outgoing socket:',r.stdout,'exit:',r.returncode,flush=True)
try: assert r.returncode==0
finally: subprocess.run(['docker','compose','-p','ar888-local-proof','-f','test/docker-compose.yaml','down','--volumes'],check=True)
