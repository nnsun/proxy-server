import socket
import threading

from cryptography.fernet import Fernet


port = 9999
ip = "127.0.0.1"
proxy_ip = "45.55.205.253"
# key = Fernet.generate_key()
key = b'ePSZxc99NH3Ey8i0CM0iGuJ-aC9zjN16d7trdGXBAWs='
f = Fernet(key)

def main():
    # proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # proxy_socket.bind((ip, port))
    # proxy_socket.listen(25)
    while True:
        # conn, addr = proxy_socket.accept()
        # data = conn.recv(buffer_size)
        conn, addr = None, None
        data = input()
        ConnectionThread(conn, data, addr).start()

    
class ConnectionThread(threading.Thread):
    def __init__(self, conn, data, addr):
        super().__init__()
        self.browser_socket = conn
        self.data = data
        self.addr = addr
        self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.proxy_socket.connect((proxy_ip, port))
        token = f.encrypt(self.data)
        print(token)
        self.proxy_socket.send(token)



if __name__ == "__main__":
    main()
