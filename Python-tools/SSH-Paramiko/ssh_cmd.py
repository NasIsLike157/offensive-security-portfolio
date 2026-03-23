import paramiko

def ssh_command(ip,port,user,paasswd,cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(ip,port=port,username=user,password=paasswd)

    _ , sdtout , stderr = client.exec_command(cmd)
    output = sdtout.readlines() + stderr.readlines()
    if output:
        print("-----Output-----")
        for line in output:
            print(line.strip())


if __name__ == '__main__':
    import getpass
    user = getpass.user()
    #user = input("Username: ")
    password = getpass.getpass()

    ip = input('Enter Server Ip: ')
    port = input('Enter Remote Port: ')
    cmd = input('Enter Command: ')

    ssh_command(ip,port,user,password,cmd)

