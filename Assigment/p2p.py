import sys
import time
import socket
import threading
import os
import shutil


class node:
    def __init__(self, arg_list):
        self._id = int(arg_list[0])
        self._port = self._id + 12000
        self._first_successor = int(arg_list[1])
        self._second_successor = int(arg_list[2])
        self._ping_interval = int(arg_list[3])
        self._alive = True
        self._host = 'localhost'
        self._file_list = []
        self._request_list = []

    def port(self, id):
        return int(id) + 12000

    def hash(self, filename):
        return int(filename) % 256

    def show_node(self):
        print('id', self._id)
        print('port', self._port)
        print('first_successor', self._first_successor)
        print('second_successor', self._second_successor)
        print('ping_interval', self._ping_interval)

    def ping_first_successor(self):
        UDP_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_client_socket.settimeout(3)
        time.sleep(3)
        loss_time = 1

        while self._alive:
            print("Ping requests sent to Peers {} and {}".format(self._first_successor, self._second_successor))
            try:
                UDP_client_socket.sendto(("Ping request," + str(self._id) + ',' + str(self.port)).encode(),
                                         (self._host, self.port(self._first_successor)))
                resp_data, resp_add = UDP_client_socket.recvfrom(2048)
                resp_data = resp_data.decode().split(',')
                if resp_data[0] == "Ping response":
                    print("Ping response received from Peer", resp_data[1])
                    loss_time = 1
            except socket.timeout:
                print("No ping response from ", self._first_successor, " for", loss_time, " times.")
                loss_time += 1
                if loss_time > 2:
                    UDP_client_socket.sendto(("Ask for first successor," + str(self._id)).encode(),
                                             (self._host, self.port(self._second_successor)))
                    resp_data, resp_add = UDP_client_socket.recvfrom(2048)
                    resp_data = resp_data.decode().split(',')
                    if resp_data[0] == "Response for first successor":
                        print("Peer {} is no longer alive".format(self._first_successor))
                        self._first_successor = self._second_successor
                        self._second_successor = resp_data[2]
                        print("My new first successor is Peer {}\nMy new second successor is Peer {}".format(
                            self._first_successor, self._second_successor))
                        loss_time = 1
                else:
                    continue

            time.sleep(self._ping_interval)

        UDP_client_socket.close()

    def ping_second_successor(self):
        UDP_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_client_socket.settimeout(3)
        time.sleep(3)
        loss_time = 1

        while self._alive:
            try:
                UDP_client_socket.sendto(("Ping request," + str(self._id) + ',' + str(self.port)).encode(),
                                         (self._host, self.port(self._second_successor)))
                resp_data, resp_add = UDP_client_socket.recvfrom(2048)
                resp_data = resp_data.decode().split(',')
                if resp_data[0] == "Ping response":
                    print("Ping response received from Peer", resp_data[1])
                    loss_time = 1
            except socket.timeout:
                print("No ping response from ", self._second_successor, " for", loss_time, " times.")
                loss_time += 1
                if loss_time > 3:
                    UDP_client_socket.sendto(("Ask for first successor," + str(self._id)).encode(),
                                             (self._host, self.port(self._first_successor)))
                    resp_data, resp_add = UDP_client_socket.recvfrom(2048)
                    resp_data = resp_data.decode().split(',')
                    if resp_data[0] == "Response for first successor":
                        print("Peer {} is no longer alive".format(self._second_successor))
                        self._second_successor = resp_data[2]
                        print("My new first successor is Peer {}\nMy new second successor is Peer {}".format(
                            self._first_successor, self._second_successor))
                        loss_time = 1
                else:
                    continue

            time.sleep(self._ping_interval)

        UDP_client_socket.close()

    def UDP_server(self):
        UDP_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_server_socket.bind((self._host, self._port))

        while self._alive:
            recv_data, recv_add = UDP_server_socket.recvfrom(2048)
            recv_data = recv_data.decode().split(',')

            if recv_data[0] == "Ping request":
                print("Ping request message received from Peer ", recv_data[1])
                UDP_server_socket.sendto(("Ping response," + str(self._id) + ',' + str(self.port)).encode(),
                                         (self._host, int(recv_add[1])))
            elif recv_data[0] == "Ask for first successor":
                print("Ask for first successor", recv_data[1])
                UDP_server_socket.sendto(
                    ("Response for first successor," + str(self._id) + ',' + str(self._first_successor)).encode(),
                    (self._host, int(recv_add[1])))
            elif recv_data[0] == "Ask for second successor":
                print("Ask for second successor", recv_data[1])
                UDP_server_socket.sendto(
                    ("Response for second successor," + str(self._id) + ',' + str(self._second_successor)).encode(),
                    (self._host, int(recv_add[1])))

        UDP_server_socket.close()

    def TCP_server(self):
        TCP_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_server_socket.bind((self._host, self._port))
        TCP_server_socket.listen(5)

        while self._alive:
            recv_socket, recv_add = TCP_server_socket.accept()
            recv_data = recv_socket.recv(2048).decode().split(',')

            if recv_data[0] == 'Position search':
                temp_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if (self._id < int(recv_data[1]) < self._first_successor) or (
                        self._id < int(recv_data[1]) and int(recv_data[1]) > self._id > self._first_successor):
                    temp_TCP_socket.connect((self._host, self.port(int(recv_data[1]))))
                    temp_TCP_socket.send((str(self._first_successor) + ',' + str(self._second_successor)).encode())
                    self._second_successor = self._first_successor
                    self._first_successor = int(recv_data[1])
                    print("Peer {} Join request received\nMy new first successor is Peer {}\nMy new second successor "
                          "is Peer {}".format(self._first_successor, self._first_successor, self._second_successor))
                    temp_TCP_socket.close()
                    temp_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    temp_TCP_socket.connect((self._host, self.port(int(recv_data[2]))))
                    temp_TCP_socket.send(('Change sec_successor,' + recv_data[1]).encode())
                    temp_TCP_socket.close()

                else:
                    temp_TCP_socket.connect((self._host, self.port(self._first_successor)))
                    temp_TCP_socket.send(("Position search," + recv_data[1] + ',' + str(self._id)).encode())
                    print("Peer {} Join request forwarded to my successor".format(recv_data[1]))
                    temp_TCP_socket.close()
            elif recv_data[0] == 'Change sec_successor':
                self._second_successor = int(recv_data[1])
                print("Successor Change request received\nMy new first successor is Peer {}\nMy new second successor "
                      "is Peer {}".format(self._first_successor, self._second_successor))
            elif recv_data[0] == 'Graceful leave':
                if self._second_successor == int(recv_data[1]):
                    self._second_successor = int(recv_data[2])
                    print("Peer {} will depart from the network\nMy new first successor is Peer {}\nMy new second "
                          "successor is Peer {}".format(int(recv_data[1]), self._first_successor,
                                                        self._second_successor))
                    temp_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    temp_TCP_socket.connect((self._host, self.port(self._first_successor)))
                    temp_TCP_socket.send(
                        ("Graceful leave," + recv_data[1] + ',' + recv_data[2] + ',' + recv_data[3]).encode())
                    temp_TCP_socket.close()
                elif self._first_successor == int(recv_data[1]):
                    self._first_successor = int(recv_data[2])
                    self._second_successor = int(recv_data[3])
                    print("Peer {} will depart from the network\nMy new first successor is Peer {}\nMy new second "
                          "successor is Peer {}".format(int(recv_data[1]), self._first_successor,
                                                        self._second_successor))
                else:
                    temp_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    temp_TCP_socket.connect((self._host, self.port(self._first_successor)))
                    temp_TCP_socket.send(
                        ("Graceful leave," + recv_data[1] + ',' + recv_data[2] + ',' + recv_data[3]).encode())
                    temp_TCP_socket.close()
            elif recv_data[0] == "Store file":
                self.store_file(int(recv_data[1]))
            elif recv_data[0] == "Request file":
                self.request_file(int(recv_data[1]), int(recv_data[2]))
            elif recv_data[0] == "Send file":
                print("Peer {} had File {}\nReceiving File {} from Peer {}".format(recv_data[2], recv_data[1], recv_data[1], recv_data[2]))
                time.sleep(1)
                print("File {} received".format(recv_data[1]))

        TCP_server_socket.close()

    def store_file(self, filename):
        if (self.hash(filename) <= self._id) or (self.hash(filename) >= self._id > self._first_successor):
            print('Store {} request accepted'.format(filename))
            self._file_list.append(int(filename))
            print('Now files: ', self._file_list)
        else:
            temp_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_TCP_socket.connect((self._host, self.port(self._first_successor)))
            temp_TCP_socket.send(("Store file," + str(filename)).encode())
            print("Store {} request forwarded to my successor".format(filename))
            temp_TCP_socket.close()

    def search_file_startswith(self, filename):
        for f_name in os.listdir('./'):
            if f_name.startswith(str(filename)):
                return f_name

    def request_file(self, filename, id):
        if filename in self._file_list:
            print('File {} is stored here\nSending file {} to Peer {}'.format(filename, filename, id))
            temp_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_TCP_socket.connect((self._host, self.port(id)))
            full_filename = self.search_file_startswith(filename)
            recv_full_filename = "received_"+full_filename
            temp_TCP_socket.send(("Send file," + str(filename) + ',' + str(self._id) + ',' + full_filename).encode())
            shutil.copy(full_filename, recv_full_filename)
            temp_TCP_socket.close()
        else:
            if filename in self._request_list:
                print("Can not find the file!!")
            else:
                temp_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                temp_TCP_socket.connect((self._host, self.port(self._first_successor)))
                temp_TCP_socket.send(("Request file," + str(filename) + ',' + str(id)).encode())
                if id == self._id:
                    print("File request for {} has been sent to my successor".format(filename))
                else:
                    print('Request for File {} has been received, but the file is not stored here'.format(filename))
                temp_TCP_socket.close()

    def input_listener(self):
        while self._alive:
            command = input().split()

            if len(command) == 1 and command[0].lower() == 'q-------------':
                print("exiting")
                self._alive = False
                time.sleep(1)
                os._exit(0)
            elif len(command) == 1 and command[0].lower() == 'quit':
                print("Peer Departure (Graceful)")
                self._alive = False
                temp_TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                temp_TCP_socket.connect((self._host, self.port(self._first_successor)))
                temp_TCP_socket.send(("Graceful leave," + str(self._id) + ',' + str(self._first_successor) + ',' + str(
                    self._second_successor)).encode())
                temp_TCP_socket.close()
                time.sleep(1)
                os._exit(0)
            elif len(command) == 2 and command[0].lower() == 'store':
                self.store_file(command[1])
            elif len(command) == 2 and command[0].lower() == 'request':
                self.request_file(command[1], self._id)
                self._request_list.append(int(command[1]))


