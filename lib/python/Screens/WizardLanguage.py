from Components.Label import Label
from Components.Language import language
from Components.Sources.StaticText import StaticText
from Screens.Wizard import Wizard

class WizardLanguage(Wizard):
	def __init__(self, session, showSteps=True, showStepSlider=True, showList=True, showConfig=True):
		Wizard.__init__(self, session, showSteps, showStepSlider, showList, showConfig)
		self.locale = language.getLocale()
		self.locales = []
		if language.packageDirectories:
			for package in language.packageDirectories:
				self.locales.append(language.packageToLocales(package)[0])
		if "en_US" not in self.locales:
			self.locales.append("en_US")
		self.localeIndex = 0
		if len(self.locales) > 1:
			self["key_red"] = StaticText(_("Change Language"))
			try:
				self.localeIndex = self.locales.index(self.locale)
			except ValueError:
				pass
		else:
			self["key_red"] = StaticText("")
		self["languagetext"] = Label()
		self.updateLanguageDescription()

	def red(self):
		self.resetCounter()
		self.languageSelect()

	def languageSelect(self):
		# print "[WizardLanguage] languageSelect"
		self.localeIndex += 1
		if self.localeIndex >= len(self.locales):
			self.localeIndex = 0
		self.locale = self.locales[self.localeIndex]
		language.activateLocale(self.locale)
		self.updateTexts()

	def updateLanguageDescription(self):
		# print "[WizardLanguage] updateLanguageDescription Trying locale '%s'." % self.locale
		self["languagetext"].text = "%s:  %s (%s)  :  %s (%s)  :  %s" % (_("Language"), language.getLanguageNative(self.locale), language.getCountryNative(self.locale), language.getLanguageName(self.locale), language.getCountryName(self.locale), self.locale)

	def updateTexts(self):
		# print "[WizardLanguage] updateTexts"
		self.updateText(firstset=True)
		self.updateValues()
		self.updateLanguageDescription()
