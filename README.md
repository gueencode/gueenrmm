# Gueen RMM

[![Build Status](https://dev.azure.com/dcparsi/gueen%20RMM/_apis/build/status/gueencode.gueenrmm?branchName=develop)](https://dev.azure.com/dcparsi/gueen%20RMM/_build/latest?definitionId=4&branchName=develop)
[![Coverage Status](https://coveralls.io/repos/github/gueencode/gueenrmm/badge.png?branch=develop&kill_cache=1)](https://coveralls.io/github/gueencode/gueenrmm?branch=develop)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Gueen RMM is a remote monitoring & management tool for Windows computers, built with Django and Vue.\
It uses an [agent](https://github.com/gueencode/rmmagent) written in golang and integrates with [MeshCentral](https://github.com/Ylianst/MeshCentral)

# [LIVE DEMO](https://rmm.gueenrmm.io/)
Demo database resets every hour. A lot of features are disabled for obvious reasons due to the nature of this app.

### [Discord Chat](https://discord.gg/upGTkWp)

### [Documentation](https://gueencode.github.io/gueenrmm/)

## Features

- Teamviewer-like remote desktop control
- Real-time remote shell
- Remote file browser (download and upload files)
- Remote command and script execution (batch, powershell and python scripts)
- Event log viewer
- Services management
- Windows patch management
- Automated checks with email/SMS alerting (cpu, disk, memory, services, scripts, event logs)
- Automated task runner (run scripts on a schedule)
- Remote software installation via chocolatey
- Software and hardware inventory

## Windows versions supported

- Windows 7, 8.1, 10, Server 2008R2, 2012R2, 2016, 2019

## Installation / Backup / Restore / Usage

### Refer to the [documentation](https://gueencode.github.io/gueenrmm/)
