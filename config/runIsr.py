"""
DECam-specific overrides for RunIsrTask
"""
import os.path

from lsst.utils import getPackageDir

obsConfigDir = os.path.join(getPackageDir("obs_decam"), "config")

config.isr.load(os.path.join(obsConfigDir, "isr.py"))
