from os import chmod as oschmod
from time import time
# import traceback
from enigma import eTimer, eDVBLocalTimeHandler, eEPGCache
from Components.config import config
from Components.Console import Console
from Tools.StbHardware import setRTCtime


# _session = None
#


def AutoNTPSync(session=None, **kwargs):
	global ntpsyncpoller
	ntpsyncpoller = NTPSyncPoller()
	ntpsyncpoller.start()


class NTPSyncPoller:
	"""Automatically Poll NTP"""

	def __init__(self):
		# Init Timer
		self.timer = eTimer()
		self.Console = Console()

	def start(self):
		if self.timecheck not in self.timer.callback:
			# print('[NetworkTime] start set timer callback')
			self.timer.callback.append(self.timecheck)
		self.ntpConfigUpdated() # update NTP url, create if not exists
		# self.timer.startLongTimer(0)

	def stop(self):
		if self.timecheck in self.timer.callback:
			self.timer.callback.remove(self.timecheck)
		self.timer.stop()

	def timecheck(self):
		# print("[NetworkTime] timecheck() self", self)
		# traceback.print_stack()	
		if config.misc.SyncTimeUsing.value == "ntp":
			print('[NetworkTime] Updating from NTP')
			self.Console.ePopen('/usr/bin/ntpdate-sync', self.update_schedule)
		else:
			# print('[NetworkTime] self.update_schedule()')		
			self.update_schedule()

	def update_schedule(self, result=None, retval=None, extra_args=None):
		# print('[NetworkTime] update_schedule', retval, result)
		if retval and result:
			print("[NetworkTime] Error %d: Unable to synchronize the time!\n%s" % (retval, result.strip()))
		nowTime = time()
		if nowTime > 10000:
			print('[NetworkTime] ******** setting E2 time: ', config.misc.SyncTimeUsing.value, nowTime)
			# print('[NetworkTime] ******** timers NTP, default: ', config.misc.useNTPminutes.value, config.misc.useNTPminutes.default)			
			setRTCtime(nowTime)
			eDVBLocalTimeHandler.getInstance().setUseDVBTime(config.misc.SyncTimeUsing.value == "dvb")
			eEPGCache.getInstance().timeUpdated()
			self.timer.startLongTimer(int(config.misc.useNTPminutes.value if config.misc.SyncTimeUsing.value == "ntp" else config.misc.useNTPminutes.default) * 60)
		else:
			print('[NetworkTime] NO TIME SET')
			self.timer.startLongTimer(10)

	def ntpConfigUpdated(self):
		self.updateNtpUrl()
		# print("[NetworkTime][ntpConfigUpdated] issues timecheck()"
		self.timecheck()

	def updateNtpUrl(self):
		# update "/etc/default/ntpdate"
		# don't just overwrite...
		# only change the server url
		path = "/etc/default/ntpdate"
		server = 'NTPSERVERS="' + config.misc.NTPserver.value + '"'
		ntpdate = []
		try:
			content = open(path).read()
			if server in content:
				# print("[NetworkTime][updateNtpUrl] correct NTP url already set so exit")			
				return # correct NTP url already set so exit
			if "NTPSERVERS=" in content:
				ntpdate = content.split("\n")
		except:
			# print("[NetworkTime][updateNtpUrl] except failure")
			pass
		if ntpdate:
			print("[NetworkTime][updateNtpUrl] ntpdate found")
			for i, line in enumerate(ntpdate[:]):
				if "NTPSERVERS=" in line:
					ntpdate[i] = server
					break
		else:
			# print("[NetworkTime][updateNtpUrl] ntpdate is server blank")
			ntpdate = [server, ""]
		with open(path, "w") as f:
			f.write("\n".join(ntpdate))
		oschmod("/etc/default/ntpdate", 0o755)
