import socket
import threading

import urllib.request


port = 9999

def main():
    ip = get_ip()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(25)
    while True:
        conn, addr = server_socket.accept()
        ConnectionThread(conn, addr).start()


class ConnectionThread(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__()
        self.client_socket = conn
        self.addr = addr

    def run(self):
        self.client_socket.close()


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


if __name__ == "__main__":
    main()
