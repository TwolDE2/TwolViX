from datetime import datetime
import glob
import struct
import subprocess
import tempfile
from os import listdir, path, remove as os_remove, rmdir, rename, sep, stat, statvfs, sync
import re

from Components.SystemInfo import SystemInfo, BoxInfo as BoxInfoRunningInstance, BoxInformation, BOXTYPE, CHKROOTMB, MODEL, MTDKERNEL, MTDROOTFS, UBIMB
from Tools.Directories import copyfile, fileExists, fileHas, fileReadLine, fileReadLines, pathExists, resolveFilename, SCOPE_CONFIG

MBBOOTDEVICE_CACHE = resolveFilename(SCOPE_CONFIG, "multiboot_device")


def initMultiboot():
	SystemInfo["HasRootSubdir"] = False
	SystemInfo["RecoveryMode"] = False
	SystemInfo["AndroidMode"] = False
	SystemInfo["HasMultibootMTD"] = False
	SystemInfo["resetMBoot"] = False
	SystemInfo["HasKexecUSB"] = False
	SystemInfo["HasMultibootFlags"] = False
	SystemInfo["HasKexecMultiboot"] = fileHas("/proc/cmdline", "kexec=1")
	SystemInfo["HasNewMultiboot"] = fileExists("/.newMB")  # marker the NewMB initramfs writes into the root it selected
	SystemInfo["HasChkrootMultiboot"] = isFat32("/dev/block/by-name/others") or fileExists("/dev/block/by-name/startup")
	SystemInfo["MBbootdevice"] = ""
	SystemInfo["canchkroot"] = (UBIMB or fileExists("/dev/block/by-name/others")) and not SystemInfo["HasChkrootMultiboot"] and not fileExists("/etc/.disableChkroot")
	SystemInfo["HasHiSi"] = pathExists("/proc/hisi") and BOXTYPE not in ("vipertwin", "viper4kv20", "viper4kv40", "sfx6008", "sfx6018")  # This needs to be for later checks
	SystemInfo["canMultiBoot"] = getMultibootslots()
	SystemInfo["canBackupEMC"] = MODEL in ("hd51", "h7") and ("disk.img", "%s" % SystemInfo["MBbootdevice"]) or MODEL in ("osmio4k", "osmio4kplus", "osmini4k") and ("emmc.img", "%s" % SystemInfo["MBbootdevice"]) or SystemInfo["HasHiSi"] and ("usb_update.bin", "none")
	SystemInfo["CanKexecVu"] = MODEL in ("vusolo4k", "vuduo4k", "vuduo4kse", "vuultimo4k", "vuuno4k", "vuuno4kse", "vuzero4k") and not SystemInfo["HasKexecMultiboot"]  # Was in SystemInfo.py. Seems to be unsed.


