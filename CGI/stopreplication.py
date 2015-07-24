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
    
def killPIDs():
    listpidscmd = 'ps -aux |grep '+clustername+' | awk \'{print $2}\' >> pids.log'
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