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
