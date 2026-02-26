# ============================================================
# SHOOTER - QGIS Plugin
#
# Author  : Achmad Amrulloh
# Email   : achmad.amrulloh@gmail.com
# LinkedIn: https://www.linkedin.com/in/achmad-amrulloh/
#
# Description:
# Manual Add Sector & Site Tool for RF Planning and RF Optimization.
#
# Copyright (C) 2026 Achmad Amrulloh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# ============================================================

import os

from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject

from .shooter_add_sector_tool import ShooterAddSectorTool
from .shooter_add_site_tool import ShooterAddSiteTool
from .shooter_add_mode_dialog import ShooterAddModeDialog
from .shooter_about_dialog import ShooterAboutDialog
from .shooter_layer_manager import ShooterLayerManager
from .shooter_settings_dialog import ShooterSettingsDialog


class ShooterPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.tool = None

        self.plugin_dir = os.path.dirname(__file__)

    # --------------------------------------------------
    # GUI init
    # --------------------------------------------------
    def initGui(self):
        # =========================
        # Shooter Main Action (SVG)
        # =========================
        icon_path = os.path.join(
            self.plugin_dir,
            "Icon",
            "shooter.svg"
        )

        self.action = QAction(
            QIcon(icon_path),
            "Shooter",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.activate)

        # Toolbar: only Shooter
        self.iface.addToolBarIcon(self.action)

        # =========================
        # Menu Structure
        # =========================
        self.iface.addPluginToMenu("Shooter", self.action)

        # =========================
        # Settings (SVG)
        # =========================
        settings_icon_path = os.path.join(
            self.plugin_dir,
            "Icon",
            "settings.svg"
        )

        self.action_settings = QAction(
            QIcon(settings_icon_path),
            "Settings",
            self.iface.mainWindow()
        )
        self.action_settings.triggered.connect(self.showSettingsDialog)

        self.iface.addPluginToMenu("Shooter", self.action_settings)

        # =========================
        # About (SVG)
        # =========================
        about_icon_path = os.path.join(
            self.plugin_dir,
            "Icon",
            "information.svg"
        )

        self.action_about = QAction(
            QIcon(about_icon_path),
            "About Shooter",
            self.iface.mainWindow()
        )
        self.action_about.triggered.connect(self.showAboutDialog)

        self.iface.addPluginToMenu("Shooter", self.action_about)




    # --------------------------------------------------
    # About dialog
    # --------------------------------------------------
    def showAboutDialog(self):
        dlg = ShooterAboutDialog(self.iface.mainWindow())
        dlg.exec_()
    
    
    # --------------------------------------------------
    # Settings dialog
    # --------------------------------------------------
    def showSettingsDialog(self):
        dlg = ShooterSettingsDialog(self.iface.mainWindow())
        dlg.exec_()


    # --------------------------------------------------
    # Unload plugin
    # --------------------------------------------------
    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("Shooter", self.action)
        self.iface.removePluginMenu("Shooter", self.action_settings)
        self.iface.removePluginMenu("Shooter", self.action_about)


    # --------------------------------------------------
    # Activate
    # --------------------------------------------------
    def activate(self):

        dlg = ShooterAddModeDialog(self.iface.mainWindow())
        if dlg.exec_() != dlg.Accepted:
            return

        mode = dlg.selected_mode()

        # ==================================================
        # PREPARE SHOOTER ENVIRONMENT
        # ==================================================
        ShooterLayerManager.prepareShooterEnvironment([])

        # ==================================================
        # TOOL SELECTION
        # ==================================================
        if mode == ShooterAddModeDialog.MODE_SITE:
            self.tool = ShooterAddSiteTool(self.canvas)
        else:
            self.tool = ShooterAddSectorTool(self.canvas)

        self.canvas.setMapTool(self.tool)



