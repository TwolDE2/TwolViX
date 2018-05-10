from Components.ActionMap import HelpableNumberActionMap, HelpableActionMap
from Components.config import KEY_LEFT, KEY_RIGHT, KEY_HOME, KEY_END, KEY_0, KEY_DELETE, KEY_BACKSPACE, KEY_OK, KEY_TOGGLEOW, KEY_ASCII, KEY_TIMEOUT, KEY_NUMBERS, configfile, ConfigElement, ConfigText, ConfigBoolean, ConfigSelection
from Components.GUIComponent import GUIComponent
from Components.Pixmap import Pixmap
from Components.Sources.Boolean import Boolean
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard

from enigma import eListbox, eListboxPythonConfigContent, ePoint, eRCInput, eTimer

import skin


class ConfigList(GUIComponent, object):
	def __init__(self, list, session=None):
		GUIComponent.__init__(self)
		self.l = eListboxPythonConfigContent()
		seperation = skin.parameters.get("ConfigListSeperator", 200)
		self.l.setSeperation(seperation)
		height, space = skin.parameters.get("ConfigListSlider", (17, 0))
		self.l.setSlider(height, space)
		self.timer = eTimer()
		self.list = list
		self.onSelectionChanged = []
		self.current = None
		self.session = session

	def execBegin(self):
		rcinput = eRCInput.getInstance()
		rcinput.setKeyboardMode(rcinput.kmAscii)
		self.timer.callback.append(self.timeout)

	def execEnd(self):
		rcinput = eRCInput.getInstance()
		rcinput.setKeyboardMode(rcinput.kmNone)
		self.timer.callback.remove(self.timeout)

	def toggle(self):
		selection = self.getCurrent()
		selection[1].toggle()
		self.invalidateCurrent()

	def handleKey(self, key):
		selection = self.getCurrent()
		if selection and selection[1].enabled:
			selection[1].handleKey(key)
			self.invalidateCurrent()
			if key in KEY_NUMBERS:
				self.timer.start(1000, 1)

	def getCurrent(self):
		return self.l.getCurrentSelection()

	def getCurrentIndex(self):
		return self.l.getCurrentSelectionIndex()

	def setCurrentIndex(self, index):
		if self.instance is not None:
			self.instance.moveSelectionTo(index)

	def invalidateCurrent(self):
		self.l.invalidateEntry(self.l.getCurrentSelectionIndex())

	def invalidate(self, entry):
		# When the entry to invalidate does not exist, just ignore the request.
		# This eases up conditional setup screens a lot.
		#
		if entry in self.__list:
			self.l.invalidateEntry(self.__list.index(entry))

	GUI_WIDGET = eListbox

	def selectionChanged(self):
		if isinstance(self.current, tuple) and len(self.current) >= 2:
			self.current[1].onDeselect(self.session)
		self.current = self.getCurrent()
		if isinstance(self.current, tuple) and len(self.current) >= 2:
			self.current[1].onSelect(self.session)
		else:
			return
		for x in self.onSelectionChanged:
			x()

	def hideHelp(self):
		if isinstance(self.current, tuple) and len(self.current) >= 2:
			self.current[1].hideHelp(self.session)

	def showHelp(self):
		if isinstance(self.current, tuple) and len(self.current) >= 2:
			self.current[1].showHelp(self.session)

	def postWidgetCreate(self, instance):
		instance.selectionChanged.get().append(self.selectionChanged)
		instance.setContent(self.l)
		self.instance.setWrapAround(True)

	def preWidgetRemove(self, instance):
		if isinstance(self.current, tuple) and len(self.current) >= 2:
			self.current[1].onDeselect(self.session)
		instance.selectionChanged.get().remove(self.selectionChanged)
		instance.setContent(None)

	def setList(self, l):
		self.timer.stop()
		self.__list = l
		self.l.setList(self.__list)
		if l is not None:
			for x in l:
				assert len(x) < 2 or isinstance(x[1], ConfigElement), "[ConfigList] Entry in ConfigList " + str(x[1]) + " must be a ConfigElement!"

	def getList(self):
		return self.__list

	list = property(getList, setList)

	def timeout(self):
		self.handleKey(KEY_TIMEOUT)

	def isChanged(self):
		for x in self.list:
			if x[1].isChanged():
				return True
		return False

	def moveTop(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveTop)

	def moveBottom(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveEnd)

	def pageUp(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.pageUp)

	def pageDown(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.pageDown)

	def moveUp(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveUp)

	def moveDown(self):
		if self.instance is not None:
			self.instance.moveSelection(self.instance.moveDown)

	def selectionEnabled(self, enabled):
		if self.instance is not None:
			self.instance.setSelectionEnable(enabled)


