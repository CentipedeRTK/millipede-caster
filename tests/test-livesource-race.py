#!/usr/local/bin/python3

import socket
import sys

HOST='::1'
PORT=2103

#
# Check for a race condition at SOURCE/POST connection.
#

n = 50

str_post = b'POST /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: Basic dGVzdDE6dGVzdHB3IQ==\n'
str_source = b'SOURCE testpw! TEST1\nUser-Agent: NTRIP test\n'

ni = 1
npertype = 100

#
# Mix and match request types
#
for rqs in [str_post], [str_source], [str_post, str_source]:
  lenrqs = len(rqs)
  for j in range(npertype):
    nok = 0
    socks = [socket.socket(socket.AF_INET6, socket.SOCK_STREAM) for i in range(n)]
    for i in range(n):
      socks[i].connect((HOST, PORT))

    for i in range(n):
      socks[i].sendall(rqs[i % lenrqs])

    for i in range(n):
      socks[i].sendall(b'\n')

    for i in range(n):
      r = socks[i].recv(200)
      if r == b'ICY 200 OK\r\n\r\n' or r.startswith(b'HTTP/1.1 200 OK\r\n'):
        nok += 1

    if nok != 1:
      print("FAIL at iteration", ni)
      sys.exit(1)

    for i in range(n):
      socks[i].close()

    print(".", end='')
    sys.stdout.flush()
    ni += 1

print()

sys.exit(0)
