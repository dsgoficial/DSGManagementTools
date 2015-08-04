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

def runCall(cmd):
    subprocess.call(cmd, shell=True)
    
def storeRunningDaemons():
    listdaemons = 'ps -aux |grep -E \'/usr/bin/slon.*__para__\'|grep -v grep | awk \'{print \"/usr/bin/nohup \"$11\" \"$12\" \"$13\" \"$14\" \"$15\" \"$16\" &\"}\' > running_daemons.log'
    runCall(listdaemons)
    
    daemons = open('running_daemons.log', 'r')
    lines = daemons.readlines()
    daemons.close()
    
    slon_restore = open('dsg_slon.sh', 'wb')
    conteudo = ['#!/bin/bash\n'] + lines
    slon_restore.writelines(conteudo)
    slon_restore.close()
    
    runCall('chmod +x dsg_slon.sh')

slonsubscribe = '/usr/bin/nohup sh slony_subscribe_temp.sh >> subscribe.log &'
slonmastercmd = '/usr/bin/nohup /usr/bin/slon %s \"dbname=%s user=%s host=%s password=%s\" >> master.log &' % (clustername, masterdb, masteruser, masterhost, masterpass)
slonslavecmd = '/usr/bin/nohup /usr/bin/slon %s \"dbname=%s user=%s host=%s password=%s\" >> slave.log &' % (clustername, slavedb, slaveuser, slavehost, slavepass)

# Starting daemons
runCall(slonsubscribe)
runCall(slonmastercmd)
runCall(slonslavecmd)

# Updating running slon daemons
storeRunningDaemons()

# HTML return
print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Starting replication</title>"
print "</head>"
print "<body>"
print "<h2>Clustername = %s | Master DB = %s | Slave DB = %s</h2>" % (clustername, masterdb, slavedb)
print "</body>"
print "</html>"