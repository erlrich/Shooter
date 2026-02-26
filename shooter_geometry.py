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
import math
from qgis.core import QgsPointXY, QgsGeometry

class ShooterGeometry:

    @staticmethod
    def calcAzimuth(center: QgsPointXY, point: QgsPointXY) -> float:
        dx = point.x() - center.x()
        dy = point.y() - center.y()
        az = math.degrees(math.atan2(dx, dy))
        return (az + 360) % 360

    @staticmethod
    def snapAzimuth(az: float, ctrl=False, shift=False) -> float:
        if not ctrl:
            return az
        step = 10 if shift else 5
        return round(az / step) * step


    @staticmethod
    def buildWedgePolygon(center: QgsPointXY,
                          azimuth: float,
                          radius_m: float,
                          beamwidth: float = 40,
                          segments: int = 72) -> QgsGeometry:

        from qgis.core import (
            QgsProject,
            QgsCoordinateReferenceSystem,
            QgsCoordinateTransform
        )

        project = QgsProject.instance()
        project_crs = project.crs()
        wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")

        # --------------------------------------------------
        # Transform center → WGS84 if needed
        # --------------------------------------------------
        if project_crs != wgs84:
            to_wgs = QgsCoordinateTransform(project_crs, wgs84, project)
            center_wgs = to_wgs.transform(center)
        else:
            center_wgs = center

        half_bw = beamwidth / 2.0
        start = azimuth - half_bw
        lat = center_wgs.y()

        m_per_deg_lat = 111320.0
        m_per_deg_lon = 111320.0 * math.cos(math.radians(lat))

        pts_wgs = [center_wgs]

        for i in range(segments + 1):
            ang = start + (beamwidth * i / segments)
            theta = math.radians(90 - ang)

            dx = (radius_m * math.cos(theta)) / m_per_deg_lon
            dy = (radius_m * math.sin(theta)) / m_per_deg_lat

            pts_wgs.append(
                QgsPointXY(
                    center_wgs.x() + dx,
                    center_wgs.y() + dy
                )
            )

        pts_wgs.append(center_wgs)

        geom_wgs = QgsGeometry.fromPolygonXY([pts_wgs])

        # --------------------------------------------------
        # Transform geometry back → project CRS
        # --------------------------------------------------
        if project_crs != wgs84:
            to_project = QgsCoordinateTransform(wgs84, project_crs, project)
            geom_wgs.transform(to_project)

        return geom_wgs

