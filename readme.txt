
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
