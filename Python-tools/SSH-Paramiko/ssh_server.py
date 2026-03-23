import os
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD,'test_rsa.key'))  # Use id_rsa key 

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self,kind,chanid):
            if kind == 'session':
                return paramiko.OPEN_SUCCEEDED 
            return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
        
    def check_auth_password(self,username,password):
            if(username == "kali") and (password == "temppass"):
                return paramiko.AUTH_SUCCESSFUL
            else :
                return paramiko.AUTH_FAILED  
            

if __name__ == '__main__':
    server = '192.168.15.128'
    ssh_port = 2222
    
    # Open a Socket
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server,ssh_port))
        sock.listen(100)
        print("Waiting for connections")
        client , addr = sock.accept()
    except Exception as e:
        print(f'Listen Failed + {e}')
        sys.exit(1)
    else:
        print("established connection")

    # Use the socket as an SSH channel
    ssh_session = paramiko.Transport(client)
    ssh_session.add_server_key(HOSTKEY)
    server = Server()
    ssh_session.start_server(server=server)

    chan = ssh_session.accept(20)
    if chan is None:
        print('No channel')
        sys.exit(1)
    
    print('Authenticated')
    print(chan.recv(1024))
    chan.send('Welcome to my implementation of ssh')
    try: 
        while True:
            command = input('> ')
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            
            else :
                chan.send('exit')
                print('exiting...')
                ssh_session.close()
                break
    except KeyboardInterrupt:
        ssh_session.close()
