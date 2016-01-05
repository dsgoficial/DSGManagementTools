#!/bin/bash

WGET="wget -E"
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
#rm -rf ~/.qgis2/python/plugins/DsgTools
#rm -rf ~/.qgis2/python/plugins/DSGManagementTools

#unzipping plugins
unzip ~/dsgtools.zip -d ~/
unzip ~/dsgmanagementtools.zip -d ~/

#moving new plugins versions
mv ~/$dsgtoolsfolder ~/hahaha/DsgTools
mv ~/$dsgmanagementtoolsfolder ~/hahaha/DSGManagementTools

#removing unnecessary files
rm -rf ~/lastestdsgtools.html
rm -rf ~/lastestdsgmanagementtools.html
rm -rf ~/dsgtools.zip
rm -rf ~/dsgmanagementtools.zip

exit