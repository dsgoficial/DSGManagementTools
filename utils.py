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
import sys

class Utils:
    def __init__(self):
        pass
    
    def makeRequest(self):
        osmUrl = 'http://10.67.198.233/teste.cgi'
        postFile = {'msg':'FUNCIONA!!!!'}
        req = urllib2.Request(url=osmUrl, data=postFile, headers={'Content-Type': 'application/xml'})
        return req

    def run(self):
        req = self.makeRequest()

        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            self.signals.errorOccurred.emit('Error occurred: '+str(e.args) + '\nReason: '+str(e.reason))
            return
        except urllib2.HTTPError, e:
            self.signals.errorOccurred.emit('Error occurred: '+str(e.code) + '\nReason: '+str(e.msg))
            return
        
        ret = response.read()

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