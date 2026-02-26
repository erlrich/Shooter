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

# ============================================================
# SHOOTER - Settings Dialog
# ============================================================

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QSpinBox, QCheckBox,
    QPushButton, QColorDialog
)
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QColor


class ShooterSettingsDialog(QDialog):

    SETTINGS_GROUP = "SHOOTER/settings"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Shooter Settings")
        self.setFixedWidth(340)

        layout = QVBoxLayout(self)

        settings = QSettings()
        settings.beginGroup(self.SETTINGS_GROUP)

        use_drag_radius = settings.value("use_drag_radius", True, type=bool)
        default_radius = settings.value("default_radius", 100, type=int)
        default_beamwidth = settings.value("default_beamwidth", 30, type=int)
        default_site_radius = settings.value("default_site_radius", 100, type=int)
        default_line_color = settings.value("default_line_color", "#FFFF00", type=str)
        default_line_width = settings.value("default_line_width", 2, type=int)
        default_text_color = settings.value("default_text_color", "#000000", type=str)


        settings.endGroup()

        # =========================
        # Sector Radius
        # =========================
        layout.addWidget(QLabel("Sector Radius"))

        self.cb_use_drag = QCheckBox("Use drag result")
        self.cb_use_drag.setChecked(use_drag_radius)
        layout.addWidget(self.cb_use_drag)

        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Default Radius (m)"))

        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(10, 10000)
        self.radius_spin.setValue(default_radius)
        radius_layout.addWidget(self.radius_spin)

        layout.addLayout(radius_layout)

        self.radius_spin.setEnabled(not use_drag_radius)
        self.cb_use_drag.stateChanged.connect(
            lambda: self.radius_spin.setEnabled(
                not self.cb_use_drag.isChecked()
            )
        )

        layout.addSpacing(8)

        # =========================
        # Beamwidth
        # =========================
        bw_layout = QHBoxLayout()
        bw_layout.addWidget(QLabel("Default Beamwidth (°)"))

        self.bw_spin = QSpinBox()
        self.bw_spin.setRange(10, 180)
        self.bw_spin.setValue(default_beamwidth)
        bw_layout.addWidget(self.bw_spin)

        layout.addLayout(bw_layout)

        layout.addSpacing(8)

        # =========================
        # Site Radius
        # =========================
        site_layout = QHBoxLayout()
        site_layout.addWidget(QLabel("Default Site Radius (m)"))

        self.site_spin = QSpinBox()
        self.site_spin.setRange(10, 10000)
        self.site_spin.setValue(default_site_radius)
        site_layout.addWidget(self.site_spin)

        layout.addLayout(site_layout)

        layout.addSpacing(12)

        # =========================
        # Line Color
        # =========================
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Default Line Color"))

        self.color_button = QPushButton()
        self.color_button.setFixedWidth(60)
        self.current_color = QColor(default_line_color)
        self._updateColorButton()

        self.color_button.clicked.connect(self._chooseColor)

        color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)

        layout.addSpacing(8)

        # =========================
        # Line Width
        # =========================
        lw_layout = QHBoxLayout()
        lw_layout.addWidget(QLabel("Default Line Width"))

        self.lw_spin = QSpinBox()
        self.lw_spin.setRange(1, 10)
        self.lw_spin.setValue(default_line_width)

        lw_layout.addWidget(self.lw_spin)
        layout.addLayout(lw_layout)
        
        layout.addSpacing(12)

        # =========================
        # Text Color
        # =========================
        text_color_layout = QHBoxLayout()
        text_color_layout.addWidget(QLabel("Default Text Color"))

        self.text_color_button = QPushButton()
        self.text_color_button.setFixedWidth(60)
        self.text_color = QColor(default_text_color)
        self._updateTextColorButton()

        self.text_color_button.clicked.connect(self._chooseTextColor)

        text_color_layout.addWidget(self.text_color_button)
        layout.addLayout(text_color_layout)


        layout.addStretch()

        # =========================
        # Buttons
        # =========================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")

        btn_ok.clicked.connect(self._saveSettings)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    # --------------------------------------------------
    def _chooseColor(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self._updateColorButton()

    # --------------------------------------------------
    def _updateColorButton(self):
        self.color_button.setStyleSheet(
            f"background-color: {self.current_color.name()};"
        )
    
    # --------------------------------------------------
    def _chooseTextColor(self):
        color = QColorDialog.getColor(self.text_color, self)
        if color.isValid():
            self.text_color = color
            self._updateTextColorButton()

    # --------------------------------------------------
    def _updateTextColorButton(self):
        self.text_color_button.setStyleSheet(
            f"background-color: {self.text_color.name()};"
        )

    
    # --------------------------------------------------
    def _saveSettings(self):
        settings = QSettings()
        settings.beginGroup(self.SETTINGS_GROUP)

        settings.setValue("use_drag_radius", self.cb_use_drag.isChecked())
        settings.setValue("default_radius", self.radius_spin.value())
        settings.setValue("default_beamwidth", self.bw_spin.value())
        settings.setValue("default_site_radius", self.site_spin.value())
        settings.setValue("default_line_color", self.current_color.name())
        settings.setValue("default_line_width", self.lw_spin.value())
        settings.setValue("default_text_color", self.text_color.name())

        settings.endGroup()

        self.accept()
