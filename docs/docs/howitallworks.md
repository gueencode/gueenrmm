# How It All Works

[![Network Design](images/gueenrmm-Network.png)](images/gueenrmm-Network.png)

Still need graphics for

    1. Agent installer steps

    2. Agent checks/tasks and how they work on the workstation/interact with server

## Server

Has a postgres database located here:

[Django Admin](https://gueencode.github.io/gueenrmm/functions/django_admin.html)

!!!description
    A web interface for the postgres database

All Gueen RMM dependencies are listed [here](https://github.com/gueencode/gueenrmm/blob/develop/api/gueenrmm/requirements.txt)

### System Services

This lists the system services used by the server.

#### nginx web server

Nginx is the web server for the `rmm`, `api`, and `mesh` domains. All sites redirect port 80 (HTTP) to port 443 (HTTPS).

!!! warning

    nginx does not serve the NATS service on port 4222.

???+ abstract "nginx configuration (a.k.a. sites available)"

    - [nginx configuration docs](https://docs.nginx.com/nginx/admin-guide/basic-functionality/managing-configuration-files/)

    === ":material-web: `rmm.example.com`"

        This serves the frontend website that you intereact with.

        - Config: `/etc/nginx/sites-enabled/frontend.conf`
        - root: `/var/www/rmm/dist`
        - Access log: `/var/log/nginx/frontend-access.log`
        - Error log: `/var/log/nginx/frontend-error.log`
        - TLS certificate: `/etc/letsencrypt/live/example.com/fullchain.pem`

    === ":material-web: `api.example.com`"

        This serves the grmm API for the frontend and agents. 

        - Config: `/etc/nginx/sites-enabled/rmm.conf`
        - roots:
            - `/rmm/api/gueenrmm/static/`
            - `/rmm/api/gueenrmm/gueenrmm/private/`
        - Upstreams:
            - `unix://rmm/api/gueenrmm/gueenrmm.sock`
            - `unix://rmm/daphne.sock`
        - Access log: `/rmm/api/gueenrmm/gueenrmm/private/log/access.log`
        - Error log: `/rmm/api/gueenrmm/gueenrmm/private/log/error.log`
        - TLS certificate: `/etc/letsencrypt/live/example.com/fullchain.pem`

    === ":material-web: `mesh.example.com`"

        This serves MeshCentral for remote access.

        - Config: `/etc/nginx/sites-enabled/meshcentral.conf`
        - Upstream: `http://127.0.0.1:4430/`
        - Access log: `/var/log/nginx/access.log` (uses deafult)
        - Error log: `/var/log/nginx/error.log` (uses deafult)
        - TLS certificate: `/etc/letsencrypt/live/example.com/fullchain.pem`

    === ":material-web: default"

        This is the default site installed with nginx. This listens on port 80 only.

        - Config: `/etc/nginx/sites-enabled/default`
        - root: `/var/www/rmm/dist`
        - Access log: `/var/log/nginx/access.log` (uses deafult)
        - Error log: `/var/log/nginx/error.log` (uses deafult)

???+ note "systemd config"

    === ":material-console-line: status commands"

        - Status: `systemctl status --full nginx.service`
        - Stop: `systemctl stop nginx.service`
        - Start: `systemctl start nginx.service`
        - Restart: `systemctl restart nginx.service`
        - Restart: `systemctl reload nginx.service` reloads the config without restarting
        - Test config: `nginx -t`
        - Listening process: `ss -tulnp | grep nginx`

    === ":material-ubuntu: standard"

        - Service: `nginx.service`
        - Address: `0.0.0.0`
        - Port: 443
        - Exec: `/usr/sbin/nginx -g 'daemon on; master_process on;'`
        - Version: 1.18.0

    === ":material-docker: docker"

        TBD - To Be Documented

#### Gueen RMM (Django uWSGI) service

Built on the Django framework, the Gueen RMM service is the heart of system by serving the API for the frontend and agents.

???+ note "systemd config"

    - [uWSGI docs](https://uwsgi-docs.readthedocs.io/en/latest/index.html)

    === ":material-console-line: status commands"

        - Status: `systemctl status --full rmm.service`
        - Stop: `systemctl stop rmm.service`
        - Start: `systemctl start rmm.service`
        - Restart: `systemctl restart rmm.service`
        - journalctl:
            - "tail" the logs: `journalctl --identifier uwsgi --follow`
            - View the logs: `journalctl --identifier uwsgi --since "30 minutes ago" | less`

    === ":material-ubuntu: standard"
    
        - Service: `rmm.service`
        - Socket: `/rmm/api/gueenrmm/gueenrmm.sock`
        - uWSGI config: `/rmm/api/gueenrmm/app.ini`
        - Log: None
        - Journal identifier: `uwsgi`
        - Version: 2.0.18
    
    === ":material-docker: docker"
    
        TBD - To Be Documented

#### Daphne: Django channels daemon

[Daphne](https://github.com/django/daphne) is the official ASGI HTTP/WebSocket server maintained by the [Channels project](https://channels.readthedocs.io/en/stable/index.html).

???+ note "systemd config"

    - Django [Channels configuration docs](https://channels.readthedocs.io/en/stable/topics/channel_layers.html)

    === ":material-console-line: status commands"

        - Status: `systemctl status --full daphne.service`
        - Stop: `systemctl stop daphne.service`
        - Start: `systemctl start daphne.service`
        - Restart: `systemctl restart daphne.service`
        - journalctl (this provides only system start/stop logs, not the actual logs):
            - "tail" the logs: `journalctl --identifier daphne --follow`
            - View the logs: `journalctl --identifier daphne --since "30 minutes ago" | less`

    === ":material-ubuntu: standard"

        - Service: `daphne.service`
        - Socket: `/rmm/daphne.sock`
        - Exec: `/rmm/api/env/bin/daphne -u /rmm/daphne.sock gueenrmm.asgi:application`
        - Config: `/rmm/api/gueenrmm/gueenrmm/local_settings.py`
        - Log: `/rmm/api/gueenrmm/gueenrmm/private/log/debug.log`

    === ":material-docker: docker"

        TBD - To Be Documented

#### NATS server service

[NATS](https://nats.io/) is a messaging bus for "live" communication between the agent and server. NATS provides the framework for the server to push commands to the agent and receive information back.

???+ note "systemd config"

    - [NATS server configuration docs](https://docs.nats.io/running-a-nats-service/configuration)

    === ":material-console-line: status commands"

        - Status: `systemctl status --full nats.service`
        - Stop: `systemctl stop nats.service`
        - Start: `systemctl start nats.service`
        - Restart: `systemctl restart nats.service`
        - Restart: `systemctl reload nats.service` reloads the config without restarting
        - journalctl:
            - "tail" the logs: `journalctl --identifier nats-server --follow`
            - View the logs: `journalctl --identifier nats-server --since "30 minutes ago" | less`
        - Listening process: `ss -tulnp | grep nats-server`

    === ":material-ubuntu: standard"
    
        - Service: `nats.service`
        - Address: `0.0.0.0`
        - Port: `4222`
        - Exec: `/usr/local/bin/nats-server --config /rmm/api/gueenrmm/nats-rmm.conf`
        - Config: `/rmm/api/gueenrmm/nats-rmm.conf`
            - TLS: `/etc/letsencrypt/live/example.com/fullchain.pem`
        - Log: None
        - Version: v2.3.3
    
    === ":material-docker: docker"
    
        TBD - To Be Documented

#### NATS API service

The NATS API service appears to bridge the connection between the NATS server and database, allowing the agent to save (i.e. push) information in the database.

???+ note "systemd config"

    === ":material-console-line: status commands"

        - Status: `systemctl status --full nats-api.service`
        - Stop: `systemctl stop nats-api.service`
        - Start: `systemctl start nats-api.service`
        - Restart: `systemctl restart nats-api.service`
        - journalctl: This application does not appear to log anything.

    === ":material-ubuntu: standard"
    
         - Service: `nats-api.service`
         - Exec: `/usr/local/bin/nats-api --config /rmm/api/gueenrmm/nats-api.conf`
         - Config: `/rmm/api/gueenrmm/nats-api.conf`
             - TLS: `/etc/letsencrypt/live/example.com/fullchain.pem`
         - Log: None
    
    === ":material-docker: docker"
    
        TBD - To Be Documented

#### Celery service

[Celery](https://github.com/celery/celery) is a task queue focused on real-time processing and is responsible for scheduling tasks to be sent to agents.

Log located at `/var/log/celery`

???+ note "systemd config"

    - [Celery docs](https://docs.celeryproject.org/en/stable/index.html)
    - [Celery configuration docs](https://docs.celeryproject.org/en/stable/userguide/configuration.html)

    === ":material-console-line: status commands"

        - Status: `systemctl status --full celery.service`
        - Stop: `systemctl stop celery.service`
        - Start: `systemctl start celery.service`
        - Restart: `systemctl restart celery.service`
        - journalctl: Celery executes `sh` causing the systemd identifier to be `sh`, thus mixing the `celery` and `celerybeat` logs together.
            - "tail" the logs: `journalctl --identifier sh --follow`
            - View the logs: `journalctl --identifier sh --since "30 minutes ago" | less`
        - Tail logs: `tail -F /var/log/celery/w*-*.log`

    === ":material-ubuntu: standard"
    
        - Service: `celery.service`
        - Exec: `/bin/sh -c '${CELERY_BIN} -A $CELERY_APP multi start $CELERYD_NODES --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} --loglevel="${CELERYD_LOG_LEVEL}" $CELERYD_OPTS'`
        - Config: `/etc/conf.d/celery.conf`
        - Log: `/var/log/celery/w*-*.log`
    
    === ":material-docker: docker"
    
        TBD - To Be Documented

#### Celery Beat service

[celery beat](https://github.com/celery/django-celery-beat) is a scheduler; It kicks off tasks at regular intervals, that are then executed by available worker nodes in the cluster.

???+ note "systemd config"

    - [Celery beat docs](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html)

    === ":material-console-line: status commands"

        - Status: `systemctl status --full celerybeat.service`
        - Stop: `systemctl stop celerybeat.service`
        - Start: `systemctl start celerybeat.service`
        - Restart: `systemctl restart celerybeat.service`
        - journalctl: Celery executes `sh` causing the systemd identifier to be `sh`, thus mixing the `celery` and `celerybeat` logs together.
            - "tail" the logs: `journalctl --identifier sh --follow`
            - View the logs: `journalctl --identifier sh --since "30 minutes ago" | less`
        - Tail logs: `tail -F /var/log/celery/beat.log`

    === ":material-ubuntu: standard"
    
        - Service: `celerybeat.service`
        - Exec: `/bin/sh -c '${CELERY_BIN} -A ${CELERY_APP} beat --pidfile=${CELERYBEAT_PID_FILE} --logfile=${CELERYBEAT_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL}'`
        - Config: `/etc/conf.d/celery.conf`
        - Log: `/var/log/celery/beat.log`
    
    === ":material-docker: docker"
    
        TBD - To Be Documented

#### MeshCentral

[MeshCentral](https://github.com/Ylianst/MeshCentral) is used for: "Take Control" (connecting to machine for remote access), and 2 screens of the "Remote Background" (Terminal, and File Browser).

???+ note "meshcentral"

    - [MeshCentral docs](https://info.meshcentral.com/downloads/MeshCentral2/MeshCentral2UserGuide.pdf)

    === ":material-console-line: status commands"

        - Status: `systemctl status --full meshcentral`
        - Stop: `systemctl stop meshcentral`
        - Start: `systemctl start meshcentral`
        - Restart: `systemctl restart meshcentral`

    === ":material-remote-desktop: Debugging"

        - Open either "Take Control" or "Remote Background" to get mesh login token
        - Open https://mesh.example.com to open native mesh admin interface
        - Left-side "My Server" > Choose "Console" > type `agentstats`
        - To view detailed logging goto "Trace" > click Tracing button and choose categories

### Other Dependencies

[Django](https://www.djangoproject.com/) - Framework to integrate the server to interact with browser.

<details>
  <summary>Django dependencies</summary>

```text
future==0.18.2
loguru==0.5.3
msgpack==1.0.2
packaging==20.9
psycopg2-binary==2.9.1
pycparser==2.20
pycryptodome==3.10.1
pyotp==2.6.0
pyparsing==2.4.7
pytz==2021.1
```
</details>

[qrcode](https://pypi.org/project/qrcode/) - Creating QR codes for 2FA.

<details>
  <summary>qrcode dependencies</summary>

```text
redis==3.5.3
requests==2.25.1
six==1.16.0
sqlparse==0.4.1
```
</details>

[twilio](https://www.twilio.com/) - Python SMS notification integration.

<details>
  <summary>twilio dependencies</summary>

```text
urllib3==1.26.5
uWSGI==2.0.19.1
validators==0.18.2
vine==5.0.0
websockets==9.1
zipp==3.4.1
```
</details>


## Windows Agent

Found in `%programfiles%\gueenAgent`

### Outbound Firewall Rules

If you have strict firewall rules these are the only outbound rules from the agent needed for all functionality:

1. All agents have to be able to connect outbound to grmm server on the 3 domain names on ports: 443 (agent and mesh) and 4222 (nats for checks/tasks/data)

2. The agent uses `https://icanhazip.gueenrmm.io/` to get public IP info. If this site is down for whatever reason, the agent will fallback to `https://icanhazip.com` and then `https://ifconfig.co/ip`

#### Unsigned Agents

Unsigned agents require access to: `https://github.com/gueencode/rmmagent/releases/*`

#### Signed Agents

Signed agents will require: `https://exe.gueenrmm.io/` and `https://exe2.gueenrmm.io/` for downloading/updating agents

### Services

3 services exist on all clients

* `Mesh Agent`
![MeshService](images/grmm_services_mesh.png)
![MeshAgentTaskManager](images/grmm_services__taskmanager_mesh.png)

**AND**

* `gueenAgent` and `Gueen RMM RPC Service`
![gueenAgentServices](images/grmm_services.png)
![gueenAgentTaskManager](images/grmm_services__taskmanager_agent.png)

The [MeshCentral](https://meshcentral.com/) system which is accessible from `https://mesh.example.com` and is used

* It runs 2 goroutines
  * one is the checkrunner which runs all the checks and then just sleeps until it's time to run more checks
  * 2nd goroutine periodically sends info about the agent to the rmm and also handles agent recovery

!!!note
    In Task Manager you will see additional `Gueen RMM Agent` processes appear and disappear. These are your Checks and Tasks running at scheduled intervals

`Gueen RMM RPC Service`

* Uses the pub/sub model so anytime you do anything realtime from rmm (like a send command or run script)
* It maintains a persistent connection to your to the api.example.com rmm server on `port:4222` and is listening for events (using [nats](https://nats.io/))
* It handles your Agent updates (Auto triggers at 35mins past every hour or when run manually from server Agents | Update Agents menu)

***

### Agent Installation Process

* Adds Defender AV exclusions
* Copies temp files to `c:\windows\temp\gueenxxx` folder.
* INNO setup installs app into `%ProgramData%\gueenAgent\` folder

***

### Agent Update Process

Downloads latest `winagent-vx.x.x-x86/64.exe` to `%programfiles%`

Executes the file (INNO setup exe)

Files create `c:\Windows\temp\gueenxxxx\` folder for install (and log files)

***

### Agent Recovery

#### Mesh Agent Recovery

gueen Agent just runs `mesh_agent.exe -something` to get the mesh agent id and saves it to the django database.

#### gueen RPC Recovery

#### gueen Agent Recovery

### Windows Update Management

Gueen RMM Agent sets:

```reg
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU
AUOptions (REG_DWORD):
1: Keep my computer up to date is disabled in Automatic Updates.
```

Uses this Microsoft API to handle updates: [https://docs.microsoft.com/en-us/windows/win32/api/_wua/](https://docs.microsoft.com/en-us/windows/win32/api/_wua/)

### Log files

You can find 3 sets of detailed logs at `/rmm/api/gueenrmm/gueenrmm/private/log`

* `error.log` nginx log for all errors on all grmm URL's: rmm, api and mesh

* `access.log` nginx log for access auditing on all URL's: rmm, api and mesh (_this is a large file, and should be cleaned periodically_)

* `django_debug.log` created by django webapp
