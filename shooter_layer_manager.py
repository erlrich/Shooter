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

from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsField,
    QgsFeature,
    QgsFields,
    QgsSingleSymbolRenderer,
    QgsFillSymbol,
    QgsPalLayerSettings,
    QgsTextFormat,
    QgsProperty,
    QgsVectorLayerSimpleLabeling
)

from PyQt5.QtCore import QVariant, QSettings
from PyQt5.QtGui import QColor, QFont
from qgis.core import QgsProperty

LAYER_NAME = "SHOOTER_ADD_SECTOR"
LAYER_ADD_SECTOR = "SHOOTER_ADD_SECTOR"
LAYER_ADD_SITE   = "SHOOTER_ADD_SITE"


class ShooterLayerManager:

    @staticmethod
    def getOrCreateLayerByName(layer_name: str):
        project = QgsProject.instance()
        layers = project.mapLayersByName(layer_name)
        
        if layers:
            layer = layers[0]
            ShooterLayerManager.ensureShooterGroupAndLayerVisible(layer_name)
            return layer

        # Jika belum ada, buat baru
        project_crs = QgsProject.instance().crs().authid()

        layer = QgsVectorLayer(
            f"Polygon?crs={project_crs}",
            layer_name,
            "memory"
        )
        provider = layer.dataProvider()

        # Define fields
        fields = QgsFields()
        fields.append(QgsField("sector_id", QVariant.String))
        fields.append(QgsField("dummy_id", QVariant.String))
        fields.append(QgsField("azimuth", QVariant.Double))
        fields.append(QgsField("radius_m", QVariant.Double))
        fields.append(QgsField("beamwidth", QVariant.Double))
        fields.append(QgsField("center_lat", QVariant.Double))
        fields.append(QgsField("center_lon", QVariant.Double))
        fields.append(QgsField("line_color", QVariant.String))
        fields.append(QgsField("line_width", QVariant.Int))
        fields.append(QgsField("show_label", QVariant.Bool))
        provider.addAttributes(fields)
        layer.updateFields()

        # Styling & Labeling (Sama seperti sebelumnya)
        symbol = QgsFillSymbol.createSimple({"style": "no"})

        layer_symbol = symbol.symbolLayer(0)

        # Stroke Color (sudah ada sebelumnya)
        layer_symbol.setDataDefinedProperty(
            layer_symbol.PropertyStrokeColor,
            QgsProperty.fromExpression('coalesce("line_color", \'#FFFF00\')')
        )

        # 🔥 Stroke Width (TAMBAHAN FIX)
        layer_symbol.setDataDefinedProperty(
            layer_symbol.PropertyStrokeWidth,
            QgsProperty.fromExpression('coalesce("line_width", 2)')
        )

        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        
        # Setup Labeling secara stabil
        label_settings = QgsPalLayerSettings()
        label_settings.enabled = True
        label_settings.fieldName = "sector_id" # Selalu arahkan ke sector_id
        
        # Gunakan Data Defined Property untuk On/Off label
        # Ini akan melihat field 'show_label', jika 1 maka tampil, jika 0 maka sembunyi
        label_settings.dataDefinedProperties().setProperty(
            QgsPalLayerSettings.Show,
            QgsProperty.fromExpression("show_label = 1")
        )

        

        settings = QSettings()
        settings.beginGroup("SHOOTER/settings")
        default_text_color = settings.value("default_text_color", "#000000", type=str)
        settings.endGroup()

        text_format = QgsTextFormat()
        text_format.setFont(QFont("Arial", 10, QFont.Bold))
        text_format.setColor(QColor(default_text_color))

        
        label_settings.setFormat(text_format)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        layer.setLabelsEnabled(True)

        # # Tambahkan ke project DAHULU baru diatur posisinya
        # project.addMapLayer(layer)
        # ShooterLayerManager.ensureShooterGroupAndLayerVisible(layer_name)
        
        # return layer
        
        project.addMapLayer(layer)
        ShooterLayerManager.ensureShooterGroupAndLayerVisible(layer_name)

        # =========================================
        # AUTO START EDITING (DESIGN TOOL MODE)
        # =========================================
        if not layer.isEditable():
            layer.startEditing()

        return layer



    @staticmethod
    def addFeatureByLayer(layer_name: str, geometry, attrs: dict):
        layer = ShooterLayerManager.getOrCreateLayerByName(layer_name)

        feature = QgsFeature(layer.fields())
        for key, val in attrs.items():
            feature[key] = val

        feature.setGeometry(geometry)

        # =========================================
        # ALWAYS KEEP LAYER EDITABLE
        # =========================================
        if not layer.isEditable():
            layer.startEditing()

        layer.addFeature(feature)
        layer.triggerRepaint()


    @staticmethod
    def ensureShooterGroupAndLayerVisible(layer_name: str):
        """
        Memastikan Group SHOOTER ada dan layer berada di dalamnya secara aman.
        """
        project = QgsProject.instance()
        root = project.layerTreeRoot()

        # 1. Pastikan Group SHOOTER ada di paling atas
        group = root.findGroup("SHOOTER")
        if not group:
            group = root.insertGroup(0, "SHOOTER")
        
        # 2. Cari layer berdasarkan nama
        layers = project.mapLayersByName(layer_name)
        if not layers:
            return
        
        layer = layers[0]
        layer_id = layer.id()
        
        # Cari node layer di seluruh tree
        layer_node = root.findLayer(layer_id)
        
        if layer_node:
            # Cek apakah sudah di dalam group yang benar
            current_parent = layer_node.parent()
            
            if current_parent != group:
                # Pindahkan secara aman: Clone -> Add to Group -> Remove Old
                new_node = layer_node.clone()
                group.insertChildNode(0, new_node)
                current_parent.removeChildNode(layer_node)
                # Gunakan node baru untuk operasi selanjutnya
                layer_node = new_node
            else:
                # Jika sudah di dalam group, cukup geser ke urutan paling atas di dalam group tersebut
                if group.children()[0] != layer_node:
                    new_node = layer_node.clone()
                    group.insertChildNode(0, new_node)
                    group.removeChildNode(layer_node)
                    layer_node = new_node

            # Pastikan checkbox layer tercentang (Visible)
            layer_node.setItemVisibilityChecked(True)
            # Pastikan group juga terexpand/tercentang
            group.setItemVisibilityChecked(True)
            group.setExpanded(True)
    
    @staticmethod
    def prepareShooterEnvironment(layer_names=None):
        """
        Menyiapkan group SHOOTER di panel layer agar siap digunakan.
        """
        project = QgsProject.instance()
        root = project.layerTreeRoot()

        # Mencari atau membuat group SHOOTER di posisi paling atas
        group = root.findGroup("SHOOTER")
        if group is None:
            group = root.insertGroup(0, "SHOOTER")
        else:
            # Jika sudah ada, pastikan posisinya tetap di paling atas (index 0)
            if root.children()[0] != group:
                clone = group.clone()
                root.removeChildNode(group)
                root.insertChildNode(0, clone)