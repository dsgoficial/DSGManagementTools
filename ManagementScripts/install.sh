#!/bin/bash

#----------------setting proxy--------------------------------------------
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
#----------------setting proxy--------------------------------------------

#----------------installing and configuring packages-------------------------------------------
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
	
#configuring postgresql network
postgresqlversion=$(psql -V | awk -F' ' '{print $3}' | awk -F'.' '{print $1 "." $2}')
postgresqlfolder="/etc/postgresql/$postgresqlversion/main"
sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '\*'/g" $postgpostgresqlfolder/postgresql.conf
sudo sed -i "s/max_connections = 100/max_connections = 1000/g" $postgpostgresqlfolder/postgresql.conf
sudo sed -i "s:127.0.0.1/32:0.0.0.0/0:g" $postgpostgresqlfolder/pg_hba.conf
#sudo printf "\n" >> ~/hba.conf
#sudo echo "host	all		all		0.0.0.0/0		md5" >> ~/hba.conf
#----------------installing and configuring packages--------------------------------------------
	
#----------------updating plugins-------------------------------------------
#getting plugins latest tag html files
$WGET https://github.com/lcoandrade/DsgTools/releases/latest -O ~/lastestdsgtools.html
$WGET https://github.com/phborba/DSGManagementTools/releases/latest -O ~/lastestdsgmanagementtools.html

#getting latest tags urls
dsgtoolsurl=$(grep -r "/lcoandrade/DsgTools/archive/" ~/lastestdsgtools.html | grep ".zip" | awk -F' ' '{print $2}' | awk -F'=' '{print $2}' | awk -F'"' '{print $2}')
dsgmanagementtoolsurl=$(grep -r "/phborba/DSGManagementTools/archive/" ~/lastestdsgmanagementtools.html | grep ".zip" | awk -F' ' '{print $2}' | awk -F'=' '{print $2}' | awk -F'"' '{print $2}')

#downloading latest tags
$WGET https://github.com/$dsgtoolsurl -O ~/dsgtools.zip
$WGET https://github.com/$dsgmanagementtoolsurl -O ~/dsgmanagementtools.zip

#getting folder names
dsgtoolsfolder=$(zipinfo -1 ~/dsgtools.zip | head -1 |awk -F'/' '{print $1}')
dsgmanagementtoolsfolder=$(zipinfo -1 ~/dsgmanagementtools.zip | head -1 |awk -F'/' '{print $1}')

#deleting old plugins
sudo rm -rf ~/.qgis2/python/plugins/DsgTools
sudo rm -rf ~/.qgis2/python/plugins/DSGManagementTools

#unzipping plugins
unzip ~/dsgtools.zip -d ~/
unzip ~/dsgmanagementtools.zip -d ~/

#moving new plugins versions
sudo mv ~/$dsgtoolsfolder ~/.qgis2/python/plugins/DsgTools
sudo mv ~/$dsgmanagementtoolsfolder ~/.qgis2/python/plugins/DsgTools

#removing unnecessary files
rm -rf ~/lastestdsgtools.html
rm -rf ~/lastestdsgmanagementtools.html
rm -rf ~/dsgtools.zip
rm -rf ~/dsgmanagementtools.zip

sudo chmod 777 -R ~/.qgis2/python/plugins
#----------------installing and configuring packages--------------------------------------------

#----------------updating CGI and Shell Scripts for DSGManagementTools-------------------------------------------
#copying files
for f in ~/.qgis2/python/plugins/DSGManagementTools/CGI/*.py
do
  sudo cp $f /usr/lib/cgi-bin
done

for f in ~/.qgis2/python/plugins/DSGManagementTools/ShellScripts/*.sh
do
  sudo cp $f /usr/lib/cgi-bin
done

sudo chmod 777 -R /usr/lib/cgi-bin

#configuring crontab
sudo crontab -u www-data -l > mycron
echo "@reboot /usr/lib/cgi-bin/dsg_slon.sh" > mycron
sudo crontab -u www-data mycron
rm mycron
#----------------updating CGI and Shell Scripts for DSGManagementTools--------------------------------------------

exit
