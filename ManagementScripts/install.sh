#!/bin/bash

function set_proxy {
	echo "A conexão é feita com proxy?: (s/n)"; read USEPROXY
	USEPROXY="${USEPROXY:-s}"
	if [ "$USEPROXY" == "s" ]; then
		echo "Entre com o endereço do proxy: "; read PROXYHOST
		echo "Entre com a porta do proxy: "; read PROXYPORT
		echo "Entre com o usuário do proxy: "; read PROXYUSER
		echo "Entre com o password do proxy: "; read PROXYPASS
	  
		export http_proxy="http://$PROXYUSER:$PROXYPASS@$PROXYHOST:$PROXYPORT"
		export https_proxy="http://$PROXYUSER:$PROXYPASS@$PROXYHOST:$PROXYPORT"
	  
		SUDO="sudo -E"
		WGET="wget -E"
	elif [ "$USEPROXY" == "n" ]; then
		SUDO="sudo"
		WGET="wget"	
	else
	  echo "Parâmetro inválido! Nada foi feito"
	  exit
	fi
}

function add_qgis_repository {
#preparing QGIS repository
	$SUDO add-apt-repository ppa:ubuntugis/ubuntugis-unstable
	$SUDO apt-get update
}

function install_packages {
#installing packages
	$SUDO apt-get install synaptic qgis saga python-saga otb-bin python-otb otb-bin-qt grass qgis-plugin-grass postgresql postgis slony1-2-bin postgresql-9.3-slony1-2 pgadmin3 apache2 libapache2-mod-python python-qt4-sql libqt4-sql-psql libqt4-sql-sqlite
}

function configure_apache { 
#configuring apache2
	sudo a2enmod cgi
	sudo /etc/init.d/apache2 restart
}
	
function configure_postgresql {
	export PGPASSWORD=postgres
	postgresqlfolder=$(psql -c 'show config_file' -U postgres -h localhost -p 5432 |grep postgresql.conf)
	pghbafolder=$(psql -c 'show hba_file' -U postgres -h localhost -p 5432 |grep pg_hba.conf)
	sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '\*'/g" $postgpostgresqlfolder
	sudo sed -i "s/max_connections = 100/max_connections = 1000/g" $postgpostgresqlfolder
	sudo sed -i "s:127.0.0.1/32:0.0.0.0/0:g" $pgpghbafolder
	#sudo printf "\n" >> ~/hba.conf
	#sudo echo "host	all		all		0.0.0.0/0		md5" >> $pgpghbafolder
	sudo /etc/init.d/postgresql restart
}

function update_plugins {	
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
}

function update_dsgmanagementtools {
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
}

function configure_crontab {
	sudo crontab -u www-data -l > mycron
	echo "@reboot /usr/lib/cgi-bin/dsg_slon.sh" > mycron
	sudo crontab -u www-data mycron
	rm mycron
}

set_proxy
echo "Adicionar repositório do QGIS?"; read addqgisrepository
addqgisrepository="${addqgisrepository:=s}"
if [[ "addqgisrepository" == [sS] ]]; then
	add_qgis_repository
fi

echo "Instalar pacotes?"; read instalarpacotes
instalarpacotes="${instalarpacotes:=s}"
if [[ "instalarpacotes" == [sS] ]]; then
	install_packages
fi

echo "Configurar Apache?"; read configurarapache
configurarapache="${configurarapache:=s}"
if [[ "configurarapache" == [sS] ]]; then
	configure_apache
fi

echo "Configurar PostgresSQL?"; read configurarpostgres
configurarpostgres="${configurarpostgres:=s}"
if [[ "configurarpostgres" == [sS] ]]; then
	configure_postgresql
fi

echo "Atualizatr plugins?"; read atualizarplugins
atualizarplugins="${atualizarplugins:=s}"
if [[ "atualizarplugins" == [sS] ]]; then
	update_plugins
fi

echo "Atualizar DSGManagementTools?"; read atualizardsgmanagementtools
atualizardsgmanagementtools="${atualizardsgmanagementtools:=s}"
if [[ "atualizardsgmanagementtools" == [sS] ]]; then
	update_dsgmanagementtools
fi

echo "Configurar Crontab?"; read configurarcrontab
configurarcrontab="${configurarcrontab:=s}"
if [[ "configurarcrontab" == [sS] ]]; then
	configurarcrontab
fi

exit
