#!/bin/bash

echo "A conexão é feita com proxy?: (S/N)"; read USEPROXY
if [ "$USEPROXY" == "S" ]; then
  echo "Entre com o endereço do proxy: "; read PROXYHOST
  echo "Entre com a porta do proxy: "; read PROXYPORT
  echo "Entre com o usuário do proxy: "; read PROXYUSER
  echo "Entre com o password do proxy: "; read PROXYPASS
  
  export http_proxy="http://$PROXYUSER:$PROXYPASS@$PROXYHOST:$PROXYPORT"
  export https_proxy="http://$PROXYUSER:$PROXYPASS@$PROXYHOST:$PROXYPORT"
  
  $SUDO = "sudo -E"
elif [ "$USEPROXY" == "N" ]; then
  $SUDO = "sudo"
else
  echo "Parâmetro inválido! Nada foi feito"
  exit
fi

#preparing QGIS repository
$SUDO add-apt-repository ppa:ubuntugis/ubuntugis-unstable
$SUDO apt-get update

#installing synaptic
$SUDO apt-get install synaptic

#installing packages
$SUDO apt-get install qgis saga python-saga otb-bin python-otb otb-bin-qt grass qgis-plugin-grass postgresql postgis slony1-2-bin postgresql-9.3-slony1-2 pgadmin3 apache2 libapache2-mod-python python-qt4-sql libqt4-sql-psql libqt4-sql-sqlite

#configuring apache2
sudo a2enmod cgi

exit
