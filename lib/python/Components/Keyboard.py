from os.path import isfile
from Components.config import config
from Components.Console import Console
from Tools.Directories import SCOPE_KEYMAPS, fileReadXML, pathExists, resolveFilename


class Keyboard:

	KEYBOARD_KMAP = 0
	KEYBOARD_PATH = 1
	KEYBOARD_NAME = 2
	KEYBOARD_DISPLAY_NAME = 3

	def __init__(self):
		self.keyboardMaps = []
		self.readKeyboardMapFiles()

	def readKeyboardMapFiles(self):
		self.keyboards = []
		self.Default = 0
		keyboards = fileReadXML(resolveFilename(SCOPE_KEYMAPS, "keyboards.xml"))
		if keyboards is not None:
			for keyboard in sorted(keyboards.findall("keyboard"), key=lambda keyboard: (keyboard.tag, keyboard.get("name"))):
				keyboardKmap = keyboard.attrib.get("kmap")
				keyboardName = keyboard.attrib.get("name")
				if keyboardKmap and keyboardName:
					keyboardKmapPath = resolveFilename(SCOPE_KEYMAPS, keyboardKmap)
					print(f"[Keyboard][readKeyboardMapFiles] keyboardKmapPath:{keyboardKmapPath}")
					if isfile(keyboardKmapPath):
						self.keyboards.append((keyboardKmap, keyboardKmapPath, keyboardName, _(keyboardName)))
						# self.keyboardMaps.append((keyboardKmap, keyboardName))
					else:
						print(f"[Keyboard] Error: Keyboard definition '{keyboardKmapPath}' doesn't exist for '{keyboardName}'!")
				else:
					print(f"[Keyboard] Error: Keyboard definition is invalid!  (kmap='{keyboardKmap}', name='{keyboardName}')")
			self.Default, self.keyboardMaps = self.setupFinalise()

	def activateKeyboardMap(self, index):
		print(f"[Keyboard][activateKeyboardMap] index '{index}'")
		if 0 <= index < len(self.keyboards):
			path = self.keyboards[index][self.KEYBOARD_PATH]
			print(f"[Keyboard] Loading selected keyboard '{self.keyboards[index][self.KEYBOARD_NAME]}' from '{path}'.")
			if isfile(path):
				Console().ePopen(f"/sbin/loadkmap < {path}")
			else:
				print(f"[Keyboard] Error: Keyboard definition '{path}' does not exist!")
		else:
			print(f"[Keyboard] Error: Keyboard definition index '{index}' is invalid!")

	def getKeyboardMaplist(self):
		print(f"[Keyboard][getKeyboardMaplist]  self.keyboardMaps:{self.keyboardMaps}")
		return self.keyboardMaps

	def getDefaultKeyboardMap(self):
		return self.Default

	def setupFinalise(self):
		keyboardLanguage = {"en": "qwerty.kmap", "de": "qwertz.kmap", "fr": "azerty.kmap", "us": "qwerty.kmap"}
		try:
			language = config.osd.language.value[0:2]
		except Exception as error:
			language = "en" # set default as English
			print(f"[Keyboard] getDefaultKeyboardMap error:{error} language:{language}")
			pass
		print(f"[Keyboard] getDefaultKeyboardMap language:{language}")
		languageDefault = keyboardLanguage.get(language, "querty.kmap")
		print(f"[Keyboard] languageDefault:{languageDefault}")
		keyboardChoices = []
		default = 0
		for index, keyboard in enumerate(self.keyboards):
			print(f"[Keyboard] index:{index} keyboard:{keyboard}")
			keyboardChoices.append((index, keyboard[self.KEYBOARD_DISPLAY_NAME]))
			if languageDefault == keyboard[self.KEYBOARD_KMAP]:
				print(f"[Keyboard] Default keyboard identified as '{keyboard[self.KEYBOARD_DISPLAY_NAME]}' using '{keyboard[self.KEYBOARD_KMAP]}'.")
				default = index
		return default, keyboardChoices


keyboard = Keyboard()
