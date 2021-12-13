#!/bin/bash

SCRIPT_VERSION="127"
SCRIPT_URL='https://raw.githubusercontent.com/gueencode/gueenrmm/master/update.sh'
LATEST_SETTINGS_URL='https://raw.githubusercontent.com/gueencode/gueenrmm/master/api/gueenrmm/gueenrmm/settings.py'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
THIS_SCRIPT=$(readlink -f "$0")

TMP_FILE=$(mktemp -p "" "rmmupdate_XXXXXXXXXX")
curl -s -L "${SCRIPT_URL}" > ${TMP_FILE}
NEW_VER=$(grep "^SCRIPT_VERSION" "$TMP_FILE" | awk -F'[="]' '{print $3}')

if [ "${SCRIPT_VERSION}" -ne "${NEW_VER}" ]; then
    printf >&2 "${YELLOW}Old update script detected, downloading and replacing with the latest version...${NC}\n"
    wget -q "${SCRIPT_URL}" -O update.sh
    exec ${THIS_SCRIPT}
fi

rm -f $TMP_FILE

force=false
if [[ $* == *--force* ]]; then
    force=true
fi

if [ $EUID -eq 0 ]; then
  echo -ne "\033[0;31mDo NOT run this script as root. Exiting.\e[0m\n"
  exit 1
fi

sudo apt update

strip="User="
ORIGUSER=$(grep ${strip} /etc/systemd/system/rmm.service | sed -e "s/^${strip}//")

if [ "$ORIGUSER" != "$USER" ]; then
  printf >&2 "${RED}ERROR: You must run this update script from the same user account used during install: ${GREEN}${ORIGUSER}${NC}\n"
  exit 1
fi

TMP_SETTINGS=$(mktemp -p "" "rmmsettings_XXXXXXXXXX")
curl -s -L "${LATEST_SETTINGS_URL}" > ${TMP_SETTINGS}
SETTINGS_FILE="/rmm/api/gueenrmm/gueenrmm/settings.py"

LATEST_grmm_VER=$(grep "^grmm_VERSION" "$TMP_SETTINGS" | awk -F'[= "]' '{print $5}')
CURRENT_grmm_VER=$(grep "^grmm_VERSION" "$SETTINGS_FILE" | awk -F'[= "]' '{print $5}')

if [[ "${CURRENT_grmm_VER}" == "${LATEST_grmm_VER}" ]] && ! [[ "$force" = true ]]; then
  printf >&2 "${GREEN}Already on latest version. Current version: ${CURRENT_grmm_VER} Latest version: ${LATEST_grmm_VER}${NC}\n"
  rm -f $TMP_SETTINGS
  exit 0
fi

LATEST_MESH_VER=$(grep "^MESH_VER" "$TMP_SETTINGS" | awk -F'[= "]' '{print $5}')
LATEST_PIP_VER=$(grep "^PIP_VER" "$TMP_SETTINGS" | awk -F'[= "]' '{print $5}')
LATEST_NPM_VER=$(grep "^NPM_VER" "$TMP_SETTINGS" | awk -F'[= "]' '{print $5}')
NATS_SERVER_VER=$(grep "^NATS_SERVER_VER" "$TMP_SETTINGS" | awk -F'[= "]' '{print $5}')

CURRENT_PIP_VER=$(grep "^PIP_VER" "$SETTINGS_FILE" | awk -F'[= "]' '{print $5}')
CURRENT_NPM_VER=$(grep "^NPM_VER" "$SETTINGS_FILE" | awk -F'[= "]' '{print $5}')

cls() {
  printf "\033c"
}


CHECK_NATS_LIMITNOFILE=$(grep LimitNOFILE /etc/systemd/system/nats.service)
if ! [[ $CHECK_NATS_LIMITNOFILE ]]; then

sudo rm -f /etc/systemd/system/nats.service

natsservice="$(cat << EOF
[Unit]
Description=NATS Server
After=network.target

[Service]
PrivateTmp=true
Type=simple
ExecStart=/usr/local/bin/nats-server -c /rmm/api/gueenrmm/nats-rmm.conf
ExecReload=/usr/bin/kill -s HUP \$MAINPID
ExecStop=/usr/bin/kill -s SIGINT \$MAINPID
User=${USER}
Group=www-data
Restart=always
RestartSec=5s
LimitNOFILE=1000000

[Install]
WantedBy=multi-user.target
EOF
)"
echo "${natsservice}" | sudo tee /etc/systemd/system/nats.service > /dev/null
sudo systemctl daemon-reload
fi

