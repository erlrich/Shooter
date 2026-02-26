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

from qgis.PyQt.QtWidgets import QMenu, QAction


class ShooterContextMenuBuilder:

    @staticmethod
    def build(
        canvas,
        target_feature,
        callbacks: dict
    ):
        """
        callbacks = {
            "edit": func,
            "move": func,
            "coord": func,
            "yellow": func,
            "white": func,
            "rename": func,
            "toggle_label": func,
            "delete": func,
            "settings": func
        }
        """

        from PyQt5.QtGui import QIcon
        from PyQt5.QtCore import QSize
        import os

        plugin_dir = os.path.dirname(__file__)
        icon_dir = os.path.join(plugin_dir, "Icon")

        def icon(name):
            path = os.path.join(icon_dir, f"{name}.svg")
            ic = QIcon()
            ic.addFile(path, QSize(18, 18))
            return ic

        menu = QMenu(canvas)

        # =========================
        # HEADER
        # =========================
        header = QAction("SHOOTER", canvas)
        header.setEnabled(False)
        font = header.font()
        font.setBold(True)
        header.setFont(font)
        menu.addAction(header)
        menu.addSeparator()

        # =========================
        # EDIT SECTION
        # =========================
        section_edit = QAction("Edit", canvas)
        section_edit.setEnabled(False)
        menu.addAction(section_edit)

        act_edit  = QAction(icon("edit"), "Edit Attributes", canvas)
        act_move  = QAction(icon("move"), "Move Center (Pick Map)", canvas)
        act_coord = QAction(icon("coordinates"), "Edit Coordinates", canvas)

        menu.addAction(act_edit)
        menu.addAction(act_move)
        menu.addAction(act_coord)

        menu.addSeparator()

        # =========================
        # STYLE SECTION
        # =========================
        section_style = QAction("Style", canvas)
        section_style.setEnabled(False)
        menu.addAction(section_style)

        act_yellow = QAction(icon("color"), "Set Color → Yellow", canvas)
        act_white  = QAction(icon("color"), "Set Color → White", canvas)
        act_rename = QAction(icon("rename"), "Rename Sector", canvas)

        act_label = QAction(icon("toggle"), "Toggle Label", canvas)
        act_label.setCheckable(True)
        act_label.setChecked(bool(target_feature["show_label"]))

        menu.addAction(act_yellow)
        menu.addAction(act_white)
        menu.addAction(act_rename)
        menu.addAction(act_label)

        menu.addSeparator()

        # =========================
        # DELETE
        # =========================
        act_del = QAction(icon("delete"), "Remove Feature", canvas)
        font = act_del.font()
        font.setBold(True)
        act_del.setFont(font)
        menu.addAction(act_del)

        # =========================
        # SETTINGS
        # =========================
        menu.addSeparator()

        act_settings = QAction(icon("settings"), "Settings", canvas)
        menu.addAction(act_settings)

        # =========================
        # CONNECT CALLBACKS
        # =========================
        act_edit.triggered.connect(callbacks["edit"])
        act_move.triggered.connect(callbacks["move"])
        act_coord.triggered.connect(callbacks["coord"])
        act_yellow.triggered.connect(callbacks["yellow"])
        act_white.triggered.connect(callbacks["white"])
        act_rename.triggered.connect(callbacks["rename"])
        act_label.triggered.connect(callbacks["toggle_label"])
        act_del.triggered.connect(callbacks["delete"])
        act_settings.triggered.connect(callbacks["settings"])

        return menu




