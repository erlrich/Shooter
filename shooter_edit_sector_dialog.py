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
from qgis.PyQt.QtCore import Qt


def snap_to_step(value, step):
    """
    Snap value to nearest step.
    Example:
      value=29, step=5  -> 30
      value=261, step=10 -> 260
    """
    if step <= 0:
        return value
    return round(value / step) * step


class ShooterEditSectorDialog(QDialog):

    def __init__(self, azimuth, radius_m, beamwidth, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Sector")
        self.setFixedWidth(280)

        layout = QVBoxLayout(self)

        # -----------------------------
        # Azimuth
        # -----------------------------
        az_layout = QHBoxLayout()
        az_layout.addWidget(QLabel("Azimuth (°)"))

        self.az_spin = QDoubleSpinBox()
        self.az_spin.setRange(0, 360)
        self.az_spin.setSingleStep(5)
        self.az_spin.setDecimals(0)

        az_step = self.az_spin.singleStep()
        self.az_spin.setValue(
            snap_to_step(azimuth, az_step)
        )

        az_layout.addWidget(self.az_spin)
        layout.addLayout(az_layout)

        # -----------------------------
        # Radius
        # -----------------------------
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("Radius (m)"))

        self.r_spin = QDoubleSpinBox()
        self.r_spin.setRange(10, 10000)
        self.r_spin.setSingleStep(10)
        self.r_spin.setDecimals(0)

        r_step = self.r_spin.singleStep()
        self.r_spin.setValue(
            snap_to_step(radius_m, r_step)
        )

        r_layout.addWidget(self.r_spin)
        layout.addLayout(r_layout)

        # -----------------------------
        # Beamwidth
        # -----------------------------
        bw_layout = QHBoxLayout()
        bw_layout.addWidget(QLabel("Beamwidth (°)"))

        self.bw_spin = QDoubleSpinBox()
        self.bw_spin.setRange(10, 180)
        self.bw_spin.setSingleStep(5)
        self.bw_spin.setDecimals(0)

        bw_step = self.bw_spin.singleStep()
        self.bw_spin.setValue(
            snap_to_step(beamwidth, bw_step)
        )

        bw_layout.addWidget(self.bw_spin)
        layout.addLayout(bw_layout)

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

    # -----------------------------
    # Getter
    # -----------------------------
    def values(self):
        """
        Return snapped integer-like values.
        (Still float type, but no decimals)
        """
        return (
            int(self.az_spin.value()),
            int(self.r_spin.value()),
            int(self.bw_spin.value())
        )
