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
  (b'GET /adm/ HTTP/1.1\nUser-Agent: NTRIP test\n\n',
   b'^HTTP/1\.1 401 Unauthorized\r\nServer: NTRIP Millipede Server .*\r\nDate: .* GMT\r\nNtrip-Version: Ntrip/2.0\r\nConnection: close\r\nWWW-Authenticate: Basic realm="/adm"\r\n\r\n401\r\n$'),
  (b'GET /adm HTTP/1.1\nUser-Agent: NTRIP test\n\n',
   b'^SOURCETABLE 200 OK\r\n(?s:.)*Content-Type: text/plain\r\n'),
  (b'POST /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: zzz dGVzdDE6dGVzdHB3IQ==\n\n',
   b'^HTTP/1\.1 401 Unauthorized\r\n'),
  (b'POST /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: basic dGVzdDE6dGVzdHB3IQ==\n\n',
   b'^HTTP/1\.1 200 OK\r\n'),
  (b'POST /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: basic\t dGVzdDE6dGVzdHB3IQ==  \n\n',
   b'^HTTP/1\.1 200 OK\r\n'),
  (b'POST /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: Basic AAAzdDE6dGVzdHB3IQ==\n\n',
   b'^HTTP/1\.1 401 Unauthorized\r\n'),
  (b'POST /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: Basic dGVzdDE6dGVzdHBZZZ==\n\n',
   b'^HTTP/1\.1 401 Unauthorized\r\n'),
  (b'POST /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: Basic  dGVzdDE6dGVzdHB3IQ==\n\n',
   b'^HTTP/1\.1 200 OK\r\n'),
  (b'POST /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: Basic dGVzdDE6dGVzdHB3IQ==\n\n',
   b'^HTTP/1\.1 200 OK\r\n'),
  (b'POST /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: Basic dGVzdDE6dGVzdHB3IQ==\nTransfer-Encoding: chunked\n\n',
   b'^HTTP/1\.1 200 OK\r\n'),
  (b'SOURCE testpw! TEST1\nUser-Agent: NTRIP test\n\n',
   b'^ICY 200 OK\r\n'),
  (b'POST /WILDCARD HTTP/1.1\nUser-Agent: NTRIP test\n\n',
   b'^HTTP/1\.1 401 Unauthorized\r\n'),
  (b'POST /WILDCARD HTTP/1.1\nUser-Agent: NTRIP test\nAuthorization: Basic d2lsZGNhcmRfdXNlcjp3aWxkY2FyZF9wdy8v\n\n',
   b'^HTTP/1\.1 401 Unauthorized\r\n'),
  (b'GET /V HTTP/1.1\nUser-Agent: NTRIP test\n\n',
   b'^ICY 200 OK\r\n\r\n$'),
  (b'GET /V HTTP/1.1\nUser-Agent: NTRIP test\n\n$GNGGA,172829.20,4332.3917404,N,00651.1321922,E,5,12,0.68,158.545,M,47.390,M,1.2,0000*62\n',
   b'^ICY 200 OK\r\n\r\n$'),
  (b'GET /V HTTP/1.1\nUser-Agent: NTRIP test\nNtrip-Version: Ntrip/2.0\n\n$GNGGA,172829.20,4332.3917404,N,00651.1321922,E,5,12,0.68,158.545,M,47.390,M,1.2,0000*62\n',
   b'^HTTP/1\.1 200 OK\r\nServer: NTRIP Millipede Server \S+\r\nDate: .*\d\d GMT\r\nNtrip-Version: Ntrip/2\.0\r\nConnection: close\r\nContent-Type: gnss/data\r\nCache-Control: no-store, no-cache, max-age=0\r\nPragma: no-cache\r\n\r\n$'),
  (b'GET /V?test HTTP/1.1\nUser-Agent: NTRIP test\nNtrip-Version: Ntrip/2.0\n\n',
   b'^HTTP/1\.1 200 OK\r\n'),
  (b'GET /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\n\n$',
   b'^SOURCETABLE 200 OK\r\nServer: NTRIP Millipede Server \S+\r\nDate: (.*) GMT\r\nNtrip-Version: Ntrip/2\.0\r\nContent-Length: \d+\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nCAS'),
  (b'GET /TEST1 HTTP/1.1\nUser-Agent: NTRIP test\nNtrip-Version: Ntrip/2.0\n\n$',
   b'^HTTP/1.1 404 Not Found\r\nServer: NTRIP Millipede Server \S+\r\nDate: .* GMT\r\nNtrip-Version: Ntrip/2\.0\r\nConnection: close\r\n\r\n'),
  (b'GET / HTTP/1.1\nUser-Agent: NTRIP test\nNtrip-Version: Ntrip/2.0\n\n',
   b'^HTTP/1\.1 200 OK\r\n(?s:.)*Content-Type: gnss/sourcetable\r\n(?s:.)*\r\nCAS;castera\.ntrip\.eu\.org;2101;NTRIP-Caster-2\.0\.45;INRAE;0;FRA;48\.82;2\.34;0\.0\.0\.0;0;http://caster\.centipede\.fr/home\r\nNET;CENTIPEDE-RTK;INRAE;B;N;https://centipede\.fr;https://docs\.centipede\.fr;contact@centipede\.fr;none\r\nSTR;AAA;AAA;(?s:.)*\r\nSTR;NNN;NNN;(?s:.)*\r\nSTR;V;V;RTCM3;1004,1005,1006,1008,1012,1019,1020,1033,1042,1045,1046,1077,1087,1097,1107,1127,1230;;GPS\+GLO\+GAL\+BDS\+QZS;NONE;NONE;48\.824;2\.344;1;0;PB-Virtual,0;NONE;N;N;;\r\nSTR;ZZZ;ZZZ;(?s:.)*\r\nENDSOURCETABLE\r\n$'),
  (b'GET / HTTP/1.1\nUser-Agent: NTRIP test\n\n',
   b'^SOURCETABLE 200 OK\r\n(?s:.)*Content-Type: text/plain\r\n(?s:.)*\r\nCAS;castera\.ntrip\.eu\.org;2101;NTRIP-Caster-2\.0\.45;INRAE;0;FRA;48\.82;2\.34;0\.0\.0\.0;0;http://caster\.centipede\.fr/home\r\nNET;CENTIPEDE-RTK;INRAE;B;N;https://centipede\.fr;https://docs\.centipede\.fr;contact@centipede\.fr;none\r\nSTR;AAA;AAA;(?s:.)*\r\nSTR;NNN;NNN;(?s:.)*\r\nSTR;V;V;RTCM3;1004,1005,1006,1008,1012,1019,1020,1033,1042,1045,1046,1077,1087,1097,1107,1127,1230;;GPS\+GLO\+GAL\+BDS\+QZS;NONE;NONE;48\.824;2\.344;1;0;PB-Virtual,0;NONE;N;N;;\r\nSTR;ZZZ;ZZZ;(?s:.)*\r\nENDSOURCETABLE\r\n$'),
  (b'GET / HTTP/1.1\nUser-Agent: random\n\n',
   b'^HTTP/1\.1 200 OK\r\n(?s:.)*Content-Type: text/plain\r\n(?s:.)*\r\nCAS;castera\.ntrip\.eu\.org;2101;NTRIP-Caster-2\.0\.45;INRAE;0;FRA;48\.82;2\.34;0\.0\.0\.0;0;http://caster\.centipede\.fr/home\r\nNET;CENTIPEDE-RTK;INRAE;B;N;https://centipede\.fr;https://docs\.centipede\.fr;contact@centipede\.fr;none\r\nSTR;AAA;AAA;(?s:.)*\r\nSTR;NNN;NNN;(?s:.)*\r\nSTR;V;V;RTCM3;1004,1005,1006,1008,1012,1019,1020,1033,1042,1045,1046,1077,1087,1097,1107,1127,1230;;GPS\+GLO\+GAL\+BDS\+QZS;NONE;NONE;48\.824;2\.344;1;0;PB-Virtual,0;NONE;N;N;;\r\nSTR;ZZZ;ZZZ;(?s:.)*\r\nENDSOURCETABLE\r\n$'),
   b'^HTTP/1\.1 200 OK\r\n(?s:.)*Content-Length: 14\r\nContent-Type: application/json\r\n(?s:.)*\r\n\{"result": 0\}\n$'),
]

err = 0

for send, expect in tests:
  s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  s.sendall(send)
  data = s.recv(10240)
  s.close()
  if re.match(expect, data):
    print(".", end='')
  else:
    print("FAIL\nExpected: %s\nGot: %s" % (expect, data))
    err = 1

print()
sys.exit(err)
