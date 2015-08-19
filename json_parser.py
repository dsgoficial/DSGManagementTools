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
        self.parsed = dict()

    def writeCluster(self, clustername, masterconn, masterpid, slaveconn, slavepid):
        self.writeMasterConn(clustername, masterconn)
        self.writeMasterPid(clustername, masterpid)
        self.writeSlaveConn(clustername, slaveconn)
        self.writeSlavePid(clustername, slavepid)

        with open(self.filename, 'w') as outfile:
            json.dump(self.parsed, outfile)

    def writeMasterConn(self, clustername, masterconn):
        data = dict()
        data['master'] = 'masterconn'
        data['master']['masterconn'] = masterconn
        self.parsed[clustername] = data

    def writeMasterPid(self, clustername, masterpid):
        dict = dict()
        self.parsed[clustername]['master']['masterpid'] = masterpid

    def writeSlaveConn(self, clustername, slaveconn):
        self.parsed[clustername]['slave']['slaveconn'] = slaveconn

    def writeSlavePid(self, clustername, slavepid):
        self.parsed[clustername]['slave']['slavepid'] = slavepid

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
    parser.writeCluster('teste', 'master', '2222', 'slave', '3333')