if ! sudo nginx -t > /dev/null 2>&1; then
  sudo nginx -t
  echo -ne "\n"
  echo -ne "${RED}You have syntax errors in your nginx configs. See errors above. Please fix them and re-run this script.${NC}\n"
  echo -ne "${RED}Aborting...${NC}\n"
  exit 1
fi

if [ ! -f /etc/systemd/system/nats-api.service ]; then
natsapi="$(cat << EOF
[Unit]
Description=gueenrmm Nats Api v1
After=nats.service

[Service]
Type=simple
ExecStart=/usr/local/bin/nats-api
User=${USER}
Group=${USER}
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF
)"
echo "${natsapi}" | sudo tee /etc/systemd/system/nats-api.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable nats-api.service
fi

for i in nginx nats-api nats rmm daphne celery celerybeat
do
printf >&2 "${GREEN}Stopping ${i} service...${NC}\n"
sudo systemctl stop ${i}
done

printf >&2 "${GREEN}Restarting postgresql database${NC}\n"
sudo systemctl restart postgresql
sleep 5

rm -f /rmm/api/gueenrmm/app.ini

numprocs=$(nproc)
uwsgiprocs=4
if [[ "$numprocs" == "1" ]]; then
  uwsgiprocs=2
else
  uwsgiprocs=$numprocs
fi

uwsgini="$(cat << EOF
[uwsgi]
chdir = /rmm/api/gueenrmm
module = gueenrmm.wsgi
home = /rmm/api/env
master = true
processes = ${uwsgiprocs}
threads = ${uwsgiprocs}
enable-threads = true
socket = /rmm/api/gueenrmm/gueenrmm.sock
harakiri = 300
chmod-socket = 660
buffer-size = 65535
vacuum = true
die-on-term = true
max-requests = 500
EOF
)"
echo "${uwsgini}" > /rmm/api/gueenrmm/app.ini

CHECK_NGINX_WORKER_CONN=$(grep "worker_connections 2048" /etc/nginx/nginx.conf)
if ! [[ $CHECK_NGINX_WORKER_CONN ]]; then
  printf >&2 "${GREEN}Changing nginx worker connections to 2048${NC}\n"
  sudo sed -i 's/worker_connections.*/worker_connections 2048;/g' /etc/nginx/nginx.conf
fi

HAS_PY39=$(which python3.9)
if ! [[ $HAS_PY39 ]]; then
  printf >&2 "${GREEN}Updating to Python 3.9${NC}\n"
  sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev
  numprocs=$(nproc)
  cd ~
  wget https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tgz
  tar -xf Python-3.9.9.tgz
  cd Python-3.9.9
  ./configure --enable-optimizations
  make -j $numprocs
  sudo make altinstall
  cd ~
  sudo rm -rf Python-3.9.9 Python-3.9.9.tgz
fi

HAS_LATEST_NATS=$(/usr/local/bin/nats-server -version | grep "${NATS_SERVER_VER}")
if ! [[ $HAS_LATEST_NATS ]]; then
  printf >&2 "${GREEN}Updating nats to v${NATS_SERVER_VER}${NC}\n"
  nats_tmp=$(mktemp -d -t nats-XXXXXXXXXX)
  wget https://github.com/nats-io/nats-server/releases/download/v${NATS_SERVER_VER}/nats-server-v${NATS_SERVER_VER}-linux-amd64.tar.gz -P ${nats_tmp}
  tar -xzf ${nats_tmp}/nats-server-v${NATS_SERVER_VER}-linux-amd64.tar.gz -C ${nats_tmp}
  sudo rm -f /usr/local/bin/nats-server
  sudo mv ${nats_tmp}/nats-server-v${NATS_SERVER_VER}-linux-amd64/nats-server /usr/local/bin/
  sudo chmod +x /usr/local/bin/nats-server
  sudo chown ${USER}:${USER} /usr/local/bin/nats-server
  rm -rf ${nats_tmp}
fi

