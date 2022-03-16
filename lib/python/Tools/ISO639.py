import pickle
import enigma
with open(enigma.eEnv.resolve("${datadir}/enigma2/iso-639-3.pck"), 'rb') as f:
	if version_info >= (3, 0):
LanguageCodes = pickle.load(f, encoding='utf-8')
