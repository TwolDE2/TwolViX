from __future__ import absolute_import

from time import time
from twisted.internet import threads

from enigma import eDBoxLCD, eTimer, iPlayableService, pNavigation, iServiceInformation
from boxbranding import getBoxType, getMachineBuild
from Components.config import config
from Components.ParentalControl import parentalControl
from Components.ServiceEventTracker import ServiceEventTracker
from Components.SystemInfo import SystemInfo
from Tools.Directories import fileExists
import Components.RecordingConfig
import NavigationInstance

POLLTIME = 5 # seconds


def SymbolsCheck(session, **kwargs):
		global symbolspoller, POLLTIME
		if getMachineBuild() in ('viper4k', 'sf8008', 'gbmv200'):
			POLLTIME = 1
		symbolspoller = SymbolsCheckPoller(session)
		symbolspoller.start()


class SymbolsCheckPoller:
	def __init__(self, session):
		self.session = session
		self.blink = False
		self.led = "0"
		self.timer = eTimer()
		self.onClose = []
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
				iPlayableService.evUpdatedInfo: self.__evUpdatedInfo,
			})

	def __onClose(self):
		pass

	def start(self):
		if self.symbolscheck not in self.timer.callback:
			self.timer.callback.append(self.symbolscheck)
		self.timer.startLongTimer(0)

	def stop(self):
		if self.symbolscheck in self.timer.callback:
			self.timer.callback.remove(self.symbolscheck)
		self.timer.stop()

	def symbolscheck(self):
		threads.deferToThread(self.JobTask)
		self.timer.startLongTimer(POLLTIME)

	def JobTask(self):
		self.Recording()
		self.PlaySymbol()
		self.timer.startLongTimer(POLLTIME)

	def __evUpdatedInfo(self):
		self.service = self.session.nav.getCurrentService()
		self.Subtitle()
		self.ParentalControl()
		del self.service

	def Recording(self):
		if fileExists("/proc/stb/lcd/symbol_circle"):
			recordings = len(NavigationInstance.instance.getRecordings(False, Components.RecordingConfig.recType(config.recording.show_rec_symbol_for_rec_types.getValue())))
			if recordings > 0:
				open("/proc/stb/lcd/symbol_circle", "w").write("3")
			else:
				open("/proc/stb/lcd/symbol_circle", "w").write("0")
		elif SystemInfo["HasHiSi"] and fileExists("/proc/stb/fp/ledpowercolor"):
			import Screens.Standby
			recordings = len(NavigationInstance.instance.getRecordings(False, Components.RecordingConfig.recType(config.recording.show_rec_symbol_for_rec_types.getValue())))
			self.blink = not self.bli
			if recordings > 0: 
				if self.blink:
					open("/proc/stb/fp/ledpowercolor", "w").write("0")
					self.led = "1"
				else:
					if Screens.Standby.inStandby:
						open("/proc/stb/fp/ledpowercolor", "w").write(config.usage.lcd_ledstandbycolor.value)
					else:
						open("/proc/stb/fp/ledpowercolor", "w").write(config.usage.lcd_ledpowercolor.value)
					self.led = "0"
			elif self.led == "1":
				if Screens.Standby.inStandby:
					open("/proc/stb/fp/ledpowercolor", "w").write(config.usage.lcd_ledstandbycolor.value)
				else:
					open("/proc/stb/fp/ledpowercolor", "w").write(config.usage.lcd_ledpowercolor.value)
		else:
			if not fileExists("/proc/stb/lcd/symbol_recording") or not fileExists("/proc/stb/lcd/symbol_record_1") or not fileExists("/proc/stb/lcd/symbol_record_2"):
				return

			recordings = len(NavigationInstance.instance.getRecordings(False, Components.RecordingConfig.recType(config.recording.show_rec_symbol_for_rec_types.getValue())))

			if recordings > 0:
				open("/proc/stb/lcd/symbol_recording", "w").write("1")
				if recordings == 1:
					open("/proc/stb/lcd/symbol_record_1", "w").write("1")
					open("/proc/stb/lcd/symbol_record_2", "w").write("0")
				elif recordings >= 2:
					open("/proc/stb/lcd/symbol_record_1", "w").write("1")
					open("/proc/stb/lcd/symbol_record_2", "w").write("1")
			else:
				open("/proc/stb/lcd/symbol_recording", "w").write("0")
				open("/proc/stb/lcd/symbol_record_1", "w").write("0")
				open("/proc/stb/lcd/symbol_record_2", "w").write("0")

	def Subtitle(self):
		if not fileExists("/proc/stb/lcd/symbol_smartcard") and not fileExists("/proc/stb/lcd/symbol_subtitle"):
			return

		subtitle = self.service and self.service.subtitle()
		subtitlelist = subtitle and subtitle.getSubtitleList()

		if subtitlelist:
			subtitles = len(subtitlelist)
			if fileExists("/proc/stb/lcd/symbol_subtitle"):
				if subtitles > 0:
					f = open("/proc/stb/lcd/symbol_subtitle", "w")
					f.write("1")
					f.close()
				else:
					f = open("/proc/stb/lcd/symbol_subtitle", "w")
					f.write("0")
					f.close()
			else:
				if subtitles > 0:
					f = open("/proc/stb/lcd/symbol_smartcard", "w")
					f.write("1")
					f.close()
				else:
					f = open("/proc/stb/lcd/symbol_smartcard", "w")
					f.write("0")
					f.close()
		else:
			if fileExists("/proc/stb/lcd/symbol_subtitle"):
				f = open("/proc/stb/lcd/symbol_subtitle", "w")
				f.write("0")
				f.close()
			else:
				f = open("/proc/stb/lcd/symbol_smartcard", "w")
				f.write("0")
				f.close()

	def ParentalControl(self):
		if not fileExists("/proc/stb/lcd/symbol_parent_rating"):
			return

		service = self.session.nav.getCurrentlyPlayingServiceReference()

		if service:
			if parentalControl.getProtectionLevel(service.toCompareString()) == -1:
				open("/proc/stb/lcd/symbol_parent_rating", "w").write("0")
			else:
				open("/proc/stb/lcd/symbol_parent_rating", "w").write("1")
		else:
			open("/proc/stb/lcd/symbol_parent_rating", "w").write("0")

	def PlaySymbol(self):
		if not fileExists("/proc/stb/lcd/symbol_play"):
			return

		if SystemInfo["SeekStatePlay"]:
			file = open("/proc/stb/lcd/symbol_play", "w")
			file.write('1')
			file.close()
		else:
			file = open("/proc/stb/lcd/symbol_play", "w")
			file.write('0')
			file.close() 

	def PauseSymbol(self):
		if not fileExists("/proc/stb/lcd/symbol_pause"):
			return

		if SystemInfo["StatePlayPause"]:
			file = open("/proc/stb/lcd/symbol_pause", "w")
			file.write('1')
			file.close()
		else:
			file = open("/proc/stb/lcd/symbol_pause", "w")
			file.write('0')
			file.close()

	def PowerSymbol(self):
		if not fileExists("/proc/stb/lcd/symbol_power"):
			return

		if SystemInfo["StandbyState"]:
			file = open("/proc/stb/lcd/symbol_power", "w")
			file.write('0')
			file.close()
		else:
			file = open("/proc/stb/lcd/symbol_power", "w")
			file.write('1')
			file.close()

	def Resolution(self):
		if not fileExists("/proc/stb/lcd/symbol_hd"):
			return

		info = self.service and self.service.info()
		if not info:
			return ""

		videosize = int(info.getInfo(iServiceInformation.sVideoWidth))

		if videosize >= 1280:
			f = open("/proc/stb/lcd/symbol_hd", "w")
			f.write("1")
			f.close()
		else:
			f = open("/proc/stb/lcd/symbol_hd", "w")
			f.write("0")
			f.close()

	def Crypted(self):
		if not fileExists("/proc/stb/lcd/symbol_scrambled"):
			return

		info = self.service and self.service.info()
		if not info:
			return ""

		crypted = info.getInfo(iServiceInformation.sIsCrypted)

		if crypted == 1:
			f = open("/proc/stb/lcd/symbol_scrambled", "w")
			f.write("1")
			f.close()
		else:
			f = open("/proc/stb/lcd/symbol_scrambled", "w")
			f.write("0")
			f.close()

	def Teletext(self):
		if not fileExists("/proc/stb/lcd/symbol_teletext"):
			return

		info = self.service and self.service.info()
		if not info:
			return ""

		tpid = int(info.getInfo(iServiceInformation.sTXTPID))

		if tpid != -1:
			f = open("/proc/stb/lcd/symbol_teletext", "w")
			f.write("1")
			f.close()
		else:
			f = open("/proc/stb/lcd/symbol_teletext", "w")
			f.write("0")
			f.close()

	def Hbbtv(self):
		if not fileExists("/proc/stb/lcd/symbol_epg"):
			return

		info = self.service and self.service.info()
		if not info:
			return ""

		hbbtv = info.getInfoString(iServiceInformation.sHBBTVUrl)

		if hbbtv != "":
			f = open("/proc/stb/lcd/symbol_epg", "w")
			f.write("1")
			f.close()
		else:
			f = open("/proc/stb/lcd/symbol_epg", "w")
			f.write("0")
			f.close()

	def Audio(self):
		if not fileExists("/proc/stb/lcd/symbol_dolby_audio"):
			return
		      
		audio = self.service.audioTracks()
		if audio:
			n = audio.getNumberOfTracks()
			idx = 0
			while idx < n:
				i = audio.getTrackInfo(idx)
				description = i.getDescription()
				if "AC3" in description or "AC-3" in description or "DTS" in description:
					f = open("/proc/stb/lcd/symbol_dolby_audio", "w")
					f.write("1")
					f.close()
					return
				idx += 1
		f = open("/proc/stb/lcd/symbol_dolby_audio", "w")
		f.write("0")
		f.close()

	def Timer(self):
		if fileExists("/proc/stb/lcd/symbol_timer"):
			timer = NavigationInstance.instance.RecordTimer.getNextRecordingTime()
			if timer > 0:
				open("/proc/stb/lcd/symbol_timer", "w").write("1")
			else:
				open("/proc/stb/lcd/symbol_timer", "w").write("0")
