from Components.config import config, ConfigNothing, ConfigBoolean, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.Boolean import Boolean
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import SystemInfo
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN, SCOPE_SKIN, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap

from boxbranding import getMachineBrand, getMachineName
from gettext import dgettext
from skin import setups

import os
import xml.etree.cElementTree

setupdoms = {}
setupdates = {}
setuptitles = {}

# Read the setupmenu
def setupdom(setup=None, plugin=None):
	if plugin:
		setupfile = resolveFilename(SCOPE_CURRENT_PLUGIN, plugin + "/setup.xml")
		msg = " from plugin '%s'" % plugin
	else:
		setupfile = resolveFilename(SCOPE_SKIN, "setup.xml")
		msg = ""
	try:
		mtime = os.path.getmtime(setupfile)
	except OSError as err:
		print "[Setup] ERROR: Unable to get '%s' modified time - Error (%d): %s!" % (setupfile, err.errno, err.strerror)
		return xml.etree.cElementTree.fromstring("<setupxml></setupxml>")
	cached = setupfile in setupdoms and setupfile in setupdates and setupdates[setupfile] == mtime
	print "[Setup] XML%s source file: '%s'" % (" cached" if cached else "", setupfile)
	if setup is not None:
		print "[Setup] XML Setup menu '%s'%s" % (setup, msg)
	if cached:
		return setupdoms[setupfile]
	try:
		fail = False
		setupfiledom = xml.etree.cElementTree.parse(setupfile)
	except (IOError, OSError) as err:
		fail = True
		print "[Setup] ERROR: Unable to open/read '%s' - Error (%d): %s!" % (setupfile, err.errno, err.strerror)
	except xml.etree.cElementTree.ParseError as err:
		fail = True
		print "[Setup] ERROR: Unable to load XML data from '%s' - %s!" % (setupfile, str(err))
	except BaseException:
		fail = True
		print "[Setup] ERROR: Unable to process XML data from '%s'!" % setupfile
	if fail:
		setupfiledom = xml.etree.cElementTree.fromstring("<setupxml></setupxml>")
	else:
		setupdoms[setupfile] = setupfiledom
		setupdates[setupfile] = mtime
		xmldata = setupfiledom.getroot()
		for x in xmldata.findall("setup"):
			key = x.get("key", "")
			if key in setuptitles:
				print "[Setup] WARNING: Setup key '%s' has been redefined!" % key
			title = x.get("menuTitle", "").encode("UTF-8")
			if title == "":
				title = x.get("title", "").encode("UTF-8")
				if title == "":
					print "[Setup] Error: Setup key '%s' title is missing or blank!" % key
					setuptitles[key] = _("** Setup error: '%s' title is missing or blank!") % key
				else:
					setuptitles[key] = _(title)
			else:
				setuptitles[key] = _(title)
			# print "[Setup] DEBUG XML Setup menu load: key='%s', title='%s', menuTitle='%s', translated title='%s'" % (key, x.get("title", "").encode("UTF-8"), x.get("menuTitle", "").encode("UTF-8"), setuptitles[key])
	return setupfiledom


class SetupSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self["SetupTitle"] = StaticText(_(parent.setup_title))
		self["SetupEntry"] = StaticText("")
		self["SetupValue"] = StaticText("")
		if hasattr(self.parent, "onChangedEntry"):
			if self.addWatcher not in self.onShow:
				self.onShow.append(self.addWatcher)
			if self.removeWatcher not in self.onHide:
				self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		if self.selectionChanged not in self.parent.onChangedEntry:
			self.parent.onChangedEntry.append(self.selectionChanged)
		if self.selectionChanged not in self.parent["config"].onSelectionChanged:
			self.parent["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def removeWatcher(self):
		if self.selectionChanged in self.parent.onChangedEntry:
			self.parent.onChangedEntry.remove(self.selectionChanged)
		if self.selectionChanged in self.parent["config"].onSelectionChanged:
			self.parent["config"].onSelectionChanged.remove(self.selectionChanged)

	def selectionChanged(self):
		self["SetupEntry"].text = self.parent.getCurrentEntry()
		self["SetupValue"].text = self.parent.getCurrentValue()


class Setup(ConfigListScreen, Screen, HelpableScreen):
	ALLOW_SUSPEND = True

	def __init__(self, session, setup, plugin=None, menu_path=None, PluginLanguageDomain=None):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.onChangedEntry = []
		# For the skin: First try a Setup_<setupKey>, then Setup
		self.skinName = ["Setup_" + setup, "Setup"]
		self.setup = setup
		self.plugin = plugin
		self.menu_path = menu_path
		self.PluginLanguageDomain = PluginLanguageDomain
		self.setup_title = "Setup"
		self.footnote = ""

		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
		self.createSetup()

		self["menu_path_compressed"] = StaticText()
		self["footnote"] = Label()
		self["footnote"].hide()
		self["description"] = Label()

		defaultmenuimage = setups.get("default", "")
		menuimage = setups.get(self.setup, defaultmenuimage)
		if menuimage:
			if menuimage is defaultmenuimage:
				msg = "Default"
			else:
				msg = "Menu"
			menuimage = resolveFilename(SCOPE_CURRENT_SKIN, menuimage)
			print "[Setup] %s image: '%s'" % (msg, menuimage)
			self.menuimage = LoadPixmap(menuimage)
			if self.menuimage:
				self["menuimage"] = Pixmap()
			else:
				print "[Setup] ERROR: Unable to load menu image '%s'!" % menuimage
		else:
			self.menuimage = None

		if self.layoutFinished not in self.onLayoutFinish:
			self.onLayoutFinish.append(self.layoutFinished)
		if self.selectionChanged not in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)

	def createSetup(self):
		currentItem = self["config"].getCurrent()
		self.list = []
		xmldata = setupdom(self.setup, self.plugin).getroot()
		for x in xmldata.findall("setup"):
			if x.get("key") == self.setup:
				self.addItems(x)
				skin = x.get("skin", "")
				if skin != "":
					self.skinName.insert(0, skin)
				if config.usage.show_menupath.value in ("large", "small") and x.get("menuTitle", "").encode("UTF-8") != "":
					self.setup_title = x.get("menuTitle", "").encode("UTF-8")
				else:
					self.setup_title = x.get("title", "").encode("UTF-8")
				# If this break is executed then there can only be one setup tag with this key.
				# This may not be appropriate if conditional setup blocks become available.
				break
		self["config"].setList(self.list)
		if config.usage.sort_settings.value:
			self["config"].list.sort()
		self.moveToItem(currentItem)

	def addItems(self, parentNode):
		for x in parentNode:
			if x.tag and x.tag == "item":
				item_level = int(x.get("level", 0))
				if item_level > config.usage.setup_level.index:
					continue

				requires = x.get("requires")
				if requires:
					negate = requires.startswith("!")
					if negate:
						requires = requires[1:]
					if requires.startswith("config."):
						item = eval(requires)
						SystemInfo[requires] = item.value and item.value != "0"
						clean = True
					else:
						clean = False
					result = bool(SystemInfo.get(requires, False))
					if clean:
						SystemInfo.pop(requires, None)
					if requires and negate == result:
						continue

				conditional = x.get("conditional")
				if conditional and not eval(conditional):
					continue

				if self.PluginLanguageDomain:
					item_text = dgettext(self.PluginLanguageDomain, x.get("text", "??").encode("UTF-8"))
					item_description = dgettext(self.PluginLanguageDomain, x.get("description", " ").encode("UTF-8"))
				else:
					item_text = _(x.get("text", "??").encode("UTF-8"))
					item_description = _(x.get("description", " ").encode("UTF-8"))
				item_text = item_text.replace("%s %s", "%s %s" % (getMachineBrand(), getMachineName()))
				item_description = item_description.replace("%s %s", "%s %s" % (getMachineBrand(), getMachineName()))
				item_data = x.get("data", "")
				item = eval(x.text or "")
				if item != "" and (item_data or not isinstance(item, ConfigNothing)):
					# Add item to configlist.
					# The first item is the item itself, ignored by the configList.
					# The second one is converted to string.
					self.list.append((item_text, item, item_description, item_data))

	def layoutFinished(self):
		if config.usage.show_menupath.value == "large" and self.menu_path:
			title = self.menu_path + _(self.setup_title)
			self["menu_path_compressed"].setText("")
		elif config.usage.show_menupath.value == "small" and self.menu_path:
			title = _(self.setup_title)
			self["menu_path_compressed"].setText(self.menu_path + " >" if not self.menu_path.endswith(" / ") else self.menu_path[:-3] + " >" or "")
		else:
			title = _(self.setup_title)
			self["menu_path_compressed"].setText("")
		self.setTitle(title)
		if self.menuimage:
			self["menuimage"].instance.setPixmap(self.menuimage)
		if not self["config"]:
			print "[Setup] No menu items available!"

	def moveToItem(self, item):
		if item != self["config"].getCurrent():
			self["config"].setCurrentIndex(self.getIndexFromItem(item))

	def getIndexFromItem(self, item):
		return self["config"].list.index(item) if item in self["config"].list else 0

	def selectionChanged(self):
		if self["config"]:
			if self.footnote:
				self["footnote"].text = _(self.footnote)
				self["footnote"].show()
			else:
				if self.getCurrentEntry().endswith("*"):
					self["footnote"].text = _("* = Restart Required")
					self["footnote"].show()
				else:
					self["footnote"].text = ""
					self["footnote"].hide()
			self["description"].text = self.getCurrentDescription()
		else:
			self["description"].text = _("There are no items currently available for this menu.")

	def changedEntry(self):
		if isinstance(self["config"].getCurrent()[1], (ConfigBoolean, ConfigSelection)):
			self.createSetup()

# Only used in AudioSelection screen...
def getConfigMenuItem(configElement):
	for item in setupdom().getroot().findall("./setup/item/."):
		if item.text == configElement:
			return _(item.attrib["text"]), eval(configElement)
	return "", None

# Only used in Menu screen...
def getSetupTitle(key):
	setupdom()		# Load (or check for an updated) setup.xml file
	key = str(key)
	title = setuptitles.get(key, None)
	if title is None:
		print "[Setup] Error: Setup key '%s' not found in setup file!" % key
		title = _("** Setup error: '%s' section not found! **") % key
	return title
