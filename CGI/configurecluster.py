#!/usr/bin/python

import subprocess
import os
# Import modules for CGI handling 
import cgi, cgitb
cgitb.enable()

# Create instance of FieldStorage 
form = cgi.FieldStorage()

# Get data from fields
masterdb = form.getvalue('MASTERDBNAME')
slavedb = form.getvalue('SLAVEDBNAME')
masterhost = form.getvalue('MASTERHOST')
slavehost = form.getvalue('SLAVEHOST')
masteruser = form.getvalue('MASTERUSER')
masterpass = form.getvalue('MASTERPASS')
slaveuser = form.getvalue('SLAVEUSER')
slavepass = form.getvalue('SLAVEPASS')
clustername = form.getvalue('CLUSTERNAME')

def updateScript(name, masterdb, slavedb, masterhost, slavehost, masteruser, masterpass, slaveuser, slavepass, cluster):
    script = open(name, 'r')
    scriptData = script.read()
    script.close()

    newData = scriptData.replace('[masterdbname]', masterdb)
    newData = newData.replace('[slavedbname]', slavedb)
    newData = newData.replace('[masterhost]', masterhost)
    newData = newData.replace('[slavehost]', slavehost)
    newData = newData.replace('[masteruser]', masteruser)
    newData = newData.replace('[masterpass]', masterpass)
    newData = newData.replace('[slaveuser]', slaveuser)
    newData = newData.replace('[slavepass]', slavepass)
    newData = newData.replace('[clustername]', cluster)
    
    split = name.split('.')
    newname = split[0]+'_temp.'+split[1]
    
    script = open(newname, 'w')
    script.write(newData)
    script.close()
    
def runCall(cmd):
    subprocess.call(cmd, shell=True)
            
# Updating scripts
updateScript('slony.sh', masterdb, slavedb, masterhost, slavehost, masteruser, masterpass, slaveuser, slavepass, clustername)
updateScript('slony_subscribe.sh', masterdb, slavedb, masterhost, slavehost, masteruser, masterpass, slaveuser, slavepass, clustername)
updateScript('slony_drop.sh', masterdb, slavedb, masterhost, slavehost, masteruser, masterpass, slaveuser, slavepass, clustername)

# Running processes
runCall('/bin/sh slony_temp.sh >> slony.log &')
runCall('/bin/sh slony_subscribe_temp.sh >> subscribe.log &')

# HTML return
print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Slony configuration</title>"
print "</head>"
print "<body>"
print "<h2>Success</h2>"
print "</body>"
print "</html>"