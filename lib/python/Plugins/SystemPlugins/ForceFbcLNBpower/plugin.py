# Author: Dimitrij <Dima-73@inbox.lv>
import os
from enigma import eTimer
from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.NimManager import nimmanager
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen


# HasFBCDVBStuner = ["Vuplus DVB-S NIM(7376 FBC)", "Vuplus DVB-S NIM(45308X FBC)", "Vuplus DVB-S NIM(45208 FBC)", "DVB-S NIM(45208 FBC)", "DVB-S2X NIM(45308X FBC)", "DVB-S2 NIM(45308 FBC)", "BCM45208", "BCM45308X"]

config.plugins.miscControl = ConfigSubsection()
config.plugins.miscControl.forceLnbPower = ConfigSelection(default="off", choices=[("on", _("Yes")), ("off", _("No")), ("auto", _("Auto"))])
config.plugins.miscControl.forceToneBurst = ConfigSelection(default="disable", choices=[("enable", _("Yes")), ("disable", _("No"))])

PROC_FORCE_LNBPOWER = "/proc/stb/frontend/fbc/force_lnbon"
PROC_FORCE_TONEBURST = "/proc/stb/frontend/fbc/force_toneburst"

IS_PROC_FORCE_LNBPOWER = os.path.exists(PROC_FORCE_LNBPOWER)
IS_PROC_FORCE_TONEBURST = os.path.exists(PROC_FORCE_TONEBURST)

def setProcValueOnOff(value, procPath):
	try:
		fd = open(procPath,'w')
		fd.write(value)
		fd.close()
		return 0
	except Exception as e:
		return -1

class FBCtunerLNBstandbyPower(Screen, ConfigListScreen):
	skin = 	"""
		<screen position="center,center" size="620,150" title="Force LNB power - FBC tuners" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="140,10" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="370,10" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="140,10" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />
			<widget source="key_green" render="Label" position="370,10" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1" />
			<widget name="config" zPosition="2" position="5,70" size="600,80" scrollbarMode="showOnDemand" transparent="1" />
		</screen>
		"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Force LNB power - FBC tuners"))
		self["shortcuts"] = ActionMap(["ShortcutActions", "SetupActions"],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
		}, -2)
		self.list = []
		ConfigListScreen.__init__(self, self.list,session=session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self.dispErrorTimer = eTimer()
		self.dispErrorTimer.callback.append(self.dispErrorMsg)
		self.onLayoutFinish.append(self.procCheck)

	def procCheck(self):
		if not IS_PROC_FORCE_LNBPOWER and not IS_PROC_FORCE_TONEBURST:
			self.dispErrorTimer.start(500, True)
		else:
			self.createSetup()

	def dispErrorMsg(self):
		self.session.openWithCallback(self.closeCallback, MessageBox, _("Driver is not supported!"), MessageBox.TYPE_ERROR)

	def closeCallback(self, answer):
		self.close()

	def createSetup(self):
		self.list = []
		self.lnbPowerEntry = getConfigListEntry(_("Force LNB power"), config.plugins.miscControl.forceLnbPower)
		self.toneBurstEntry = getConfigListEntry(_("Force ToneBurst"), config.plugins.miscControl.forceToneBurst)
		if IS_PROC_FORCE_LNBPOWER:
			self.list.append(self.lnbPowerEntry)
		if IS_PROC_FORCE_TONEBURST:
			self.list.append(self.toneBurstEntry)
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		global tunerStateChanged
		if IS_PROC_FORCE_LNBPOWER:
			if config.plugins.miscControl.forceLnbPower.value == "auto" and tunerStateChanged == None:
				tunerStateChanged = FBCtunerChanged()
			val = config.plugins.miscControl.forceLnbPower.value == "on" and "on" or "off"
			res = setProcValueOnOff(val, PROC_FORCE_LNBPOWER)
			if res == -1:
				self.resetConfig()
				self.session.openWithCallback(self.close, MessageBox, _("SET FAILED!\n"), MessageBox.TYPE_ERROR)
				return
		if IS_PROC_FORCE_TONEBURST:
			res = setProcValueOnOff(config.plugins.miscControl.forceToneBurst.value, PROC_FORCE_TONEBURST)
			if res == -1:
				self.resetConfig()
				self.session.openWithCallback(self.close, MessageBox, _("SET FAILED!\n"), MessageBox.TYPE_ERROR)
				return
		config.plugins.miscControl.save()
		self.close()

	def resetConfig(self):
		for x in self["config"].list:
			x[1].cancel()

global_set_on = False
from Components.Sources.TunerInfo import TunerInfo

class FBCtunerChanged(TunerInfo):
	def tunerUseMaskChanged(self, mask):
		global global_set_on
		if config.plugins.miscControl.forceLnbPower.value == "auto":
			set_on = False
			if mask:
				for n in nimmanager.nim_slots:
					if n.type and "DVB-S" in n.type and n.enabled and n.description in SystemInfo["HasFBCtuner"]:
						if mask & 1 << n.slot or mask == n.slot:
							if not global_set_on:
								setProcValueOnOff("on", PROC_FORCE_LNBPOWER)
							set_on = True
							global_set_on = True
							break
			if not set_on:
				if global_set_on:
					setProcValueOnOff("off", PROC_FORCE_LNBPOWER)
				global_set_on = False


def startSetup(menuid):
	if menuid == "scan":
		for slot in nimmanager.nim_slots:
			if slot.isCompatible("DVB-S") and slot.description in SystemInfo["HasFBCtuner"]:
				return [(_("FBC force LNB power"), main, "lnb_power_on", 100)]
	return []
	
def main(session, **kwargs):
	session.open(FBCtunerLNBstandbyPower)

OnStart = False
tunerStateChanged = None

def OnSessionStart(session, **kwargs):
	global OnStart, tunerStateChanged
	if not OnStart:
		OnStart = True
		if IS_PROC_FORCE_LNBPOWER:
			if config.plugins.miscControl.forceLnbPower.value == "auto":
				tunerStateChanged = FBCtunerChanged()
			val = config.plugins.miscControl.forceLnbPower.value == "on" and "on" or "off"
			setProcValueOnOff(val, PROC_FORCE_LNBPOWER)
		if IS_PROC_FORCE_TONEBURST:
			setProcValueOnOff(config.plugins.miscControl.forceToneBurst.value, PROC_FORCE_TONEBURST)

def Plugins(**kwargs):
	pList = []
	if nimmanager.hasNimType("DVB-S"):
		pList.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=OnSessionStart))
		pList.append(PluginDescriptor(name=_("FBC force LNB power"), description=_("Force LNB power - FBC tuners"), where=PluginDescriptor.WHERE_MENU, needsRestart=False, fnc=startSetup))
	return pList