def net_position_search(args):
    TCP_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCP_server_socket.bind(('localhost', 12000 + int(args[0])))
    TCP_server_socket.listen(5)

    client_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_Socket.connect(('localhost', 12000 + int(args[1])))
    client_Socket.send(("Position search," + args[0] + ',' + '0').encode())

    recv_socket, recv_add = TCP_server_socket.accept()
    recv_data = recv_socket.recv(2048).decode().split(',')
    argv = [args[0], recv_data[0], recv_data[1], args[2]]
    TCP_server_socket.close()
    client_Socket.close()

    print("Join request has been accepted\nMy first successor is Peer {}\nMy second successor is Peer {}".format(
        recv_data[0], recv_data[1]))

    return argv


def init_peer(argv):
    peer = node(argv)

    UDP_server_thread = threading.Thread(target=peer.UDP_server)
    ping_first_successor_thread = threading.Thread(target=peer.ping_first_successor)
    ping_second_successor_thread = threading.Thread(target=peer.ping_second_successor)
    TCP_server_thread = threading.Thread(target=peer.TCP_server)
    input_listener_thread = threading.Thread(target=peer.input_listener)

    ping_first_successor_thread.start()
    ping_second_successor_thread.start()
    UDP_server_thread.start()
    TCP_server_thread.start()
    input_listener_thread.start()


def main():
    if sys.argv[1] == 'init':
        init_peer(sys.argv[2:])

    elif sys.argv[1] == 'join':
        args = net_position_search(sys.argv[2:])
        # 1 2 5 30
        init_peer(args)


if __name__ == '__main__':
    main()
