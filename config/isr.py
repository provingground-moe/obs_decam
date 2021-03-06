"""
DECam-specific overrides of IsrTask
"""
import os.path

from lsst.obs.decam.crosstalk import DecamCrosstalkTask

config.datasetType = "raw"
config.fallbackFilterName = None
config.expectWcs = True
config.fwhm = 1.0

config.doConvertIntToFloat = False

config.doSaturation=True
config.saturatedMaskName = "SAT"
config.saturation = float("NaN")
config.growSaturationFootprintSize = 1

config.doSuspect=True
config.suspectMaskName = "SUSPECT"
config.numEdgeSuspect = 35

config.doSetBadRegions = True
config.badStatistic = "MEANCLIP"

config.doOverscan = True
config.overscanFitType = "MEDIAN"
config.overscanOrder = 1
config.overscanNumSigmaClip = 3.0
config.overscanNumLeadingColumnsToSkip = 0
config.overscanNumTrailingColumnsToSkip = 0
config.overscanMaxDev = 1000.0
config.overscanBiasJump = True
config.overscanBiasJumpKeyword = "FPA"
config.overscanBiasJumpDevices = ["DECAM_BKP3", "DECAM_BKP5", "DECAM_BKP1", "DECAM_BKP4"]
config.overscanBiasJumpLocation = 2098

config.doAssembleCcd = True
# Use default ISR assembleCcdTask
config.assembleCcd.doTrim = True
config.assembleCcd.keysToRemove = ['DATASECA', 'DATASECB',
                                   'TRIMSECA', 'TRIMSECB',
                                   'BIASSECA', 'BIASSECB',
                                   'PRESECA', 'PRESECB',
                                   'POSTSECA', 'POSTSECB']

config.doAssembleIsrExposures = False
config.doTrimToMatchCalib = True

config.doBias = True
config.biasDataProductName = "cpBias"

config.doVariance = True
config.gain = float("NaN")
config.readNoise = 0.0
config.doEmpiricalReadNoise = False

config.doLinearize = True

config.doCrosstalkBeforeAssemble = True
config.doCrosstalk = True
config.crosstalk.retarget(DecamCrosstalkTask)
config.crosstalk.minPixelToMask=45000.0
config.crosstalk.crosstalkMaskPlane="CROSSTALK"

config.doWidenSaturationTrails = True

config.doBrighterFatter = False

config.doDefect = True
config.doSaturationInterpolation = True
config.numEdgeSuspect=35

config.doDark = False
config.darkDataProductName = "dark"

config.doStrayLight = False

config.doFlat = True
config.flatDataProductName = "cpFlat"
config.flatScalingType = "USER"
config.flatUserScale = 1.0
config.doTweakFlat = False

config.doApplyGains = False
config.normalizeGains = False

config.doFringe = True
config.fringeAfterFlat = True
config.fringe.filters = ['z', 'y']

config.doNanInterpAfterFlat = False

config.doAddDistortionModel = False  # rely on the TPV terms instead

config.doMeasureBackground = True

config.doCameraSpecificMasking = False

config.doVignette = False
config.doAttachTransmissionCurve = False
config.doUseOpticsTransmission = False
config.doUseFilterTransmission = False
config.doUseSensorTransmission = False
config.doUseAtmosphereTransmission = False

# Illumination correction should almost certainly be done,
# but not all decam datasets yet have the necessary calibration products.
config.doIlluminationCorrection = False
# config.doIlluminationCorrection = True
config.illuminationCorrectionDataProductName = "cpIllumcor"
config.illumFilters = ['g', 'r', 'i']
