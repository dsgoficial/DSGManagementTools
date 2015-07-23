#!/usr/bin/python

import subprocess
import os
# Import modules for CGI handling 
import cgi, cgitb
cgitb.enable()

# Create instance of FieldStorage 
form = cgi.FieldStorage()

# Get data from fields
masterpid = form.getvalue('MASTERPID')
slavepid = form.getvalue('SLAVEPID')

def runCall(cmd):
    subprocess.call(cmd, shell=True)

slonmastercmd = '/bin/kill %s' % (masterpid)
slonslavecmd = '/bin/kill %s' % (slavepid)

# Starting daemons
runCall(slonmastercmd)
runCall(slonslavecmd)

# HTML return
print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Starting replication</title>"
print "</head>"
print "<body>"
print "<h2>Slon daemon %s and %s killed!</h2>" % (masterpid, slavepid)
print "</body>"
print "</html>"