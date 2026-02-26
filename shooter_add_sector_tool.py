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
# License: MIT
# ============================================================

from qgis.gui import QgsMapTool, QgsRubberBand, QgsMapToolIdentify
from qgis.core import (
    QgsWkbTypes, QgsPointXY,
    QgsDistanceArea, QgsTextAnnotation,
    QgsProject
)
from PyQt5.QtCore import Qt, QPointF, QSizeF
from PyQt5.QtGui import QColor, QTextDocument
from qgis.utils import iface
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog
from .shooter_geometry import ShooterGeometry
from .shooter_layer_manager import ShooterLayerManager
from .shooter_edit_sector_dialog import ShooterEditSectorDialog
from .shooter_edit_center_dialog import ShooterEditCenterDialog
from .shooter_context_menu_builder import ShooterContextMenuBuilder


class ShooterAddSectorTool(QgsMapTool):

    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas

        from PyQt5.QtGui import QCursor, QPixmap
        import os

        # =========================
        # Custom Cursor (SVG)
        # =========================
        plugin_dir = os.path.dirname(__file__)
        cursor_path = os.path.join(plugin_dir, "Icon", "shooter-sector.svg")
        # pixmap = QPixmap(cursor_path)
        # cursor = QCursor(pixmap, 0, 0)
        # self.setCursor(cursor)
        
        from PyQt5.QtSvg import QSvgRenderer
        from PyQt5.QtGui import QPainter, QPixmap

        renderer = QSvgRenderer(cursor_path)

        size = 28  # ideal cursor size
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        cursor = QCursor(pixmap, size // 2, size // 2)
        self.setCursor(cursor)

        
        self.center = None
        self.last_cursor_pt = None
        self.is_dragging = False
        self.is_picking_center = False
        self.feature_to_move = None
        self.layer_to_move = None

        self.ctrl_pressed = False
        self.shift_pressed = False

        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.canvas.scene().views()[0].window().statusBar().showMessage(
            "SHOOTER: Drag to add sector | Ctrl=5° snap | Shift=10°"
        )

        # Distance Area
        self.dist = QgsDistanceArea()
        self.dist.setSourceCrs(
            QgsProject.instance().crs(),
            QgsProject.instance().transformContext()
        )
        self.dist.setEllipsoid("WGS84")

        # Rubberbands
        self.rb_line = QgsRubberBand(canvas, QgsWkbTypes.LineGeometry)
        self.rb_line.setColor(QColor(255, 255, 0))
        self.rb_line.setWidth(1.4)

        self.rb_poly = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)
        self.rb_poly.setFillColor(QColor(255, 255, 0, 40))
        self.rb_poly.setStrokeColor(QColor(255, 255, 0, 200))
        self.rb_poly.setWidth(1.0)

        # Overlay
        self.annotation = None
        self._overlay_doc = QTextDocument()
        self._last_overlay_pos = None



    def canvasPressEvent(self, event):
        # Pastikan layer terlihat
        ShooterLayerManager.ensureShooterGroupAndLayerVisible("SHOOTER_ADD_SECTOR")

        # Mode Move Center
        if self.is_picking_center and event.button() == Qt.LeftButton:
            new_center = self.toMapCoordinates(event.pos())
            feature = self.feature_to_move
            layer = self.layer_to_move

            if feature and layer:
                az, r, bw = feature["azimuth"], feature["radius_m"], feature["beamwidth"]
                center_pt = QgsPointXY(new_center.x(), new_center.y())
                new_geom = ShooterGeometry.buildWedgePolygon(center_pt, az, r, bw, 72)

                layer.startEditing()
                layer.changeGeometry(feature.id(), new_geom)
                layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("center_lat"), new_center.y())
                layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("center_lon"), new_center.x())
                layer.commitChanges()
                layer.triggerRepaint()

            self.is_picking_center = False
            self.feature_to_move = None
            self.layer_to_move = None
            self.canvas.scene().views()[0].window().statusBar().clearMessage()
            return

        # Mode Normal: Mulai Drag
        if event.button() == Qt.LeftButton and not self.is_dragging:
            self.center = self.toMapCoordinates(event.pos())
            self.last_cursor_pt = self.center
            self.is_dragging = True
            self.rb_line.reset(QgsWkbTypes.LineGeometry)
            self.rb_poly.reset(QgsWkbTypes.PolygonGeometry)


    def canvasMoveEvent(self, event):
        if not self.is_dragging or not self.center:
            return

        cursor_pt = self.toMapCoordinates(event.pos())
        self.last_cursor_pt = cursor_pt

        # Hitung Azimuth & Radius
        az = ShooterGeometry.calcAzimuth(self.center, cursor_pt)
        az = ShooterGeometry.snapAzimuth(az, self.ctrl_pressed, self.shift_pressed)
        radius = self.dist.measureLine(self.center, cursor_pt)

        # Update RubberBands
        self.rb_line.reset(QgsWkbTypes.LineGeometry)
        self.rb_line.addPoint(self.center)
        self.rb_line.addPoint(cursor_pt)

        if radius > 1:
            geom = ShooterGeometry.buildWedgePolygon(self.center, az, radius, 40, 72)
            self.rb_poly.setToGeometry(geom, None)

        # Update Overlay Text (AZ & R melayang)
        self._updateOverlay(cursor_pt, az, radius, event.pos())


    def _updateOverlay(self, map_pt, az, radius, pixel_pos):
        if self._last_overlay_pos:
            diff = (pixel_pos - self._last_overlay_pos).manhattanLength()
            if diff < 3: return
        
        self._last_overlay_pos = pixel_pos
        snap_info = " (10°)" if self.ctrl_pressed and self.shift_pressed else (" (5°)" if self.ctrl_pressed else "")

        html = (
            "<div style='background-color: rgba(0,0,0,160); color: white; padding: 6px; border-radius: 4px; font-size: 11px; white-space: nowrap;'>"
            f"<b>AZ</b>: {az:.1f}°{snap_info}<br>"
            f"<b>R</b>: {radius:.1f} m"
            "</div>"
        )

        if not self.annotation:
            self.annotation = QgsTextAnnotation()
            self.annotation.setFrameSize(QSizeF(0, 0))
            self.annotation.setFrameOffsetFromReferencePoint(QPointF(15, -15))
            QgsProject.instance().annotationManager().addAnnotation(self.annotation)

        self.annotation.setMapPosition(map_pt)
        self._overlay_doc.setHtml(html)
        self.annotation.setDocument(self._overlay_doc)
        self.canvas.refresh()


    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._showContextMenu(event)
            return

        if event.button() == Qt.LeftButton and self.is_dragging:
            radius_drag = self.dist.measureLine(self.center, self.last_cursor_pt)
            if radius_drag < 5:
                self._cleanup()
                return

            dummy_id, ok = QInputDialog.getText(
                self.canvas.scene().views()[0].window(),
                "Input Sector ID",
                "Input Dummy ID for this sector:",
                text=""
            )

            if not ok or not dummy_id.strip():
                self._cleanup()
                return

            az = ShooterGeometry.calcAzimuth(self.center, self.last_cursor_pt)
            az = ShooterGeometry.snapAzimuth(az, self.ctrl_pressed, self.shift_pressed)

            from qgis.PyQt.QtCore import QSettings

            settings = QSettings()
            settings.beginGroup("SHOOTER/settings")

            use_drag_radius = settings.value("use_drag_radius", True, type=bool)
            default_radius = settings.value("default_radius", 100, type=int)
            default_beamwidth = settings.value("default_beamwidth", 30, type=int)
            default_line_color = settings.value("default_line_color", "#FFFF00", type=str)
            default_line_width = settings.value("default_line_width", 2, type=int)

            settings.endGroup()

            final_radius = radius_drag if use_drag_radius else default_radius

            geom = ShooterGeometry.buildWedgePolygon(
                self.center,
                az,
                final_radius,
                default_beamwidth,
                72
            )

            ShooterLayerManager.addFeatureByLayer(
                "SHOOTER_ADD_SECTOR",
                geom,
                {
                    "sector_id": "New Sector",
                    "dummy_id": dummy_id,
                    "azimuth": az,
                    "radius_m": final_radius,
                    "beamwidth": default_beamwidth,
                    "center_lat": self.center.y(),
                    "center_lon": self.center.x(),
                    "line_color": default_line_color,
                    "line_width": default_line_width,
                    "show_label": True
                }
            )

            self._cleanup()




    def _showContextMenu(self, event):
        layer_names = ["SHOOTER_ADD_SITE", "SHOOTER_ADD_SECTOR"]
        project = QgsProject.instance()
        target_layer, target_feature = None, None

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


    # --- Fungsi Pendukung Identik dengan sebelumnya ---
    def _openEditDialog(self, layer, feature):
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
            layer.commitChanges(); layer.triggerRepaint()


    def _editCenterCoordinates(self, layer, feature):
        dlg = ShooterEditCenterDialog(feature["center_lon"], feature["center_lat"], self.canvas)
        if dlg.exec_() == dlg.Accepted:
            n_lon, n_lat = dlg.values()
            center = QgsPointXY(n_lon, n_lat)
            new_geom = ShooterGeometry.buildWedgePolygon(center, feature["azimuth"], feature["radius_m"], feature["beamwidth"], 72)
            layer.startEditing()
            layer.changeGeometry(feature.id(), new_geom)
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("center_lon"), n_lon)
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName("center_lat"), n_lat)
            layer.commitChanges(); layer.triggerRepaint()


    def _startMoveCenter(self, layer, feature):
        self.is_picking_center = True
        self.feature_to_move, self.layer_to_move = feature, layer
        self.canvas.scene().views()[0].window().statusBar().showMessage("Click new center on map...")


    def _setSectorColor(self, layer, feature, color):
        if not layer.isEditable():
            layer.startEditing()

        layer.changeAttributeValue(
            feature.id(),
            layer.fields().indexFromName("line_color"),
            color
        )
        layer.triggerRepaint()



    def _renameSector(self, layer, feature):
        name, ok = QInputDialog.getText(
            self.canvas,
            "Rename",
            "Name:",
            text=feature["sector_id"]
        )

        if ok and name.strip():
            if not layer.isEditable():
                layer.startEditing()

            layer.changeAttributeValue(
                feature.id(),
                layer.fields().indexFromName("sector_id"),
                name.strip()
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


    def _cleanup(self):
        self.is_dragging = False
        self.center = None
        self.last_cursor_pt = None
        self._last_overlay_pos = None
        self.rb_line.reset(); self.rb_poly.reset()
        if self.annotation:
            QgsProject.instance().annotationManager().removeAnnotation(self.annotation)
            self.annotation = None
        self.canvas.refresh()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._cleanup()
            return
        if event.key() == Qt.Key_Control: self.ctrl_pressed = True
        elif event.key() == Qt.Key_Shift: self.shift_pressed = True


    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control: self.ctrl_pressed = False
        elif event.key() == Qt.Key_Shift: self.shift_pressed = False