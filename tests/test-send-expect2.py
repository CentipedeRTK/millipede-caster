#!/usr/local/bin/python3

import re
import socket
import sys

#
# send/expect tests
#

HOST='::1'
PORT=2103

tests = [
  (b'POST /WILDCARD HTTP/1.1\nUser-Agent: NTRIP test\n\n',
   b'^HTTP/1\.1 401 Unauthorized\r\n',
   b'', b''),
  (b'POST /WILDCARD HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: Basic d2lsZGNhcmRfdXNlcjp3aWxkY2FyZF9wdy8v\n\n',
   b'^HTTP/1\.1 200 OK\r\n',
   b'GET / HTTP/1.1\nUser-Agent: NTRIP test\nNtrip-Version: Ntrip/2.0\n\n',
   b'^HTTP/1\.1 200 OK\r\n(?s:.)*CAS;castera\.ntrip\.eu\.org;2101;NTRIP-Caster-2\.0\.45;INRAE;0;FRA;48\.82;2\.34;0\.0\.0\.0;0;http://caster\.centipede\.fr/home\r\nNET;CENTIPEDE-RTK;INRAE;B;N;https://centipede\.fr;https://docs\.centipede\.fr;contact@centipede\.fr;none\r\nSTR;V;V;RTCM3;1004,1005,1006,1008,1012,1019,1020,1033,1042,1045,1046,1077,1087,1097,1107,1127,1230;;GPS\+GLO\+GAL\+BDS\+QZS;NONE;NONE;48\.824;2\.344;1;0;PB-Virtual,0;NONE;N;N;;\r\nENDSOURCETABLE\r\n$'),
]

err = 0

s0 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s0.connect((HOST, PORT))

for send, expect, send0, expect0 in tests:
  s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  s.sendall(send)
  data = s.recv(1024)
  if re.match(expect, data):
    print(".", end='')
  else:
    print("FAIL\nExpected: %s\nGot: %s" % (expect, data))
    err = 1
  s.close()

  if send0 != b'':
    s0.sendall(send0)
    data0 = s0.recv(1024)
    if re.match(expect0, data0):
      print(".", end='')
    else:
      print("FAIL ON s0\nExpected: %s\nGot: %s" % (expect0, data0))
      err = 1

print()
sys.exit(err)