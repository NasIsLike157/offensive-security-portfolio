
This project is a custom SSH-based client/server implementation built using the `paramiko` library. It establishes a controlled command execution channel over SSH, where the server acts as the operator and the client executes commands remotely.

The system consists of two components:
- **SSH Server** – handles authentication, manages incoming connections, and provides an interactive interface for issuing commands.
- **SSH Client** – connects to the server and executes received commands locally, returning the output over the SSH channel.

Once authenticated, the server can send arbitrary commands to the client, which are executed via the system shell. The output is captured and transmitted back to the server, creating a fully interactive remote execution environment.

This project was designed to deepen understanding of:
- SSH protocol behavior and channel management
- Secure communication using `paramiko`
- Remote command execution and process handling
- Client-server architecture over encrypted channels

It serves as a minimal, fully controlled alternative to traditional remote administration tools, built from the ground up for learning and experimentation.


### Example Usage:

Open Server on your local machine:
```
python ssh_server.py
```

On the target end, open an ssh client:
```
python ssh_client.py -u kali -i 192.168.15.128 -p 2222
```
