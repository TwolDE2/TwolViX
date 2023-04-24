from Components.config import config, configfile
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Tools.Directories import fileExists, fileHas


class VuWizard2(Screen):

	skin = """
	<screen name="VuWizard" position="center,center" size="750,700" flags="wfNoBorder" backgroundColor="transparent">
		<eLabel name="b" position="0,0" size="750,700" backgroundColor="#00ffffff" zPosition="-2" />
		<eLabel name="a" position="1,1" size="748,698" backgroundColor="#00000000" zPosition="-1" />
		<widget source="Title" render="Label" position="center,14" foregroundColor="#00ffffff" size="e-10%,35" halign="left" valign="center" font="Regular; 28" backgroundColor="#00000000" />
		<eLabel name="line" position="1,60" size="748,1" backgroundColor="#00ffffff" zPosition="1" />
		<widget source="description" render="Label" position="2,80" size="730,300" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="action" render="Label" position="200,300" size="400,150" noWrap="1" zPosition="1" valign="center" font="Regular; 24" halign="left" backgroundColor="#00000000" foregroundColor="#00ffffff" />
	</screen>
	"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.title = _("Vu+ MultiBoot Initialisation")
		self["description"] = Label(_("Enabling MultiBoot."))
		self["action"] = StaticText("Enabling MultiBoot")
					
		if fileHas("/proc/cmdline", "kexec=1") and fileExists("/STARTUP_RECOVERY") or fileExists("/boot/STARTUP_RECOVERY"):
			config.misc.firstrun.value = 0
			config.misc.firstrun.save()
			configfile.save()
