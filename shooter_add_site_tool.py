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

from qgis.gui import QgsMapTool, QgsMapToolIdentify
from qgis.core import QgsPointXY, QgsWkbTypes, QgsProject
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog
from qgis.PyQt.QtCore import QSettings

from .shooter_geometry import ShooterGeometry
from .shooter_layer_manager import ShooterLayerManager
from .shooter_edit_sector_dialog import ShooterEditSectorDialog
from .shooter_edit_center_dialog import ShooterEditCenterDialog
from .shooter_context_menu_builder import ShooterContextMenuBuilder


class ShooterAddSiteTool(QgsMapTool):

    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas

        from PyQt5.QtGui import QCursor, QPixmap
        import os

        # =========================
        # Custom Cursor (SVG)
        # =========================
        plugin_dir = os.path.dirname(__file__)
        cursor_path = os.path.join(plugin_dir, "Icon", "shooter-site.svg")
        # pixmap = QPixmap(cursor_path)
        # cursor = QCursor(pixmap, 0, 0)
        # self.setCursor(cursor)
        
        from PyQt5.QtSvg import QSvgRenderer
        from PyQt5.QtGui import QPainter, QPixmap

        renderer = QSvgRenderer(cursor_path)

        size = 28
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        cursor = QCursor(pixmap, size // 2, size // 2)
        self.setCursor(cursor)

        
        self.is_picking_center = False
        self.feature_to_move = None
        self.layer_to_move = None

        self.canvas.scene().views()[0].window().statusBar().showMessage(
            "SHOOTER: Click map to add 3-sector site"
        )



    def canvasPressEvent(self, event):
        # 1. LOGIKA MOVE CENTER (PICK MODE)
        if hasattr(self, 'is_picking_center') and self.is_picking_center and event.button() == Qt.LeftButton:
            new_center = self.toMapCoordinates(event.pos())
            feature = self.feature_to_move
            layer = self.layer_to_move
            
            if feature and layer:
                az, r, bw = feature["azimuth"], feature["radius_m"], feature["beamwidth"]
                center_pt = QgsPointXY(new_center.x(), new_center.y())
                new_geom = ShooterGeometry.buildWedgePolygon(center_pt, az, r, bw, 72)
                
                layer.startEditing()
                layer.changeGeometry(feature.id(), new_geom)
                
                idx_lat = layer.fields().indexFromName("center_lat")
                idx_lon = layer.fields().indexFromName("center_lon")
                if idx_lat != -1: layer.changeAttributeValue(feature.id(), idx_lat, new_center.y())
                if idx_lon != -1: layer.changeAttributeValue(feature.id(), idx_lon, new_center.x())
                
                layer.commitChanges()
                layer.triggerRepaint()
            
            self.is_picking_center = False
            self.feature_to_move = None
            self.layer_to_move = None
            self.canvas.scene().views()[0].window().statusBar().clearMessage()
            return

        # 2. LOGIKA NORMAL (TAMBAH SITE)
        if event.button() != Qt.LeftButton:
            return

        dummy_id, ok = QInputDialog.getText(
            self.canvas.scene().views()[0].window(), 
            "Input Site ID", 
            "Input Dummy ID / Site ID:",
            text=""
        )

        if not ok or not dummy_id.strip():
            return

        ShooterLayerManager.ensureShooterGroupAndLayerVisible("SHOOTER_ADD_SITE")
        # Ensure layer is editable (Design Tool behavior)
        layer_list = QgsProject.instance().mapLayersByName("SHOOTER_ADD_SITE")
        if layer_list:
            layer = layer_list[0]
            if not layer.isEditable():
                layer.startEditing()

        center = self.toMapCoordinates(event.pos())
        center_pt = QgsPointXY(center.x(), center.y())

        # ------------------------------
        # BAGIAN LOOP ADD SITE - START
        # ------------------------------
        
        settings = QSettings()
        settings.beginGroup("SHOOTER/settings")
        default_site_radius = settings.value("default_site_radius", 100, type=int)
        default_beamwidth = settings.value("default_beamwidth", 30, type=int)
        default_line_color = settings.value("default_line_color", "#FFFF00", type=str)
        default_line_width = settings.value("default_line_width", 2, type=int)
        settings.endGroup()

        azimuths = [0, 120, 240]
        for idx, az in enumerate(azimuths, start=1):
            geom = ShooterGeometry.buildWedgePolygon(
                center_pt,
                az,
                default_site_radius,
                default_beamwidth,
                72
            )

            ShooterLayerManager.addFeatureByLayer(
                "SHOOTER_ADD_SITE",
                geom,
                {
                    "sector_id": f"Sector {idx}",
                    "dummy_id": dummy_id,
                    "azimuth": az,
                    "radius_m": default_site_radius,
                    "beamwidth": default_beamwidth,
                    "center_lat": center_pt.y(),
                    "center_lon": center_pt.x(),
                    "line_color": default_line_color,
                    "line_width": default_line_width,
                    "show_label": True
                }
            )

        # ------------------------------
        # BAGIAN LOOP ADD SITE - END
        # ------------------------------
        self.canvas.refresh()


    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._showContextMenu(event)


    def _showContextMenu(self, event):
        layer_names = ["SHOOTER_ADD_SITE", "SHOOTER_ADD_SECTOR"]
        project = QgsProject.instance()

        target_layer = None
        target_feature = None

        identify = QgsMapToolIdentify(self.canvas)

        for name in layer_names:
            layers = project.mapLayersByName(name)
            if not layers:
                continue

            results = identify.identify(
                event.x(),
                event.y(),
                [layers[0]],
                QgsMapToolIdentify.TopDownAll
            )

            if results:
                target_layer = layers[0]
                target_feature = results[0].mFeature
                break

        if not target_layer:
            return

        callbacks = {
            "edit": lambda: self._openEditDialog(target_layer, target_feature),
            "move": lambda: self._startMoveCenter(target_layer, target_feature),
            "coord": lambda: self._editCenterCoordinates(target_layer, target_feature),
            "yellow": lambda: self._setSectorColor(target_layer, target_feature, "#FFFF00"),
            "white": lambda: self._setSectorColor(target_layer, target_feature, "#FFFFFF"),
            "rename": lambda: self._renameSector(target_layer, target_feature),
            "toggle_label": lambda: self._toggleLabel(target_layer, target_feature),
            "delete": lambda: self._removeFeature(target_layer, target_feature),
            "settings": lambda: self._openSettings()
        }


        menu = ShooterContextMenuBuilder.build(
            self.canvas,
            target_feature,
            callbacks
        )

        menu.exec_(self.canvas.mapToGlobal(event.pos()))


    def _openEditDialog(self, layer, feature):
        from .shooter_edit_sector_dialog import ShooterEditSectorDialog
        # Mengikuti pola parameter di shooter_add_sector_tool yang Anda upload
        dlg = ShooterEditSectorDialog(feature["azimuth"], feature["radius_m"], feature["beamwidth"], self.canvas)
        if dlg.exec_() == dlg.Accepted:
            new_az, new_r, new_bw = dlg.values()
            center = QgsPointXY(feature["center_lon"], feature["center_lat"])
            new_geom = ShooterGeometry.buildWedgePolygon(center, new_az, new_r, new_bw, 72)
            layer.startEditing()
            layer.changeGeometry(feature.id(), new_geom)
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("azimuth"), new_az)
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("radius_m"), new_r)
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("beamwidth"), new_bw)
            layer.commitChanges()
            layer.triggerRepaint()


    def _editCenterCoordinates(self, layer, feature):
        dlg = ShooterEditCenterDialog(feature["center_lon"], feature["center_lat"], self.canvas)
        if dlg.exec_() == dlg.Accepted:
            n_lon, n_lat = dlg.values()
            new_center = QgsPointXY(n_lon, n_lat)
            new_geom = ShooterGeometry.buildWedgePolygon(new_center, feature["azimuth"], feature["radius_m"], feature["beamwidth"], 72)
            layer.startEditing()
            layer.changeGeometry(feature.id(), new_geom)
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("center_lon"), n_lon)
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("center_lat"), n_lat)
            layer.commitChanges()
            layer.triggerRepaint()


    def _startMoveCenter(self, layer, feature):
        self.is_picking_center = True
        self.feature_to_move = feature
        self.layer_to_move = layer
        self.canvas.scene().views()[0].window().statusBar().showMessage("Click new center on map...")


    def _setSectorColor(self, layer, feature, color_hex):
        if not layer.isEditable():
            layer.startEditing()

        layer.changeAttributeValue(
            feature.id(),
            layer.fields().indexFromName("line_color"),
            color_hex
        )
        layer.triggerRepaint()



    def _renameSector(self, layer, feature):
        new_name, ok = QInputDialog.getText(
            self.canvas,
            "Rename",
            "Name:",
            text=feature["sector_id"]
        )

        if ok and new_name.strip():
            if not layer.isEditable():
                layer.startEditing()

            layer.changeAttributeValue(
                feature.id(),
                layer.fields().indexFromName("sector_id"),
                new_name.strip()
            )
            layer.triggerRepaint()



    def _toggleLabel(self, layer, feature):
        idx = layer.fields().indexFromName("show_label")
        if idx != -1:
            new_val = 0 if feature["show_label"] == 1 else 1

            if not layer.isEditable():
                layer.startEditing()

            layer.changeAttributeValue(feature.id(), idx, new_val)
            layer.triggerRepaint()
            self.canvas.refresh()



    def _removeFeature(self, layer, feature):
        if not layer.isEditable():
            layer.startEditing()

        layer.deleteFeature(feature.id())
        layer.triggerRepaint()

        
    
    def _openSettings(self):
        from .shooter_settings_dialog import ShooterSettingsDialog
        dlg = ShooterSettingsDialog(self.canvas)
        dlg.exec_()
