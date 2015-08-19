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
import json

class JsonParser():
    def __init__(self, filename):
        self.filename = filename
        try:
            file = open(self.filename, 'r')
            data = file.read()
            self.parsed = json.loads(data)
        except:
            self.parsed = dict()

    def writeCluster(self, clustername, masterconn, masterpid, slaveconn, slavepid):
        self.parsed[clustername] = self.getClusterDict(masterconn, masterpid, slaveconn, slavepid)

        with open(self.filename, 'w') as outfile:
            json.dump(self.parsed, outfile)

    def getMasterDict(self, masterconn, masterpid):
        master = dict()
        master['masterconn'] = masterconn
        master['masterpid'] = masterpid
        return master

    def getSlaveDict(self, slaveconn, slavepid):
        slave = dict()
        slave['slaveconn'] = slaveconn
        slave['slavepid'] = slavepid
        return slave

    def getClusterDict(self, masterconn, masterpid, slaveconn, slavepid):
        cluster = dict()
        cluster['master'] = self.getMasterDict(masterconn, masterpid)
        cluster['slave'] = self.getSlaveDict(slaveconn, slavepid)
        return cluster

    def readMasterConn(self, clustername):
        return self.parsed[clustername]['master']['masterconn']

    def readMasterPid(self, clustername):
        return self.parsed[clustername]['master']['masterpid']

    def readSlaveConn(self, clustername):
        return self.parsed[clustername]['slave']['slaveconn']

    def readSlavePid(self, clustername):
        return self.parsed[clustername]['slave']['slavepid']

if __name__=='__main__':
    parser = JsonParser('/Users/luiz/Downloads/teste.json')
    parser.writeCluster('oi', 'master', '2222', 'slave', '3333')