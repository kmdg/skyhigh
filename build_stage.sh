#!/bin/bash

export PROJECT_NAME=skyhigh
export INSTANCE_TYPE=stage
export FCGI_PORT=7813
export DOMAIN=unomena.net
export NGINX_CONF_FILE=production.nginx.conf.in
export HTTPS_PORT=81

export SERVER_NAME=www-stage-421747157.us-west-2.elb.amazonaws.com
export SERVER_NAMES="$SERVER_NAME"

./build_common.sh
