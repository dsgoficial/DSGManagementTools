# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DsgManagementToolsDialog
                                 A QGIS plugin
 Tools to manage DSG's cartographic production
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

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot, Qt
from PyQt4.QtGui import QTreeWidgetItem, QMessageBox
from PyQt4.QtSql import QSqlDatabase, QSqlQuery
from DSGManagementTools.utils import Utils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dsg_management_tools_dialog_base.ui'))

class DsgManagementToolsDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DsgManagementToolsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.utils = Utils()
        
        self.populatePostGISConnectionsCombo()
        
        self.db = None
        
    def populatePostGISConnectionsCombo(self):
        self.serverCombo.clear()
        self.serverCombo.addItem("Select Database")
        self.serverCombo.addItems(self.utils.getPostGISConnections())

        self.clientCombo.clear()
        self.clientCombo.addItem("Select Database")
        self.clientCombo.addItems(self.utils.getPostGISConnections())

        self.serverCombo_2.clear()
        self.serverCombo_2.addItem("Select Database")
        self.serverCombo_2.addItems(self.utils.getPostGISConnections())

        self.clientCombo_2.clear()
        self.clientCombo_2.addItem("Select Database")
        self.clientCombo_2.addItems(self.utils.getPostGISConnections())
        
        self.serverCombo_3.clear()
        self.serverCombo_3.addItem("Select Database")
        self.serverCombo_3.addItems(self.utils.getPostGISConnections())

    @pyqtSlot(int)
    def on_serverCombo_3_currentIndexChanged(self, index):
        (slavedb, slavehost, slaveport, slaveuser, slavepass) = self.utils.getPostGISConnectionParameters(self.serverCombo_3.currentText())
        
        self.getConnection(slavedb, slavehost, slaveport, slaveuser, slavepass)

        sql = 'select schema_name from information_schema.schemata'
        query = QSqlQuery(sql, self.db)
        while query.next():
            schema = str(query.value(0))
            if schema[0] == '_':
                self.insertClusterItem(self.treeWidget.invisibleRootItem(), schema)
                
    def getConnection(self, slavedb, slavehost, slaveport, slaveuser, slavepass):
        if self.db:
            self.db.close()
            self.db = None
        
        self.db = QSqlDatabase("QPSQL")
        self.db.setDatabaseName(slavedb)
        self.db.setHostName(slavehost)
        self.db.setPort(int(slaveport))
        self.db.setUserName(slaveuser)
        self.db.setPassword(slavepass)
        
        if not self.db.open():
            print self.db.lastError().text()
            
    def insertClusterItem(self, parent, text):
        self.treeWidget.clear()
        
        item = QTreeWidgetItem(parent)
        item.setExpanded(True)
        item.setText(0,text)

    @pyqtSlot(int)
    def on_serverCombo_currentIndexChanged(self, index):
        slavedb = self.serverCombo.currentText()
        masterdb = self.clientCombo.currentText()
        self.clusterEdit.setText(masterdb+'2'+slavedb)

    @pyqtSlot(int)
    def on_clientCombo_currentIndexChanged(self, index):
        slavedb = self.serverCombo.currentText()
        masterdb = self.clientCombo.currentText()
        self.clusterEdit.setText(masterdb+'2'+slavedb)
        
    @pyqtSlot(bool)
    def on_createClusterButton_clicked(self):
        cluster = self.clusterEdit.text()
        
        (slavedb, slavehost, slaveport, slaveuser, slavepass) = self.utils.getPostGISConnectionParameters(self.serverCombo.currentText())
        (masterdb, masterhost, masterport, masteruser, masterpass) = self.utils.getPostGISConnectionParameters(self.clientCombo.currentText())
        
        req = self.utils.makeRequest('configurecluster.py', masterdb, slavedb, masterhost, slavehost, masteruser, masterpass, slaveuser, slavepass, cluster)
        self.utils.run(req)
        
    @pyqtSlot(bool)
    def on_startReplicationButton_clicked(self):
        slavedb = self.serverCombo_2.currentText()
        masterdb = self.clientCombo_2.currentText()
        cluster = masterdb+'2'+slavedb
        
        (slavedb, slavehost, slaveport, slaveuser, slavepass) = self.utils.getPostGISConnectionParameters(self.serverCombo_2.currentText())
        (masterdb, masterhost, masterport, masteruser, masterpass) = self.utils.getPostGISConnectionParameters(self.clientCombo_2.currentText())
        
        req = self.utils.makeRequest('startreplication.py', masterdb, slavedb, masterhost, slavehost, masteruser, masterpass, slaveuser, slavepass, cluster)
        self.utils.run(req)

    @pyqtSlot(bool)
    def on_removeClusterButton_clicked(self):
        #case no item is selected we should warn the user
        if len(self.treeWidget.selectedItems()) == 0:
            QMessageBox.warning(self, self.tr("Warning!"), self.tr("Please, select a cluster to be removed."))
            return

        item = self.treeWidget.selectedItems()[0]
        
        self.checkAndKillSlonDaemons(item.text(0))
        
        self.removeClusters(item.text(0))
        
    def removeClusters(self, clustername):
        cluster = clustername[1::]
        split = cluster.split('2')
        
        self.removeCluster(clustername, split[0])
        self.removeCluster(clustername, split[1])        
        
    def removeCluster(self, clustername, conn):
        (conndb, connhost, connport, connuser, connpass) = self.utils.getPostGISConnectionParameters(conn)
        
        db = QSqlDatabase("QPSQL")
        db.setDatabaseName(conndb)
        db.setHostName(connhost)
        db.setPort(int(connport))
        db.setUserName(connuser)
        db.setPassword(connpass)
        
        if not db.open():
            print db.lastError().text()

        sql = 'DROP SCHEMA '+clustername+' CASCADE'
        query = QSqlQuery(db)
        query.exec_(sql)        
    
    def checkAndKillSlonDaemons(self, clustername):
        cluster = clustername[1::]
        split = cluster.split('2')
        
        masterpid = self.getDaemonPID(clustername, split[0])
        slavepid = self.getDaemonPID(clustername, split[1])
        
        if masterpid and slavepid:
            print masterpid, slavepid
            req = self.utils.makeKillRequest('stopreplication.py', masterpid, slavepid)
            self.utils.run(req)
        
    def getDaemonPID(self, clustername, conn):
        (conndb, connhost, connport, connuser, connpass) = self.utils.getPostGISConnectionParameters(conn)
        
        db = QSqlDatabase("QPSQL")
        db.setDatabaseName(conndb)
        db.setHostName(connhost)
        db.setPort(int(connport))
        db.setUserName(connuser)
        db.setPassword(connpass)
        
        if not db.open():
            print db.lastError().text()

        sql = 'select distinct co_pid from '+clustername+'.sl_components where co_actor = \'local_sync\''
        query = QSqlQuery(sql, db)
        while query.next():
            pid = str(query.value(0))
            return pid
        