
######################################
# Install a development environment: #
######################################

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y nginx python-dev postgresql mysql-server python-setuptools zlib1g-dev libjpeg62-dev git-core memcached python-distribute libxml2-dev supervisor rabbitmq-server postgresql-server-dev-all
sudo apt-get build-dep -y python-mysqldb

sudo ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib
sudo ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib
sudo ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib

sudo rabbitmqctl add_user skyhigh skyhigh
sudo rabbitmqctl add_vhost /skyhigh
sudo rabbitmqctl set_permissions -p /skyhigh skyhigh ".*" ".*" ".*"

git clone git@github.com:kmdg/skyhigh.git

cd skyhigh

./build_dev.sh

###############################
# Configure local settings.py #
###############################

By default the system will initialiZe a sqlite database (for testing and dev purposes).
You need to configure it to run with the actual MySQL databse by adding the following 
in a file called settings_local.py located in src/project/
This file does not get stored in git, as it may contain sensitive data.
You can override anything in src/project/settings.py in this file and it will not be pushed to GitHub.

src/project/settings_local.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'skyhigh,                       # Or path to database file if using sqlite3.
        'USER': 'skyhigh',                      # Not used with sqlite3.
        'PASSWORD': 'skyhigh',                  # Not used with sqlite3.
        'HOST': 'localhost',                    # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

You can then just run ./build_dev.sh again.

##########################
# Configure build_dev.sh #
##########################

build_dev.sh has the following variables that you can change.

export PROJECT_NAME=skyhigh
export INSTANCE_TYPE=dev
export DOMAIN=unomena.net

It produces a domain of: skyhigh.dev.unomena.net

The same goes for build_qa.sh and build_prod.sh


