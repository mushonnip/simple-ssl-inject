import socket
import threading
import select
import configparser

configParser = configparser.RawConfigParser()   
configFilePath = r'config.txt'
configParser.read(configFilePath)

SNI_HOST = configParser.get('INJECT_CONFIG', 'SNI_HOST')
LISTEN_PORT = int(configParser.get('OTHER_CONFIG', 'LISTEN_PORT'))
SSH_HOST = configParser.get('SSH_CONFIG', 'SSH_HOST')
SSH_PORT = int(configParser.get('SSH_CONFIG', 'SSH_PORT'))
SSH_USERNAME = configParser.get('SSH_CONFIG', 'SSH_USERNAME')
SSH_PASSWORD = configParser.get('SSH_CONFIG', 'SSH_PASSWORD')
SESSION_NAME = configParser.get('OTHER_CONFIG', 'SESSION_NAME')

def handle_connection(client, address):
    print("Client Connection From {}".format(address[-1]))
    req = client.recv(8192)
    print("{} : {}".format(SSH_HOST, SSH_PORT))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((str(SSH_HOST), int(SSH_PORT)))

    import ssl

    ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    server = ctx.wrap_socket(server, server_hostname=str(SNI_HOST))

    # Mode Direct ssl
    client.send(b"HTTP/1.1 200 Established\r\n\r\n")

    conneted = True
    while conneted:
        read, write, x = select.select(
            [client, server], [], [client, server], 3)
        if x:
            conneted = False
            break
        for i in read:
            try:
                data = i.recv(8192)
                if not data:
                    conneted = False
                    break
                if i is server:
                    client.send(data)
                else:
                    server.send(data)
            except:
                conneted = False
                break
    client.close()
    server.close()

    print("Disconnected")

def handle_putty():
    import os
    os.system("putty -load {} -ssh {}@{} {} -pw {}".format(SESSION_NAME, SSH_USERNAME, SSH_HOST, SSH_PORT, SSH_PASSWORD))

print("Start SSL Server Injection")

local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_server.bind(('', LISTEN_PORT))
local_server.listen(0)
print("Server Listen on: 127.0.0.1:{}".format(LISTEN_PORT))
threading.Thread(target=handle_putty).start()
while True:
    client, address = local_server.accept()
    threading.Thread(target=handle_connection, args=(client, address)).start()

local_server.close()
