# Management Commands

To run any of the management commands you must first activate the python virtual env:

```bash
cd /rmm/api/gueenrmm
source ../env/bin/activate
```

or docker version:

```bash
docker exec -it grmm-backend /bin/bash
/opt/venv/bin/python /opt/gueen/api/manage.py shell
```

!!!tip
    The Dev Docker version it would be `docker exec -it grmm-api-dev env/bin/python manage.py shell`

## Bulk Delete old agents by last checkin date or agent version

Test to see what will happen

```bash
python manage.py bulk_delete_agents --days 60
python manage.py bulk_delete_agents --agentver 1.5.0
```

Do the delete

```bash
python manage.py bulk_delete_agents --days 60 --delete
python manage.py bulk_delete_agents --agentver 1.5.0 --delete
```

## Reset a user's password

```bash
python manage.py reset_password <username>
```

## Reset a user's 2fa token

```bash
python manage.py reset_2fa <username>
```

## Find all agents that have X software installed

```bash
python manage.py find_software "adobe"
```

## Set specific Windows update to not install

```bash
from winupdate.models import WinUpdate
WinUpdate.objects.filter(kb="KB5007186").update(action="ignore", date_installed=None)
```

## Show outdated online agents

```bash
python manage.py show_outdated_agents
```

## Log out all active web sessions

```bash
python manage.py delete_tokens
```

## Reset all Auth Tokens for Install agents and web sessions

```bash
python manage.py shell
from knox.models import AuthToken
AuthToken.objects.all().delete()
```

## Check for orphaned tasks on all agents and remove them

```bash
python manage.py remove_orphaned_tasks
```

## Create a MeshCentral agent invite link

```bash
python manage.py get_mesh_exe_url
```

## Bulk update agent offline/overdue time

Change offline time on all agents to 5 minutes

```bash
python manage.py bulk_change_checkin --offline --all 5
```

Change offline time on all agents in site named *Example Site* to 2 minutes

```bash
python manage.py bulk_change_checkin --offline --site "Example Site" 2
```

Change offline time on all agents in client named *Example Client* to 12 minutes

```bash
python manage.py bulk_change_checkin --offline --client "Example Client" 12
```

Change overdue time on all agents to 10 minutes

```bash
python manage.py bulk_change_checkin --overdue --all 10
```

Change overdue time on all agents in site named *Example Site* to 4 minutes

```bash
python manage.py bulk_change_checkin --overdue --site "Example Site" 4
```

Change overdue time on all agents in client named *Example Client* to 14 minutes

```bash
python manage.py bulk_change_checkin --overdue --client "Example Client" 14
```
