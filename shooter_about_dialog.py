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
    QDialog, QVBoxLayout, QLabel, QPushButton
)
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtCore import Qt


class ShooterAboutDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About Shooter")
        self.setFixedWidth(420)

        layout = QVBoxLayout(self)

        # -----------------------------
        # Title
        # -----------------------------
        title = QLabel("Shooter")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # -----------------------------
        # Info
        # -----------------------------
        info = QLabel(
            "Manual Add Sector & Site Tool\n"
            "for RF / NPI / GIS Planning.\n\n"
            "Author  : Achmad Amrulloh\n"
            "Email   : achmad.amrulloh@gmail.com\n"
            "LinkedIn: https://www.linkedin.com/in/achmad-amrulloh/\n\n"
            "Community Edition"
        )
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        info.setStyleSheet(
            "margin-top: 10px; margin-bottom: 10px;"
        )

        # -----------------------------
        # OK Button
        # -----------------------------
        btn = QPushButton("OK")
        btn.setFixedWidth(80)
        btn.clicked.connect(self.accept)

        # -----------------------------
        # Layout assemble
        # -----------------------------
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
        layout.addWidget(btn, 0, Qt.AlignCenter)
