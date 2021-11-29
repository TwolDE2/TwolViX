from Components.ActionMap import HelpableActionMap
from Components.config import config
import Components.HdmiCec
from Components.Sources.StaticText import StaticText
from Screens.Setup import Setup


class HdmiCECSetupScreen(Setup):
	def __init__(self, session):
		self["key_yellow"] = StaticText(_("Set fixed"))
		self["key_blue"] = StaticText(_("Clear fixed"))
		Setup.__init__(self, session=session, setup="hdmicec", plugin="SystemPlugins/HdmiCEC")
		self["actions"] = HelpableActionMap(self, ["ColorActions"],
		{
<<<<<<< HEAD
			"yellow": (self.setFixedAddress, _("Set HDMI-CEC fixed address")),
			"blue": (self.clearFixedAddress, _("Clear HDMI-CEC fixed address")),
		}, prio=-2, description=_("HDMI-CEC address editing actions"))
=======
			"ok": self.keyGo,
			"save": self.keyGo,
			#"cancel": self.keyCancel,
			"cancel": self.closeRecursive,
			"green": self.keyGo,
			#"red": self.keyCancel,
			"red": self.closeRecursive,
			"yellow": self.setFixedAddress,
			"blue": self.clearFixedAddress,
			"up": self.keyUp,
			"down": self.keyDown,
		}, -2)

		self.onChangedEntry = []
		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
		self.advancedSettings("start")
		self.createSetup()

	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Enabled"), config.hdmicec.enabled, _('helptext'), 'refreshlist'))
		if config.hdmicec.enabled.value:
			tab = ' ' * 10
			self.list.append(getConfigListEntry(_("Advanced Settings"), config.hdmicec.advanced_settings, _('helptext'), 'refreshlist'))
			if config.hdmicec.advanced_settings.value:
				self.list.append(getConfigListEntry(_("Load Default Settings"), config.hdmicec.default_settings, _('helptext'), 'refreshlist'))
			self.list.append(getConfigListEntry(_("Regard deep standby as standby"), config.hdmicec.handle_deepstandby_events, _('helptext'), 'refreshlist'))
			if config.hdmicec.advanced_settings.value and config.hdmicec.handle_deepstandby_events.value and config.workaround.deeprecord.value:
				self.list.append(getConfigListEntry(tab + _("Wait for timesync at startup"), config.hdmicec.deepstandby_waitfortimesync, _("If the 'deep standby workaround' is enabled, it waits until the system time is synchronized. Depending on the requirement, the devices wake up will continuing after a maximum of 2 minutes."), ))
			self.list.append(getConfigListEntry(_("Put TV in standby"), config.hdmicec.control_tv_standby, _('helptext'), 'refreshlist'))
			if config.hdmicec.advanced_settings.value and config.hdmicec.control_tv_standby.value:
				self.list.append(getConfigListEntry(tab + _("Even if TV has another input active?"), config.hdmicec.tv_standby_notinputactive, _('You can skip this function and turn off the TV when you wake the receiver from standby and immediately switch back to standby.'), ))
			self.list.append(getConfigListEntry(_("Wakeup TV from standby"), config.hdmicec.control_tv_wakeup, _('helptext'), 'refreshlist'))
			if config.hdmicec.advanced_settings.value and config.hdmicec.control_tv_wakeup.value:
				self.list.append(getConfigListEntry(tab + _("Even if a 'Zap' recording timer starting?"), config.hdmicec.tv_wakeup_zaptimer, _('helptext'), ))
				self.list.append(getConfigListEntry(tab + _("Even if a 'Zap and Record' recording timer starting?"), config.hdmicec.tv_wakeup_zapandrecordtimer, _('helptext'), ))
				self.list.append(getConfigListEntry(tab + _("Even if a 'Wakeup' power timer starting?"), config.hdmicec.tv_wakeup_wakeuppowertimer, _('helptext'), ))
			self.list.append(getConfigListEntry(_("Switch TV to correct input"), config.hdmicec.report_active_source, _('helptext'), 'refreshlist'))
			if config.hdmicec.advanced_settings.value and config.hdmicec.report_active_source.value:
				self.list.append(getConfigListEntry(tab + _("Switch off the TV to correct input"), config.hdmicec.workaround_activesource, _("Some TV devices can't swich to correct input if a another hdmi port active. This setting set the TV to standby before.\n(If the TV does not turn back on, may require a slower transmission interval or the repetition of wake-up commands.)"),))
			self.list.append(getConfigListEntry(_("Handle wakeup from TV"), config.hdmicec.handle_tv_wakeup, _('Choose a setting where your receiver wakes up from standby.'),))
			self.list.append(getConfigListEntry(_("Handle standby from TV"), config.hdmicec.handle_tv_standby, _('helptext'), 'refreshlist'))
			if config.hdmicec.advanced_settings.value:
				self.list.append(getConfigListEntry(_("Handle input from TV"), config.hdmicec.handle_tv_input, _('helptext'), 'refreshlist'))
				if config.hdmicec.handle_tv_standby.value != 'disabled' or config.hdmicec.handle_tv_input.value != 'disabled':
					self.list.append(getConfigListEntry(_("Time delay until standby or deep standby"), config.hdmicec.handle_tv_delaytime, _("'Handle standby from TV' has a higher priority as 'Handle input from TV'"),))
			self.list.append(getConfigListEntry(_("Forward volume keys"), config.hdmicec.volume_forwarding, _('Activation takes place immediately. If this feature is not supported, the volume keys has no function!'),))
			self.list.append(getConfigListEntry(_("Put your AV Receiver in standby"), config.hdmicec.control_receiver_standby, _('helptext'),))
			self.list.append(getConfigListEntry(_("Wakeup your AV Receiver from standby"), config.hdmicec.control_receiver_wakeup, _('helptext'),))
			self.list.append(getConfigListEntry(_("Use TV remote control"), config.hdmicec.report_active_menu, _('Activation takes place immediately. If it does feature not work, then try again with a slower send interval.'),))
			self.list.append(getConfigListEntry(_("Minimum send interval"), config.hdmicec.minimum_send_interval, _('Try to slow down the send interval if not all commands are executed.'), ))
			if config.hdmicec.advanced_settings.value:
				self.list.append(getConfigListEntry(_("Repeat the sent standby and wakeup commands"), config.hdmicec.messages_repeat, _('Try to send repeated commands if not all commands are executed.\n') + _('(e.g. TV wakeup, but not switched to correct input)'), 'refreshlist'))
				if int(config.hdmicec.messages_repeat.value):
					self.list.append(getConfigListEntry(tab + _("Time delay for the repeated transmission"), config.hdmicec.messages_repeat_slowdown, _('The time is multiplied by the current repeat counter.'), ))
					self.list.append(getConfigListEntry(tab + _("Repeat the standby commands?"), config.hdmicec.messages_repeat_standby, _('Is not necessary in most cases.'), 'refreshlist'))
				self.list.append(getConfigListEntry(_("Check power and input state from TV"), config.hdmicec.check_tv_state, _('An attempt is made to capture the current TV status. If this is not possible due to incorrect or missing status messages, it may cause the receiver to respond unexpectedly.\nOn the other hand, tries to respond better to different operating conditions.'), ))
				self.list.append(getConfigListEntry(_("Ignore unexpectedly wakeup and stay in standby"), config.hdmicec.workaround_turnbackon, _("This is a workaround for some devices there wakeup again after switching in standby. The wak up command's from other devices will ignored for few seconds."),))
			if fileExists("/proc/stb/hdmi/preemphasis"):
				self.list.append(getConfigListEntry(_("Use HDMI-preemphasis"), config.hdmicec.preemphasis, _('With this setting, you can probably improve the signal quality or eliminate problems that can occur with longer HDMI cables.'),))
			self.list.append(getConfigListEntry(_("Enable command line function"), config.hdmicec.commandline, _("Activate an way to send individual or specific internal HDMI-CEC commands from the command line. Type on command line 'echo help > %s' and then read the file '%s' for a short help.") % (Components.HdmiCec.cmdfile, Components.HdmiCec.hlpfile), ))
			self.list.append(getConfigListEntry(_("Enable debug log *"), config.hdmicec.debug, _('Allows you to enable the debug log. They contain very detailed information of everything the system does.') + _("\n* Logs location: logs settings, Filename: Enigma2-hdmicec-[date].log"), ))

		self["config"].list = self.list
		self["config"].l.setList(self.list)
