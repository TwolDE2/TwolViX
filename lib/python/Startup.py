from __future__ import print_function
import enigma
import os
import sys

from boxbranding import getImageArch, getImageBuild, getImageDevBuild, getImageType, getImageVersion
from sys import stdout
from time import localtime, strftime, time
from traceback import print_exc

from Tools.Profile import profile, profile_final
import Tools.RedirectOutput  # Don't remove this line. It may seem to do nothing, but if removed it will break output redirection for crash logs.
import eConsoleImpl
import eBaseImpl
enigma.eTimer = eBaseImpl.eTimer
enigma.eSocketNotifier = eBaseImpl.eSocketNotifier
enigma.eConsoleAppContainer = eConsoleImpl.eConsoleAppContainer

# This includes initializing the translation engine.
# Moving this further down will break translation.
# Moving further up will break imports in config.py
profile("SetupDevices")
print("[Enigma2] Initialising SetupDevices.")
import Components.SetupDevices
Components.SetupDevices.InitSetupDevices()

if getImageArch() in ("aarch64"):
	import usb.core
	import usb.backend.libusb1
	usb.backend.libusb1.get_backend(find_library=lambda x: "/lib64/libusb-1.0.so.0")

if os.path.isfile("/usr/lib/enigma2/python/enigma.zip"):
	sys.path.append("/usr/lib/enigma2/python/enigma.zip")

profile("PYTHON_START")
print("[Enigma2] Starting Python Level Initialisation.")
print("[Enigma2] Image Type -> '%s'" % getImageType())
print("[Enigma2] Image Version -> '%s'" % getImageVersion())
print("[Enigma2] Image Build -> '%s'" % getImageBuild())
if getImageType() != "release":
	print("[Enigma2] Image DevBuild -> '%s'" % getImageDevBuild())

profile("ClientMode")
print("[Enigma2] Initialising ClientMode.")
import Components.ClientMode
Components.ClientMode.InitClientMode()

profile("InfoBar")
print("[Enigma2] Initialising InfoBar.")
from Screens import InfoBar

profile("Bouquets")
print("[Enigma2] Initialising Bouquets.")
from Components.config import config, configfile, ConfigText, ConfigYesNo, ConfigInteger, NoSave
config.misc.load_unlinked_userbouquets = ConfigYesNo(default=False)
def setLoadUnlinkedUserbouquets(configElement):
	enigma.eDVBDB.getInstance().setLoadUnlinkedUserbouquets(configElement.value)
config.misc.load_unlinked_userbouquets.addNotifier(setLoadUnlinkedUserbouquets)
if config.clientmode.enabled.value == False:
	enigma.eDVBDB.getInstance().reloadBouquets()

profile("ParentalControl")
print("[Enigma2] Initialising ParentalControl.")
import Components.ParentalControl
Components.ParentalControl.InitParentalControl()

profile("LOAD:Navigation")
print("[Enigma2] Initialising Navigation.")
from Navigation import Navigation

profile("LOAD:skin")
print("[Enigma2] Initialising Skin.")
from skin import readSkin

profile("LOAD:Tools")
print("[Enigma2] Initialising FallbackFiles.")
from Components.config import config, configfile, ConfigInteger, ConfigSelection, ConfigText, ConfigYesNo, NoSave
from Tools.Directories import InitFallbackFiles, resolveFilename, SCOPE_PLUGINS, SCOPE_ACTIVE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_CONFIG
InitFallbackFiles()

profile("config.misc")
print("[Enigma2] Initialising Misc Config Variables.")
config.misc.radiopic = ConfigText(default=resolveFilename(SCOPE_CURRENT_SKIN, "radio.mvi"))
config.misc.blackradiopic = ConfigText(default=resolveFilename(SCOPE_CURRENT_SKIN, "black.mvi"))
config.misc.isNextRecordTimerAfterEventActionAuto = ConfigYesNo(default=False)
config.misc.isNextPowerTimerAfterEventActionAuto = ConfigYesNo(default=False)
config.misc.SyncTimeUsing = ConfigSelection(default="0", choices=[("0", "Transponder Time"), ("1", _("NTP"))])
config.misc.NTPserver = ConfigText(default="pool.ntp.org", fixed_size=False)
config.misc.startCounter = ConfigInteger(default=0)  # number of e2 starts...
config.misc.standbyCounter = NoSave(ConfigInteger(default=0))  # number of standby
config.misc.DeepStandby = NoSave(ConfigYesNo(default=False))  # detect deepstandby

