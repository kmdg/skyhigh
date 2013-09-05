#!/bin/bash

echo "Building "$SERVER_NAME

python bootstrap.py -v1.7.1
bin/buildout \
    buildout:server-names="$SERVER_NAMES" \
    buildout:server-name=$SERVER_NAME \
    buildout:fcgi-port=$FCGI_PORT \
    buildout:nginx_conf_file=$NGINX_CONF_FILE \
    buildout:https-port=$HTTPS_PORT

sudo chmod -R 777 logs

bin/django syncdb
bin/django evolve --execute --noinput

sudo rm /etc/nginx/sites-available/$SERVER_NAME.conf
sudo ln -s $PWD/nginx/$SERVER_NAME.conf /etc/nginx/sites-available/$SERVER_NAME.conf
sudo rm /etc/nginx/sites-enabled/$SERVER_NAME.conf
sudo ln -s /etc/nginx/sites-available/$SERVER_NAME.conf /etc/nginx/sites-enabled/$SERVER_NAME.conf

sudo bin/django.fcgi restart
sudo bin/celeryd.sh restart
sudo service nginx restart
sudo service memcached restart
