import glob
from time import sleep
from boxbranding import getBoxType, getMachineMtdKernel, getMachineMtdRoot
from Components.config import config, configfile
from Components.Console import Console
from Components.Pixmap import Pixmap
from Components.Sources.Boolean import Boolean
from Screens.MessageBox import MessageBox
from Screens.Rc import Rc
from Screens.Screen import Screen
from Screens.WizardLanguage import WizardLanguage
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_SKIN


STARTUP = "kernel=/zImage root=/dev/%s rootsubdir=linuxrootfs0" % getMachineMtdRoot()					# /STARTUP
STARTUP_RECOVERY = "kernel=/zImage root=/dev/%s rootsubdir=linuxrootfs0" % getMachineMtdRoot() 			# /STARTUP_RECOVERY
STARTUP_1 = "kernel=/linuxrootfs1/zImage root=/dev/%s rootsubdir=linuxrootfs1" % getMachineMtdRoot() 	# /STARTUP_1
STARTUP_2 = "kernel=/linuxrootfs2/zImage root=/dev/%s rootsubdir=linuxrootfs2" % getMachineMtdRoot() 	# /STARTUP_2
STARTUP_3 = "kernel=/linuxrootfs3/zImage root=/dev/%s rootsubdir=linuxrootfs3" % getMachineMtdRoot() 	# /STARTUP_3


class VuWizard(WizardLanguage, Rc):
	def __init__(self, session, interface=None):
		self.xmlfile = resolveFilename(SCOPE_SKIN, "vuwizard.xml")
		WizardLanguage.__init__(self, session, showSteps=False, showStepSlider=False)
		Rc.__init__(self)
		self.skinName = ["VuWizard", "StartWizard"]
		self.session = session
		self.Console = Console(binary=True)
		self["wizard"] = Pixmap()
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["VKeyIcon"] = Boolean(False)

		self.NextStep = None
		self.Text = None

		if self.welcomeWarning not in self.onShow:
			self.onShow.append(self.welcomeWarning)

	def welcomeWarning(self):
		if self.welcomeWarning in self.onShow:
			self.onShow.remove(self.welcomeWarning)
		popup = self.session.openWithCallback(self.welcomeAction, MessageBox, _("Welcome to OpenViX!\n\n"
			"Your Vu4K receiver is capable of Multiboot or Vu Standalone options"
			"If you wish to use the Standard Vu image setup, hit enter or No.\n\n"
			"Select Yes to continue with Vu Multiboot initialisation "
			"Note:- restoring eMMC slots takes upto 5 minutes per slot.\n\n" 
			"Receiver will then reboot to setup Wizard.\n In Wizard finalise Recovery image, or exit and \n - select restored eMMC image with MultiBootSelector.   \n or \n - flash new image into multiboot slot via ImageManager."
			"Select Yes to install or No to skip this step."), type=MessageBox.TYPE_YESNO, timeout=-1, default=False)
		popup.setTitle(_("Start Wizard - Vu+ 4K install options"))

	def welcomeAction(self, answer):
		if answer:
			if fileExists("/STARTUP_RECOVERY") or fileExists("/boot/STARTUP_RECOVERY"):
				self.close
			else:
				with open("/STARTUP", 'w') as f:
					f.write(STARTUP)
				with open("/STARTUP_RECOVERY", 'w') as f:
					f.write(STARTUP_RECOVERY)
				with open("/STARTUP_1", 'w') as f:
					f.write(STARTUP_1)
				with open("/STARTUP_2", 'w') as f:
					f.write(STARTUP_2)
				with open("/STARTUP_3", 'w') as f:
					f.write(STARTUP_3)
				cmdlist = []
				cmdlist.append("dd if=/dev/%s of=/zImage" % getMachineMtdKernel())					# backup old kernel
				cmdlist.append("dd if=/usr/bin/kernel_auto.bin of=/dev/%s" % getMachineMtdKernel())	# create new kernel
				cmdlist.append("mv /usr/bin/STARTUP.cpio.gz /STARTUP.cpio.gz")						# copy userroot routine
				for file in glob.glob("/media/*/vuplus/*/force.update", recursive=True):
					cmdlist.append("mv %s %s" % (file, file.replace("force.update", "noforce.update")))						# remove Vu force update(Vu+ Zero4k)			
				self.Console.eBatch(cmdlist, self.RootInitEnd, debug=False)
		else:
			self.close()

	def RootInitEnd(self, *args, **kwargs):
		cmdlist = []
		slotlist = []	
		for eMMCslot in range(1,4):		
			if pathExists("/media/hdd/%s/linuxrootfs%s" % (getBoxType(), eMMCslot)):
				slotlist.append(eMMCslot)		
#				self["action"].setText(_("Restoring MultiBoot Slots %s." % slotlist))
				cmdlist.append("cp -R /media/hdd/%s/linuxrootfs%s . /" % (getBoxType(), eMMCslot))
		if cmdlist:
			self.Console.eBatch(cmdlist, self.reBoot, debug=False)
		else:
#			sleep(5)
			self.reBoot()					

	def reBoot(self, *args, **kwargs):
		config.misc.restorewizardrun.value = True
		config.misc.restorewizardrun.save()
		config.misc.firstrun.value = 0
		config.misc.firstrun.save()		
		configfile.save()		
		self.Console.ePopen("killall -9 enigma2 && init 6")

	def exitWizardQuestion(self, ret=False):
		if ret:
			self.markDone()
			self.close()

	def markDone(self):
		pass

	def back(self):
		WizardLanguage.back(self)	