# demo code for use of standby enter leave callbacks
# def leaveStandby():
# 	print "!!!!!!!!!!!!!!!!!leave standby"

# def standbyCountChanged(configElement):
# 	print "!!!!!!!!!!!!!!!!!enter standby num", configElement.value
# 	from Screens.Standby import inStandby
# 	inStandby.onClose.append(leaveStandby)

# config.misc.standbyCounter.addNotifier(standbyCountChanged, initial_call = False)
# ###################################################

def useSyncUsingChanged(configElement):
	if configElement.value == "0":
		print("[[Enigma2]Time By]: Transponder")
		enigma.eDVBLocalTimeHandler.getInstance().setUseDVBTime(True)
		enigma.eEPGCache.getInstance().timeUpdated()
	else:
		print("[Enigma2][Time By]: NTP")
		enigma.eDVBLocalTimeHandler.getInstance().setUseDVBTime(False)
		enigma.eEPGCache.getInstance().timeUpdated()


config.misc.SyncTimeUsing.addNotifier(useSyncUsingChanged)

def NTPserverChanged(configElement):
	f = open("/etc/default/ntpdate", "w")
	f.write("NTPSERVERS=\"%s\"\n" % configElement.value)
	f.close()
	os.chmod("/etc/default/ntpdate", 0o755)
	from Components.Console import Console
	Console = Console()
	Console.ePopen("/usr/bin/ntpdate-sync")


config.misc.NTPserver.addNotifier(NTPserverChanged, immediate_feedback = False)

profile("Twisted")
print("[Enigma2] Initialising Twisted.")
try:
	import twisted.python.runtime
	twisted.python.runtime.platform.supportsThreads = lambda: True

	import e2reactor
	e2reactor.install()

	from twisted.internet import reactor

	def runReactor():
		reactor.run(installSignalHandlers=False)
except ImportError:
	print("[Enigma2] twisted not available")

	def runReactor():
		enigma.runMainloop()


from twisted.python import log
config.misc.enabletwistedlog = ConfigYesNo(default = False)
if config.misc.enabletwistedlog.value == True:
	log.startLogging(open('/tmp/twisted.log', 'w'))
	print("[Enigma2] Twisted log ->  /tmp/twisted.log.")
else:
	log.startLogging(sys.stdout)
	print("[Enigma2] Twisted log ->  sys.stdout.")


profile("LOAD:Plugin")
print("[Enigma2] Initialising Plugins.")
# initialize autorun plugins and plugin menu entries
from Components.PluginComponent import plugins

profile("LOAD:Wizard")
print("[Enigma2] Initialising Wizards.")
from Screens.StartWizard import *
import Screens.Rc
from Tools.BoundFunction import boundFunction
from Plugins.Plugin import PluginDescriptor

from Tools.FlashInstall import FlashInstallTime
FlashInstallTime()

profile("misc")
had = dict()

def dump(dir, p = ""):
	if isinstance(dir, dict):
		for (entry, val) in list(dir.items()):
			dump(val, "%s(dict)/%s" % (p, entry))
	if hasattr(dir, "__dict__"):
		for name, value in list(dir.__dict__.items()):
			if str(value) not in had:
				had[str(value)] = 1
				dump(value, "%s/%s" % (p, str(name)))
			else:
				print("%s/%s:%s(cycle)" % (p, str(name), str(dir.__class__)))
	else:
		print("%s:%s" % (p, str(dir)))  # + ":" + str(dir.__class__)


