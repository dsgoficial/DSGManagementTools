#!/bin/bash

#configuring postgresql network--------------------------------------------
postgresqlversion=$(psql -V | awk -F' ' '{print $3}' | awk -F'.' '{print $1 "." $2}')
postgresqlfolder="/etc/postgresql/$postgresqlversion/main"
sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '\*'/g" ~/pg.conf
sudo sed -i "s/max_connections = 100/max_connections = 1000/g" ~/pg.conf
sudo sed -i "s:127.0.0.1/32:0.0.0.0/0:g" ~/hba.conf
sudo printf "\n" >> ~/hba.conf
sudo echo "host	all		all		0.0.0.0/0		md5" >> ~/hba.conf
#----------------installing and configuring packages--------------------------------------------

exit