def getMultibootslots():
	bootslots = {}
	slotname = ""
	SystemInfo["MultiBootSlot"] = None
	SystemInfo["VuUUIDSlot"] = ""
	SystemInfo["BootDevice"] = ""
	UUID = ""
	UUIDnum = 0
	tmpdir = tempfile.mkdtemp(prefix="getMultibootslots")
	print(f"[multiboot][getMultibootslots]root:{MTDROOTFS} UBIMB:{UBIMB} CHKROOTMB:{CHKROOTMB}")
	if SystemInfo["HasKexecMultiboot"]:
		MbootList = (f"/dev/{MTDROOTFS}", )  # kexec kernel Vu+ multiboot
	else:
		MbootList = ("/dev/mmcblk0p1", "/dev/mmcblk1p1", "/dev/mmcblk0p3", "/dev/mmcblk0p4", "/dev/mtdblock2", "/dev/block/by-name/bootoptions", "/dev/block/by-name/others", "/dev/block/by-name/startup")
		cachedDevice = fileReadLine(MBBOOTDEVICE_CACHE)
		if cachedDevice and cachedDevice in MbootList:  # try the device found on a previous boot first, avoiding a probe of every candidate again
			print(f"[multiboot][getMultiboots] using cachedDevice:{cachedDevice} in MbootList")
			MbootList = (cachedDevice, ) + tuple(device for device in MbootList if device != cachedDevice)
	for device in MbootList:
		if bootslots:  # if bootslots is populated, the correct device has already been found so abort search
			break

		print(f"[multiboot][getMultibootslots]device:{device}")
		if not path.exists(device):
			continue

		print(f"[multiboot][getMultibootslots]root:{MTDROOTFS} device:{device} UBIMB:{UBIMB} CHKROOTMB:{CHKROOTMB}")
		_mount(device, tmpdir)

		if not path.isfile(path.join(tmpdir, "STARTUP")):  # Not Multiboot receiver
			_unmount(tmpdir)
			continue

		print(f"[multiboot][getMultibootslots]device:{device} found STARTUP")
		STARTUP = fileReadLine(path.join(tmpdir, "STARTUP"))
		print(f"[multiboot][getMultibootslots] STARTUP:{STARTUP}")
		if SystemInfo["HasKexecMultiboot"] and not path.isfile(dest := path.join(tmpdir, "etc/init.d/kexec-multiboot-recovery")) and path.isfile("/etc/init.d/kexec-multiboot-recovery"):  # check Recovery & slot image for recovery script
			if path.isfile(etc_issue := path.join(tmpdir, "etc/issue")):
				try:
					Creator = open(etc_issue).readlines()[-2].lower().split(maxsplit=1)[0]
				except IndexError:  # /etc/issue non standard file content
					Creator = ""
				if Creator in ("openvix", "openbh"):
					copyfile("/etc/init.d/kexec-multiboot-recovery", dest)
		# print(f"[multiboot][getMultibootslots]1 bootargs?: {path.exists('/sys/firmware/devicetree/base/chosen/bootargs')}")
		SystemInfo["MBbootdevice"] = resolveDevice(device)  # used in SystemInfo
		SystemInfo["BootDevice"] = SystemInfo["MBbootdevice"].rsplit("/", 1)[1]  # used by About
		saveBootDevice(device)  # the (unresolved) MbootList entry that matched, cached by saveBootDevice
		print(f"[Multiboot][[getMultibootslots]2 *** Bootdevice found: {SystemInfo['BootDevice']} CHKROOTMB:{CHKROOTMB} MBbootdevice:{SystemInfo['MBbootdevice']} device:{device}")
		if path.exists("/sys/firmware/devicetree/base/chosen/bootargs") or CHKROOTMB:  # check validity for multiboot
			for file in glob.glob(path.join(tmpdir, "STARTUP_*")):
				slotnumber = file.rsplit("_", 3 if "BOXMODE" in file else 1)[1]
				# slotname - WIP
				# slotname = file.rsplit("_", 3 if "BOXMODE" in file else 1)[0]
				# slotname = file.rsplit("/", 1)[1]
				# slotname = slotname if len(slotname) > 1 else ""
				slotname = ""  # nullify for current moment
				if "STARTUP_ANDROID" in file:
					SystemInfo["AndroidMode"] = True
					continue
				if "STARTUP_RECOVERY" in file:
					slotnumber = "0"
					SystemInfo["RecoveryMode"] = BOXTYPE != "gbquad4kpro"
				if "STARTUP_FLASH" in file:
					slotnumber = "0"

				if not slotnumber.isdigit():
					continue

				if int(slotnumber) in bootslots:
					continue

				slot = _parseStartupFile(file)
				print(f"[Multiboot][[getMultibootslots]3 slotnumber:{slotnumber} slot:{slot}")
				if slotnumber == "0":
					slot["slotType"] = "" if not UBIMB else "eMMC"
					slot["startupfile"] = path.basename(file)
				else:
					slot["slotType"] = "eMMC" if "root" in slot and "mmc" in slot["root"] else "USB"  # ("root" in slot) add to protected against possible crash... we dont know "root" was in the START file
				print(f"[Multiboot][[getMultibootslots]4 slotnumber:{slotnumber} slotType:{slot["slotType"]}")
				if SystemInfo["HasKexecMultiboot"] and int(slotnumber) > 3:
					SystemInfo["HasKexecUSB"] = True
				if "root" in slot:
					if "UUID=" in slot["root"]:	 # KexecMultiboot or UBIMB
						UUIDValue = slot["root"]
						slotx = getUUIDtoSD(slot["root"])
						if slotx is not None:
							slot["root"] = slotx
							UUID = slot["root"]
							UUIDnum += 1
						if not UBIMB:
							slot["kernel"] = f"/linuxrootfs{slotnumber}/zImage"
					if SystemInfo["HasNewMultiboot"] and slot.get("rootsubdir") and not path.exists(slot["root"]):  # the bootloader and Linux can number the same USB/SD/SATA partition differently
						slot["root"] = _findNewMBRoot(slot["rootsubdir"], slot["root"]) or slot["root"]
					if not (path.exists(slot["root"]) or slot["root"] in ("ubi0:ubifs", "ubi0:rootfs")):
						continue
					slot["startupfile"] = path.basename(file)
					slot["slotname"] = slotname
					if not UBIMB:
						SystemInfo["HasMultibootMTD"] = slot.get("mtd")
						SystemInfo["HasMultibootFlags"] = path.exists("/dev/block/by-name/flag")
					if SystemInfo["HasNewMultiboot"]:  # NewMB slots on USB/SD/SATA keep their rootsubdir
						slot.setdefault("rootsubdir", None)
						if slotnumber != "0":
							slot["slotType"] = _newMBSlotType(slot["root"])
					elif not SystemInfo["HasKexecMultiboot"] and not UBIMB and "sda" in slot["root"]:		# Not Kexec Vu+ receiver -- sf8008 type receiver with sd card, reset value as SD card slot has no rootsubdir
						slot["rootsubdir"] = None
						slot["slotType"] = "SDCARD"
					elif "STARTUP_RECOVERY" not in file:
						SystemInfo["HasRootSubdir"] = slot.get("rootsubdir")
					if "kernel" not in slot:
						if SystemInfo["HasNewMultiboot"]:
							slot["kernel"] = f"/dev/{MTDKERNEL}"  # NewMB slots share the internal kernel
						else:
							slot["kernel"] = f"{slot['root'].split('p')[0]}p{int(slot['root'].split('p')[1]) - 1}"  # oldstyle MB kernel = root-1
					bootslots[int(slotnumber)] = slot
				elif slotnumber == "0":
					bootslots[int(slotnumber)] = slot
		else:  # kernel corruption set corruption flag
			# print(f"[multiboot][getMultibootslots]3 bootargs?: {path.exists("/sys/firmware/devicetree/base/chosen/bootargs")}")
			SystemInfo["resetMBoot"] = True
			bootslots = {}
		_unmount(tmpdir)
	_unmountAndRemove(tmpdir)
	if bootslots:
		print(f"[multiboot][getMultibootslots] bootslots: {bootslots}")
		if SystemInfo["HasNewMultiboot"]:
			SystemInfo["HasRootSubdir"] = any(slot.get("rootsubdir") for slot in bootslots.values())
			SystemInfo["MultiBootSlot"] = getNewMultibootSlot(bootslots)
			print(f"[Multiboot][MultiBootSlot]3 NewMB current slot used:{SystemInfo['MultiBootSlot']}")
		elif not CHKROOTMB:
			bootArgs = open("/sys/firmware/devicetree/base/chosen/bootargs", "r").read()
			print(f"[multiboot][getMultibootslots]4 bootArgs: {bootArgs}")
			if SystemInfo["HasKexecMultiboot"] and SystemInfo["HasRootSubdir"]:							# Kexec Vu+ receiver
				rootsubdir = [x for x in bootArgs.split() if x.startswith("rootsubdir")]
				char = "/" if "/" in rootsubdir[0] else "="
				SystemInfo["MultiBootSlot"] = int(rootsubdir[0].rsplit(char, 1)[1][11:])
				SystemInfo["VuUUIDSlot"] = (UUID, UUIDnum) if UUIDnum != 0 else ""
			elif SystemInfo["HasMultibootFlags"]:  # Qviart Dual 4K
				with open('/dev/block/by-name/flag', 'rb') as f:
					struct_fmt = "B"
					flag = f.read(struct.calcsize(struct_fmt))
					slot = struct.unpack(struct_fmt, flag)
					SystemInfo["MultiBootSlot"] = int(slot[0])  # needs to be tested so this comment can be removed.
			elif bootArgs and SystemInfo["HasRootSubdir"] and "root=/dev/sda" not in bootArgs and not UBIMB:							# RootSubdir receiver or sf8008 receiver with root in eMMC slot
				slot = [x[-1] for x in bootArgs.split() if x.startswith("rootsubdir")]
				SystemInfo["MultiBootSlot"] = int(slot[0])
			else:
				root = dict([(x.split("=", 1)[0].strip(), x.split("=", 1)[1].strip()) for x in bootArgs.strip().split(" ") if "=" in x])["root"]  # Broadband receiver (e.g. gbue4k) or sf8008 with sd card as root/kernel pair
				for slot in bootslots:
					if "root" not in bootslots[slot]:
						continue
					if bootslots[slot]["root"] == root:
						SystemInfo["MultiBootSlot"] = slot
						print(f"[Multiboot][MultiBootSlot]2 current slot used:{SystemInfo['MultiBootSlot']}")
						break
		else:
			if UBIMB:
				SystemInfo["VuUUIDSlot"] = (UUID, UUIDnum, UUIDValue) if UUIDnum != 0 else ""
			SystemInfo["MultiBootSlot"] = 0 if "linuxrootfs" not in STARTUP else int(STARTUP.replace("\n", "").replace(" rootfstype=ext4", "").split("linuxrootfs")[1])
	print(f"[multiboot][getMultibootslots] bootslots: {bootslots} Activeslot:{SystemInfo['MultiBootSlot']}")
	return bootslots


