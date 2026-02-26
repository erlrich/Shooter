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