HAS_NODE14=$(/usr/bin/node --version | grep v14)
if ! [[ $HAS_NODE14 ]]; then
  printf >&2 "${GREEN}Updating NodeJS to v14${NC}\n"
  rm -rf /rmm/web/node_modules
  sudo systemctl stop meshcentral
  sudo apt remove -y nodejs
  sudo rm -rf /usr/lib/node_modules
  sudo rm -rf /home/${USER}/.npm/*
  curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
  sudo apt update
  sudo apt install -y nodejs
  sudo npm install -g npm
  sudo chown ${USER}:${USER} -R /meshcentral
  cd /meshcentral
  rm -rf node_modules/
  npm install meshcentral@${LATEST_MESH_VER}
  sudo systemctl start meshcentral
fi

sudo npm install -g npm

cd /rmm
git config user.email "admin@example.com"
git config user.name "Bob"
git fetch
git checkout master
git reset --hard FETCH_HEAD
git clean -df
git pull

SETUPTOOLS_VER=$(grep "^SETUPTOOLS_VER" "$SETTINGS_FILE" | awk -F'[= "]' '{print $5}')
WHEEL_VER=$(grep "^WHEEL_VER" "$SETTINGS_FILE" | awk -F'[= "]' '{print $5}')


sudo chown ${USER}:${USER} -R /rmm
sudo chown ${USER}:${USER} /var/log/celery
sudo chown ${USER}:${USER} -R /etc/conf.d/
sudo chown -R $USER:$GROUP /home/${USER}/.npm
sudo chown -R $USER:$GROUP /home/${USER}/.config
sudo chown -R $USER:$GROUP /home/${USER}/.cache
sudo chown ${USER}:${USER} -R /etc/letsencrypt
sudo chmod 775 -R /etc/letsencrypt

CHECK_ADMIN_ENABLED=$(grep ADMIN_ENABLED /rmm/api/gueenrmm/gueenrmm/local_settings.py)
if ! [[ $CHECK_ADMIN_ENABLED ]]; then
adminenabled="$(cat << EOF
ADMIN_ENABLED = False
EOF
)"
echo "${adminenabled}" | tee --append /rmm/api/gueenrmm/gueenrmm/local_settings.py > /dev/null
fi

sudo cp /rmm/natsapi/bin/nats-api /usr/local/bin
sudo chown ${USER}:${USER} /usr/local/bin/nats-api
sudo chmod +x /usr/local/bin/nats-api

if [[ "${CURRENT_PIP_VER}" != "${LATEST_PIP_VER}" ]] || [[ "$force" = true ]]; then
  rm -rf /rmm/api/env
  cd /rmm/api
  python3.9 -m venv env
  source /rmm/api/env/bin/activate
  cd /rmm/api/gueenrmm
  pip install --no-cache-dir --upgrade pip
  pip install --no-cache-dir setuptools==${SETUPTOOLS_VER} wheel==${WHEEL_VER}
  pip install --no-cache-dir -r requirements.txt
else
  source /rmm/api/env/bin/activate
  cd /rmm/api/gueenrmm
  pip install -r requirements.txt
fi

python manage.py pre_update_tasks
python manage.py migrate
python manage.py delete_tokens
python manage.py collectstatic --no-input
python manage.py reload_nats
python manage.py load_chocos
python manage.py create_installer_user
python manage.py create_natsapi_conf
python manage.py post_update_tasks
deactivate

rm -rf /rmm/web/dist
rm -rf /rmm/web/.quasar
cd /rmm/web
if [[ "${CURRENT_NPM_VER}" != "${LATEST_NPM_VER}" ]] || [[ "$force" = true ]]; then
  rm -rf /rmm/web/node_modules
fi

npm install
npm run build
sudo rm -rf /var/www/rmm/dist
sudo cp -pr /rmm/web/dist /var/www/rmm/
sudo chown www-data:www-data -R /var/www/rmm/dist

for i in nats nats-api rmm daphne celery celerybeat nginx
do
printf >&2 "${GREEN}Starting ${i} service${NC}\n"
sudo systemctl start ${i}
done

sleep 1
/rmm/api/env/bin/python /rmm/api/gueenrmm/manage.py update_agents

CURRENT_MESH_VER=$(cd /meshcentral/node_modules/meshcentral && node -p -e "require('./package.json').version")
if [[ "${CURRENT_MESH_VER}" != "${LATEST_MESH_VER}" ]] || [[ "$force" = true ]]; then
  printf >&2 "${GREEN}Updating meshcentral from ${CURRENT_MESH_VER} to ${LATEST_MESH_VER}${NC}\n"
  sudo systemctl stop meshcentral
  sudo chown ${USER}:${USER} -R /meshcentral
  cd /meshcentral
  rm -rf node_modules/
  npm install meshcentral@${LATEST_MESH_VER}
  sudo systemctl start meshcentral
fi

# apply redis configuration
sudo redis-cli config set appendonly yes
sudo redis-cli config rewrite

rm -f $TMP_SETTINGS
printf >&2 "${GREEN}Update finished!${NC}\n"