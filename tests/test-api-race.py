#!/usr/local/bin/python3

import socket
import sys
import time

HOST='::1'
PORT=2103

#
# Test for race condition on API calls
#
err = 0
for req in [
  b'POST /adm/api/v1/sync HTTP/1.1\r\nContent-Length: 11\r\nAuthorization: internal 587e5bbadbc6186fad0d6177eb10a6cd9d5cb934d3d5f155107592535bd20290\r\nContent-Type: application/json\r\n\r\n{"a":null}\n',
  b'GET /adm/api/v1/net?user=admin&password=%3dadminpw... HTTP/1.1\r\nContent-Length: 0\r\nAuthorization: internal 587e5bbadbc6186fad0d6177eb10a6cd9d5cb934d3d5f155107592535bd20290\r\n\r\n',
  b'GET /adm/api/v1/rtcm?user=admin&password=%3dadminpw... HTTP/1.1\r\nContent-Length: 0\r\nAuthorization: internal 587e5bbadbc6186fad0d6177eb10a6cd9d5cb934d3d5f155107592535bd20290\r\n\r\n'
  b'GET /adm/api/v1/mem?user=admin&password=%3dadminpw... HTTP/1.1\r\nContent-Length: 0\r\nAuthorization: internal 587e5bbadbc6186fad0d6177eb10a6cd9d5cb934d3d5f155107592535bd20290\r\n\r\n'
  b'GET /adm/api/v1/livesources?user=admin&password=%3dadminpw... HTTP/1.1\r\nContent-Length: 0\r\nAuthorization: internal 587e5bbadbc6186fad0d6177eb10a6cd9d5cb934d3d5f155107592535bd20290\r\n\r\n'
  b'GET /adm/api/v1/sourcetables?user=admin&password=%3dadminpw... HTTP/1.1\r\nContent-Length: 0\r\nAuthorization: internal 587e5bbadbc6186fad0d6177eb10a6cd9d5cb934d3d5f155107592535bd20290\r\n\r\n'
  b'POST /adm/api/v1/reload HTTP/1.1\r\nContent-Length: 33\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\nuser=admin&password=%3dadminpw...',
  b'POST /adm/api/v1/drop HTTP/1.1\r\nContent-Length: 33\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\nuser=admin&password=%3dadminpw...',
  ]:

  for i in range(100):
    sclient = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
      sclient.connect((HOST, PORT))
      sclient.sendall(req)
      sclient.close()

    except BrokenPipeError as e:
      err = 1
      print(e)
      break
    except ConnectionResetError as e:
      err = 1
      print(e)
      break

    print('.', end='')
    sys.stdout.flush()

if err:
  print("FAILED")
else:
  print()

sys.exit(err)
