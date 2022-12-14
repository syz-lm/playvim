import socket
import struct
import json
import traceback


DEBUG = False


class Client(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = socket.socket()

    def get_name(self):
        try:
            return getattr(self, '_name')
        except Exception:
            return None

    def login(self, name):
        try:
            self._sock.connect((self._host, self._port))
            data = json.dumps({
                'action': 'login',
                'name': name
            }).encode()
            send_header = struct.pack('!i', len(data))
            self._sock.send(send_header + data)

            recv_header = self._sock.recv(4)
            data_size, = struct.unpack('!i', recv_header)

            packet = b''
            has_read = 0
            while not getattr(self._sock, '_closed') \
                    and has_read < data_size:
                d = b''
                if data_size - has_read < 1024:
                    d = self._sock.recv(data_size - has_read)
                else:
                    d = self._sock.recv(1024)
                ld = len(d)
                if ld > 0:
                    has_read = has_read + ld
                    packet = packet + d
                else:
                    break
            jd = json.loads(packet)
            if jd['status'] == 200:
                self._name = name
                return True
            else:
                self.close()
                return False
        except Exception:
            print(traceback.format_exc())
            return False

    def status(self):
        try:
            return not getattr(self._sock, '_closed')
        except Exception as e:
            print(e)
            return False

    def recv(self):
        if getattr(self, '_name'):
            try:
                recv_header = self._sock.recv(4)
                if len(recv_header) == 0:
                    raise
                data_size, = struct.unpack('!i', recv_header)
                packet = b''
                has_read = 0
                while not getattr(self._sock, '_closed') and\
                        has_read < data_size:
                    d = b''

                    if data_size - has_read < 1024:
                        d = self._sock.recv(data_size - has_read)
                    else:
                        d = self._sock.recv(1024)

                    ld = len(d)
                    if ld > 0:
                        has_read = has_read + ld
                        packet = packet + d
                    else:
                        break
                jd = json.loads(packet)
                return jd
            except Exception:
                if DEBUG:
                    print(traceback.format_exc(), packet)
                return None
        else:
            raise Exception('???????????????????????????????????????????????????')

    def send(self, to, msg, action):
        if getattr(self, '_name'):
            jd = {
                'action': action,
                'from': self._name,
                'to': to,
                'msg': msg
            }
            try:
                jd = json.dumps(jd).encode()
                send_header = struct.pack('!i', len(jd))
                self._sock.send(send_header + jd)
                return True
            except Exception:
                if DEBUG:
                    print(traceback.format_exc())
                return False
        else:
            raise Exception('??????????????????????????????????????????')

    def qunfa(self, msg):
        if getattr(self, '_name'):
            jd = {
                'action': 'qunfa',
                'from': self._name,
                'msg': msg
            }
            try:
                jd = json.dumps(jd).encode()
                send_header = struct.pack('!i', len(jd))
                self._sock.send(send_header + jd)
                return True
            except Exception:
                if DEBUG:
                    print(traceback.format_exc())
                return False
        else:
            raise Exception('??????????????????????????????????????????')

    def quit(self):
        jd = json.dumps({
            'action': 'quit'
        }).encode()
        send_header = struct.pack('!i', len(jd))
        self._sock.send(send_header + jd)

    def close(self):
        try:
            self._sock.close()
        except Exception:
            if DEBUG:
                print(traceback.format_exc())


if __name__ == '__main__':
    c0 = Client('localhost', 23456)
    c1 = Client('localhost', 23456)
    c2 = Client('localhost', 23456)
    err = 0
    try:
        if c0.login('xh'):
            print('xh????????????')
            print('??????:', c0.recv())
        else:
            print('xh????????????')
            err = err + 1
        if c1.login('xb'):
            print('xb????????????')
            print('??????:', c0.recv())
        else:
            print('xb????????????')
            err = err + 1
        if c2.login('xl'):
            print('xl????????????')
            print('??????:', c0.recv())
        else:
            print('xl????????????')
            err = err + 1

        if err > 0:
            import sys
            sys.exit(-1)
        else:
            print('????????????')
            if c0.send('xb', '??????xb?????????xh', 'forward'):
                print('1. xh ???????????? ??? xb ??????')
            jd = c1.recv()
            if jd:
                print(jd)
            else:
                print('c1??????????????????')
            if c1.send('xh', '???????????????????????????', 'forward'):
                print('2. xb ???????????? ??? xh ??????')
            else:
                print('2. xb ???????????? ???xh ??????')
            jd = c0.recv()
            if jd:
                print(jd)
            else:
                print('c0??????????????????')

            print('????????????')
            if c2.qunfa('??????????????????'):
                print('c0?????????:', c0.recv())
                print('c1?????????:', c1.recv())
            else:
                print('????????????')
    except Exception:
        import traceback
        print(traceback.format_exc())
    finally:
        c0.close()
        c1.close()
        c1.close()
