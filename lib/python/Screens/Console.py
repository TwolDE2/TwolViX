from enigma import eConsoleAppContainer

from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Screens.Screen import Screen


class Console(Screen):
	def __init__(self, session, title="Console", cmdlist=None, finishedCallback=None, closeOnSuccess=False):
		Screen.__init__(self, session)

		self.finishedCallback = finishedCallback
		self.closeOnSuccess = closeOnSuccess
		self.errorOcurred = False

		self["text"] = ScrollLabel("")
		self["actions"] = ActionMap(["SetupActions", "NavigationActions"],
		{
			"ok": self.cancel,
			"cancel": self.cancel,
			"up": self["text"].pageUp,
			"pageUp": self["text"].firstPage,
			"left": self["text"].pageUp,
			"down": self["text"].pageDown,
			"right": self["text"].pageDown,
			"pageDown": self["text"].lastPage,
		}, prio=1)

		self.cmdlist = cmdlist
		self.newtitle = title

		self.onShown.append(self.updateTitle)

		self.container = eConsoleAppContainer()
		self.run = 0
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)  # dont start before gui is finished

	def updateTitle(self):
		self.setTitle(self.newtitle)

	def startRun(self):
		self["text"].setText(_("Execution progress:") + "\n\n")
		print("[Console] executing in run", self.run, " the command:", self.cmdlist[self.run])
		if self.container.execute(self.cmdlist[self.run]):  # start of container application failed...
			self.runFinished(-1)  # so we must call runFinished manual

	def runFinished(self, retval):
		if retval:
			self.errorOcurred = True
		self.run += 1
		if self.run != len(self.cmdlist):
			if self.container.execute(self.cmdlist[self.run]):  # start of container application failed...
				self.runFinished(-1)  # so we must call runFinished manual
		else:
			self["text"].appendText(_("Execution finished!!"))
			if self.finishedCallback is not None:
				self.finishedCallback()
			if not self.errorOcurred and self.closeOnSuccess:
				self.cancel()

	def cancel(self):
		if self.run == len(self.cmdlist):
			self.close()
			self.container.appClosed.remove(self.runFinished)
			self.container.dataAvail.remove(self.dataAvail)

	def dataAvail(self, output):
		# print("[Console][dataAvail] data is:", output)
		self["text"].appendText(output.decode())
