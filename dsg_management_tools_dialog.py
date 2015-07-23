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
        
    def populatePostGISConnectionsCombo(self):
        self.serverCombo.clear()
        self.serverCombo.addItem("Select Database")
        self.serverCombo.addItems(self.utils.getPostGISConnections())

        self.clientCombo.clear()
        self.clientCombo.addItem("Select Database")
        self.clientCombo.addItems(self.utils.getPostGISConnections())
        
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
    def on_createClusterButton_clicked(self, clicked):
        self.makeRequestOnServer('configurecluster.py')
        
    @pyqtSlot(bool)
    def on_startReplicationButton_clicked(self, clicked):
        self.makeRequestOnServer('startreplication.py')
        
    def makeRequestOnServer(self, script):
        cluster = self.clusterEdit.text()
        
        (slavedb, slavehost, slaveport, slaveuser, slavepass) = self.utils.getPostGISConnectionParameters(self.serverCombo.currentText())
        (masterdb, masterhost, masterport, masteruser, masterpass) = self.utils.getPostGISConnectionParameters(self.clientCombo.currentText())
        
        req = self.utils.makeRequest(script, masterdb, slavedb, masterhost, slavehost, masteruser, masterpass, slaveuser, slavepass, cluster)
        self.utils.run(req)
        