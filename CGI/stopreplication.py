#!/usr/bin/python

import subprocess
import os
# Import modules for CGI handling 
import cgi, cgitb
cgitb.enable()

# Create instance of FieldStorage 
form = cgi.FieldStorage()

# Get data from fields
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

def killPIDs():
    listpidscmd = 'ps -aux |grep '+clustername+' | awk \'{print $2}\' > pids.log'
    runCall(listpidscmd)
    
    pidfile = open('pids.log', 'r')
    pids = pidfile.readlines()
    pidfile.close()
    for pid in pids:
        cmd = '/bin/kill %s' % (pid)
        runCall(cmd)

killpids = 'ps -aux |grep '+clustername+' | awk \'{print $2}\' >> pids.log'

# Killing daemons
killPIDs()

# Updating running slon daemons
storeRunningDaemons()

# HTML return
print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Starting replication</title>"
print "</head>"
print "<body>"
print "<h2>Slon daemons kill for cluster %s</h2>" % (clustername)
print "</body>"
print "</html>"