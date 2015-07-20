# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DsgManagementTools
                                 A QGIS plugin
 Tools to manage DSG's cartographic production
                             -------------------
        begin                : 2015-07-20
        copyright            : (C) 2015 by Brazilian Army - Geographic Service Bureau
        email                : suporte.dsgtools@dsg.eb.mil.br
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DsgManagementTools class from file DsgManagementTools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .dsg_management_tools import DsgManagementTools
    return DsgManagementTools(iface)
