#!/usr/bin/env bash

set -o errexit
set -o pipefail

# gueen gueen-frontend gueen-nats gueen-nginx gueen-meshcentral
DOCKER_IMAGES="gueen gueen-frontend gueen-nats gueen-nginx gueen-meshcentral"

cd ..

for DOCKER_IMAGE in ${DOCKER_IMAGES}; do
  echo "Building gueen Image: ${DOCKER_IMAGE}..."
  docker build --pull --no-cache -t "${DOCKER_IMAGE}" -f "docker/containers/${DOCKER_IMAGE}/dockerfile" .
done