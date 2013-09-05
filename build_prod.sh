#!/bin/bash

export PROJECT_NAME=skyhigh
export INSTANCE_TYPE=prod
export FCGI_PORT=7814
export DOMAIN=unomena.net
export NGINX_CONF_FILE=production.nginx.conf.in
export HTTPS_PORT=81

export SERVER_NAME=www.skyhighnetworks.com
export SERVER_NAMES="$SERVER_NAME"

./build_common.sh
