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
    QDialog, QVBoxLayout, QLabel,
    QRadioButton, QDialogButtonBox
)
from qgis.PyQt.QtCore import Qt


class ShooterAddModeDialog(QDialog):

    MODE_SECTOR = "sector"
    MODE_SITE = "site"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Shooter - Add Mode")
        self.setFixedWidth(260)

        layout = QVBoxLayout(self)

        label = QLabel("What do you want to add?")
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label)

        self.rb_sector = QRadioButton("Add Sector (Manual)")
        self.rb_site = QRadioButton("Add Site (3 Sectors)")

        self.rb_sector.setChecked(True)

        layout.addWidget(self.rb_sector)
        layout.addWidget(self.rb_site)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def selected_mode(self):
        if self.rb_site.isChecked():
            return self.MODE_SITE
        return self.MODE_SECTOR