>>>>>>> 76bd5f8a82... [HDMICECSetup]

		self.updateAddress()

	def selectionChanged(self): # This is needed because the description is not standard. i.e. a concatenation.
		self.updateDescription()

	def updateDescription(self): # Called by selectionChanged() or updateAddress()
		self["description"].setText("%s\n%s\n\n%s" % (self.current_address, self.fixed_address, self.getCurrentDescription()))

	def keySelect(self):
		if self.getCurrentItem() == config.hdmicec.log_path:
			self.set_path()
		else:
			Setup.keySelect(self)

	def setFixedAddress(self):
		Components.HdmiCec.hdmi_cec.setFixedPhysicalAddress(Components.HdmiCec.hdmi_cec.getPhysicalAddress())
		self.updateAddress()

	def clearFixedAddress(self):
		Components.HdmiCec.hdmi_cec.setFixedPhysicalAddress("0.0.0.0")
		self.updateAddress()

	def updateAddress(self):
		self.current_address = _("Current CEC address") + ": " + Components.HdmiCec.hdmi_cec.getPhysicalAddress()
		if config.hdmicec.fixed_physical_address.value == "0.0.0.0":
			self.fixed_address = ""
		else:
			self.fixed_address = _("Using fixed address") + ": " + config.hdmicec.fixed_physical_address.value
		self.updateDescription()

	def logPath(self, res):
		if res is not None:
			config.hdmicec.log_path.value = res

	def set_path(self):
		inhibitDirs = ["/autofs", "/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/tmp", "/usr"]
		from Screens.LocationBox import LocationBox
		txt = _("Select directory for logfile")
		self.session.openWithCallback(self.logPath, LocationBox, text=txt, currDir=config.hdmicec.log_path.value,
				bookmarks=config.hdmicec.bookmarks, autoAdd=False, editDir=True,
				inhibitDirs=inhibitDirs, minFree=1
				)


def Plugins(**kwargs):
	# imported directly by menu.xml based on SystemInfo["HDMICEC"]
	return []