profile("LOAD:ScreenGlobals")
print("[Enigma2] Initialising ScreenGlobals.")
from Screens.Globals import Globals
from Screens.SessionGlobals import SessionGlobals
from Screens.Screen import Screen, ScreenSummary

profile("Screen")
Screen.globalScreen = Globals()

# Session.open:
# * push current active dialog ("current_dialog") onto stack
# * call execEnd for this dialog
#   * clear in_exec flag
#   * hide screen
# * instantiate new dialog into "current_dialog"
#   * create screens, components
#   * read, apply skin
#   * create GUI for screen
# * call execBegin for new dialog
#   * set in_exec
#   * show gui screen
#   * call components' / screen's onExecBegin
# ... screen is active, until it calls "close"...
# Session.close:
# * assert in_exec
# * save return value
# * start deferred close handler ("onClose")
# * execEnd
#   * clear in_exec
#   * hide screen
# .. a moment later:
# Session.doClose:
# * destroy screen

class Session:
	def __init__(self, desktop = None, summary_desktop = None, navigation = None):
		self.desktop = desktop
		self.summary_desktop = summary_desktop
		self.nav = navigation
		self.delay_timer = enigma.eTimer()
		self.delay_timer.callback.append(self.processDelay)
		self.current_dialog = None
		self.dialog_stack = []
		self.summary_stack = []
		self.summary = None
		self.in_exec = False
		self.screen = SessionGlobals(self)
		for p in plugins.getPlugins(PluginDescriptor.WHERE_SESSIONSTART):
			try:
				p(reason=0, session=self)
			except Exception:
				print("Plugin raised exception at WHERE_SESSIONSTART")
				print_exc()

	def processDelay(self):
		callback = self.current_dialog.callback
		retval = self.current_dialog.returnValue
		if self.current_dialog.isTmp:
			self.current_dialog.doClose()
			# dump(self.current_dialog)
			del self.current_dialog
		else:
			del self.current_dialog.callback
		self.popCurrent()
		if callback is not None:
			callback(*retval)

	def execBegin(self, first=True, do_show = True):
		assert not self.in_exec
		self.in_exec = True
		c = self.current_dialog
		# when this is an execbegin after a execend of a "higher" dialog,
		# popSummary already did the right thing.
		if first:
			self.instantiateSummaryDialog(c)
		c.saveKeyboardMode()
		c.execBegin()
		# when execBegin opened a new dialog, don't bother showing the old one.
		if c == self.current_dialog and do_show:
			c.show()

	def execEnd(self, last=True):
		assert self.in_exec
		self.in_exec = False
		self.current_dialog.execEnd()
		self.current_dialog.restoreKeyboardMode()
		self.current_dialog.hide()
		if last and self.summary is not None:
			self.current_dialog.removeSummary(self.summary)
			self.popSummary()

	def instantiateDialog(self, screen, *arguments, **kwargs):
		return self.doInstantiateDialog(screen, arguments, kwargs, self.desktop)

	def deleteDialog(self, screen):
		screen.hide()
		screen.doClose()

	def deleteDialogWithCallback(self, callback, screen, *retval):
		screen.hide()
		screen.doClose()
		if callback is not None:
			callback(*retval)

	def instantiateSummaryDialog(self, screen, **kwargs):
		if self.summary_desktop is not None:
			self.pushSummary()
			summary = screen.createSummary() or ScreenSummary
			arguments = (screen,)
			self.summary = self.doInstantiateDialog(summary, arguments, kwargs, self.summary_desktop)
			self.summary.show()
			screen.addSummary(self.summary)

	def doInstantiateDialog(self, screen, arguments, kwargs, desktop):
		# create dialog
		dlg = screen(self, *arguments, **kwargs)
		if dlg is None:
			return
		# read skin data
		readSkin(dlg, None, dlg.skinName, desktop)
		# create GUI view of this dialog
		dlg.setDesktop(desktop)
		dlg.applySkin()
		return dlg

	def pushCurrent(self):
		if self.current_dialog is not None:
			self.dialog_stack.append((self.current_dialog, self.current_dialog.shown))
			self.execEnd(last=False)

	def popCurrent(self):
		if self.dialog_stack:
			(self.current_dialog, do_show) = self.dialog_stack.pop()
			self.execBegin(first=False, do_show=do_show)
		else:
			self.current_dialog = None

	def execDialog(self, dialog):
		self.pushCurrent()
		self.current_dialog = dialog
		self.current_dialog.isTmp = False
		self.current_dialog.callback = None # would cause re-entrancy problems.
		self.execBegin()

	def openWithCallback(self, callback, screen, *arguments, **kwargs):
		dlg = self.open(screen, *arguments, **kwargs)
		dlg.callback = callback
		return dlg

	def open(self, screen, *arguments, **kwargs):
		if self.dialog_stack and not self.in_exec:
			raise RuntimeError("modal open are allowed only from a screen which is modal!")
			# ...unless it's the very first screen.

		self.pushCurrent()
		dlg = self.current_dialog = self.instantiateDialog(screen, *arguments, **kwargs)
		dlg.isTmp = True
		dlg.callback = None
		self.execBegin()
		return dlg

	def close(self, screen, *retval):
		if not self.in_exec:
			print("close after exec!")
			return

		# be sure that the close is for the right dialog!
		# if it's not, you probably closed after another dialog
		# was opened. this can happen if you open a dialog
		# onExecBegin, and forget to do this only once.
		# after close of the top dialog, the underlying will
		# gain focus again (for a short time), thus triggering
		# the onExec, which opens the dialog again, closing the loop.
		assert screen == self.current_dialog

		self.current_dialog.returnValue = retval
		self.delay_timer.start(0, 1)
		self.execEnd()

	def pushSummary(self):
		if self.summary is not None:
			self.summary.hide()
			self.summary_stack.append(self.summary)
			self.summary = None

	def popSummary(self):
		if self.summary is not None:
			self.summary.doClose()
		if not self.summary_stack:
			self.summary = None
		else:
			self.summary = self.summary_stack.pop()
		if self.summary is not None:
			self.summary.show()

	def reloadSkin(self):
		from Screens.MessageBox import MessageBox
		reloadNotification = self.instantiateDialog(MessageBox, _("Loading skin"), MessageBox.TYPE_INFO, 
			simple=True, picon=False, title=_("Please wait"))
		reloadNotification.show()

		# close all open dialogs by emptying the dialog stack
		# remove any return values and callbacks for a swift exit
		while self.current_dialog is not None and type(self.current_dialog) is not InfoBar.InfoBar:
			print("[SkinReloader] closing %s" % type(self.current_dialog))
			self.current_dialog.returnValue = None
			self.current_dialog.callback = None
			self.execEnd()
			self.processDelay()
		# need to close the infobar outside the loop as its exit causes a new infobar to be created
		print("[SkinReloader] closing InfoBar")
		InfoBar.InfoBar.instance.close("reloadskin", reloadNotification)


