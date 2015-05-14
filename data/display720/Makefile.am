installdir = $(pkgdatadir)/display

if ET8500
dist_install_DATA = skin_display.xml skin_display_templates.xml
SUBDIRS = LCDAnalogClock_1_Standby LCDAnalogClock_2_Standby ATV_default et8500_XTA_blue
endif
if ET10000
dist_install_DATA = skin_display.xml
endif

skin_display.xml: $(srcdir)/skin_display_default.xml
	test -f $(srcdir)/skin_display_$(BOXTYPE).xml && cp $(srcdir)/skin_display_$(BOXTYPE).xml skin_display.xml || cp $(srcdir)/skin_display_default.xml skin_display.xml
