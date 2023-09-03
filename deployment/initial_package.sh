#!/bin/bash

mkdir /home/ubuntu/log/nginx /home/ubuntu/log/uwsgi

sudo apt update
sudo apt -y upgrade
sudo apt install -y build-essential
sudo apt install -y python3-dev, python3-pip
sudo apt install -y libmysqlclient-dev

sudo apt install -y nginx uwsgi uwsgi-plugin-python3

sudo rm /etc/nginx/sites-enabled/default
sudo cp -f conf/nginx.conf /etc/nginx/nginx.conf
sudo cp -f conf/nginx_site.conf /etc/nginx/sites-enabled/kook
sudo cp -f conf/uwsgi.ini /etc/uwsgi/apps-enabled/kook.ini

sudo service uwsgi restart
sudo service nginx restart