profile("Standby,PowerKey")
import Screens.Standby
from Screens.Menu import MainMenu, mdom
from GlobalActions import globalActionMap

class PowerKey:
	""" PowerKey stuff - handles the powerkey press and powerkey release actions"""

	def __init__(self, session):
		self.session = session
		globalActionMap.actions["power_down"] = self.powerdown
		globalActionMap.actions["power_up"] = self.powerup
		globalActionMap.actions["power_long"] = self.powerlong
		globalActionMap.actions["deepstandby"] = self.shutdown  # frontpanel long power button press
		globalActionMap.actions["discrete_off"] = self.standby
		self.standbyblocked = 1

	def MenuClosed(self, *val):
		self.session.infobar = None

	def shutdown(self):
		wasRecTimerWakeup = False
		recordings = self.session.nav.getRecordings()
		if not recordings:
			next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
		if recordings or (next_rec_time > 0 and (next_rec_time - time()) < 360):
			if os.path.exists("/tmp/was_rectimer_wakeup") and not self.session.nav.RecordTimer.isRecTimerWakeup():
				f = open("/tmp/was_rectimer_wakeup", "r")
				file = f.read()
				f.close()
				wasRecTimerWakeup = int(file) and True or False
			if self.session.nav.RecordTimer.isRecTimerWakeup() or wasRecTimerWakeup:
				print("PowerOff (timer wakewup) - Recording in progress or a timer about to activate, entering standby!")
				self.standby()
			else:
				print("PowerOff - Now!")
				self.session.open(Screens.Standby.TryQuitMainloop, 1)
		elif not Screens.Standby.inTryQuitMainloop and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND:
			print("PowerOff - Now!")
			self.session.open(Screens.Standby.TryQuitMainloop, 1)

	def powerlong(self):
		if Screens.Standby.inTryQuitMainloop or (self.session.current_dialog and not self.session.current_dialog.ALLOW_SUSPEND):
			return
		self.doAction(action = config.usage.on_long_powerpress.value)

	def doAction(self, action):
		self.standbyblocked = 1
		if action == "shutdown":
			self.shutdown()
		elif action == "show_menu":
			print("Show shutdown Menu")
			root = mdom.getroot()
			for x in root.findall("menu"):
				y = x.find("id")
				if y is not None:
					id = y.get("val")
					if id and id == "shutdown":
						self.session.infobar = self
						menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, x)
						menu_screen.setTitle(_("Standby / restart"))
						return
		elif action == "standby":
			self.standby()

	def powerdown(self):
		self.standbyblocked = 0

	def powerup(self):
		if self.standbyblocked == 0:
			self.doAction(action = config.usage.on_short_powerpress.value)

	def standby(self):
		if not Screens.Standby.inStandby and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND and self.session.in_exec:
			self.session.open(Screens.Standby.Standby)

