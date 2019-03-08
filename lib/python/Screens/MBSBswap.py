import os
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.ChoiceList import ChoiceList, ChoiceEntryComponent
from Screens.Console import Console
from Components.Label import Label
from Components.SystemInfo import SystemInfo
from Screens.Standby import TryQuitMainloop
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.BoundFunction import boundFunction
from Tools.Multiboot import GetCurrentImage


class MBSBswap(Screen):

	skin = """
	<screen name="MBSBswap" position="center,center" size="750,900" flags="wfNoBorder" backgroundColor="transparent">
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
		<ePixmap pixmap="skin_default/buttons/red.png" position="30,200" size="40,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="230,200" size="40,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="430,200" size="40,40" alphatest="on" />
	</screen>
	"""

	def __init__(self, session, *args):
		Screen.__init__(self, session)
		self.skinName = "MBSBswap"
		screentitle = _("switch from Multiboot to Singleboot")
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Reboot"))
		self["key_yellow"] = StaticText(_("SwaptoSingle"))
		self.title = screentitle
		self.switchtype = " "
		self["actions"] = ActionMap(["ColorActions"],
		{
			"red": boundFunction(self.close, None),
			"green": self.Reboot,
			"yellow": self.SwaptoSB,
		}, -1)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.title)



	def SwaptoSB(self):
		if GetCurrentImage() != 1:
			self.session.open(MessageBox, _("Unable to switch to single boot mode - please multiboot to slot 1. "), MessageBox.TYPE_INFO, timeout=20)
		else:
			self.TITLE = _("Switch from multiboot to single boot - please reboot after use.")
			cmdlist = []
			cmdlist.append("parted -s /dev/mmcblk1 rm 4")
			cmdlist.append("parted -s /dev/mmcblk1 rm 5")
			cmdlist.append("parted -s /dev/mmcblk1 rm 6")
			cmdlist.append("parted -s /dev/mmcblk1 rm 7")
			cmdlist.append('parted -s /dev/mmcblk1 rm 8')
			cmdlist.append("parted -s /dev/mmcblk1 rm 9")
			cmdlist.append("parted /dev/mmcblk1 unit % resizepart 3 Yes 100%")
			cmdlist.append("rm -f /.resizerootfs")
			exec "self.session.open(Console, title = self.TITLE, cmdlist = cmdlist)"
#			self.session.open(Console, title = self.title, cmdlist = cmdlist, closeOnSuccess = True)

	def Reboot(self):
		self.session.open(TryQuitMainloop, 2)
