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

#QGIS Imports
from qgis.core import QgsCredentials

from PyQt4 import QtGui, uic, QtCore
from PyQt4.QtCore import pyqtSlot, Qt, QSettings
from PyQt4.QtGui import QTreeWidgetItem, QMessageBox
from PyQt4.QtSql import QSqlDatabase, QSqlQuery
from DSGManagementTools.utils import Utils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dsg_management_tools_dialog_base.ui'))

separador = '_to_'

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
        
        #Ip validator
        regex = QtCore.QRegExp("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        self.validator=QtGui.QRegExpValidator(regex, self.ipLineEdit)
        self.ipLineEdit.setValidator(self.validator)
        
        settings = QSettings()
        settings.beginGroup('Slony/server/')
        host = settings.value('host')
        if not host:
            host = '127.0.0.1'
        settings.endGroup()
        
        self.ipLineEdit.setText(host)
        #--------------
        self.utils = Utils(host)
        self.populatePostGISConnectionsCombo()
        
    @pyqtSlot(bool)
    def on_saveServerButton_clicked(self):
        settings = QSettings()
        settings.beginGroup('Slony/server/')
        settings.setValue('host', self.ipLineEdit.text())
        settings.endGroup()
        
        self.utils = Utils(self.ipLineEdit.text())       
    
    def setCredentials(self, db, conInfo, user):
        (success, user, password) = QgsCredentials.instance().get(conInfo, user, None)
        if not success:
            return
        else:
            db.setPassword(password)
            if not db.open():
                self.setCredentials(db, conInfo, user)
            else:
                QgsCredentials.instance().put(conInfo, user, password)
                                    
    def populatePostGISConnectionsCombo(self):
        """
        Populate all the combo boxes with PostGIS connections
        """

        self.serverCombo.clear()
        self.serverCombo.addItem(self.tr("Select Database"))
        self.serverCombo.addItems(self.utils.getPostGISConnections())

        self.clientCombo.clear()
        self.clientCombo.addItem(self.tr("Select Database"))
        self.clientCombo.addItems(self.utils.getPostGISConnections())

        self.serverCombo_2.clear()
        self.serverCombo_2.addItem(self.tr("Select Database"))
        self.serverCombo_2.addItems(self.utils.getPostGISConnections())

        self.clientCombo_2.clear()
        self.clientCombo_2.addItem(self.tr("Select Database"))
        self.clientCombo_2.addItems(self.utils.getPostGISConnections())
        
        self.serverCombo_3.clear()
        self.serverCombo_3.addItem(self.tr("Select Database"))
        self.serverCombo_3.addItems(self.utils.getPostGISConnections())
        
        self.serverCombo_4.clear()
        self.serverCombo_4.addItem(self.tr("Select Database"))
        self.serverCombo_4.addItems(self.utils.getPostGISConnections())
        
    def queryClusterNames(self, connectionParameters):
        """
        Get clusters names for a PostGIS Connection
        """
        clusternames = []

        (conndb, connhost, connport, connuser, connpass) = self.utils.getPostGISConnectionParameters(connectionParameters)
        if conndb and connhost and connport and connuser:
            db = self.getConnection(conndb, connhost, connport, connuser, connpass)

            sql = 'select schema_name from information_schema.schemata'
            query = QSqlQuery(sql, db)
            while query.next():
                schema = str(query.value(0))
                if schema[0] == '_':
                    clusternames.append(schema)
        else:
            QMessageBox.warning(self, self.tr("Warning!"), self.tr('It is not possible to get all server parameters. Please, use DsgTools to edit the server.'))
                    
        return clusternames

    @pyqtSlot(int)
    def on_serverCombo_3_currentIndexChanged(self, index):
        """
        Populate the clusters tree widget
        """
        self.treeWidget.clear()
        
        if index == 0:
            return
        
        clusternames = self.queryClusterNames(self.serverCombo_3.currentText())
        for clustername in clusternames:
            self.insertClusterItem(self.treeWidget, clustername)
                
    @pyqtSlot(int)
    def on_serverCombo_4_currentIndexChanged(self, index):
        """
        Populate the clusters tree widget
        """
        self.treeWidget_2.clear()

        if index == 0:
            return
        
        clusternames = self.queryClusterNames(self.serverCombo_4.currentText())
        for clustername in clusternames:
            self.insertClusterItem(self.treeWidget_2, clustername)
                
    def getConnection(self, conndb, connhost, connport, connuser, connpass):
        """
        Get a QSqlDatabase for a specific set of connection parameters
        """

        db = None
        
        db = QSqlDatabase("QPSQL")
        db.setDatabaseName(conndb)
        db.setHostName(connhost)
        db.setPort(int(connport))
        db.setUserName(connuser)

        if not connpass or connpass == '':
            conInfo = 'host='+connhost+' port='+connport+' dbname='+conndb
            self.setCredentials(db, conInfo, connuser)
        else:
            db.setPassword(connpass)

        if not db.open():
            QMessageBox.critical(self, self.tr("Critical!"), self.tr('Database connection problem: \n') + db.lastError().text())
            
        return db
            
    def insertClusterItem(self, tree, text):
        """
        Creates an item for the tree widget for a specific parent item and a specific text (cluster name)
        """
        parent = tree.invisibleRootItem()
        item = QTreeWidgetItem(parent)
        item.setExpanded(True)
        item.setText(0,text)

    @pyqtSlot(int)
    def on_serverCombo_currentIndexChanged(self, index):
        """
        Sets the cluster name on the fly
        """

        slavedb = self.serverCombo.currentText()
        masterdb = self.clientCombo.currentText()
        self.clusterEdit.setText(masterdb+separador+slavedb)

    @pyqtSlot(int)
    def on_clientCombo_currentIndexChanged(self, index):
        """
        Sets the cluster name on the fly
        """

        slavedb = self.serverCombo.currentText()
        masterdb = self.clientCombo.currentText()
        self.clusterEdit.setText(masterdb+separador+slavedb)
        
    def checkPasswordSupply(self, db, host, port, user, password):
        if not password or password == '':
            conInfo = 'host='+host+' port='+port+' dbname='+db
            (success, user, password) = QgsCredentials.instance().get(conInfo, user, None)
            if not success:
                QMessageBox.warning(self, self.tr('Warning!'), self.tr('Password not supplied. Nothing can be done!'))
                return False, None
        return True, password
        
    @pyqtSlot(bool)
    def on_createClusterButton_clicked(self):
        """
        Creates a cluster, subscribes master and slave and starts the daemons to begin replication 
        """

        cluster = self.clusterEdit.text()
        if len(cluster) > 48:
            QMessageBox.warning(self, self.tr('Warning!'), self.tr('Cluster name too long'))
            return
        
        (slavedb, slavehost, slaveport, slaveuser, slavepass) = self.utils.getPostGISConnectionParameters(self.serverCombo.currentText())
        supplied, slavepass = self.checkPasswordSupply(slavedb, slavehost, slaveport, slaveuser, slavepass)
        if not supplied:
            return
        
        #checking slave's database version
        db = self.getConnection(slavedb, slavehost, slaveport, slaveuser, slavepass)
        slaveversion = self.getDatabaseVersion(db)

        (masterdb, masterhost, masterport, masteruser, masterpass) = self.utils.getPostGISConnectionParameters(self.clientCombo.currentText())
        supplied, masterpass = self.checkPasswordSupply(masterdb, masterhost, masterport, masteruser, masterpass)
        if not supplied:
            return

        #checking master's database version
        db = self.getConnection(masterdb, masterhost, masterport, masteruser, masterpass)
        masterversion = self.getDatabaseVersion(db)
        
        if masterversion != slaveversion:
            QMessageBox.warning(self, self.tr('Warning!'), self.tr('Slave and Master databases have different versions!'))
            return

        req = self.utils.makeRequest('configurecluster.py', masterdb, slavedb, masterhost, slavehost, masterport, slaveport, masteruser, masterpass, slaveuser, slavepass, cluster, masterversion)
        (ret, success) = self.utils.run(req)
        ret = ret.decode(encoding='UTF-8')
        if success:
            QMessageBox.information(self, self.tr('Information!'), ret.strip())
        else:
            QMessageBox.warning(self, self.tr('Warning!'), self.tr('Error while creating cluster:')+'\n'+ret.strip())
        
    @pyqtSlot(bool)
    def on_startReplicationButton_clicked(self):
        """
        Starts daemons for the selected master and slave databases
        """

        slavedb = self.serverCombo_2.currentText()
        masterdb = self.clientCombo_2.currentText()
        cluster = masterdb+separador+slavedb
        
        (slavedb, slavehost, slaveport, slaveuser, slavepass) = self.utils.getPostGISConnectionParameters(self.serverCombo_2.currentText())
        supplied, slavepass = self.checkPasswordSupply(slavedb, slavehost, slaveport, slaveuser, slavepass)
        if not supplied:
            return

        #checking slave's database version
        db = self.getConnection(slavedb, slavehost, slaveport, slaveuser, slavepass)
        slaveversion = self.getDatabaseVersion(db)

        (masterdb, masterhost, masterport, masteruser, masterpass) = self.utils.getPostGISConnectionParameters(self.clientCombo_2.currentText())
        supplied, masterpass = self.checkPasswordSupply(masterdb, masterhost, masterport, masteruser, masterpass)
        if not supplied:
            return
        
        #checking master's database version
        db = self.getConnection(masterdb, masterhost, masterport, masteruser, masterpass)
        masterversion = self.getDatabaseVersion(db)
        
        if masterversion != slaveversion:
            QMessageBox.warning(self, self.tr('Warning!'), self.tr('Slave and Master databases have different versions!'))
            return

        req = self.utils.makeRequest('startreplication.py', masterdb, slavedb, masterhost, slavehost, masterport, slaveport, masteruser, masterpass, slaveuser, slavepass, cluster, masterversion)
        (ret, success) = self.utils.run(req)
        ret = ret.decode(encoding='UTF-8')
        if success:
            QMessageBox.information(self, self.tr('Information!'), ret.strip())
        else:
            QMessageBox.warning(self, self.tr('Warning!'), self.tr('Error while starting replication:')+'\n'+ret.strip())

    @pyqtSlot(bool)
    def on_removeClusterButton_clicked(self):
        """
        Removes a selected cluster.
        Before the actual removal a check for running daemons is made.
        """

        #case no item is selected we should warn the user
        if len(self.treeWidget.selectedItems()) == 0:
            QMessageBox.warning(self, self.tr("Warning!"), self.tr('Please, select a cluster to be removed.'))
            return

        item = self.treeWidget.selectedItems()[0]
        
        self.checkAndKillSlonDaemons(item.text(0))
        
        self.removeClusters(item.text(0))
        
    @pyqtSlot(bool)
    def on_stopReplicationButton_clicked(self):
        """
        Check for running slon daemons and kill them.
        """

        #case no item is selected we should warn the user
        if len(self.treeWidget_2.selectedItems()) == 0:
            QMessageBox.warning(self, self.tr("Warning!"), self.tr('Please, select a cluster to be removed.'))
            return

        item = self.treeWidget_2.selectedItems()[0]
        
        self.checkAndKillSlonDaemons(item.text(0))
        
    def removeClusters(self, clustername):
        """
        Remove cluster from master and slave databases
        """

        cluster = clustername[1::]
        split = cluster.split(separador)
        
        self.removeCluster(clustername, split[0])
        self.removeCluster(clustername, split[1])        
        
    def removeCluster(self, clustername, conn):
        """
        Removes a cluster
        """

        (conndb, connhost, connport, connuser, connpass) = self.utils.getPostGISConnectionParameters(conn)
        supplied, connpass = self.checkPasswordSupply(conndb, connhost, connport, connuser, connpass)
        if not supplied:
            return

        #Gets the connection
        db = self.getConnection(conndb, connhost, connport, connuser, connpass)

        #Drop schema query
        sql = 'DROP SCHEMA '+clustername+' CASCADE'
        query = QSqlQuery(db)
        query.exec_(sql)        
    
    def checkAndKillSlonDaemons(self, clustername):
        """
        Check for active slon daemons and kill them
        """

        cluster = clustername[1::]
        split = cluster.split(separador)
        slave = split[1]
        (slavedb, slavehost, slaveport, slaveuser, slavepass) = self.utils.getPostGISConnectionParameters(slave)
        supplied, slavepass = self.checkPasswordSupply(slavedb, slavehost, slaveport, slaveuser, slavepass)
        if not supplied:
            return
        
        req = self.utils.makeKillRequest('stopreplication.py', cluster, slavehost)
        (ret, success) = self.utils.run(req)
        ret = ret.decode(encoding='UTF-8')
        if success:
            QMessageBox.information(self, self.tr('Information!'), ret.strip())
        else:
            QMessageBox.warning(self, self.tr('Warning!'), self.tr('Error while stopping replication:')+'\n'+ret.strip())
       
    @pyqtSlot(bool) 
    def on_refreshButton_clicked(self):
        """
        Check running daemons and make a user readable information
        """
        
        req = self.utils.makeGetRunningDaemonsRequest('getrunningdaemons.py')
        (ret, success) = self.utils.run(req)
        ret = ret.decode(encoding='UTF-8')
        if not success:
            QMessageBox.warning(self, self.tr("Warning!"), self.tr('Error while checking for active replications:')+'\n'+ret)
            return
        split = ret.strip().split('*')
        
        self.daemonsTreeWidget.clear()
        parent = self.daemonsTreeWidget.invisibleRootItem()

        children = []
        #checking if the text is already in the tree widget
        for text in split:
            if text not in children and text != '':
                item = QTreeWidgetItem(parent)
                item.setExpanded(True)
                item.setText(0,text)
                children.append(text)

    def getDatabaseVersion(self, db):
        version = '-1'
        if not db.open():
            return version
        sqlVersion = 'SELECT edgvversion FROM db_metadata LIMIT 1'
        queryVersion = QSqlQuery(sqlVersion, db)
        while queryVersion.next():
            version = queryVersion.value(0)
        return version