profile("Scart")
print("[Enigma2] Initialising Scart.")
from Screens.Scart import Scart

class AutoScartControl:
	def __init__(self, session):
		self.force = False
		self.current_vcr_sb = enigma.eAVSwitch.getInstance().getVCRSlowBlanking()
		if self.current_vcr_sb and config.av.vcrswitch.value:
			self.scartDialog = session.instantiateDialog(Scart, True)
		else:
			self.scartDialog = session.instantiateDialog(Scart, False)
		config.av.vcrswitch.addNotifier(self.recheckVCRSb)
		enigma.eAVSwitch.getInstance().vcr_sb_notifier.get().append(self.VCRSbChanged)

	def recheckVCRSb(self, configElement):
		self.VCRSbChanged(self.current_vcr_sb)

	def VCRSbChanged(self, value):
		# print("vcr sb changed to", value)
		self.current_vcr_sb = value
		if config.av.vcrswitch.value or value > 2:
			if value:
				self.scartDialog.showMessageBox()
			else:
				self.scartDialog.switchToTV()

profile("Load:CI")
print("[Enigma2] Initialising CommonInterface.")
from Screens.Ci import CiHandler

profile("Load:VolumeControl")
print("[Enigma2] Initialising VolumeControl.")
from Components.VolumeControl import VolumeControl
from Tools.StbHardware import setFPWakeuptime, setRTCtime

