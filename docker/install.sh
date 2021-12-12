#!/usr/bin/env bash
set -o nounset
set -o errexit
set -o pipefail

temp="/tmp/gueen"

args="$*"
version="latest"
branch="master"
repo="gueencode"

branchRegex=" --branch ([^ ]+)"
if [[ " ${args}" =~ ${branchRegex} ]]; then
  branch="${BASH_REMATCH[1]}"
fi

repoRegex=" --repo ([^ ]+)"
if [[ " ${args}" =~ ${repoRegex} ]]; then
  repo="${BASH_REMATCH[1]}"
fi

echo "repo=${repo}"
echo "branch=${branch}"
gueen_cli="https://raw.githubusercontent.com/${repo}/gueenrmm/${branch}/docker/gueen-cli"

versionRegex=" --version ([^ ]+)"
if [[ " ${args}" =~ ${versionRegex} ]]; then
  version="${BASH_REMATCH[1]}"
fi

rm -rf "${temp}"
if ! mkdir "${temp}"; then
  echo >&2 "Failed to create temporary directory"
  exit 1
fi

cd "${temp}"
echo "Downloading gueen-cli from branch ${branch}"
if ! curl -sS "${gueen_cli}"; then
  echo >&2 "Failed to download installation package ${gueen_cli}"
  exit 1
fi

chmod +x gueen-cli
gueen-cli ${args} --version "${version}" 2>&1 | tee -a ~/install.log

cd ~
if ! rm -rf "${temp}"; then
  echo >&2 "Warning: Failed to remove temporary directory ${temp}"
fi
