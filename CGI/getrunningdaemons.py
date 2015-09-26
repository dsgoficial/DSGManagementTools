#!/usr/bin/python

import subprocess
import os
# Import modules for CGI handling 
import cgi, cgitb
cgitb.enable()

separador = '_to_'

def runCall(cmd):
    subprocess.call(cmd, shell=True)    
    
def getRunningDaemons():
    listdaemons = 'ps -aux |grep -E \'/usr/bin/slon.*'+separador+'\'|grep -v grep | awk \'{print \"\"$8\" \"$11\" \"$12\" \"$13\" \"$14\" \"$15\" \"$16\"\"}\' > running_daemons.log'
    runCall(listdaemons)
    
    daemons = open('running_daemons.log', 'r')
    lines = daemons.readlines()
    daemons.close()
    return lines

def makeResponse(lines):
    if len(lines) == 0:
        return 'Nada sendo replicado'
    
    response = ''
    for i in range(len(lines)):
        line = lines[i]
        clustername = line.split(' ')[2]
        split = clustername.split(separador)
        de = split[0]
        para = split[1]
        response += 'Replicando de '+de+' para '+para
        if i != len(lines)-1:
            response += '*'
    return response

response = makeResponse(getRunningDaemons())

# HTML return
print "Content-type:text/plain"
print 
print response