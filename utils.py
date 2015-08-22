# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DSGManagementTools
                                 A QGIS plugin
 Plugin to manage DSG's Cartographic production
                             -------------------
        begin                : 2015-07-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Brazilian Army - Geographic Service Bureau
        email                : suporte.dsgtools@dsg.eb.mil.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import subprocess
import urllib2
import urllib
import sys

from PyQt4.QtCore import *

class Utils:
    def __init__(self):
        pass
    
    def getPostGISConnections(self):
        settings = QSettings()
        settings.beginGroup('PostgreSQL/connections')
        currentConnections = settings.childGroups()
        settings.endGroup()
        return currentConnections
    
    def getPostGISConnectionParameters(self, name):
        settings = QSettings()
        settings.beginGroup('PostgreSQL/connections/'+name)
        database = settings.value('database')
        host = settings.value('host')
        port = settings.value('port')
        user = settings.value('username')
        password = settings.value('password')
        settings.endGroup()
        return (database, host, port, user, password)    
    
    def makeRequest(self, script, masterdb, slavedb, masterhost, slavehost, masteruser, masterpass, slaveuser, slavepass, cluster):
        serverUrl = 'http://localhost/cgi-bin/'+script
        data = {'MASTERDBNAME':masterdb,
                'SLAVEDBNAME':slavedb,
                'MASTERHOST':masterhost,
                'SLAVEHOST':slavehost,
                'MASTERUSER':masteruser,
                'MASTERPASS':masterpass,
                'SLAVEUSER':slaveuser,
                'SLAVEPASS':slavepass,
                'CLUSTERNAME':cluster}
        postFile = urllib.urlencode(data)
        req = urllib2.Request(url=serverUrl, data=postFile)
        return req

    def makeKillRequest(self, script, clustername):
        serverUrl = 'http://localhost/cgi-bin/'+script
        data = {'CLUSTERNAME':clustername}
        postFile = urllib.urlencode(data)
        req = urllib2.Request(url=serverUrl, data=postFile)
        return req
    
    def makeGetRunningDaemonsRequest(self, script):
        serverUrl = 'http://localhost/cgi-bin/'+script
        req = urllib2.Request(url=serverUrl)
        return req

    def run(self, req):
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            return ('Error occurred: '+str(e.args) + '\nReason URL: '+str(e.reason), False)
        except urllib2.HTTPError, e:
            return ('Error occurred: '+str(e.code) + '\nReason HTTP: '+str(e.msg), False)

        resp = response.read()
        ret = resp
        while resp:
            print resp
            resp = response.read()
            resp += resp
        return (ret, True)

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