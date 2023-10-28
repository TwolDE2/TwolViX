from Components.config import config, ConfigBoolean, configfile
from Components.Pixmap import Pixmap
from Screens.LanguageSelection import LanguageWizard  # noqa: F401
from Screens.NetworkWizard import NetworkWizard
from Screens.Rc import Rc
from Screens.VideoWizard import VideoWizard
from Screens.VuWizard import VuWizard
from Screens.WizardLanguage import WizardLanguage
from Screens.Wizard import wizardManager
from Screens.WizardUserInterfacePositioner import UserInterfacePositionerWizard
from Tools.Directories import fileExists, fileHas

config.misc.firstrun = ConfigBoolean(default=True)
config.misc.languageselected = ConfigBoolean(default=True)
config.misc.videowizardenabled = ConfigBoolean(default=True)
config.misc.networkenabled = ConfigBoolean(default=False)
config.misc.networkenabled_negative = ConfigBoolean(default=False)
config.misc.Vuwizardenabled = ConfigBoolean(default=False)
config.misc.restorewizardrun = ConfigBoolean(default=False)

if fileExists("/usr/bin/kernel_auto.bin") and fileExists("/usr/bin/STARTUP.cpio.gz") and not fileHas("/proc/cmdline", "kexec=1") and config.misc.firstrun.value:
	config.misc.Vuwizardenabled.value = True
config.misc.networkenabled_negative = not config.misc.networkenabled	
print("[StartWizard][import] import.......")


class StartWizard(WizardLanguage, Rc):
	def __init__(self, session, silent=True, showSteps=False, neededTag=None):
		self.xmlfile = ["startwizard.xml"]
		WizardLanguage.__init__(self, session, showSteps=False)
		Rc.__init__(self)
		self["wizard"] = Pixmap()
		print("[StartWizard][Init] import.......")

	def markDone(self):
		config.misc.firstrun.value = 0
		config.misc.firstrun.save()
		configfile.save()


# wizardManager.registerWizard(VideoWizard, config.misc.Vuwizardenabled.value, priority=2)
wizardManager.registerWizard(VuWizard, config.misc.Vuwizardenabled.value, priority=3)
wizardManager.registerWizard(VideoWizard, config.misc.videowizardenabled.value, priority=10)
wizardManager.registerWizard(NetworkWizard, config.misc.videowizardenabled_negative.value, priority=15)
wizardManager.registerWizard(UserInterfacePositionerWizard, config.misc.firstrun.value, priority=20)
wizardManager.registerWizard(StartWizard, config.misc.firstrun.value, priority=25)
