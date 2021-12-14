GUEEN_DIR#!/usr/bin/env bash

set -e

: "${grmm_USER:=gueen}"
: "${grmm_PASS:=gueen}"
: "${POSTGRES_HOST:=gueen-postgres}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=gueen}"
: "${POSTGRES_PASS:=gueen}"
: "${POSTGRES_DB:=gueenrmm}"
: "${MESH_CONTAINER:=gueen-meshcentral}"
: "${MESH_USER:=meshcentral}"
: "${MESH_PASS:=meshcentralpass}"
: "${MESH_HOST:=gueen-meshcentral}"
: "${API_HOST:=gueen-backend}"
: "${APP_HOST:=gueen-frontend}"
: "${REDIS_HOST:=gueen-redis}"


function check_gueen_ready {
  sleep 15
  until [ -f "${gueen_READY_FILE}" ]; do
    echo "waiting for init container to finish install or update..."
    sleep 10
  done
}

# gueen-init
if [ "$1" = 'gueen-init' ]; then

  test -f "${gueen_READY_FILE}" && rm "${gueen_READY_FILE}"

  # copy container data to volume
  rsync -a --no-perms --no-owner --delete --exclude "tmp/*" --exclude "certs/*" --exclude="api/gueenrmm/private/*" "${gueen_TMP_DIR}/" "${gueen_DIR}/"

  mkdir -p ${gueen_DIR}/tmp
  mkdir -p ${gueen_DIR}/api/gueenrmm/private/exe
  mkdir -p ${gueen_DIR}/api/gueenrmm/private/log
  touch ${gueen_DIR}/api/gueenrmm/private/log/django_debug.log
  
  until (echo > /dev/tcp/"${POSTGRES_HOST}"/"${POSTGRES_PORT}") &> /dev/null; do
    echo "waiting for postgresql container to be ready..."
    sleep 5
  done

  until (echo > /dev/tcp/"${MESH_CONTAINER}"/443) &> /dev/null; do
    echo "waiting for meshcentral container to be ready..."
    sleep 5
  done

  # configure django settings
  MESH_TOKEN=$(cat ${gueen_DIR}/tmp/mesh_token)
  ADMINURL=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 70 | head -n 1)
  DJANGO_SEKRET=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 80 | head -n 1)
  
  localvars="$(cat << EOF
SECRET_KEY = '${DJANGO_SEKRET}'

DEBUG = False

DOCKER_BUILD = True

CERT_FILE = '/opt/gueen/certs/fullchain.pem'
KEY_FILE = '/opt/gueen/certs/privkey.pem'

EXE_DIR = '/opt/gueen/api/gueenrmm/private/exe'
LOG_DIR = '/opt/gueen/api/gueenrmm/private/log'

SCRIPTS_DIR = '/opt/gueen/scripts'

ALLOWED_HOSTS = ['${API_HOST}', 'gueen-backend']

ADMIN_URL = '${ADMINURL}/'

CORS_ORIGIN_WHITELIST = [
    'https://${APP_HOST}'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '${POSTGRES_DB}',
        'USER': '${POSTGRES_USER}',
        'PASSWORD': '${POSTGRES_PASS}',
        'HOST': '${POSTGRES_HOST}',
        'PORT': '${POSTGRES_PORT}',
    }
}

MESH_USERNAME = '${MESH_USER}'
MESH_SITE = 'https://${MESH_HOST}'
MESH_TOKEN_KEY = '${MESH_TOKEN}'
REDIS_HOST    = '${REDIS_HOST}'
MESH_WS_URL = 'ws://${MESH_CONTAINER}:443'
ADMIN_ENABLED = False
EOF
)"

  echo "${localvars}" > ${gueen_DIR}/api/gueenrmm/local_settings.py


uwsgiconf="$(cat << EOF
[uwsgi]
chdir = /opt/gueen/api
module = gueenrmm.wsgi
home = /opt/venv
master = true
processes = 8
threads = 2
enable-threads = true
socket = 0.0.0.0:80
chmod-socket = 660
buffer-size = 65535
vacuum = true
die-on-term = true
max-requests = 2000
EOF
)"

  echo "${uwsgiconf}" > ${gueen_DIR}/api/uwsgi.ini


  # run migrations and init scripts
  python manage.py migrate --no-input
  python manage.py collectstatic --no-input
  python manage.py initial_db_setup
  python manage.py initial_mesh_setup
  python manage.py load_chocos
  python manage.py load_community_scripts
  python manage.py reload_nats
  python manage.py create_natsapi_conf
  python manage.py create_installer_user

  # create super user 
  echo "from accounts.models import User; User.objects.create_superuser('${grmm_USER}', 'admin@example.com', '${grmm_PASS}') if not User.objects.filter(username='${grmm_USER}').exists() else 0;" | python manage.py shell

  # chown everything to gueen user
  chown -R "${gueen_USER}":"${gueen_USER}" "${gueen_DIR}"

  # create install ready file
  su -c "echo 'gueen-init' > ${gueen_READY_FILE}" "${gueen_USER}"

fi

# backend container
if [ "$1" = 'gueen-backend' ]; then
  check_gueen_ready

  uwsgi ${gueen_DIR}/api/uwsgi.ini
fi

if [ "$1" = 'gueen-celery' ]; then
  check_gueen_ready
  celery -A gueenrmm worker -l info
fi

if [ "$1" = 'gueen-celerybeat' ]; then
  check_gueen_ready
  test -f "${gueen_DIR}/api/celerybeat.pid" && rm "${gueen_DIR}/api/celerybeat.pid"
  celery -A gueenrmm beat -l info
fi

# websocket container
if [ "$1" = 'gueen-websockets' ]; then
  check_gueen_ready

  export DJANGO_SETTINGS_MODULE=gueenrmm.settings

  daphne gueenrmm.asgi:application --port 8383 -b 0.0.0.0
fi