def saveBootDevice(device):
	# persist the multiboot device found this boot, so future boots can try it first instead of probing every MbootList candidate again
	print(f"[multiboot][saveBootDevice] device:{device}")
	if device and device != fileReadLine(MBBOOTDEVICE_CACHE):  # only write when changed, to avoid a flash write on every boot
		try:
			with open(MBBOOTDEVICE_CACHE, "w") as f:
				f.write(device)
		except OSError as err:
			print(f"[multiboot][saveBootDevice] {err}")


NEWMB_STARTUP = re.compile(r"(STARTUP(?:_LINUX)?_)(\d+)((?:_BOXMODE_\d+)?)")  # the STARTUP file names the NewMB initramfs looks up for a slot
NEWMB_FILESYSTEMS = ("ext2", "ext3", "ext4")
NEWMB_MIN_FREE_MB = 1024


def getFilesystemType(device):
	try:
		return _run(["/sbin/blkid", "-o", "value", "-s", "TYPE", device]).stdout.decode(errors="ignore").strip()
	except OSError:
		return ""


def getNewMultibootSlotDevices():
	# mounted ext2/3/4 partitions outside the boot disk that can hold extra NewMB slots
	internal = _parentDevice(path.basename(SystemInfo["MBbootdevice"]))
	devices = {}
	for line in fileReadLines("/proc/mounts", default=[]):
		fields = line.split()
		if len(fields) < 3 or not fields[0].startswith("/dev/") or fields[2] not in NEWMB_FILESYSTEMS:
			continue
		name = path.basename(path.realpath(fields[0]))
		if not path.exists(f"/sys/class/block/{name}") or f"/dev/{name}" in devices or _parentDevice(name) == internal:  # pseudo names such as /dev/root are skipped
			continue
		try:
			stats = statvfs(fields[1].replace("\\040", " "))
		except OSError:
			continue
		devices[f"/dev/{name}"] = {"device": f"/dev/{name}", "mountpoint": fields[1], "freeMB": stats.f_bavail * stats.f_frsize // (1024 * 1024), "label": _partitionLabel(name)}
	return [devices[device] for device in sorted(devices)]


def _renderNewMBStartup(content, device, rootsubdir):
	# same edit the initramfs makes when it stores the selected slot: point root= and rootsubdir= at the slot
	if not re.search(r"(?<!\w)root=", content):
		return None
	content = re.sub(r"(?<!\w)root=[^\s'\"]*", lambda match: f"root={device}", content)
	if "rootsubdir=" in content:
		return re.sub(r"rootsubdir=[^\s'\"]*", lambda match: f"rootsubdir={rootsubdir}", content)
	return content.replace(f"root={device}", f"root={device} rootsubdir={rootsubdir}", 1)


def createNewMultibootSlots(device, count=4):
	# Add count slots on device by cloning the lowest slot's STARTUP files (kernel, boxmode variants and all) on the boot partition.
	# The numbers come from the files on the boot partition, so the STARTUP files of slots on devices that are not attached are never overwritten.
	# Returns the new slot numbers, or [] if nothing was created. ofgwrite creates the linuxrootfs<n> directories when an image is flashed.
	tmpdir = tempfile.mkdtemp(prefix="NewMBSlots")
	written = []
	_mount(SystemInfo["MBbootdevice"], tmpdir)
	try:
		startups = {}
		for name in listdir(tmpdir):
			match = NEWMB_STARTUP.fullmatch(name)
			if match:
				startups.setdefault(int(match.group(2)), []).append((name, match))
		if not startups:
			return []
		template = startups[min(startups)]
		first = max(startups) + 1
		files = {}
		for number in range(first, first + count):
			for name, match in template:
				with open(path.join(tmpdir, name)) as fd:
					content = _renderNewMBStartup(fd.read(), device, f"linuxrootfs{number}")
				if content is None:
					print(f"[multiboot][createNewMultibootSlots] no root= in {name}")
					return []
				files[f"{match.group(1)}{number}{match.group(3)}"] = content
		try:
			for name, content in files.items():
				with open(path.join(tmpdir, name), "w") as fd:
					fd.write(content)
				written.append(name)
		except OSError as err:
			print(f"[multiboot][createNewMultibootSlots] {err}")
			for name in written:
				try:
					os_remove(path.join(tmpdir, name))
				except OSError:
					pass
			return []
		sync()
		return list(range(first, first + count))
	finally:
		_unmountAndRemove(tmpdir)


def _sgdisk():
	return next((tool for tool in ("/usr/sbin/sgdisk", "/sbin/sgdisk") if fileExists(tool)), None)


def _isGPTDisk(disk):
	# sgdisk converts an MBR disk to GPT when it saves, so only ever name partitions on a disk that is already GPT
	sectorSize = int(fileReadLine(f"/sys/class/block/{path.basename(disk)}/queue/logical_block_size", default="512") or 512)
	try:
		with open(disk, "rb") as fd:
			fd.seek(sectorSize)  # the GPT header is in LBA 1
			return fd.read(8) == b"EFI PART"
	except OSError:
		return False


def _gptPartition(device):
	# (disk device, partition number) for a partition on a GPT disk, otherwise None
	name = path.basename(path.realpath(device))
	number = fileReadLine(f"/sys/class/block/{name}/partition")
	disk = f"/dev/{_parentDevice(name)}"
	if number and number.isdigit() and _isGPTDisk(disk):
		return disk, int(number)
	return None


def _gptName(disk, number):
	# the name stored in the GPT, unlike the kernel's copy this is current even right after a rename
	try:
		output = _run([_sgdisk(), "-i", str(number), disk]).stdout.decode(errors="ignore")
	except OSError:
		return None
	match = re.search(r"Partition name: '(.*)'", output)
	return match.group(1) if match else None


def canNameNewMultibootPartition(device):
	return _sgdisk() is not None and _gptPartition(device) is not None


def getNewMultibootPartitionName(device):
	target = _gptPartition(device) if _sgdisk() else None
	name = _gptName(*target) if target else None
	return _partitionLabel(device) if name is None else name


def nameNewMultibootPartition(device, name="rootfs"):
	# Give a partition on a GPT disk a name the NewMB initramfs recognises so it can still find the slots after a device is renumbered.
	# Only the name in the GPT changes. Returns True once the new name reads back.
	target = _gptPartition(device)
	tool = _sgdisk()
	if not target or not tool:
		return False
	disk, number = target
	try:
		_run([tool, "-c", f"{number}:{name}", disk])
	except OSError as err:
		print(f"[multiboot][nameNewMultibootPartition] {err}")
		return False
	named = _gptName(disk, number) == name
	print(f"[multiboot][nameNewMultibootPartition] device:{device} disk:{disk} partition:{number} name:{name} named:{named}")
	return named


def removeNewMultibootSlots(slots):
	# Remove the STARTUP files of slots whose device has just been erased, so they do not linger on the boot partition.
	# Only numbered slot files are touched, never STARTUP itself or the recovery, flash and android files, and nothing is removed
	# if that would leave no numbered slot to clone new ones from. Returns the slot numbers whose files were all removed.
	wanted = {slot for slot in slots if slot > 0}
	if not wanted:
		return []
	tmpdir = tempfile.mkdtemp(prefix="NewMBRemove")
	_mount(SystemInfo["MBbootdevice"], tmpdir)
	try:
		files = {}
		for name in listdir(tmpdir):
			match = NEWMB_STARTUP.fullmatch(name)
			if match:
				files.setdefault(int(match.group(2)), []).append(name)
		doomed = wanted & set(files)
		if not doomed or not set(files) - doomed:
			return []
		removed = []
		for number in sorted(doomed):
			try:
				for name in files[number]:
					os_remove(path.join(tmpdir, name))
				removed.append(number)
			except OSError as err:
				print(f"[multiboot][removeNewMultibootSlots] slot {number}: {err}")
		sync()
		return removed
	finally:
		_unmountAndRemove(tmpdir)


NEWMB_MIN_DISK_MB = 2048
# ext4 features the 4.x kernels of these receivers mount. Named explicitly because newer mke2fs defaults add ones they cannot, e.g. orphan_file needs kernel 5.15
NEWMB_MKFS_FEATURES = "none,has_journal,ext_attr,resize_inode,dir_index,filetype,extent,flex_bg,sparse_super,large_file,huge_file,dir_nlink,extra_isize"


def _partitionNode(disk):
	return f"{disk}p1" if path.basename(disk).startswith(("mmcblk", "nvme")) else f"{disk}1"


def _partitionCommands(disk):
	sgdisk = _sgdisk()
	return [f"{sgdisk} -Z {disk}", f"{sgdisk} -o {disk}", f"{sgdisk} -n 1:0:0 -t 1:8300 -c 1:rootfs {disk}"]


def _mkfsCommand(partition):
	return f"/sbin/mkfs.ext4 -F -m1 -L rootfs -O {NEWMB_MKFS_FEATURES} {partition}"


def getNewMultibootPrepareDevices():
	# whole external disks that can be erased and prepared for slots. The boot disk and the disk holding the running root are never offered
	if not _sgdisk() or not fileExists("/sbin/mkfs.ext4"):
		return []
	busy = {_parentDevice(path.basename(SystemInfo["MBbootdevice"]))}
	rootDevice = _parseRootMount(fileReadLines("/proc/self/mountinfo", default=[]))[0]
	if rootDevice:
		busy.add(_parentDevice(path.basename(path.realpath(rootDevice))))
	mounts = {}
	for line in fileReadLines("/proc/mounts", default=[]):
		fields = line.split()
		if len(fields) > 1 and fields[0].startswith("/dev/"):
			mounts.setdefault(path.basename(path.realpath(fields[0])), fields[1].replace("\\040", " "))
	slots = SystemInfo["canMultiBoot"] or {}
	disks = []
	for sysdir in sorted(glob.glob("/sys/class/block/*")):
		name = path.basename(sysdir)
		if not re.fullmatch(r"sd[a-z]+|mmcblk\d+", name) or name in busy:
			continue
		sizeMB = int(fileReadLine(f"{sysdir}/size", default="0") or 0) * 512 // (1024 * 1024)
		if sizeMB < NEWMB_MIN_DISK_MB:
			continue
		partitions = [part for part in sorted(listdir(sysdir)) if part.startswith(name) and path.exists(f"{sysdir}/{part}/partition")]
		disks.append({
			"disk": f"/dev/{name}",
			"sizeMB": sizeMB,
			"model": (fileReadLine(f"{sysdir}/device/model", default="") or fileReadLine(f"{sysdir}/device/name", default="") or "").strip(),
			"bus": _busName(name),
			"partitions": [(f"/dev/{part}", mounts.get(part, "")) for part in partitions],
			"slots": sorted(slot for slot, data in slots.items() if _parentDevice(path.basename(data.get("root", ""))) == name)
		})
	return disks


def getNewMultibootPrepareCommands(disk, partitions):
	# The Console screen carries on after a failed command, so everything from wiping the disk to formatting is one && chain: a failed step means nothing after it runs
	partition = _partitionNode(disk)
	nomount = " ".join(f"/dev/nomount.{path.basename(device)}" for device in (disk, partition))  # keeps the hotplug automounter away while the disk is rewritten
	commands = [f"touch {nomount}"]
	if partitions:
		commands.append(f"for n in {' '.join(partitions)}; do swapoff $n; umount -lf $n; done > /dev/null 2>&1")
	steps = _partitionCommands(disk) + [
		f"(/usr/sbin/partprobe {disk} || hdparm -z {disk})",
		f"{{ for i in 1 2 3 4 5 6 7 8 9 10; do [ -b {partition} ] && break; sleep 1; done; [ -b {partition} ]; }}",
		_mkfsCommand(partition),
		"sync"
	]
	commands.append(" && ".join(steps))
	commands.append(f"rm -f {nomount}")
	return commands


def verifyNewMultibootPartition(disk):
	# the partition the prepare commands should have left behind, judged from the disk rather than from exit codes
	partition = _partitionNode(disk)
	if path.exists(partition) and _gptName(disk, 1) == "rootfs" and getFilesystemType(partition).startswith("ext"):
		return partition
	return None


def getUUIDtoSD(UUID):  # returns None on failure
	if not fileExists("/sbin/blkid"):
		return None
	try:
		lines = subprocess.check_output(["/sbin/blkid"]).decode(encoding="utf8", errors="ignore").split("\n")
	except subprocess.CalledProcessError as err:
		print(f"[multiboot][getUUIDtoSD] {err}")
		return None
	for line in lines:
		if UUID in line.replace('"', ''):
			return line.split(":")[0].strip()
	return None


def resolveDevice(devicepath):
	if path.islink(devicepath):
		return path.realpath(devicepath)
	else:
		return devicepath


# NewMB (native multiboot) helpers. The NewMB initramfs takes root= and rootsubdir= from STARTUP, binds
# the subdir as the root filesystem and writes /.newMB. Slots can be on internal or external partitions.
NEWMB_ROOT_LABELS = ("linuxrootfs", "rootfs", "userdata", "linuxdata", "data")  # GPT partition names that can hold slot subdirs


def _parentDevice(name):
	return re.sub(r"p\d+$" if name.startswith(("mmcblk", "nvme")) else r"\d+$", "", name)


def _partitionLabel(device):
	for line in fileReadLines(f"/sys/class/block/{path.basename(device)}/uevent", default=[]):
		if line.startswith("PARTNAME="):
			return line.split("=", 1)[1].strip()
	return ""


def _slotFromName(name):
	# slots are named after their rootsubdir or partition label: [linux]rootfs<n>, plain [linux]rootfs being slot 1
	match = re.fullmatch(r"(?:linux)?rootfs(\d*)", name or "")
	return int(match.group(1) or 1) if match else None


def _newMBSlotType(device):
	name = path.basename(device)
	if _parentDevice(name) == _parentDevice(path.basename(SystemInfo["MBbootdevice"])):
		return "eMMC"  # on the same disk as the boot partition
	return _busName(name)


def _busName(name):
	bus = path.realpath(f"/sys/class/block/{name}")
	if "/usb" in bus:
		return "USB"
	if "/ata" in bus:
		return "SATA"
	return "SDCARD" if name.startswith("mmcblk") else "USB"


def _findNewMBRoot(rootsubdir, requestedRoot):
	# Like the initramfs does, find the partition that really holds rootsubdir when the requested root has been renumbered or is missing
	tmpdir = tempfile.mkdtemp(prefix="NewMBRoot")
	found = None
	for sysdir in sorted(glob.glob("/sys/class/block/*/partition")):
		device = f"/dev/{sysdir.split('/')[4]}"
		label = _partitionLabel(device)
		if device == requestedRoot or not label.startswith(NEWMB_ROOT_LABELS):
			continue
		_run(["mount", "-o", "ro", device, tmpdir])
		found = device if path.isdir(path.join(tmpdir, rootsubdir)) else None
		_unmount(tmpdir)
		if found:
			break
	_unmountAndRemove(tmpdir)
	print(f"[multiboot][_findNewMBRoot] rootsubdir:{rootsubdir} requestedRoot:{requestedRoot} found:{found}")
	return found


def _parseRootMount(lines):
	# returns (source device, subdir the mount was bound from) of "/" using /proc/self/mountinfo lines
	device, subdir = None, ""
	for line in lines:
		head, _dash, tail = line.partition(" - ")
		fields = head.split()
		info = tail.split()
		if len(fields) > 4 and fields[4] == "/" and len(info) > 1 and info[0] != "rootfs":
			device, subdir = info[1], fields[3].strip("/")
	return device, subdir


def _matchNewMBSlot(bootslots, device, subdir):
	sameDevice = lambda a, b: bool(a and b) and path.realpath(a) == path.realpath(b)  # noqa: E731
	if subdir:
		matches = [slot for slot, data in bootslots.items() if data.get("rootsubdir") == subdir]
		if len(matches) > 1:
			matches = [slot for slot in matches if sameDevice(bootslots[slot].get("root"), device)] or matches
		if matches:
			return matches[0]
		return next((slot for slot in (_slotFromName(subdir),) if slot in bootslots), None)
	for slot, data in bootslots.items():
		if not data.get("rootsubdir") and sameDevice(data.get("root"), device):
			return slot
	return next((slot for slot in (_slotFromName(_partitionLabel(device)),) if slot in bootslots), None)


def getNewMultibootSlot(bootslots):
	# The initramfs can fall back to another slot or renumbered device, so the mounted root is more reliable than the command line
	device, subdir = _parseRootMount(fileReadLines("/proc/self/mountinfo", default=[]))
	mounted = device is not None and device.startswith("/dev/")
	if not mounted:
		cmdline = dict(item.split("=", 1) for item in (fileReadLine("/proc/cmdline", default="") or "").split() if "=" in item)
		device, subdir = cmdline.get("root"), cmdline.get("rootsubdir", "")
	if not device:
		return None
	slot = _matchNewMBSlot(bootslots, device, subdir)
	if slot is not None and mounted:
		bootslots[slot]["root"] = device  # the running slot's real device, whatever name the STARTUP file used
	return slot


def getNewMultibootFlashOptions(slot):
	# ofgwrite options to flash a NewMB slot, or None if ofgwrite can't address it. Slots share a kernel device, so only the lowest slot using it may rewrite it
	slots = SystemInfo["canMultiBoot"]
	data = slots[slot]
	options = [f"-r{path.basename(data['root'])}"]
	kernel = data.get("kernel")
	if kernel and slot == min(number for number, item in slots.items() if number and item.get("kernel") == kernel):
		options.append(f"-k{path.basename(kernel)}")
	rootsubdir = data.get("rootsubdir")
	if rootsubdir:
		prefix = rootsubdir.rstrip("0123456789")
		if rootsubdir != f"{prefix}{slot}":  # ofgwrite builds the directory name from the slot number
			return None
		options.append(f"-m{slot}")
		if prefix != "linuxrootfs":
			options.append(f"-s{prefix}")
	else:
		options.append("-m0")  # a whole partition, flashed without the rootsubdir check
	if slot == SystemInfo["MultiBootSlot"]:
		options.append("-f")  # ofgwrite judges the running slot from /proc/cmdline, so make sure it stops enigma2 when it is ours
	return " ".join(options)


def GetCurrentImageMode():
	if SystemInfo["canMultiBoot"] and SystemInfo["canMode12"]:
		bootargs = open("/sys/firmware/devicetree/base/chosen/bootargs", "r").read()
		if (r := re.search(r"\bboxmode=(\d+)\b", bootargs)):
			return int(r.group(1))


def GetImagelist(Recovery=None):
	Imagelist = {}
	tmpdir = tempfile.mkdtemp(prefix="GetImagelist")
	from Components.config import config		# here to prevent boot loop
	slotRoot = ""
	for slot in sorted(list(SystemInfo["canMultiBoot"].keys())):
		if slot == 0:
			if UBIMB:
				continue
			elif not Recovery:		# called by ImageManager
				continue
			else:					# called by MultiBootSelector
				Imagelist[slot] = {"imagename": _("Recovery Mode")}
				continue
		BuildVersion = "  "
		Imagelist[slot] = {"imagename": _("Empty slot")}
		imagedir = "/"
		if SystemInfo["MultiBootSlot"] != slot or SystemInfo["HasHiSi"]:
			print(f"[multiboot][GetImagelist] SystemInfo['canMultiBoot'][slot]['root']:{SystemInfo['canMultiBoot'][slot]['root']}")
			if SystemInfo['canMultiBoot'][slot]['root'] != slotRoot:
				print(f"[multiboot][GetImagelist] slotRoot]:{slotRoot}")
				_unmount(tmpdir)
				slotRoot = SystemInfo['canMultiBoot'][slot]['root']
				_mount(SystemInfo['canMultiBoot'][slot]['root'], tmpdir, ubifs=SystemInfo["HasMultibootMTD"])
			imagedir = _imageDir(tmpdir, slot)
		print(f"[multiboot][GetImagelist] imagedir:{imagedir}")
		if path.isfile(path.join(imagedir, "usr/bin/enigma2")):
			if path.isfile(path.join(imagedir, "usr/lib/enigma.info")):
				print("[multiboot] [GetImagelist] using enigma.info")
				BuildVersion = createInfo(slot, imagedir=imagedir)
			else:
				print("[multiboot] [GetImagelist] using etc/issue")
				BuildVersion = _legacyImageName(imagedir)
			if SystemInfo["HasKexecMultiboot"] and Recovery and config.usage.bootlogo_identify.value:
				bootmviSlot(imagedir=imagedir, text=BuildVersion, slot=slot)
			Imagelist[slot] = {"imagename": f"{BuildVersion}"}
		elif path.isfile(path.join(imagedir, "usr/bin/enigmax")):
			Imagelist[slot] = {"imagename": _("Deleted image")}
		else:
			Imagelist[slot] = {"imagename": _("Empty slot")}
	_unmountAndRemove(tmpdir)
	return Imagelist


def createInfo(slot, imagedir="/"):
	BoxInfo = BoxInformation(root=imagedir) if SystemInfo["MultiBootSlot"] != slot else BoxInfoRunningInstance
	Creator = (distro := str(BoxInfo.getItem("displaydistro", ""))) and (distro := distro.split()[0]) and distro[:1].upper() + distro[1:] or str(BoxInfo.getItem("distro", "")).capitalize()
	BuildImgVersion = str(BoxInfo.getItem("imgversion", "")).replace("-release", "")  # replace("-release", "") for PLi 9.0
	BuildType = str(BoxInfo.getItem("imagetype", "rel"))
	if BuildType.lower().startswith("dev"):
		BuildType = BuildType[:3]
	BuildDev = str(idb).zfill(3) if Creator.lower().startswith(("openvix", "openpli")) and BuildType and not BuildType.lower().startswith("rel") and (idb := BoxInfo.getItem("imagedevbuild")) else ""
	if BuildType.lower().startswith("rel"):
		BuildType = ""  # don't bother displaying "release" in the interface as this is the default image type
	elif (iv := BoxInfo.getItem("imgversion")) and BoxInfo.getItem("imagetype") == iv:
		BuildType = ""  # do not display anything if "imagetype" and "imgversion" are identical
	BuildVer = str(BoxInfo.getItem("imagebuild", ""))
	CompileDate = str(BoxInfo.getItem("compiledate", ""))

	try:  # checking for valid YYYYMMDD format date in BuildVer, if so, don't display it
		if BuildVer and (CompileDate == BuildVer or len(BuildVer) == 8 and BuildVer.startswith("20") and BuildVer.isnumeric() and datetime.strptime(BuildVer, '%Y%m%d')):
			BuildVer = ""
	except (TypeError, ValueError):
		pass

	if BuildVer and len(BuildVer) == 3 and BuildVer.isnumeric():
		BuildImgVersion = BuildImgVersion + "." + BuildVer
		BuildVer = ""

	if BuildDev and len(BuildDev) == 3 and BuildDev.isnumeric():
		BuildImgVersion = BuildImgVersion + "." + BuildDev
		BuildDev = ""

	try:
		BuildDate = datetime.strptime(CompileDate, '%Y%m%d').strftime("%d-%m-%Y")
	except (TypeError, ValueError):  # sanity for enigma.info containing bad/no entry
		BuildDate = VerDate(imagedir)

	return " ".join([str(x).strip() for x in (Creator, BuildImgVersion, BuildType, BuildVer, BuildDev, f"({BuildDate})") if x and str(x).strip()])


def _legacyImageName(imagedir):
	date = VerDate(imagedir)
	try:
		Creator = open(f"{imagedir}/etc/issue").readlines()[-2].capitalize().strip()[:-6]
	except IndexError:  # /etc/issue no standard file content
		Creator = _("Unknown image")
	if SystemInfo["HasKexecMultiboot"] and path.isfile(path.join(imagedir, "etc/vtiversion.info")):
		Vti = open(path.join(imagedir, "etc/vtiversion.info")).read()
		Creator = Vti[0:3]
		Build = Vti[-8:-1]
		BuildVersion = f"{Creator} {Build} ({date}) "
	else:
		Creator = Creator.replace("-release", " ")
		BuildVersion = f"{Creator} ({date})"
	return BuildVersion


def VerDate(imagedir):
	def mtime(fpath):
		return fileExists(file := path.join(imagedir, fpath)) and int(stat(file).st_mtime) or 0
	return datetime.fromtimestamp(max(mtime("var/lib/opkg/status"), mtime("usr/bin/enigma2"), mtime("usr/share/bootlogo.mvi"))).strftime("%d-%m-%Y")


def emptySlot(slot):
	imagedir, tmpdir = _mountSlot(slot)
	if path.isfile(path.join(imagedir, "usr/bin/enigma2")):
		rename(path.join(imagedir, "usr/bin/enigma2"), path.join(imagedir, "usr/bin/enigmax"))
		ret = 0
	else:
		ret = 4  # NO enigma2 found to rename
	_unmountAndRemove(tmpdir)
	return ret


def bootmviSlot(imagedir="/", text=" ", slot=0):
	inmviPath = path.join(imagedir, "usr/share/bootlogo.mvi")
	outmviPath = path.join(imagedir, "usr/share/enigma2/bootlogo.mvi")
	txtPath = path.join(imagedir, "usr/share/enigma2/bootlogo.txt")
	tmpBootLogo = "/tmp/bootlogo.m1v"
	tmpEditedLogo = "/tmp/mypicture.m1v"
	outpng = "/tmp/out1.png"
	text = f"booting slot {slot} {text}"
	if path.exists(inmviPath):
		if path.exists(outmviPath) and path.exists(txtPath) and open(txtPath).read() == text:
			return

		from PIL import Image, ImageDraw, ImageFont

		_run(["cp", inmviPath, tmpBootLogo])

		_run([
			"ffmpeg",
			"-skip_frame", "nokey",
			"-i", tmpBootLogo,
			"-vsync", "0",
			"-y",
			outpng
		])

		_run(["rm", "-f", tmpEditedLogo])  # remove old junk before using this location

		if path.exists(outpng):
			img = Image.open(outpng)						# Open an Image
		else:
			return
		I1 = ImageDraw.Draw(img)									# Call draw Method to add 2D graphics in an image
		myFont = ImageFont.truetype("/usr/share/fonts/OpenSans-Regular.ttf", 65)		# Custom font style and font size
		I1.text((52, 12), text, font=myFont, fill=(255, 0, 0))		# Add Text to an image
		I1.text((50, 10), text, font=myFont, fill=(255, 255, 255))
		img.save(outpng)									# Save the edited image

		_run([
			"ffmpeg",
			"-i", outpng,
			"-r", "25",
			"-b", "20000",
			"-y",
			tmpEditedLogo
		])

		_run(["cp", tmpEditedLogo, outmviPath])

		with open(txtPath, "w") as f:
			f.write(text)


def restoreSlots():
	for slot in SystemInfo["canMultiBoot"]:
		imagedir, tmpdir = _mountSlot(slot)
		if path.isfile(path.join(imagedir, "usr/bin/enigmax")):
			rename(path.join(imagedir, "usr/bin/enigmax"), path.join(imagedir, "usr/bin/enigma2"))
		_unmountAndRemove(tmpdir)


def isFat32(device):
	try:
		with open(device, "rb") as fd:
			bootSector = fd.read(512)
			fsType = bootSector[82:90].decode("ascii", errors="ignore").strip()
			return fsType == "FAT32" or int.from_bytes(bootSector[36:40], "little") != 0
	except Exception:
		return False

# helper functions


def _parseStartupFile(file):
	line = open(file).read() \
		.replace("'", "") \
		.replace('"', "") \
		.replace("\n", " ") \
		.replace("ubi.mtd", "mtd") \
		.replace("bootargs=", "")

	return {
		x.split("=", 1)[0].strip(): x.split("=", 1)[1].strip()
		for x in line.split()
		if "=" in x
	}


def _run(cmd):
	"""Run cmd via subprocess, logging stderr on non-zero exit."""
	result = subprocess.run(cmd, capture_output=True, check=False)
	if result.returncode != 0:
		print(f"[multiboot] {' '.join(cmd)} failed: {result.stderr.decode(errors='ignore').strip()}")
	return result


def _mount(device, mountpoint, ubifs=False):
	cmd = ["mount"]
	if ubifs:
		cmd += ["-t", "ubifs"]
	cmd += [device, mountpoint]
	_run(cmd)


def _mountSlot(slot):
	mountpoint = tempfile.mkdtemp(prefix="multibootSlot")
	root = SystemInfo['canMultiBoot'][slot]['root']
	_mount(root, mountpoint, ubifs=SystemInfo["HasMultibootMTD"])
	return _imageDir(mountpoint, slot), mountpoint


def _unmount(mountpoint):
	if not mountpoint:
		return
	while path.ismount(mountpoint):
		result = _run(["umount", mountpoint])
		if result.returncode != 0:
			break


def _unmountAndRemove(mountpoint):
	_unmount(mountpoint)
	if mountpoint and not path.ismount(mountpoint):
		rmdir(mountpoint)


def _imageDir(mountroot, slot):
	return sep.join([_f for _f in [mountroot, SystemInfo["canMultiBoot"][slot].get("rootsubdir", "")] if _f])
# 	end helper functions


# 	following added for OpenWebif canMultiBoot getCurrentSlotAndBootCodes getSlotImageList getBootCodeDescription activateSlot
def canMultiBoot():
	# print(f"[multiboot][canMultiBoot] ")
	return bool(SystemInfo["canMultiBoot"])


def getCurrentSlotAndBootCodes():
	bootCode = " "
	print(f"[MultiBoot][getCurrentSlotAndBootCodes] bootSlot:{SystemInfo['MultiBootSlot']} bootCode:{bootCode}")
	return SystemInfo["MultiBootSlot"], bootCode


def getSlotImageList(callback):
	imageList = GetImagelist()
	print(f"[MultiBoot][getSlotImageLists] keys:{imageList.keys()} {imageList}")
	callback(imageList)


def getBootCodeDescription(bootCode=None):
	bootCodeDescriptions = {
		"": _("Normal: No boot modes required."),
		"1": _("Mode 1: Supports Kodi but PiP may not work"),
		"12": _("Mode 12: Supports PiP but Kodi may not work")
	}
	if bootCode is None:
		return bootCodeDescriptions
	return bootCodeDescriptions.get(bootCode, "")


def activateSlot(slotCode, bootCode, callback):
	print(f"[MultiBoot][activateSlot] slotCode:{slotCode} bootCode:{bootCode}")
	slot = int(slotCode)
	tmpdir = tempfile.mkdtemp(prefix="Webif_Multiboot")
	_mount(SystemInfo['MBbootdevice'], tmpdir)
	copyfile(path.join(tmpdir, SystemInfo["canMultiBoot"][slot]["startupfile"]), path.join(tmpdir, "STARTUP"))
	if SystemInfo["HasMultibootMTD"]:
		with open('/dev/block/by-name/flag', 'wb') as f:
			f.write(struct.pack("B", int(slotCode)))
	_unmountAndRemove(tmpdir)
	callback(0, 0)
