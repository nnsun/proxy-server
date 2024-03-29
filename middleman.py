import select
import socket
import threading

from cryptography.fernet import Fernet


port = 9999
buffer_size = 16384
ip = "127.0.0.1"
proxy_ip = "45.55.205.253"
# key = Fernet.generate_key()
key = b'ePSZxc99NH3Ey8i0CM0iGuJ-aC9zjN16d7trdGXBAWs='
f = Fernet(key)

def main():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((ip, port))
    proxy_socket.listen(25)
    while True:
        conn, addr = proxy_socket.accept()
        data = conn.recv(buffer_size)
        ConnectionThread(conn, data, addr).start()


class ConnectionThread(threading.Thread):
    def __init__(self, conn, data, addr):
        super().__init__()
        self.browser_socket = conn
        self.data = data
        self.addr = addr
        self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.browser_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
        self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)

    def run(self):
        self.proxy_socket.connect((proxy_ip, port))
        token = f.encrypt(self.data)
        self.proxy_socket.send(token)
        self.exchange()

        self.browser_socket.close()
        self.proxy_socket.close()

    def exchange(self):
        sockets = [self.browser_socket, self.proxy_socket]
        exit_flag = False
        while not exit_flag:
            recv_buffer = b''
            (recv, _, error) = select.select(sockets, [], sockets, 5)
            if len(recv) == 0 or error:
                break
            for sock in recv:
                data = sock.recv(buffer_size)
                if len(data) == 0:
                    exit_flag = True
                    continue
                if sock is self.browser_socket:
                    token = f.encrypt(data)
                    print("to proxy:", len(token))
                    self.proxy_socket.send(token)
                else:
                    print(len(data))
                    try:
                        if len(recv_buffer) == 0:
                            data = f.decrypt(data)
                        else:
                            data = f.decrypt(recv_buffer + data)
                            recv_buffer = b''
                        print("to browser:", len(data))
                        self.browser_socket.send(data)
                    except:
                        recv_buffer += data


if __name__ == "__main__":
    main()
