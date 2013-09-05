#!/bin/bash

export PROJECT_NAME=skyhigh
export INSTANCE_TYPE=qa
export FCGI_PORT=7812
export DOMAIN=unomena.net
export NGINX_CONF_FILE=nginx.conf.in
export HTTPS_PORT=443

export SERVER_NAME=$PROJECT_NAME.$INSTANCE_TYPE.$DOMAIN
export SERVER_NAMES="$SERVER_NAME"

./build_common.sh
