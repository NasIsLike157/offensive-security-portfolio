
A raw-socket network scanner that discovers live hosts on a subnet by exploiting a fundamental behavior of the IP stack: when you send a `UDP` packet to a closed port on a live host, the host responds with an `ICMP` "Port Unreachable" error.  A dead host stays silent.

Implemented with raw sockets in Python, manual IP/ICMP header decoding, and concurrent spraying + sniffing via threading.

# Usage

Requires root (Linux) or Administrator (Windows).

```bash
sudo python3 host_scanner.py -h <IP_listen>
```

 Windows (run as Administrator)
```powershell
python host_scanner.py -h <IP_listen>
```

Press Ctrl+C to stop and print the host summary.

#### How does it work?
*  Some machines are configured to return an `icmp` type `3` error for any `udp` datagram that reached a closed port. In other words, we can generate a `UDP` datagram and send it to a closed port, if the host is alive we will receive `icmp` back from the host, if it says silent, is probably not alive.(Or configured otherwise).
* A string can be added to the `UDP` packet, which will be included in the respond also  this will confirm that the received packet was indeed triggered due to our `UDP` packet.
* After we set a listener, a function to spray `udp` datagrams will get executed, then all left is to wait. 


#### Manual Headers Decode
I chose to implement manual header decoding in this script. In this directory you'll find two decoder implementations — one using `ctypes`, one using struct. In the scanner itself I went with struct, mainly because it's more readable for anyone going through the code and doesn't require overriding __new__ on the object like `ctypes` does. Both decode the same IP and ICMP headers, and both follow the real header architecture — the fields, their sizes, and their order are taken directly from the actual protocol specs and can't be changed arbitrarily.

#### Windows vs Linux
On Linux you can just ask for ICMP directly via raw sockets using `IPPROTO_ICMP`, the kernel handles the filtering for you. On Windows that's not an option; the `nt` kernel won't do that filtering, so you have to request general IP packets instead with `IPPROTO_IP`. To actually receive those packets, promiscuous mode has to be enabled  this is required just to receive inbound raw packets. (a restriction Microsoft added since XP SP2).

One side effect of this difference is that on Linux, since the socket already filters for ICMP, you only need to decode the ICMP header, the IP layer is handled before the packet even reaches you. On Windows you get a raw IP packet, so you have to decode both the IP and ICMP headers yourself. That means a Linux-only version of this script could be noticeably more compact 

#### Why multithreading is not optional here
The spray and the sniff have to run at the same time. The ICMP replies arrive within milliseconds of the UDP probes going out, it means that  if you spray first and then start sniffing, by the time `recvfrom()` is listening the replies are already gone. Running `spray_udp() `in a background thread and calling `sniff()` immediately after on the main thread solves this, both are live before the first probe leaves the `NIC`.