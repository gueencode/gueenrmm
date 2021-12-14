GUEEN_DIR#!/usr/bin/env bash

set -e

: "${MESH_USER:=meshcentral}"
: "${MESH_PASS:=meshcentralpass}"
: "${MONGODB_USER:=mongouser}"
: "${MONGODB_PASSWORD:=mongopass}"
: "${MONGODB_HOST:=gueen-mongodb}"
: "${MONGODB_PORT:=27017}"
: "${NGINX_HOST_IP:=172.20.0.20}"
: "${MESH_PERSISTENT_CONFIG:=0}"

mkdir -p /home/node/app/meshcentral-data
mkdir -p ${gueen_DIR}/tmp

if [ ! -f "/home/node/app/meshcentral-data/config.json" ] || [[ "${MESH_PERSISTENT_CONFIG}" -eq 0 ]]; then

encoded_uri=$(node -p "encodeURI('mongodb://${MONGODB_USER}:${MONGODB_PASSWORD}@${MONGODB_HOST}:${MONGODB_PORT}')")

mesh_config="$(cat << EOF
{
  "settings": {
    "mongodb": "${encoded_uri}",
    "Cert": "${MESH_HOST}",
    "TLSOffload": "${NGINX_HOST_IP}",
    "RedirPort": 80,
    "WANonly": true,
    "Minify": 1,
    "Port": 443,
    "AllowLoginToken": true,
    "AllowFraming": true,
    "_AgentPing": 60,
    "AgentPong": 300,
    "AllowHighQualityDesktop": true,
    "agentCoreDump": false,
    "Compression": true,
    "WsCompression": true,
    "AgentWsCompression": true,
    "MaxInvalidLogin": {
      "time": 5,
      "count": 5,
      "coolofftime": 30
    }
  },
  "domains": {
    "": {
      "Title": "Gueen RMM",
      "Title2": "gueenrmm",
      "NewAccounts": false,
      "mstsc": true,
      "GeoLocation": true,
      "CertUrl": "https://${NGINX_HOST_IP}:443"
    }
  }
}
EOF
)"

echo "${mesh_config}" > /home/node/app/meshcentral-data/config.json

fi

node node_modules/meshcentral --createaccount ${MESH_USER} --pass ${MESH_PASS} --email example@example.com
node node_modules/meshcentral --adminaccount ${MESH_USER}

if [ ! -f "${gueen_DIR}/tmp/mesh_token" ]; then
    mesh_token=$(node node_modules/meshcentral --logintokenkey)

    if [[ ${#mesh_token} -eq 160 ]]; then
      echo ${mesh_token} > /opt/gueen/tmp/mesh_token
    else
      echo "Failed to generate mesh token. Fix the error and restart the mesh container"
    fi
fi

# wait for nginx container
until (echo > /dev/tcp/"${NGINX_HOST_IP}"/443) &> /dev/null; do
  echo "waiting for nginx to start..."
  sleep 5
done

# start mesh
node node_modules/meshcentral
