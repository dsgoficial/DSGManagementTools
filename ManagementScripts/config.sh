#!/bin/bash

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

exit