def runScreenTest():
	config.misc.startCounter.value += 1
	config.misc.startCounter.save()

	profile("readPluginList")
	enigma.pauseInit()
	plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
	enigma.resumeInit()

	profile("Init:Session")
	nav = Navigation(config.misc.isNextRecordTimerAfterEventActionAuto.value, config.misc.isNextPowerTimerAfterEventActionAuto.value)
	session = Session(desktop = enigma.getDesktop(0), summary_desktop = enigma.getDesktop(1), navigation = nav)

	CiHandler.setSession(session)
	screensToRun = [p.__call__ for p in plugins.getPlugins(PluginDescriptor.WHERE_WIZARD)]
	profile("wizards")
	screensToRun += wizardManager.getWizards()
	screensToRun.append((100, InfoBar.InfoBar))
	screensToRun.sort()

	enigma.ePythonConfigQuery.setQueryFunc(configfile.getResolvedKey)

	def runNextScreen(session, screensToRun, *result):
		if result:
			if result[0] == "reloadskin":
				skin.InitSkins(False)
				session.openWithCallback(boundFunction(runNextScreen, session, []), InfoBar.InfoBar)
				if result[1]:
					session.deleteDialog(result[1])
			else:
				enigma.quitMainloop(*result)
		else:
			screen = screensToRun[0][1]
			args = screensToRun[0][2:]
			session.openWithCallback(boundFunction(runNextScreen, session, screensToRun[1:]), screen, *args)

	runNextScreen(session, screensToRun)

	profile("Init:VolumeControl")
	vol = VolumeControl(session)
	profile("Init:PowerKey")
	power = PowerKey(session)

	# we need session.scart to access it from within menu.xml
	session.scart = AutoScartControl(session)

	profile("Init:Trashcan")
	import Tools.Trashcan
	Tools.Trashcan.init(session)

	profile("Init:AutoVideoMode")
	import Screens.VideoMode
	Screens.VideoMode.autostart(session)

	profile("RunReactor")
	profile_final()
	runReactor()

	profile("wakeup")
	# get currentTime
	nowTime = time()
	wakeupList = [x for x in (
		(session.nav.RecordTimer.getNextRecordingTime(), 0, session.nav.RecordTimer.isNextRecordAfterEventActionAuto()),
		(session.nav.RecordTimer.getNextZapTime(), 1),
		(plugins.getNextWakeupTime(), 2),
		(session.nav.PowerTimer.getNextPowerManagerTime(), 3, session.nav.PowerTimer.isNextPowerManagerAfterEventActionAuto())
	) if x[0] != -1]
	wakeupList.sort()
	recordTimerWakeupAuto = False
	if wakeupList and wakeupList[0][1] != 3:
		startTime = wakeupList[0]
		if (startTime[0] - nowTime) < 270:  # no time to switch box back on
			wptime = nowTime + 30  # so switch back on in 30 seconds
		else:
			wptime = startTime[0] - 240
		if not config.misc.SyncTimeUsing.value == "0":
			print("dvb time sync disabled... so set RTC now to current linux time!", strftime("%Y/%m/%d %H:%M", localtime(nowTime)))
			setRTCtime(nowTime)
		print("set wakeup time to", strftime("%Y/%m/%d %H:%M", localtime(wptime)))
		setFPWakeuptime(wptime)
		recordTimerWakeupAuto = startTime[1] == 0 and startTime[2]
		print("recordTimerWakeupAuto", recordTimerWakeupAuto)
	config.misc.isNextRecordTimerAfterEventActionAuto.value = recordTimerWakeupAuto
	config.misc.isNextRecordTimerAfterEventActionAuto.save()
	PowerTimerWakeupAuto = False
	if wakeupList and wakeupList[0][1] == 3:
		startTime = wakeupList[0]
		if (startTime[0] - nowTime) < 60:  # no time to switch box back on
			wptime = nowTime + 30  # so switch back on in 30 seconds
		else:
			wptime = startTime[0]
		if not config.misc.SyncTimeUsing.value == "0":
			print("dvb time sync disabled... so set RTC now to current linux time!", strftime("%Y/%m/%d %H:%M", localtime(nowTime)))
			setRTCtime(nowTime)
		print("set wakeup time to", strftime("%Y/%m/%d %H:%M", localtime(wptime + 60)))
		setFPWakeuptime(wptime)
		PowerTimerWakeupAuto = startTime[1] == 3 and startTime[2]
		print("PowerTimerWakeupAuto", PowerTimerWakeupAuto)
	config.misc.isNextPowerTimerAfterEventActionAuto.value = PowerTimerWakeupAuto
	config.misc.isNextPowerTimerAfterEventActionAuto.save()
	profile("stopService")
	session.nav.stopService()
	profile("nav shutdown")
	session.nav.shutdown()
	profile("configfile.save")
	configfile.save()
	from Screens import InfoBarGenerics
	InfoBarGenerics.saveResumePoints()
	return 0


