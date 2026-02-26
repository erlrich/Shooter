# ============================================================
# SHOOTER - QGIS Plugin
# ============================================================

def classFactory(iface):
    from .shooter_plugin import ShooterPlugin
    return ShooterPlugin(iface)
