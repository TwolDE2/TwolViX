from enigma import eHdmiCEC

from Components.ActionMap import HelpableActionMap
from Components.config import config
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
		self.setTitle(_("HDMI-CEC Setup (PhysicalAddress = %s)" % getPhysicalAddress()))
		self["addressActions"] = HelpableActionMap(self, ["ColorActions"],
		{
			"yellow": (self.setFixedAddress, _("Set HDMI-CEC fixed address %s" % getPhysicalAddress())),
			"blue": (self.clearFixedAddress, _("Clear HDMI-CEC fixed address")),
		}, prio=0, description=_("HDMI-CEC Setup Actions CEC = %s" % getPhysicalAddress()))
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText()
		print("[CecSetup][init] Physical addr=%s config.hdmicec.fixed_physical_address.value=%s" % (getPhysicalAddress(), config.hdmicec.fixed_physical_address.value)) 


	def setFixedAddress(self):
		setFixedPhysicalAddress(getPhysicalAddress())
		self.updateAddress()

	def clearFixedAddress(self):
		setFixedPhysicalAddress("0.0.0.0")
		self.updateAddress()


	def updateAddress(self):
		self.current_address = _("Current CEC address") + ": " + getPhysicalAddress()
		if config.hdmicec.fixed_physical_address.value == "0.0.0.0":
			self.fixed_address = ""
		else:
			self.fixed_address = _("Using fixed address") + ": " + config.hdmicec.fixed_physical_address.value
		self.updateDescription()		

	def updateDescription(self): # Called by selectionChanged() or updateAddress()
		self["description"].setText("%s\n%s\n\n%s" % (self.current_address, self.fixed_address, self.getCurrentDescription()))


	def selectionChanged(self):
		if self.getCurrentItem() == config.hdmicec.enabled:
			if config.hdmicec.enabled.value:
				self["addressActions"].setEnabled(True)
				self["key_yellow"].setText(_("Fix Cec to %s" % getPhysicalAddress()))
				self["key_blue"].setText(_("Clear Cec"))						
				self.updateAddress()
			else:
				self["key_yellow"].setText("")
				self["key_blue"].setText("")
		print("[CecSetup][selectionChanged] Physical addr=%s config.hdmicec.fixed_physical_address.value=%s" % (getPhysicalAddress(), config.hdmicec.fixed_physical_address.value))
		self.updateDescription()			
		Setup.selectionChanged(self)

	def keySave(self):
		config.hdmicec.save()
		Setup.keySave(self)
