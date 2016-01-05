#!/bin/bash

echo "A conexão é feita com proxy?: (S/N)"; read USEPROXY
if [ "$USEPROXY" == "S" ]; then
	echo "Entre com o endereço do proxy: "; read PROXYHOST
	echo "Entre com a porta do proxy: "; read PROXYPORT
	echo "Entre com o usuário do proxy: "; read PROXYUSER
	echo "Entre com o password do proxy: "; read PROXYPASS
  
	export http_proxy="http://$PROXYUSER:$PROXYPASS@$PROXYHOST:$PROXYPORT"
	export https_proxy="http://$PROXYUSER:$PROXYPASS@$PROXYHOST:$PROXYPORT"
  
	SUDO="sudo -E"
	WGET="wget -E"
elif [ "$USEPROXY" == "N" ]; then
	SUDO="sudo"
	WGET="wget"	
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
sudo /etc/init.d/apache2 restart
	
#getting plugins latest tag html files
$WGET https://github.com/lcoandrade/DsgTools/releases/latest -O ~/lastestdsgtools.html
$WGET https://github.com/phborba/DSGManagementTools/releases/latest -O ~/lastestdsgmanagementtools.html

#getting latest tags urls
dsgtoolsurl=$(grep -r "/lcoandrade/DsgTools/archive/" ~/lastestdsgtools.html | grep ".zip" | awk -F' ' '{print $2}' | awk -F'=' '{print $2}' | awk -F'"' '{print $2}')
dsgmanagementtoolsurl=$(grep -r "/phborba/DSGManagementTools/archive/" ~/lastestdsgmanagementtools.html | grep ".zip" | awk -F' ' '{print $2}' | awk -F'=' '{print $2}' | awk -F'"' '{print $2}')

#removing unnecessary files
rm -rf ~/lastestdsgtools.html
rm -rf ~/lastestdsgmanagementtools.html

#downloading latest tags
$WGET https://github.com/$dsgtoolsurl -O ~/dsgtools.zip
$WGET https://github.com/$dsgmanagementtoolsurl -O ~/dsgmanagementtools.zip

#getting folder names
dsgtoolsfolder=$(zipinfo -1 ~/dsgtools.zip | head -1 |awk -F'/' '{print $1}')
dsgmanagementtoolsfolder=$(zipinfo -1 ~/dsgmanagementtools.zip | head -1 |awk -F'/' '{print $1}')

#deleting old plugins
#rm -rf ~/.qgis2/python/plugins/DsgTools
#rm -rf ~/.qgis2/python/plugins/DSGManagementTools

#unzipping plugins
unzip ~/dsgtools.zip -d ~/
unzip ~/dsgmanagementtools.zip -d ~/

#moving new plugins versions
mv ~/$dsgtoolsfolder ~/hahaha/DsgTools
mv ~/$dsgmanagementtoolsfolder ~/hahaha/DSGManagementTools

exit
