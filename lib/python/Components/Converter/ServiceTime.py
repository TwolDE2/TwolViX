from enigma import iServiceInformation, eServiceReference

from Components.Converter.Converter import Converter
from Components.Element import cached, ElementError


class ServiceTime(Converter):
	STARTTIME = 0
	ENDTIME = 1
	DURATION = 2

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "EndTime":
			self.type = self.ENDTIME
		elif type == "StartTime":
			self.type = self.STARTTIME
		elif type == "Duration":
			self.type = self.DURATION
		else:
			raise ElementError("'%s' is not <StartTime|EndTime|Duration> for ServiceTime converter" % type)

	@cached
	def getTime(self):
		service = self.source.service
		info = self.source.info

		if not info or not service:
			return None

		# directories and collections don't have a begin or end time
		if service.flags & (eServiceReference.isDirectory | eServiceReference.isGroup):
			return None

		if self.type == self.STARTTIME:
			return info.getInfo(service, iServiceInformation.sTimeCreate)
		elif self.type == self.ENDTIME:
			begin = info.getInfo(service, iServiceInformation.sTimeCreate)
			length = info.getLength(service)
			return begin + length
		elif self.type == self.DURATION:
			len = info.getLength(service)
			if len == -1:  # try to get duration from event
				ev = info.getEvent(service)
				if ev:
					len = ev.getDuration()
			return len + 10  # added 10 seconds to fix round to minutes

	time = property(getTime)
