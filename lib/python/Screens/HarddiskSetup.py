from Components.ActionMap import ActionMap
from Components.Harddisk import harddiskmanager
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Task import job_manager
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
import Screens.InfoBar


def getProcMounts():
	try:
		with open("/proc/mounts", "r") as fd:
			lines = fd.readlines()
	except (IOError, OSError) as err:
		print("[Harddisk][getProcMounts] Error: Failed to open '/proc/mounts':", err)
		return []
	result = [line.strip().split(" ") for line in lines]
	for item in result:
		item[1] = item[1].replace("\\040", " ")  # Spaces are encoded as \040 in mounts.
		# Also, map any fuseblk fstype to the real file-system behind it...
		# Use blkid to get the info we need....
		#
		if item[2] == 'fuseblk':
			import subprocess
			res = subprocess.run(['blkid', '-sTYPE', '-ovalue', item[0]], capture_output=True)
			if res.returncode == 0:
				# print("[Harddisk][getProcMounts] fuseblk", res.stdout)
				item[2] = res.stdout.strip().decode()
	print("[Harddisk][getProcMounts] ProcMounts", result)
	return result


class HarddiskSetup(Screen):
	def __init__(self, session, hdd, action, text, question):
		Screen.__init__(self, session)
		self.setTitle(text)

		self.action = action
		self.question = question
		self.curentservice = None
		self["model"] = Label(_("Model: ") + hdd.model())
		self["capacity"] = Label(_("Capacity: ") + hdd.capacity())
		self["bus"] = Label(_("Bus: ") + hdd.bus())
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(text)  # text can be either "Initialize" or "Check"
		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.hddQuestion,
			"cancel": self.close
		})
		self["shortcuts"] = ActionMap(["ShortcutActions"],
		{
			"red": self.close,
			"green": self.hddQuestion
		})

	def hddQuestion(self, answer=False):
		print('[HarddiskSetup] answer:', answer)
		if Screens.InfoBar.InfoBar.instance.timeshiftEnabled():
			message = self.question + "\n\n" + _("You seem to be in timeshft, the service will briefly stop as timeshift stops.")
			message += '\n' + _("Do you want to continue?")
			self.session.openWithCallback(self.stopTimeshift, MessageBox, message)
		else:
			message = self.question + "\n" + _("You can continue watching TV while this is running.")
			self.session.openWithCallback(self.hddConfirmed, MessageBox, message)

	def stopTimeshift(self, confirmed):
		if confirmed:
			self.curentservice = self.session.nav.getCurrentlyPlayingServiceReference()
			self.session.nav.stopService()
			Screens.InfoBar.InfoBar.instance.stopTimeshiftcheckTimeshiftRunningCallback(True)
			self.hddConfirmed(True)

	def hddConfirmed(self, confirmed):
		if not confirmed:
			return
		try:
			job_manager.AddJob(self.action())
			for job in job_manager.getPendingJobs():
				if job.name in (_("Initializing storage device..."), _("Checking filesystem..."), _("Converting ext3 to ext4...")):
					self.showJobView(job)
					break
		except Exception as ex:
			self.session.open(MessageBox, str(ex), type=MessageBox.TYPE_ERROR, timeout=10)

		if self.curentservice:
			self.session.nav.playService(self.curentservice)
		self.close()

	def showJobView(self, job):
		from Screens.TaskView import JobView
		job_manager.in_background = False
		self.session.openWithCallback(self.JobViewCB, JobView, job, cancelable=False, afterEventChangeable=False, afterEvent="close")

	def JobViewCB(self, in_background):
		job_manager.in_background = in_background


class HarddiskSelection(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Initialize Devices"))

		self.skinName = "HarddiskSelection"  # For derived classes
		if harddiskmanager.HDDCount() == 0:
			tlist = [(_("no storage devices found"), 0)]
			self["hddlist"] = MenuList(tlist)
		else:
			self["hddlist"] = MenuList(harddiskmanager.HDDList())

		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.okbuttonClick,
			"cancel": self.close
		})

	def doIt(self, selection):
		self.session.openWithCallback(self.close, HarddiskSetup, selection,
			action=selection.createInitializeJob,
			text=_("Initialize"),
			question=_("Do you really want to initialize this device?\nAll the data on the device will be lost!"))

	def okbuttonClick(self):
		selection = self["hddlist"].getCurrent()
		if selection[1] != 0:
			self.doIt(selection[1])
			self.close(True)


class HarddiskPartitionSelect(HarddiskSelection):
	def __init__(self, session):
		HarddiskSelection.__init__(self, session)
		self.session = session
		self.setTitle(_("Initialize Devices"))
		tlist = []
		self.skinName = "HarddiskSelection"  # For derived classes
		procMounts = getProcMounts()
		partitions = harddiskmanager.getMountedPartitions()
		for partition in partitions:
			# print(f"[HarddiskSetup][HarddiskPartitionSelect]1 partition.mountpoint:{partition.mountpoint}")
			if partition.mountpoint == "/":
				continue
			capacity = partition.total() // 1000 // 1000 // 1000
			filesystem = partition.filesystem()
			description = partition.description
			# print(f"[HarddiskSetup][HarddiskPartitionSelect]2 partition.mountpoint:{partition.mountpoint} description:{description} device:{partition.device}")
			partitionDesc = f"{description} {capacity}GB  {filesystem}"
			# print(f"[HarddiskSetup][HarddiskPartitionSelect]3 partition:{partition} partitionDesc:{partitionDesc}")
			for dev in procMounts:
				if "dev" not in dev[0]:
					continue
				# print(f"[HarddiskSetup][HarddiskPartitionSelect]4 dev0:{dev[0]} dev1:{dev[1]} partition.mountpoint:{partition.mountpoint}")
				if dev[1] == partition.mountpoint[0:-1]:
					tlist.append((partitionDesc, dev[0]))
					# print(f"[HarddiskSetup][HarddiskPartitionSelect]5 tlist:{tlist}")
		self["hddlist"] = MenuList(tlist)
		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.doPart,
			"cancel": self.close
		})


	def doPart(self):
		selection = self["hddlist"].getCurrent()
		# print(f"[HarddiskSetup][doPart] selection:{selection[1]}")
		if selection[1] == 0:
			self.close()
		self.Header = "Initialize Devices"
		cmdlist = []
		cmdlist.append(f"umount {selection[1]}")
		cmdlist.append(f"mkfs.ext4 -T largefile -N 262144 {selection[1]}")
		cmdlist.append(f"partprobe {selection[1]}")
		# print(f"[HarddiskSetup][okbuttonClick] cmdlist:{cmdlist}")
		self.session.open(Console, title=self.Header, cmdlist=cmdlist, closeOnSuccess=True)

# This is actually just HarddiskSelection but with correct type


class HarddiskFsckSelection(HarddiskSelection):
	def __init__(self, session):
		HarddiskSelection.__init__(self, session)
		self.setTitle(_("Filesystem Check"))
		self.skinName = "HarddiskSelection"

	def doIt(self, selection):
		self.session.openWithCallback(self.close, HarddiskSetup, selection,
			action=selection.createCheckJob,
			text=_("Check"),
			question=_("Do you really want to check the filesystem?\nThis could take a long time!"))
