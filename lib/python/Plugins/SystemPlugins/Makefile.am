installdir = $(pkglibdir)/python/Plugins/SystemPlugins

SUBDIRS = PositionerSetup Satfinder \
	VideoTune Hotplug OpentvZapper \
	DefaultServicesScanner CommonInterfaceAssignment \
	ForceFbcLNBpower \
	VideoClippingSetup \
	VideoEnhancement WirelessLan ViX \
	FastScan SatelliteEquipmentControl DiseqcTester

if VUZERO4K
SUBDIRS += CableScan
endif

if VUSOLO4K
SUBDIRS += CableScan
endif

if VUUNO4K
SUBDIRS += CableScan
endif

if VUUNO4KSE
SUBDIRS += CableScan
endif

if VUDUO4K
SUBDIRS += CableScan
endif

if VUDUO4KSE
SUBDIRS += CableScan
endif

if VUULTIMO4K
SUBDIRS += CableScan
endif

if HAVE_LIBVUGLES2
SUBDIRS += AnimationSetup
endif

if HAVE_OSDANIMATION
SUBDIRS += AnimationSetup
endif

if HAVE_FCC
SUBDIRS += FastChannelChange
endif

install_PYTHON = __init__.py