profile("Init:skin")
print("[Enigma2] Initialising Skin.")
import skin
skin.InitSkins()
print("[Enigma2] Initialisation of Skins complete.")

profile("InputDevice")
print("[Enigma2] Initialising InputDevice.")
import Components.InputDevice
Components.InputDevice.InitInputDevices()
import Components.InputHotplug

profile("UserInterface")
print("[Enigma2] Initialising UserInterface.")
import Screens.UserInterfacePositioner
Screens.UserInterfacePositioner.InitOsd()

profile("AVSwitch")
print("[Enigma2] Initialising AVSwitch.")
import Components.AVSwitch
Components.AVSwitch.InitAVSwitch()
Components.AVSwitch.InitiVideomodeHotplug()

profile("EpgConfig")
import Components.EpgConfig
Components.EpgConfig.InitEPGConfig()

profile("RecordingConfig")
print("[Enigma2] Initialising RecordingConfig.")
import Components.RecordingConfig
Components.RecordingConfig.InitRecordingConfig()

profile("UsageConfig")
print("[Enigma2] Initialising UsageConfig.")
import Components.UsageConfig
Components.UsageConfig.InitUsageConfig()

profile("TimeZones")
print("[Enigma2] Initialising Timezones.")
import Components.Timezones
Components.Timezones.InitTimeZones()

profile("Init:DebugLogCheck")
print("[Enigma2] Initialising DebugLogCheck.")
import Screens.LogManager
Screens.LogManager.AutoLogManager()

profile("Init:OnlineCheckState")
print("[Enigma2] Initialising OnlineCheckState.")
import Components.OnlineUpdateCheck
Components.OnlineUpdateCheck.OnlineUpdateCheck()

profile("Init:NTPSync")
print("[Enigma2] Initialising NTPSync.")
import Components.NetworkTime
Components.NetworkTime.AutoNTPSync()

profile("keymapparser")
print("[Enigma2] Initialising KeymapParser.")
import keymapparser
keymapparser.readKeymap(config.usage.keymap.value)

profile("Network")
print("[Enigma2] Initialising Network.")
import Components.Network
Components.Network.InitNetwork()

profile("LCD")
print("[Enigma2] Initialising LCD / FrontPanel.")
import Components.Lcd
Components.Lcd.InitLcd()
# ------------------>Components.Lcd.IconCheck()

profile("UserInterface")
print("[Enigma2] Initialising UserInterface.")
import Screens.UserInterfacePositioner
Screens.UserInterfacePositioner.InitOsdPosition()

profile("EpgCacheSched")
print("[Enigma2] Initialising EPGCacheScheduler.")
import Components.EpgLoadSave
Components.EpgLoadSave.EpgCacheSaveCheck()
Components.EpgLoadSave.EpgCacheLoadCheck()

profile("RFMod")
print("[Enigma2] Initialising RFMod.")
import Components.RFmod
Components.RFmod.InitRFmod()

profile("Init:CI")
print("[Enigma2] Initialising CommonInterface.")
import Screens.Ci
Screens.Ci.InitCiConfig()

profile("RcModel")
print("[Enigma2] Initialising RCModel.")
import Components.RcModel

if config.clientmode.enabled.value:
	import Components.ChannelsImporter
	Components.ChannelsImporter.autostart()

# from enigma import dump_malloc_stats
# t = eTimer()
# t.callback.append(dump_malloc_stats)
# t.start(1000)

# first, setup a screen
print("[Enigma2] Starting User Interface.")
try:
	runScreenTest()
	plugins.shutdown()
	Components.ParentalControl.parentalControl.save()
except Exception:
	print("EXCEPTION IN PYTHON STARTUP CODE:")
	print("-" * 60)
	print_exc(file=stdout)
	enigma.quitMainloop(5)
	print("-" * 60)
