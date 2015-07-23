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

slonmastercmd = '/usr/bin/nohup /usr/bin/slon %s \"dbname=%s user=%s host=%s password=%s\" >> master.log &' % (clustername, masterdb, masteruser, masterhost, masterpass)
slonslavecmd = '/usr/bin/nohup /usr/bin/slon %s \"dbname=%s user=%s host=%s password=%s\" >> slave.log &' % (clustername, slavedb, slaveuser, slavehost, slavepass)

# Running processes
runCall(slonmastercmd)
runCall(slonslavecmd)

# HTML return
print "Success!"