from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import thread
import time
import datetime

host = '127.0.0.1'
port = 1313
buff = 2048
addr = (host, port)

serversocket = socket(AF_INET, SOCK_STREAM)
serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serversocket.bind(addr)
serversocket.listen(10)

clients = [serversocket]

def handler(clientsocket, clientaddr):

    print "Creston accepted connection from: ", clientaddr

    while True:
        data = clientsocket.recv(buff)

        if not data:
            break
        else:
            print("%s" % data)

        data = data.strip()
        if data == "Update":
            clientsocket.send("Status-Ok")

    clients.remove(clientsocket)
    clientsocket.close()


def push():
    while True:
        for i in clients:
            if i is not serversocket:
                i.send("OK\n")
        time.sleep(10)


thread.start_new_thread(push, ())


while True:
    try:
        print "Cresont server is listening for connections on port %s host %s\n" % (port, host)
        clientsocket, clientaddr = serversocket.accept()
        clients.append(clientsocket)
        thread.start_new_thread(handler, (clientsocket, clientaddr))
    except KeyboardInterrupt:
        print "Closing Creston server socket..."
        serversocket.close()
        break
