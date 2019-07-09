import select
import socket
import threading

import urllib.request


port = 9999
buffer_size = 4096

def main():
    # ip = get_ip()
    ip = "127.0.0.1"

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((ip, port))
    proxy_socket.listen(25)
    while True:
        conn, addr = proxy_socket.accept()
        data = conn.recv(buffer_size)
        ConnectionThread(conn, data, addr).start()


def server_info(data):
    if len(data) == 0:
        return (None, None, None)

    url = data.decode('latin-1').split(' ')[1]
    port = 80
    server = url
    path = ""

    # strip protocol from URL
    http_pos = url.find("://")
    if http_pos != -1:
        url = url[http_pos + 3:]
        if url[:http_pos].lower().find("https") != -1:
            port = 443

    # get port number
    port_pos = url.find(":")
    if port_pos != -1:
        server = url[:port_pos]
        port = int(url[port_pos + 1:])

    # get relative path
    path_pos = url.find("/")
    if path_pos != -1:
        server = url[:path_pos]
        path = url[path_pos:port_pos]

    return (server, port, path)


class ConnectionThread(threading.Thread):
    def __init__(self, conn, data, addr):
        super().__init__()
        self.client_socket = conn
        self.data = data
        self.addr = addr
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        (self.server, self.port, self.path) = server_info(self.data)

    def run(self):
        if self.server is None:
            return

        self.server_socket.connect((self.server, self.port))

        if self.data[:7] == b"CONNECT":
            self.client_socket.send(b"HTTP/1.0 200 Connection established\r\n\r\n")
            self.exchange()
        else:
            self.server_socket.send(self.data)
            self.exchange()

        self.client_socket.close()

    def exchange(self):
        sockets = [self.client_socket, self.server_socket]
        exit_flag = False
        while not exit_flag:
            (recv, _, error) = select.select(sockets, [], sockets, 5)
            if len(recv) == 0 or error:
                break
            for sock in recv:
                data = sock.recv(buffer_size)
                if len(data) == 0:
                    exit_flag = True
                if sock is self.client_socket:
                    self.server_socket.send(data)
                else:
                    self.client_socket.send(data)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


if __name__ == "__main__":
    main()
