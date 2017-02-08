#!/bin/bash

function set_proxy {
	echo "A conexão é feita com proxy?: (s/n)"; read USEPROXY
	USEPROXY="${USEPROXY:-s}"
	if [ "$USEPROXY" == "s" ]; then
		echo "Entre com o endereço do proxy: "; read PROXYHOST
		echo "Entre com a porta do proxy: "; read PROXYPORT
		echo "O proxy necessita de usuário e senha? (s/n)"; read USERNEEDED
		USERNEEDED="${USERNEEDED:=s}"
		if [[ $USERNEEDED == [sS] ]]; then
			echo "Entre com o usuário do proxy: "; read PROXYUSER
			echo "Entre com o password do proxy: "; read -s PROXYPASS
			export http_proxy="http://$PROXYUSER:$PROXYPASS@$PROXYHOST:$PROXYPORT"
			export https_proxy="http://$PROXYUSER:$PROXYPASS@$PROXYHOST:$PROXYPORT"
		else
			export http_proxy="http://$PROXYHOST:$PROXYPORT"
			export https_proxy="http://$PROXYHOST:$PROXYPORT"						
		fi
	  
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
#preparing QGIS repository
	codeName=$(lsb_release -sc)
	if grep -q "deb http://qgis.org/ubuntugis-ltr/ $codeName main" /etc/apt/sources.list; then
		echo "repositório QGIS LTR já adicionado"
	else
		$SUDO echo "deb http://qgis.org/ubuntugis-ltr/ $codeName main" | sudo tee -a /etc/apt/sources.list
	fi
	$SUDO add-apt-repository ppa:ubuntugis/ubuntugis-unstable
	$SUDO apt-get update
}

function install_packages {
#removing previously installed packages
	$SUDO apt-get remove qgis saga python-saga otb-bin python-otb otb-bin-qt grass qgis-plugin-grass libgdal1h
#cleaning and updating apt-get
	$SUDO apt-get update
	$SUDO apt-get autoclean
	$SUDO apt-get clean
	$SUDO apt-get autoremove
#installing packages
	$SUDO apt-get install synaptic qgis saga python-saga otb-bin python-otb otb-bin-qt grass qgis-plugin-grass postgresql pgadmin3 apache2 libapache2-mod-python python-qt4-sql libqt4-sql-psql libqt4-sql-sqlite
	$SUDO apt-get install postgis --install-suggests
	$SUDO apt-get install slony1-2-bin --install-suggests
	sudo mkdir -p ~/.qgis2/python/plugins	
	sudo chmod 777 -R ~/.qgis2
}

function configure_apache { 
#configuring apache2
	sudo a2enmod cgi
	sudo /etc/init.d/apache2 restart
}
	
function configure_postgresql() {
#Postgres user first password definition
	sudo -u postgres psql postgres -c "ALTER USER postgres WITH PASSWORD '$1'"
#configuring Postgresql
	export PGPASSWORD=$1
	postgresqlfolder=$(psql -c 'show config_file' -U postgres -h localhost -p 5432 |grep postgresql.conf)
	pghbafolder=$(psql -c 'show hba_file' -U postgres -h localhost -p 5432 |grep pg_hba.conf)
	sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '\*'/g" $postgresqlfolder
	sudo sed -i "s/max_connections = 100/max_connections = 1000/g" $postgresqlfolder
	sudo sed -i "s:127.0.0.1/32:0.0.0.0/0:g" $pghbafolder
	#sudo printf "\n" >> ~/hba.conf
	#sudo echo "host	all		all		0.0.0.0/0		md5" >> $pgpghbafolder
	sudo /etc/init.d/postgresql restart
}

function alter_postgres_password() {
	export PGPASSWORD=$1
	psql -c "ALTER USER postgres WITH PASSWORD '$2'" -U postgres -h localhost -p 5432
}

