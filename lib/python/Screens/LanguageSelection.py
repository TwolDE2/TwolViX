from enigma import eTimer, getDesktop
import xml.etree.cElementTree

from skin import domScreens
from Components.ActionMap import HelpableActionMap
from Components.config import config, configfile, ConfigSubsection, ConfigSelection
from Components.Label import Label
from Components.Language import language
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.HelpMenu import HelpableScreen
from Screens.Rc import Rc
from Screens.Screen import Screen
from Screens.Setup import Setup
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap

config.locales = ConfigSubsection()
config.locales.packageLocales = ConfigSelection(default="Packages", choices=[
	("L", _("Packages and associated locales")),
	("P", _("Packaged locales only"))
])
config.locales.localesSortBy = ConfigSelection(default="2", choices=[
	("2", _("English name (Ascending)")),
	("20", _("English name (Descending)")),
	("1", _("Native name (Ascdending)")),
	("10", _("Native name (Descending)")),
	("3", _("Locale (Ascending)")),
	("30", _("Locale (Descending)"))
])

inWizard = False


class LanguageSelection(Screen, HelpableScreen):
	LIST_FLAGICON = 0
	LIST_NATIVE = 1
	LIST_NAME = 2
	LIST_LOCALE = 3
	LIST_STATICON = 4
	LIST_STATUS = 5
	LIST_PACKAGE = 6

	PACK_INSTALLED = 1
	PACK_AVAILABLE = 2
	PACK_INUSE = 3

	skinTemplate = """
	<screen name="LanguageSelection" position="center,center" size="%d,%d">
		<widget source="locales" render="Listbox" position="center,%d" size="%d,%d" enableWrapAround="1" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{
				"template": [
					MultiContentEntryPixmapAlphaBlend(pos = (%d, %d), size = (%d, %d), flags = BT_SCALE, png = 0),
					MultiContentEntryText(pos = (%d, 0), size = (%d, %d), font = 0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 1),
					MultiContentEntryText(pos = (%d, 0), size = (%d, %d), font = 0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 2),
					MultiContentEntryText(pos = (%d, 0), size = (%d, %d), font = 0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 3),
					MultiContentEntryPixmapAlphaBlend(pos = (%d, %d), size = (%d, %d), png = 4)
				],
				"fonts": [gFont("Regular",%d)],
				"itemHeight": %d
				}
			</convert>
		</widget>
		<widget source="description" render="Label" position="center,e-%d" size="%d,%d" font="Regular;%d" valign="center" />
		<widget source="key_red" render="Label" position="%d,e-%d" size="%d,%d" backgroundColor="key_red" font="Regular;%d" foregroundColor="key_text" halign="center" valign="center" />
		<widget source="key_green" render="Label" position="%d,e-%d" size="%d,%d" backgroundColor="key_green" font="Regular;%d" foregroundColor="key_text" halign="center" valign="center" />
		<widget source="key_yellow" render="Label" position="%d,e-%d" size="%d,%d" backgroundColor="key_yellow" font="Regular;%d" foregroundColor="key_text" halign="center" valign="center" />
	</screen>"""
	scaleData = [
		898, 560,
		10, 874, 442,
		5, 2, 60, 30,
		80, 340, 34,
		430, 290, 34,
		730, 90, 34,
		0, 0, 0, 0,  # These values are calculated based on the available image size.
		25, 34,
		85, 874, 25, 20,
		10, 50, 140, 40, 20,
		160, 50, 140, 40, 20,
		310, 50, 140, 40, 20
	]
	skin = None

	def __init__(self, session, menu_path=""):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.available = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, "icons/lock_off.png"))
		self.installed = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, "icons/lock_on.png"))
		self.inUse = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, "icons/lock_error.png"))
		if LanguageSelection.skin is None:
			self.initialiseSkin()
		self["key_menu"] = StaticText(_("MENU"))
		self["key_red"] = StaticText()
		self["key_green"] = StaticText()
		self["key_yellow"] = StaticText()
		self["locales"] = List(None, enableWrapAround=True)
		self["locales"].onSelectionChanged.append(self.selectionChanged)
		self["description"] = StaticText()
		self["selectionActions"] = HelpableActionMap(self, "LanguageSelectionActions", {
			"menu": (self.settings, _("Manage Language/Locale Selection settings")),
			"select": (self.select, _("Select the currently highlighted locale to be the user interface locale")),
			"close": (self.closeRecursive, _("Cancel any changes the active locale and exit all menus")),
			"cancel": (self.cancel, _("Cancel any changes to the active locale and exit")),
			"save": (self.apply, _("Apply any changes to the active langauge and exit"))
		}, prio=0, description=_("Language/Locale Selection Actions"))
		self["manageActions"] = HelpableActionMap(self, "LanguageSelectionActions", {
			"manage": (self.manage, _("Add / Delete the currently highlighted language / locale"))
		}, prio=0, description=_("Language/Locale Selection Actions"))
		self["navigationActions"] = HelpableActionMap(self, "NavigationActions", {
			"top": (self.moveTop, _("Move up to first line")),
			"pageUp": (self.movePageUp, _("Move up a screen")),
			"up": (self.moveUp, _("Move up a line")),
			"first": (self.moveTop, _("Move up to first line")),
			"left": (self.movePageUp, _("Move up a screen")),
			"right": (self.movePageDown, _("Move down a screen")),
			"last": (self.moveBottom, _("Move down to last line")),
			"down": (self.moveDown, _("Move down a line")),
			"pageDown": (self.movePageDown, _("Move down a screen")),
			"bottom": (self.moveBottom, _("Move down to last line"))
		}, prio=-1, description=_("Navigation Actions"))
		self.initialLocale = language.getLocale()
		self.currentLocale = self.initialLocale
		self.changedTimer = eTimer()
		self.changedTimer.callback.append(self.selectionChangedDone)
		self.selectTimer = eTimer()
		self.selectTimer.callback.append(self.selectDone)
		self.packageTimer = eTimer()
		self.packageTimer.callback.append(self.processPackage)
		self.manageTimer = eTimer()
		self.manageTimer.callback.append(self.manageDone)
		self.selectError = False
		self.updateLocaleList(self.initialLocale)
		if self.layoutFinished not in self.onLayoutFinish:
			self.onLayoutFinish.append(self.layoutFinished)

	def initialiseSkin(self):
		element, path = domScreens.get("LanguageSelection", (None, None))
		if element is None:  # This skin does not have a LanguageSelection screen.
			buildSkin = True
		else:  # Test the skin's LanguageSelection screen to ensure it works with the new code.
			buildSkin = False
			widgets = element.findall("widget")
			if widgets is not None:
				for widget in widgets:
					source = widget.get("source", None)
					if source == "languages":
						print "[LanguageSelection] Warning: Current skin '%s' does not support this version of LanguageSelection!    Please contact the skin's author!" % config.skin.primary_skin.value
						del domScreens["LanguageSelection"]  # It is incompatible, delete the screen from the skin.
						buildSkin = True
						break
		if buildSkin:  # Build the embedded skin and scale it to the current screen resolution.
			# The skin template is designed for a HD screen so the scaling factor is 720.
			scaleData = [x * getDesktop(0).size().height() / 720 for x in LanguageSelection.scaleData]
			imageWidth = self.available.size().width()
			imageHeight = self.available.size().height()
			scaleData[18] = scaleData[3] - imageWidth - 25
			scaleData[19] = (scaleData[23] - imageHeight) / 2
			scaleData[20] = imageWidth
			scaleData[21] = imageHeight
			LanguageSelection.skin = LanguageSelection.skinTemplate % tuple(scaleData)
			# print "[LanguageSelection] DEBUG: Height=%d\n" % getDesktop(0).size().height(), LanguageSelection.skin
		else:
			LanguageSelection.skin = "<screen />"

	def updateLocaleList(self, inUseLoc=None):
		if inUseLoc is None:
			inUseLoc = self.currentLocale
		self.list = []
		for package in language.availablePackages:
			try:
				language.installedPackages.index(package)
				installStatus = self.PACK_INSTALLED
			except ValueError:
				installStatus = self.PACK_AVAILABLE
			locales = language.packageToLocales(package)
			for loc in locales:
				data = language.splitLocale(loc)
				if len(locales) > 1 and "%s-%s" % (data[0], data[1].lower()) in language.availablePackages:
					continue
				png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "countries/%s.png" % data[1].lower()))
				if png is None:
					png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "countries/missing.png"))
				name = "%s (%s)" % (language.languageData[data[0]][language.LANG_NAME], data[1])
				if installStatus == self.PACK_INSTALLED:
					icon = self.installed
				else:
					icon = self.available
				if loc == inUseLoc:
					status = self.PACK_INUSE
					icon = self.inUse
				else:
					status = installStatus
				self.list.append((png, language.languageData[data[0]][language.LANG_NATIVE], name, loc, icon, status, package))
				if config.locales.packageLocales.value == "P":
					break
		if inUseLoc not in [x[self.LIST_LOCALE] for x in self.list]:
			data = language.splitLocale(inUseLoc)
			png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "countries/%s.png" % data[1].lower()))
			if png is None:
				png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "countries/missing.png"))
			name = "%s (%s)" % (language.languageData[data[0]][language.LANG_NAME], data[1])
			package = language.getPackage(inUseLoc)
			self.list.append((png, language.languageData[data[0]][language.LANG_NATIVE], name, inUseLoc, self.inUse, self.PACK_INUSE, package))
		sortBy = int(config.locales.localesSortBy.value)
		order = sortBy / 10 if sortBy > 9 else sortBy
		reverse = True if sortBy > 9 else False
		self.list = sorted(self.list, key=lambda x: x[order], reverse=reverse)
		self["locales"].updateList(self.list)

	def layoutFinished(self):
		self.moveToLocale(self.currentLocale)
		self.updateText(updateDescription=True)

	def selectionChanged(self):
		self.changedTimer.start(250)
		self.updateText(updateDescription=True)

	def selectionChangedDone(self):
		self.changedTimer.stop()
		loc = self["locales"].getCurrent()[self.LIST_LOCALE]
		if loc in language.localeList:
			language.activateLocale(loc, runCallbacks=False)
		self.updateText(updateDescription=True)

	def updateText(self, updateDescription=True):
		current = self["locales"].getCurrent()
		Screen.setTitle(self, _("Language/Locale Selection"))
		self["key_red"].text = _("Cancel")
		self["key_green"].text = _("Save")
		if current[self.LIST_PACKAGE] == language.getPackage(self.currentLocale):
			self["key_yellow"].text = ""
			self["manageActions"].setEnabled(False)
			if current[self.LIST_STATUS] == self.PACK_INUSE:
				msg = _("This is the currently selected locale.")
			else:
				msg = _("Press OK to use this locale.")
		else:
			if language.splitPackage(current[self.LIST_PACKAGE])[1] is None:
				deleteText = _("Delete Lang")
				installText = _("Install Lang")
			else:
				deleteText = _("Delete Loc")
				installText = _("Install Loc")
			if current[self.LIST_STATUS] == self.PACK_INSTALLED:
				self["key_yellow"].text = deleteText
				msg = _("Press OK to use this locale.")
			else:
				self["key_yellow"].text = installText
				msg = _("Press OK to install and use this locale.")
			self["manageActions"].setEnabled(True)
		if updateDescription:
			self["description"].text = "%s  [%s (%s) %s]" % (msg, _(language.getLanguageName(current[self.LIST_LOCALE])), _(language.getCountryName(current[self.LIST_LOCALE])), current[self.LIST_LOCALE])

	def moveToLocale(self, loc):
		index = 0
		for entry in self.list:
			if entry[self.LIST_LOCALE] == loc:
				break
			index += 1
		if index == len(self.list):
			index = 0
		self["locales"].index = index  # This will trigger an onSelectionChanged event!

	def settings(self):
		self.listEntry = self["locales"].getCurrent()[self.LIST_LOCALE]
		self.session.openWithCallback(self.settingsClosed, LanguageSettings)

	def settingsClosed(self, status=None):
		self.updateLocaleList(self.currentLocale)
		self.moveToLocale(self.listEntry)
		self.updateText(updateDescription=True)

	def select(self):
		self["selectionActions"].setEnabled(False)
		self["manageActions"].setEnabled(False)
		self.selectError = False
		if self["locales"].getCurrent()[self.LIST_STATUS] == self.PACK_AVAILABLE:
			self.manage()
			self.selectTimer.start(5000)
		else:
			self.selectDone()

	def selectDone(self):
		self.selectTimer.stop()
		current = self["locales"].getCurrent()
		if not self.selectError:
			self.currentLocale = current[self.LIST_LOCALE]
			self.updateLocaleList(self.currentLocale)
			self["key_yellow"].text = ""
			if current[self.LIST_STATUS] == self.PACK_AVAILABLE:
				self["description"].text = _("Locale %s (%s) has been installed and selected as the active locale.") % (current[self.LIST_NATIVE], current[self.LIST_NAME])
			elif current[self.LIST_STATUS] == self.PACK_INSTALLED:
				self["description"].text = _("Locale %s (%s) has been selected as the active locale.") % (current[self.LIST_NATIVE], current[self.LIST_NAME])
			else:
				self["description"].text = _("This is already the active locale.")
		self["selectionActions"].setEnabled(True)
		self["manageActions"].setEnabled(True)

	def closeRecursive(self):
		self.cancel(recursive=True)

	def cancel(self, recursive=False):
		# if self["messages"].isChanged():
		#	self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), default=False)
		# else:
		language.activateLocale(self.initialLocale, runCallbacks=False)
		self.close(recursive)

	def cancelConfirm(self, result):
		if not result:
			return
		for x in self["config"].list:
			x[1].cancel()
		self.close(recursive)

	def apply(self):
		# language.activateLocale(self.currentLocale, runCallbacks=True)
		config.osd.language.setValue(self.currentLocale)
		config.osd.language.save()
		configfile.save()
		self.close()

	def manage(self):
		current = self["locales"].getCurrent()
		if current[self.LIST_LOCALE] != self.currentLocale:
			if current[self.LIST_STATUS] == self.PACK_INSTALLED:
				print "[LanguageSelection] Deleting language/locale %s (%s)..." % (current[self.LIST_NATIVE], current[self.LIST_NAME])
				self["description"].text = _("Deleting %s (%s)...") % (current[self.LIST_NATIVE], current[self.LIST_NAME])
			elif current[self.LIST_STATUS] == self.PACK_AVAILABLE:
				print "[LanguageSelection] Installing language/locale %s (%s)..." % (current[self.LIST_NATIVE], current[self.LIST_NAME])
				self["description"].text = _("Installing %s (%s)...") % (current[self.LIST_NATIVE], current[self.LIST_NAME])
			self.packageTimer.start(500)

	def processPackage(self):
		self.packageTimer.stop()
		current = self["locales"].getCurrent()
		if current[self.LIST_STATUS] == self.PACK_INSTALLED:
			language.activateLocale(self.currentLocale, runCallbacks=False)
			status = language.deleteLanguagePackages([current[self.LIST_PACKAGE]])
		elif current[self.LIST_STATUS] == self.PACK_AVAILABLE:
			status = language.installLanguagePackages([current[self.LIST_PACKAGE]])
			if status[0].startswith("Error:"):
				self.selectError = True
			else:
				language.activateLocale(self["locales"].getCurrent()[self.LIST_LOCALE], runCallbacks=False)
		else:
			status = [_("No action required.")]
		self["description"].text = "\n".join(status)
		if not self.selectTimer.isActive():
			self.updateLocaleList(self.currentLocale)
		self.manageTimer.start(750)

	def manageDone(self):
		self.updateText(updateDescription=False)

	def moveTop(self):
		# self["locales"].moveTop()
		self["locales"].setIndex(0)

	def movePageUp(self):
		# self["locales"].movePageUp()
		self["locales"].pageUp()

	def moveUp(self):
		# self["locales"].moveUp()
		self["locales"].up()

	def moveDown(self):
		# self["locales"].moveDown()
		self["locales"].down()

	def movePageDown(self):
		# self["locales"].movePageDown()
		self["locales"].pageDown()

	def moveBottom(self):
		# self["locales"].moveBottom()
		self["locales"].setIndex(self["locales"].count() - 1)

	def run(self, justlocal=False):
		# print "[LanguageSelection] updating locale..."
		lang = self["locales"].getCurrent()[self.LIST_LOCALE]

		if lang != config.osd.language.value:
			config.osd.language.setValue(lang)
			config.osd.language.save()

		if justlocal:
			return

		language.activateLanguage(lang, runCallbacks=True)
		config.misc.languageselected.value = 0
		config.misc.languageselected.save()


class LanguageSettings(Setup, HelpableScreen):
	def __init__(self, session):
		Setup.__init__(self, session=session, setup="languagesettings")


class LanguageWizard(LanguageSelection, Rc):
	def __init__(self, session):
		LanguageSelection.__init__(self, session)
		Rc.__init__(self)
		global inWizard
		inWizard = True
		self.onLayoutFinish.append(self.selectKeys)
		self["wizard"] = Pixmap()
		self["summarytext"] = StaticText()
		self["text"] = Label()
		self.setText()

	def selectKeys(self):
		self.clearSelectedKeys()
		self.selectKey("UP")
		self.selectKey("DOWN")

	def changed(self):
		self.run(justlocal=True)
		self.setText()

	def setText(self):
		self["text"].setText(_("Use the UP and DOWN buttons to select your locale then press the OK or GREEN button to continue."))
		self["summarytext"].setText(_("Use the UP and DOWN buttons to select your locale then press the OK or GREEN button to continue."))

	def createSummary(self):
		return LanguageWizardSummary


class LanguageWizardSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent)
