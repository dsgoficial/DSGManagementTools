#!/usr/bin/python

import subprocess
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

cmd_list = []
cmd_list.append('sh slony.sh')
cmd_list.append('sh slony_subscribe.sh')

slonmastercmd = 'slon %s \"dbname=%s user=%s host=%s password=%s\"' % (clustername, masterdb, masteruser, masterhost, masterpass)
slonslavecmd = 'slon %s \"dbname=%s user=%s host=%s password=%s\"' % (clustername, slavedb, slaveuser, slavehost, slavepass)

cmd_list.append(slonmastercmd)
cmd_list.append(slonslavecmd)

def updateScript(name, masterdb, slavedb, masterhost, slavehost, masteruser, masterpass, slaveuser, slavepass, cluster):
    script = open(name, 'r')
    scriptData = script.read()
    script.close()

    newData = scriptData.replace('[masterdbname]', masterdb)
    newData = scriptData.replace('[slavedbname]', slavedb)
    newData = scriptData.replace('[masterhost]', masterhost)
    newData = scriptData.replace('[slavehost]', slavehost)
    newData = scriptData.replace('[masteruser]', masteruser)
    newData = scriptData.replace('[masterpass]', masterpass)
    newData = scriptData.replace('[slaveuser]', slaveuser)
    newData = scriptData.replace('[slavepass]', slavepass)
    newData = scriptData.replace('[clustername]', cluster)
    
    script = open(name, 'w')
    script.write(newData)
    script.close()

def runProcess(self, cmd_list):
    #command samples
    #cmd_list = ['uname -r', 'uptime']
    
    out = []
    err = []
    
    for cmd in cmd_list:
        args = cmd.split()
        proc = subprocess.Popen(args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (stdoutdata, stderrdata) = proc.communicate()
        out.append(stdoutdata)
        err.append(stderrdata)
    
    print 'out=',out
    print 'err=',err
