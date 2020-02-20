"""Constants for ha_pywinrm."""
# Base component constants
DOMAIN = "ha_pywinrm"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
PLATFORMS = ["binary_sensor", "sensor", "switch"]
REQUIRED_FILES = [
    "const.py",
    "manifest.json",
    "sensor.py",
    "binary_sensor.py",
    "switch.py",
]
ISSUE_URL = "https://github.com/k3wio/ha_pywinrm/issues"

# Icons
ICON = "mdi:windows"
