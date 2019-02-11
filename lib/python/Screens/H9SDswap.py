from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.ChoiceList import ChoiceList, ChoiceEntryComponent
from Components.Console import Console
from Components.Label import Label
from Components.SystemInfo import SystemInfo
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.BoundFunction import boundFunction


class H9SDswap(Screen):

	skin = """
	<screen name="H9SDswap" position="center,center" size="750,900" flags="wfNoBorder" backgroundColor="transparent">
		<eLabel name="b" position="0,0" size="750,700" backgroundColor="#00ffffff" zPosition="-2" />
		<eLabel name="a" position="1,1" size="748,698" backgroundColor="#00000000" zPosition="-1" />
		<widget source="Title" render="Label" position="60,10" foregroundColor="#00ffffff" size="480,50" halign="left" font="Regular; 28" backgroundColor="#00000000" />
		<eLabel name="line" position="1,60" size="748,1" backgroundColor="#00ffffff" zPosition="1" />
		<eLabel name="line2" position="1,250" size="748,4" backgroundColor="#00ffffff" zPosition="1" />
		<widget name="config" position="2,280" size="730,380" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00e5b243" />
		<widget source="labe14" render="Label" position="2,80" size="730,30" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="labe15" render="Label" position="2,130" size="730,60" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="key_red" render="Label" position="30,200" size="150,30" noWrap="1" zPosition="1" valign="center" font="Regular; 20" halign="left" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="key_green" render="Label" position="230,200" size="150,30" noWrap="1" zPosition="1" valign="center" font="Regular; 20" halign="left" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="key_yellow" render="Label" position="430,200" size="150,30" noWrap="1" zPosition="1" valign="center" font="Regular; 20" halign="left" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="key_blue" render="Label" position="630,200" size="150,30" noWrap="1" zPosition="1" valign="center" font="Regular; 20" halign="left" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<eLabel position="20,200" size="6,40" backgroundColor="#00e61700" /> <!-- Should be a pixmap -->
		<eLabel position="190,200" size="6,40" backgroundColor="#0061e500" /> <!-- Should be a pixmap -->
	</screen>
	"""

	def __init__(self, session, *args):
		Screen.__init__(self, session)
		self.skinName = "H9SDswap"
		screentitle = _("H9 swap root to SD card")
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("SwaptoNand"))
		self["key_yellow"] = StaticText(_("SwaptoSD"))
		self["key_blue"] = StaticText(_("Reboot"))
		self.title = screentitle
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"red": boundFunction(self.close, None),
			"green": self.SDInit,
			"yellow": self.SDswap,
			"blue": self.reboot,
			"ok": self.reboot,
			"cancel": boundFunction(self.close, None),
		}, -1)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.title)
#
#				if os.path.exists("/usr/scripts/standby_enter.sh"):
#					Console().ePopen("/usr/scripts/standby_enter.sh")

	def SwaptoNand(self):
#		cmdlist = []
#		cmdlist.append("dd if=/usr/script/bootargs-nand.bin of=/dev/mtdblock1")
#		self.session.open(Console, cmdlist = cmdlist, closeOnSuccess = True)
		self.container = Console()
		self.container.ePopen("dd if=/usr/lib/enigma2/python/Plugins/SystemPlugins/ViX/bootargs-nand.bin of=/dev/mtdblock1", self.ContainterFallback)
	

	def SwaptoSD(self):
#		cmdlist = []
#		cmdlist.append("dd if=/usr/H9S/bootargs-mmc.bin of=/dev/mtdblock1")
#		self.session.open(Console, cmdlist = cmdlist, closeOnSuccess = True)
		self.container = Console()
		self.container.ePopen("dd if=/usr/lib/enigma2/python/Plugins/SystemPlugins/ViX/bootargs-nand.bin of=/dev/mtdblock1", self.ContainterFallback)

	def reboot(self):
		self.session.open(TryQuitMainloop, 2)


	def ContainterFallback(self, data=None, retval=None, extra_args=None):
		self.container.killAll()	