class ConfigListScreen:
	def __init__(self, list, session=None, on_change=None):
		self.cancelMsg = _("Really close without saving settings?")
		if "key_red" not in self:
			self["key_red"] = StaticText(_("Cancel"))
		if "key_green" not in self:
			self["key_green"] = StaticText(_("Save"))
		if "key_help" not in self:
			self["key_help"] = StaticText(_("HELP"))
		if "HelpWindow" not in self:
			self["HelpWindow"] = Pixmap()
			self["HelpWindow"].hide()
		if "VKeyIcon" not in self:
			self["VKeyIcon"] = Boolean(False)

		self["config_actions"] = HelpableNumberActionMap(self, "ConfigListActions", {
			"cancel": (self.keyCancel, _("Cancel any changed settings and exit")),
			"red": (self.keyCancel, _("Cancel any changed settings and exit")),
			"close": (self.closeRecursive, _("Cancel any changed settings and exit all menus")),
			"save": (self.keySave, _("Save all changed settings and exit")),
			"green": (self.keySave, _("Save all changed settings and exit")),
			"ok": (self.keyOK, _("Select, toggle, process or edit the current entry")),
			"menu": (self.keyMenu, _("Display selection list as a selection menu")),
			"top": (self.keyTop, _("Move to first line")),
			"pageUp": (self.keyPageUp, _("Move up a screen")),
			"up": (self.keyUp, _("Move up a line")),
			"first": (self.keyFirst, _("Jump to first item in list or the start of text")),
			"left": (self.keyLeft, _("Select the previous item in list or move cursor left")),
			"right": (self.keyRight, _("Select the next item in list or move cursor right")),
			"last": (self.keyLast, _("Jump to last item in list or the end of text")),
			"down": (self.keyDown, _("Move down a line")),
			"pageDown": (self.keyPageDown, _("Move down a screen")),
			"bottom": (self.keyBottom, _("Move to last line")),
			"toggleOverwrite": (self.keyToggleOW, _("Toggle new text inserts before or overwrites existing text")),
			"backspace": (self.keyBackspace, _("Delete the character to the left of cursor")),
			"delete": (self.keyDelete, _("Delete the character under the cursor")),
			"1": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"2": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"3": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"4": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"5": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"6": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"7": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"8": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"9": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"0": (self.keyNumberGlobal, _("Number or SMS style data entry")),
			"gotAsciiCode": (self.keyGotAscii, _("Keyboard data entry"))
		}, prio=-1, description=_("Common Setup Functions"))

		self.onChangedEntry = []

		self["VirtualKB"] = HelpableActionMap(self, "VirtualKeyboardActions", {
			"showVirtualKeyboard": (self.KeyText, _("Display the virtual keyboard for data entry"))
		}, prio=-2, description=_("Common Setup Functions"))

		self["VirtualKB"].setEnabled(False)

		self["config"] = ConfigList(list, session=session)

		if on_change is not None:
			self.__changed = on_change
		else:
			self.__changed = lambda: None

		if self.handleInputHelpers not in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.handleInputHelpers)
		if self.ShowHelp not in self.onExecBegin:
			self.onExecBegin.append(self.ShowHelp)
		if self.HideHelp not in self.onExecEnd:
			self.onExecEnd.append(self.HideHelp)

	# This should not be required if ConfigList is invoked via Setup (as it should).
	#
	def createSummary(self):
		self.setup_title = self.getTitle()
		from Screens.Setup import SetupSummary
		return SetupSummary

	def getCurrentEntry(self):
		return self["config"].getCurrent() and self["config"].getCurrent()[0] or ""

	def getCurrentValue(self):
		return self["config"].getCurrent() and str(self["config"].getCurrent()[1].getText()) or ""

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def getCurrentData(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 3 and self["config"].getCurrent()[3] or ""

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def handleInputHelpers(self):
		currConfig = self["config"].getCurrent()
		if currConfig is not None and isinstance(currConfig[1], ConfigText):
			self.showVKeyboard(True)
			if "HelpWindow" in self and currConfig[1].help_window and currConfig[1].help_window.instance is not None:
				helpwindowpos = self["HelpWindow"].getPosition()
				currConfig[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))
		else:
			self.showVKeyboard(False)

	def showVKeyboard(self, state):
		if "VKeyIcon" in self:
			self["VirtualKB"].setEnabled(state)
			self["VKeyIcon"].boolean = state

	def ShowHelp(self):
		self.displayHelp(True)

	def HideHelp(self):
		self.displayHelp(False)

	def displayHelp(self, state):
		if "config" in self and "HelpWindow" in self and self["config"].getCurrent() is not None:
			currConf = self["config"].getCurrent()[1]
			if isinstance(currConf, ConfigText) and currConf.help_window.instance is not None:
				if state:
					currConf.help_window.show()
				else:
					currConf.help_window.hide()

	def KeyText(self):
		self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].value)

	def VirtualKeyBoardCallback(self, callback=None):
		if callback is not None and len(callback):
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent())

	def keyOK(self):
		currConfig = self["config"].getCurrent()
		if isinstance(currConfig[1], ConfigBoolean):
			self.keyRight()
		elif isinstance(currConfig[1], ConfigSelection):
			self.keyMenu()
		else:
			self["config"].handleKey(KEY_OK)
			# self.__changed()
			self.testChanged()

	def keyMenu(self):
		selection = self["config"].getCurrent()
		if selection and selection[1].enabled and hasattr(selection[1], "description"):
			self.session.openWithCallback(
				self.handleKeyMenuCallback, ChoiceBox, selection[0],
				list=zip(selection[1].description, selection[1].choices),
				selection=selection[1].choices.index(selection[1].value),
				keys=[]
			)

	def handleKeyMenuCallback(self, answer):
		if answer:
			self["config"].getCurrent()[1].value = answer[1]
			self["config"].invalidateCurrent()
			# self.__changed()
			self.testChanged()

	def keyFirst(self):
		self["config"].handleKey(KEY_HOME)
		# self.__changed()
		self.testChanged()

	def keyLast(self):
		self["config"].handleKey(KEY_END)
		# self.__changed()
		self.testChanged()

	def keyLeft(self):
		self["config"].handleKey(KEY_LEFT)
		# self.__changed()
		self.testChanged()

	def keyRight(self):
		self["config"].handleKey(KEY_RIGHT)
		# self.__changed()
		self.testChanged()

	def keyHome(self):
		self["config"].handleKey(KEY_HOME)
		# self.__changed()
		self.testChanged()

	def keyEnd(self):
		self["config"].handleKey(KEY_END)
		# self.__changed()
		self.testChanged()

	def keyDelete(self):
		self["config"].handleKey(KEY_DELETE)
		# self.__changed()
		self.testChanged()

	def keyBackspace(self):
		self["config"].handleKey(KEY_BACKSPACE)
		# self.__changed()
		self.testChanged()

	def keyToggleOW(self):
		self["config"].handleKey(KEY_TOGGLEOW)
		# self.__changed()
		self.testChanged()

	def keyGotAscii(self):
		self["config"].handleKey(KEY_ASCII)
		# self.__changed()
		self.testChanged()

	def keyNumberGlobal(self, number):
		self["config"].handleKey(KEY_0 + number)
		# self.__changed()
		self.testChanged()

	def testChanged(self):
		if self["config"].isChanged():
			print "[ConfigList] Value has changed!"
			self.__changed()
		else:
			print "[ConfigList] Value has NOT changed!"

	def keyTop(self):
		self["config"].moveTop()

	def keyBottom(self):
		self["config"].moveBottom()

	def keyPageUp(self):
		self["config"].pageUp()

	def keyPageDown(self):
		self["config"].pageDown()

	def keyUp(self):
		self["config"].moveUp()

	def keyDown(self):
		self["config"].moveDown()

	def keySave(self):
		self.saveAll()
		self.close()

	def saveAll(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()

	def keyCancel(self):
		self.closeConfigList(False)

	def closeRecursive(self):
		self.closeConfigList(True)

	def closeConfigList(self, recursiveClose):
		if self["config"].isChanged():
			self.recursiveClose = recursiveClose
			self.session.openWithCallback(self.cancelConfirm, MessageBox, self.cancelMsg, default=False)
		else:
			self.close(recursiveClose)

	def cancelConfirm(self, result):
		if not result:
			return
		for x in self["config"].list:
			x[1].cancel()
		self.close(self.recursiveClose)
