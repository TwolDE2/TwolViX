from enigma import eHdmiCEC

from Components.ActionMap import HelpableActionMap
from Components.config import config, configfile
from Components.HdmiCec import HdmiCec
from Components.Sources.StaticText import StaticText
from Screens.Setup import Setup

def getPhysicalAddress():
	physicaladdress = eHdmiCEC.getInstance().getPhysicalAddress()
	hexstring = "%04x" % physicaladdress
	return hexstring[0] + "." + hexstring[1] + "." + hexstring[2] + "." + hexstring[3]

def setFixedPhysicalAddress(address):
	if address != config.hdmicec.fixed_physical_address.value:
		config.hdmicec.fixed_physical_address.value = address
		config.hdmicec.fixed_physical_address.save()
	hexstring = address[0] + address[2] + address[4] + address[6]
	eHdmiCEC.getInstance().setFixedPhysicalAddress(int(float.fromhex(hexstring)))


class CecSetup(Setup):
	def __init__(self, session):
		Setup.__init__(self, session=session, setup="HdmiCec")
		self.setTitle(_("HDMI-CEC Setup"))
		self["addressActions"] = HelpableActionMap(self, ["ColorActions"], {
			"yellow": (self.updateFixedAddress, _("Set current CEC address as fixed address"))
		}, prio=0, description=_("HDMI-CEC Setup Actions"))
		self["defaultActions"] = HelpableActionMap(self, ["ColorActions"], {
			"blue": (self.setDefaults, _("Reset HDMI-CEC settings to default"))
		}, prio=0, description=_("HDMI-CEC Setup Actions"))
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText()
		self["current_address"] = StaticText()
		self["fixed_address"] = StaticText()

	def updateFixedAddress(self):
		config.hdmicec.fixed_physical_address.value = getPhysicalAddress() if config.hdmicec.fixed_physical_address.value == "0.0.0.0" else "0.0.0.0"
		setFixedPhysicalAddress(config.hdmicec.fixed_physical_address.value)
		self.updateAddress()

	def updateAddress(self):
		self["current_address"].setText("%s: %s" % (_("Current CEC address"), getPhysicalAddress()))
		value = config.hdmicec.fixed_physical_address.value
		if value == "0.0.0.0":
			self["fixed_address"].setText(_("Using automatic address"))
			if getPhysicalAddress() != "0.0.0.0":
				self["addressActions"].setEnabled(True)
				self["key_yellow"].setText(_("Set fixed"))
			else:
				self["addressActions"].setEnabled(False)
				self["key_yellow"].setText("")
		else:
			self["fixed_address"].setText("%s: %s" % (_("Using fixed address"), value))
			self["addressActions"].setEnabled(True)
			self["key_yellow"].setText(_("Clear fixed"))

	def setDefaults(self):
		for item in config.hdmicec.dict():
#			if item in ("enabled", "advanced_settings"):
#				continue
			configItem = getattr(config.hdmicec, item)
			configItem.value = configItem.default
		self.createSetup()

	def selectionChanged(self):
		if self.getCurrentItem() == config.hdmicec.enabled:
			if config.hdmicec.enabled.value:
				self.updateAddress()
			else:
				self["key_yellow"].setText("")
				self["current_address"].setText("")
				self["fixed_address"].setText("")
			self["addressActions"].setEnabled(config.hdmicec.enabled.value)
			self["key_blue"].setText(_("Use defaults") if config.hdmicec.enabled.value else "")
			self["defaultActions"].setEnabled(config.hdmicec.enabled.value)
		Setup.selectionChanged(self)

	def keySave(self):
		config.hdmicec.save()
		Setup.keySave(self)
