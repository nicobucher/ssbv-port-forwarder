#! /usr/bin/env python
import socket
import sys
from threading import Thread
import errno
from time import sleep

def main(setup):
    threads = []
    for settings in parse(setup):
        try:
            thread = Thread(target=server, args=settings)
            thread.start()
        except Exception as err:
            print(err)
    for thread in threads:
        thread.join()
    print('Quitting')

def parse(setup):
    settings = list()
    i = 0
    for line in open(setup):
        parts = line.split()
        settings.append((parts[0], int(parts[1]), int(parts[2])))
        if len(parts) > 3:
            settings[i] += (int(parts[3]),)
        i = i+1
    return settings

def server(*settings):
    try:
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        dock_socket.bind(('', settings[2]))
        dock_socket.listen(5)
        dock_socket2 = None
        if len(settings) > 3:
            dock_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dock_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            dock_socket2.bind(('', settings[3]))
            dock_socket2.listen(5)
            dock_socket2.setblocking(0)
        if dock_socket2 is not None:
            print('New server forwarding ' + str(settings[0]) + ':' + str(settings[1]) + ' to:\nPrimary Socket listening on port ' + str(dock_socket.getsockname()) + '\nSecondary Socket listening on port ' + str(dock_socket2.getsockname()) + '\n\n')
        else:
            print('New server forwarding ' + str(settings[0]) + ':' + str(settings[1]) + ' to:\nPrimary Socket listening on port ' + str(dock_socket.getsockname()) + '\n\n')
        while True:
            client_socket = dock_socket.accept()[0]
            print('Primary Client Socket connected ' + str(client_socket.getpeername()))
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((settings[0], settings[1]))
            print('Connected to Server Socket ' + str(server_socket.getsockname()))
            _thread.start_new_thread(forward, (client_socket, server_socket))
            if dock_socket2 is not None:
                _thread.start_new_thread(forward_splice, (server_socket, client_socket, dock_socket2))
            else:
                _thread.start_new_thread(forward, (server_socket, client_socket))
    finally:
        _thread.start_new_thread(server, settings)

def forward(source, destination):
    string = ' '
    while string:
        string = source.recv(2048)
        if string:
            destination.sendall(string)
        else:
            source.shutdown(socket.SHUT_RD)
            destination.shutdown(socket.SHUT_WR)

def forward_splice(source, destination1, dock_socket2):
    source.setblocking(0)
    string = ' '
    secondary_connected = False
    destination2 = None
    while string:
        if secondary_connected is False:
            try:
                destination2 = dock_socket2.accept()[0]
                secondary_connected = True
                print('Secondary Client Socket connected' + str(destination2.getpeername()))
            except:
                pass
        try:
            string = source.recv(2048)
            destination1.sendall(string)
            try:
                destination2.sendall(string[20:1135])
                print('Sent bytes: ' + str(string[20:1135]))
            except Exception:
                secondary_connected = False

        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                continue
            else:
                # a "real" error occurred
                print(e)
                print('No more Data, closing all connections...')
                source.shutdown(socket.SHUT_RD)
                destination1.shutdown(socket.SHUT_WR)
                if destination2 is not None:
                    destination2.shutdown(socket.SHUT_WR)
        else:
            pass

if __name__ == '__main__':
    main('proxy.ini')
