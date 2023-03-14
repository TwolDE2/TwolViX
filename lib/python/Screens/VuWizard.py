from boxbranding import getBoxType, getMachineMtdKernel, getMachineMtdRoot
from Components.Console import Console
from Tools.Directories import fileExists, pathExists

STARTUP = "kernel=/zImage root=/dev/%s rootsubdir=linuxrootfs0" % getMachineMtdRoot()					# /STARTUP
STARTUP_RECOVERY = "kernel=/zImage root=/dev/%s rootsubdir=linuxrootfs0" % getMachineMtdRoot() 			# /STARTUP_RECOVERY
STARTUP_1 = "kernel=/linuxrootfs1/zImage root=/dev/%s rootsubdir=linuxrootfs1" % getMachineMtdRoot() 	# /STARTUP_1
STARTUP_2 = "kernel=/linuxrootfs2/zImage root=/dev/%s rootsubdir=linuxrootfs2" % getMachineMtdRoot() 	# /STARTUP_2
STARTUP_3 = "kernel=/linuxrootfs3/zImage root=/dev/%s rootsubdir=linuxrootfs3" % getMachineMtdRoot() 	# /STARTUP_3

class VuWizard():
	def __init__(self, session):
		self.session = session
		if fileExists("/STARTUP_RECOVERY") or fileExists("/boot/STARTUP_RECOVERY"):
			return	
		else:
			self.session.Console = Console()
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
			print("[VuplusKexec][RootInit] Kernel Root", getMachineMtdKernel(), "   ", getMachineMtdRoot())
			cmdlist = []
			cmdlist.append("dd if=/dev/%s of=/zImage" % getMachineMtdKernel())					# backup old kernel
			cmdlist.append("dd if=/usr/bin/kernel_auto.bin of=/dev/%s" % getMachineMtdKernel())	# create new kernel
			cmdlist.append("mv /usr/bin/STARTUP.cpio.gz /STARTUP.cpio.gz")						# copy userroot routine
			cmdlist.append("killall -9 enigma2 && init 6")										# reboot
			self.session.Console().eBatch(cmdlist, self.RootInitEnd, debug=False)

	def RootInitEnd(self, *args, **kwargs):
		print("[VuplusKexec][RootInitEnd] rebooting")
#		for eMMCslot in range(1,4):		
#			if pathExists("/media/hdd/%s/linuxrootfs%s" % (getBoxType(), eMMCslot)):
#				self.session.Console().ePopen("cp -R /media/hdd/%s/linuxrootfs%s . /" % (getBoxType(), eMMCslot))
