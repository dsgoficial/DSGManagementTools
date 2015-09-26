#!/usr/bin/python

import subprocess
import os, time
# Import modules for CGI handling 
import cgi, cgitb
cgitb.enable()

separador = '_to_'

# Create instance of FieldStorage 
form = cgi.FieldStorage()

# Get data from fields
clustername = form.getvalue('CLUSTERNAME')
slavehost = form.getvalue('SLAVEHOST')

def runCall(cmd):
    subprocess.call(cmd, shell=True)
    
def storeRunningDaemons():
    listdaemons = 'ps -aux |grep -E \'/usr/bin/slon.*'+separador+'\'|grep -v grep | awk \'{print \"\"$8\" \"$11\" \"$12\" \"$13\" \"$14\" \"$15\" \"$16\"\"}\' > running_daemons.log'
    runCall(listdaemons)
    
    daemons = open('running_daemons.log', 'r')
    lines = daemons.readlines()
    daemons.close()
    newlines = []
    for line in lines:
        split = line.split(' ')
        if split[0] == 'S':
            if split[5] == 'host='+slavehost:
                hostType = 'slave'
            else:
                hostType = 'master'
            s = '/usr/bin/nohup '+split[1]+' '+split[2]+' \"'+split[3]+' '+split[4]+' '+split[5]+' '+split[6].strip('\n')+'\" >> /usr/lib/cgi-bin/'+split[2]+'_'+hostType+'.log &\n'
            newlines.append(s)
                
    slon_restore = open('dsg_slon.sh', 'wb')
    conteudo = ['#!/bin/bash\n'] + newlines
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

def message(msg):
    # HTML return
    print "Content-type:text/plain"
    print
    print msg,

killpids = 'ps -aux |grep '+clustername+' | awk \'{print $2}\' >> pids.log'

# Killing daemons
killPIDs()
time.sleep(3)

# Updating running slon daemons
storeRunningDaemons()

msg = 'Replicação do cluster %s parada com sucesso!' % clustername
message(msg)
