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

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QDoubleSpinBox, QPushButton
)
from PyQt5.QtCore import Qt


class ShooterEditCenterDialog(QDialog):

    def __init__(self, lon, lat, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Center Coordinates")
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)

        # -----------------------------
        # Longitude
        # -----------------------------
        lon_layout = QHBoxLayout()
        lon_layout.addWidget(QLabel("Longitude"))

        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180.0, 180.0)
        self.lon_spin.setDecimals(7)
        self.lon_spin.setValue(lon)

        lon_layout.addWidget(self.lon_spin)
        layout.addLayout(lon_layout)

        # -----------------------------
        # Latitude
        # -----------------------------
        lat_layout = QHBoxLayout()
        lat_layout.addWidget(QLabel("Latitude"))

        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90.0, 90.0)
        self.lat_spin.setDecimals(7)
        self.lat_spin.setValue(lat)

        lat_layout.addWidget(self.lat_spin)
        layout.addLayout(lat_layout)

        # -----------------------------
        # Buttons
        # -----------------------------
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def values(self):
        return self.lon_spin.value(), self.lat_spin.value()