function update_plugins {	
#getting plugins latest tag html files
	$WGET https://github.com/lcoandrade/DsgTools/releases/latest -O ~/lastestdsgtools.html
	$WGET https://github.com/phborba/DSGManagementTools/releases/latest -O ~/lastestdsgmanagementtools.html
	
#getting latest tags urls
	dsgtoolsurl=$(sudo grep -r "/lcoandrade/DsgTools/archive/" ~/lastestdsgtools.html | grep ".zip" | awk -F' ' '{print $2}' | awk -F'=' '{print $2}' | awk -F'"' '{print $2}')
	dsgmanagementtoolsurl=$(sudo grep -r "/phborba/DSGManagementTools/archive/" ~/lastestdsgmanagementtools.html | grep ".zip" | awk -F' ' '{print $2}' | awk -F'=' '{print $2}' | awk -F'"' '{print $2}')
	
#downloading latest tags
	$WGET https://github.com/$dsgtoolsurl -O ~/dsgtools.zip
	$WGET https://github.com/$dsgmanagementtoolsurl -O ~/dsgmanagementtools.zip
	
#getting folder names
	dsgtoolsfolder=$(sudo zipinfo -1 ~/dsgtools.zip | head -1 |awk -F'/' '{print $1}')
	dsgmanagementtoolsfolder=$(sudo zipinfo -1 ~/dsgmanagementtools.zip | head -1 |awk -F'/' '{print $1}')
	
#deleting old plugins
	sudo rm -rf ~/.qgis2/python/plugins/DsgTools
	sudo rm -rf ~/.qgis2/python/plugins/DSGManagementTools
	
#unzipping plugins
	sudo unzip ~/dsgtools.zip -d ~/
	sudo unzip ~/dsgmanagementtools.zip -d ~/
	
#moving new plugins versions
	sudo mv ~/$dsgtoolsfolder ~/.qgis2/python/plugins/DsgTools
	sudo mv ~/$dsgmanagementtoolsfolder ~/.qgis2/python/plugins/DSGManagementTools
	
#removing unnecessary files
	sudo rm -rf ~/lastestdsgtools.html
	sudo rm -rf ~/lastestdsgmanagementtools.html
	sudo rm -rf ~/dsgtools.zip
	sudo rm -rf ~/dsgmanagementtools.zip	
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
#editing the crontab
	sudo crontab -u www-data -l > mycron
	echo "@reboot /usr/lib/cgi-bin/dsg_slon.sh" > mycron
	sudo crontab -u www-data mycron
	rm mycron
}

set_proxy
echo "Adicionar repositório do QGIS? (s/n)"; read addqgisrepository
addqgisrepository="${addqgisrepository:=s}"
if [[ $addqgisrepository == [sS] ]]; then
	add_qgis_repository
fi

echo "Instalar pacotes? (s/n)"; read instalarpacotes
instalarpacotes="${instalarpacotes:=s}"
if [[ $instalarpacotes == [sS] ]]; then
	install_packages
fi

echo "Configurar Apache? (s/n)"; read configurarapache
configurarapache="${configurarapache:=s}"
if [[ $configurarapache == [sS] ]]; then
	configure_apache
fi

echo "Configurar PostgresSQL? (s/n)"; read configurarpostgres
configurarpostgres="${configurarpostgres:=s}"
if [[ $configurarpostgres == [sS] ]]; then
	echo "Entre com o password: "; read PASSWORD
	configure_postgresql $PASSWORD
fi

echo "Alterar senha do usuário Postgres? (s/n)"; read alterarsenha
alterarsenha="${alterarsenha:=s}"
if [[ $alterarsenha == [sS] ]]; then
	echo "Entre com o password atual: "; read PASSWORD
	echo "Entre com o novo password: "; read NEWPASSWORD
	alter_postgres_password $PASSWORD $NEWPASSWORD
fi

echo "Atualizar plugins? (s/n)"; read atualizarplugins
atualizarplugins="${atualizarplugins:=s}"
if [[ $atualizarplugins == [sS] ]]; then
	update_plugins
fi

echo "Atualizar scripts do DSGManagementTools? (s/n)"; read atualizardsgmanagementtools
atualizardsgmanagementtools="${atualizardsgmanagementtools:=s}"
if [[ $atualizardsgmanagementtools == [sS] ]]; then
	update_dsgmanagementtools
fi

echo "Configurar Crontab? (s/n)"; read configurarcrontab
configurarcrontab="${configurarcrontab:=s}"
if [[ $configurarcrontab == [sS] ]]; then
	configure_crontab
fi

exit
