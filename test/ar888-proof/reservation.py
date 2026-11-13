import collections,errno,pathlib,socket,struct
reserved=pathlib.Path('/proc/sys/net/ipv4/ip_local_reserved_ports')
print('namespace range:',pathlib.Path('/proc/sys/net/ipv4/ip_local_port_range').read_text().strip(),flush=True)
print('namespace initial reservations:',repr(reserved.read_text().strip()),flush=True)
server=socket.socket();server.bind(('127.0.0.1',15432));server.listen()
def samples(target,count):
 counts=collections.Counter()
 for _ in range(count):
  c=socket.socket();c.setsockopt(socket.SOL_IP,51,struct.pack('I',target|((target+3)<<16)))
  c.connect(server.getsockname());p,_=server.accept();counts[c.getsockname()[1]]+=1
  c.setsockopt(socket.SOL_SOCKET,socket.SO_LINGER,struct.pack('ii',1,0));c.close();p.close()
 return dict(sorted(counts.items()))
if not reserved.read_text().strip():
 for port in [33306,54320]:
  before=samples(port,2000);print('before reservation',port,before,flush=True);assert port in before
 server.close();print('PASS: automatic allocation can use both service ports',flush=True);raise SystemExit(0)
for port in [33306,54320]:
 after=samples(port,10000);print('after reservation',port,after,flush=True);assert port not in after
 c=socket.socket();c.setsockopt(socket.SOL_IP,51,struct.pack('I',port|(port<<16)))
 try: c.connect(server.getsockname());raise AssertionError('reserved port allocated')
 except OSError as e: print('automatic allocation restricted to reserved port',port,repr(e),flush=True);assert e.errno==errno.EADDRNOTAVAIL
 finally:c.close()
 listener=socket.socket();listener.bind(('0.0.0.0',port));listener.listen();print('explicit listen succeeds:',listener.getsockname(),flush=True);listener.close()
server.close();print('PASS: both reserved ports excluded from 20,000 automatic connections, explicit binds allowed',flush=True)
