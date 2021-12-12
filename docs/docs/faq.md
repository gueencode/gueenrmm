# FAQ

## Is it possible to use XXX with Gueen RMM

While it _may be possible_ to use XXX, we have not configured it and therefore it is [Unsupported](../unsupported_guidelines). We cannot help you configure XXX as it pertains to **your environment**. 

## Is it possible to use XXX proxy server with Gueen RMM

If you wish to stray from the [easy install](../install_server/#option-1-easy-install) of a standard install in a VPS, you need to have the knowledge on how to troubleshoot your own custom environment.

The most common reasons you're running a proxy is:

1. Because you only have a single public IP and you already have something on Port 443. **Workaround**: Get another public IP from your ISP
2. Because you want to monitor traffic for security reasons: You're a [Networking Wizard](../unsupported_guidelines).

There are some [implementations](../unsupported_scripts) that others have done, but be aware it is [Unsupported](../unsupported_guidelines) and if you're requesting help in Discord please let us know in advance.

## How do I do X feature in the web UI?

Alot of features in the web UI are hidden behind right-click menus; almost everything has a right click menu so if you don't see something, try right clicking on it.

## Where are the Linux / Mac agents?

Linux / Mac agents are currently under development.

## Can I run Gueen RMM locally behind NAT without exposing anything to the internet?

Yes, you will just need to setup local DNS for the 3 subdomains, either by editing host files on all your agents or through a local DNS server.

## I am locked out of the web UI. How do I reset my password?

SSH into your server and run:

```bash
/rmm/api/env/bin/python /rmm/api/gueenrmm/manage.py reset_password <username>
```

## How do I reset password or 2 factor token?

From the web UI, click **Settings > User Administration** and then right-click on a user:
![reset2fa](images/reset2fa.png)

Or from the command line:

```bash
/rmm/api/env/bin/python /rmm/api/gueenrmm/manage.py reset_2fa <username>
```

Then simply log out of the web UI and next time the user logs in they will be redirected to the 2FA setup page which will present a barcode to be scanned with the Authenticator app.

## How do I recover my MeshCentral login credentials?

From gueen's web UI: *Settings > Global Settings > MeshCentral*

Copy the username then ssh into the server and run:

```bash
cd /meshcentral/
sudo systemctl stop meshcentral
node node_modules/meshcentral --resetaccount <username> --pass <newpassword>
sudo systemctl start meshcentral
```

## Help! I've been hacked there are weird agents appearing in my Gueen RMM

No, you haven't.

1. Your installer was scanned by an antivirus.

2. It didn't recognize the exe.

3. You have the option enabled to submit unknown applications for analysis.

    ![AV Option1](images/faq_av_option1.png)

4. They ran it against their virtualization testing cluster.

5. You allow anyone to connect to your rmm server (you should look into techniques to hide your server from the internet).

6. Here are some examples of what that looks like.

![AV Sandbox1](images/faq_av_sandbox1.png)

![AV Sandbox1](images/faq_av_sandbox2.png)

![AV Sandbox1](images/faq_av_sandbox3.png)

![AV Sandbox1](images/faq_av_sandbox4.png)
