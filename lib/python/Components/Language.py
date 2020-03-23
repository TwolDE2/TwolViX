# -*- coding: UTF-8 -*-

import errno
import gettext
import locale

from os import environ, listdir, strerror
from os.path import exists, expanduser, join as pathjoin
from subprocess import Popen, PIPE
from time import localtime, strftime, time

from Tools.Directories import resolveFilename, SCOPE_LANGUAGE

def _(x):
	return x

def InitLanguages():
	language.InitLang()


class Language:
	LANG_NAME = 0
	LANG_TRANSLATED = 1
	LANG_NATIVE = 2
	LANG_ENCODING = 3
	LANG_COUNTRYCODE = 4
	LANG_MAX = 4

	COUNTRY_NAME = 0
	COUNTRY_TRANSLATED = 1
	COUNTRY_NATIVE = 2
	COUNTRY_MAX = 2

	CAT_ENVIRONMENT = 0
	CAT_PYTHON = 1

	def __init__(self):
		# DEVELOPER NOTE:
		#
		# Should this language table include the ISO three letter code for use in the subtitle code?
		# Perhaps also have a flag to indicate that the language should be listed in the subtitle list?
		#
		self.languageData = {
			# Fields: English Name, Translated Name, Localised Name,
			# 	Character Set, [List of ISO-3166 Country Codes].
			# To make managing this list easier please keep languages in
			# ISO 639-2 Code order.  Language codes should be in lower
			# case and country codes should be in upper case.  Be
			# careful not to confuse / mix the language and country!
			#
			# The Character Set entry is only used to set a shell
			# variable used by Gstreamer.
			#
			# If a language is used in more than one country then the
			# default locale contry should be listed first.
			#
			# https://www.loc.gov/standards/iso639-2/php/code_list.php
			# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
			# https://lh.2xlibre.net/locales/
			"aa": ("Afar", _("Afar"), "Afaraf", "UTF-8", "DJ", "ER", "ET"),
			"ab": ("Abkhazian", _("Abkhazian"), "Аҧсуа Бызшәа / Аҧсшәа", "UTF-8"),
			"ae": ("Avestan", _("Avestan"), "Avesta", "UTF-8"),
			"af": ("Afrikaans", _("Afrikaans"), "Afrikaans", "UTF-8", "ZA"),
			"ak": ("Akan", _("Akan"), "Akan", "UTF-8", "GH"),
			"am": ("Amharic", _("Amharic"), "አማርኛ", "UTF-8", "ET"),
			"an": ("Aragonese", _("Aragonese"), "Aragonés", "UTF-8", "ES"),
			"ar": ("Arabic", _("Arabic"), "العربية", "ISO-8859-15", "AE", "BH", "DZ", "EG", "IN", "IQ", "JO", "KW", "LB", "LY", "MA", "OM", "QA", "SA", "SD", "SS", "SY", "TN", "YE"),
			"as": ("Assamese", _("Assamese"), "অসমীয়া", "UTF-8", "IN"),
			"av": ("Avaric", _("Avaric"), "Авар мацӀ / МагӀарул мацӀ", "UTF-8"),
			"ay": ("Aymara", _("Aymara"), "Aymar Aru", "UTF-8", "PE"),
			"az": ("Azerbaijani", _("Azerbaijani"), "Azərbaycan Dili", "UTF-8", "AZ", "IR"),
			"ba": ("Bashkir", _("Bashkir"), "башҡорт теле", "UTF-8"),
			"be": ("Belarusian", _("Belarusian"), "беларуская мова", "UTF-8", "BY"),
			"bg": ("Bulgarian", _("Bulgarian"), "български език", "ISO-8859-15", "BG"),
			"bh": ("Bihari languages", _("Bihari languages"), "भोजपुरी", "UTF-8"),
			"bi": ("Bislama", _("Bislama"), "Bislama", "UTF-8", "TV", "VU"),
			"bm": ("Bambara", _("Bambara"), "Bamanankan", "UTF-8", "ML"),
			"bn": ("Bengali", _("Bengali"), "বাংলা", "UTF-8", "BD", "IN"),
			"bo": ("Tibetan", _("Tibetan"), "བོད་ཡིག", "UTF-8", "CN", "IN"),
			"br": ("Breton", _("Breton"), "Brezhoneg", "UTF-8", "FR"),
			"bs": ("Bosnian", _("Bosnian"), "Bosanski Jezik", "UTF-8", "BA"),
			"ca": ("Catalan / Valencian", _("Catalan / Valencian"), "Català / Valencià", "ISO-8859-15", "AD", "ES", "FR", "IT"),
			"ce": ("Chechen", _("Chechen"), "Нохчийн Мотт", "UTF-8", "RU"),
			"ch": ("Chamorro", _("Chamorro"), "Chamoru", "UTF-8"),
			"co": ("Corsican", _("Corsican"), "Corsu, Lingua Corsa", "UTF-8"),
			"cr": ("Cree", _("Cree"), "ᓀᐦᐃᔭᐍᐏᐣ", "UTF-8"),
			"cs": ("Czech", _("Czech"), "Čeština / Český Jazyk", "ISO-8859-15", "CZ"),
			"cu": ("Church Slavic", _("Church Slavic"), "Ѩзыкъ Словѣньскъ", "UTF-8"),
			"cv": ("Chuvash", _("Chuvash"), "Чӑваш Чӗлхи", "UTF-8", "RU"),
			"cy": ("Welsh", _("Welsh"), "Cymraeg", "UTF-8", "GB"),
			"da": ("Danish", _("Danish"), "Dansk", "ISO-8859-15", "DK"),
			"de": ("German", _("German"), "Deutsch", "ISO-8859-15", "DE", "AT", "BE", "CH", "IT", "LI", "LU"),
			"dv": ("Divehi / Dhivehi / Maldivian", _("Divehi / Dhivehi / Maldivian"), "ދިވެހި", "UTF-8", "MV"),
			"dz": ("Dzongkha", _("Dzongkha"), "རྫོང་ཁ", "UTF-8", "BT"),
			"ee": ("Ewe", _("Ewe"), "Eʋegbe", "UTF-8"),
			"el": ("Greek", _("Greek"), "Ελληνικά", "ISO-8859-7", "GR", "CY"),
			"en": ("English", _("English"), "English", "ISO-8859-15", "US", "AG", "AU", "BW", "BZ", "CA", "DK", "GB", "HK", "IE", "IL", "IN", "JM", "KH", "NG", "NZ", "PH", "SC", "SG", "TT", "ZA", "ZM", "ZW"),
			"eo": ("Esperanto", _("Esperanto"), "Esperanto", "UTF-8"),
			"es": ("Spanish / Castilian", _("Spanish / Castilian"), "Español", "ISO-8859-15", "ES", "AR", "BO", "CL", "CO", "CR", "CU", "DO", "EC", "GT", "HN", "MX", "NI", "PA", "PE", "PR", "PY", "SV", "US", "UY", "VE"),
			"et": ("Estonian", _("Estonian"), "Eesti / Eesti keel", "ISO-8859-15", "EE"),
			"eu": ("Basque", _("Basque"), "Euskara / Euskera", "UTF-8", "ES"),
			"fa": ("Farsi / Persian", _("Farsi / Persian"), "فارسی", "ISO-8859-15", "IR"),
			"ff": ("Fulah", _("Fulah"), "Fulfulde / Pulaar / Pular", "UTF-8", "SN"),
			"fi": ("Finnish", _("Finnish"), "Suomi / Suomen kieli", "ISO-8859-15", "FI"),
			"fj": ("Fijian", _("Fijian"), "Vosa Vakaviti", "UTF-8"),
			"fo": ("Faroese", _("Faroese"), "Føroyskt", "UTF-8", "FO"),
			"fr": ("French", _("French"), "Français", "ISO-8859-15", "FR", "AG", "AI", "BE", "BB", "BS", "CA", "CG", "CH", "CI", "CM", "CU", "DO", "DM", "GD", "GY", "HT", "JM", "KN", "LC", "LU", "MA", "MC", "ML", "MQ", "PR", "SN", "SR", "SX", "TT", "VC", "VI"),
			"fy": ("Western Frisian", _("Western Frisian"), "Frysk", "ISO-8859-15", "NL", "DE"),
			"ga": ("Irish", _("Irish"), "Gaeilge", "UTF-8", "IE"),
			"gd": ("Gaelic", _("Gaelic"), "Gàidhlig", "UTF-8", "GB"),
			"gl": ("Galician", _("Galician"), "Galego", "UTF-8", "ES"),
			"gn": ("Guarani", _("Guarani"), "Avañe'ẽ", "UTF-8", "PY"),
			"gu": ("Gujarati", _("Gujarati"), "ગુજરાતી", "UTF-8", "IN"),
			"gv": ("Manx", _("Manx"), "Gaelg / Gailck", "UTF-8", "GB"),
			"ha": ("Hausa", _("Hausa"), "هَوُسَ", "UTF-8", "NG"),
			"he": ("Hebrew", _("Hebrew"), "עברית‎", "ISO-8859-15", "IL"),
			"hi": ("Hindi", _("Hindi"), "हिन्दी / हिंदी", "UTF-8", "IN"),
			"ho": ("Hiri Motu", _("Hiri Motu"), "Hiri Motu", "UTF-8"),
			"hr": ("Croatian", _("Croatian"), "Hrvatski Jezik", "ISO-8859-15", "HR"),
			"ht": ("Haitian / Haitian Creole", _("Haitian / Haitian Creole"), "Kreyòl ayisyen", "UTF-8", "HT"),
			"hu": ("Hungarian", _("Hungarian"), "Magyar", "ISO-8859-15", "HU"),
			"hy": ("Armenian", _("Armenian"), "Հայերեն", "UTF-8", "AM"),
			"hz": ("Herero", _("Herero"), "Otjiherero", "UTF-8"),
			"ia": ("Interlingua", _("Interlingua"), "Interlingua", "UTF-8", "FR"),
			"id": ("Indonesian", _("Indonesian"), "Bahasa Indonesia", "ISO-8859-15", "ID"),
			"ie": ("Interlingue / Occidental", _("Interlingue / Occidental"), "Interlingue", "UTF-8"),
			"ig": ("Igbo", _("Igbo"), "Asụsụ Igbo", "UTF-8", "NG"),
			"ii": ("Sichuan Yi / Nuosu", _("Sichuan Yi / Nuosu"), "ꆈꌠ꒿ Nuosuhxop", "UTF-8"),
			"ik": ("Inupiaq", _("Inupiaq"), "Iñupiaq / Iñupiatun", "UTF-8", "CA"),
			"io": ("Ido", _("Ido"), "Ido", "UTF-8"),
			"is": ("Icelandic", _("Icelandic"), "Íslenska", "ISO-8859-15", "IS"),
			"it": ("Italian", _("Italian"), "Italiano", "ISO-8859-15", "IT", "CH"),
			"iu": ("Inuktitut", _("Inuktitut"), "ᐃᓄᒃᑎᑐᑦ", "UTF-8", "CA"),
			"ja": ("Japanese", _("Japanese"), "日本語 (にほんご)", "UTF-8", "JP"),
			"jv": ("Javanese", _("Javanese"), "ꦧꦱꦗꦮ / Basa Jawa", "UTF-8"),
			"ka": ("Georgian", _("Georgian"), "ქართული", "UTF-8", "GE"),
			"kg": ("Kongo", _("Kongo"), "Kikongo", "UTF-8"),
			"ki": ("Kikuyu / Gikuyu", _("Kikuyu / Gikuyu"), "Gĩkũyũ", "UTF-8"),
			"kj": ("Kuanyama / Kwanyama", _("Kuanyama / Kwanyama"), "Kuanyama", "UTF-8"),
			"kk": ("Kazakh", _("Kazakh"), "Қазақ тілі", "UTF-8", "KZ"),
			"kl": ("Kalaallisut / Greenlandic", _("Kalaallisut / Greenlandic"), "Kalaallisut / Kalaallit oqaasii", "UTF-8", "GL"),
			"km": ("Central Khmer", _("Central Khmer"), "ខ្មែរ, ខេមរភាសា, ភាសាខ្មែរ", "UTF-8", "KH"),
			"kn": ("Kannada", _("Kannada"), "ಕನ್ನಡ", "UTF-8", "IN"),
			"ko": ("Korean", _("Korean"), "한국어", "UTF-8", "KR"),
			"kr": ("Kanuri", _("Kanuri"), "Kanuri", "UTF-8"),
			"ks": ("Kashmiri", _("Kashmiri"), "कश्मीरी / كشميري", "UTF-8", "IN"),
			"ku": ("Kurdish", _("Kurdish"), "Kurdî / کوردی", "ISO-8859-15", "TR"),
			"kv": ("Komi", _("Komi"), "Коми кыв", "UTF-8"),
			"kw": ("Cornish", _("Cornish"), "Kernewek", "UTF-8", "GB"),
			"ky": ("Kirghiz / Kyrgyz", _("Kirghiz / Kyrgyz"), "Кыргызча, Кыргыз тили", "UTF-8", "KG"),
			"la": ("Latin", _("Latin"), "Latine / Lingua Latina", "UTF-8"),
			"lb": ("Luxembourgish / Letzeburgesch", _("Luxembourgish / Letzeburgesch"), "Lëtzebuergesch", "UTF-8", "LU"),
			"lg": ("Ganda", _("Ganda"), "Luganda", "UTF-8", "UG"),
			"li": ("Limburgan / Limburger / Limburgish", _("Limburgan / Limburger / Limburgish"), "Limburgs", "UTF-8", "BE", "NL"),
			"ln": ("Lingala", _("Lingala"), "Lingála", "UTF-8", "CD"),
			"lo": ("Lao", _("Lao"), "ພາສາລາວ", "UTF-8", "LA"),
			"lt": ("Lithuanian", _("Lithuanian"), "Lietuvių Kalba", "ISO-8859-15", "LT"),
			"lu": ("Luba-Katanga", _("Luba-Katanga"), "Kiluba", "UTF-8"),
			"lv": ("Latvian", _("Latvian"), "Latviešu Valoda", "ISO-8859-15", "LV"),
			"mg": ("Malagasy", _("Malagasy"), "Fiteny Malagasy", "UTF-8", "MG"),
			"mh": ("Marshallese", _("Marshallese"), "Kajin M̧ajeļ", "UTF-8", "MH"),
			"mi": ("Maori", _("Maori"), "te reo Māori", "UTF-8", "NZ"),
			"mk": ("Macedonian", _("Macedonian"), "Македонски Јазик", "UTF-8", "MK"),
			"ml": ("Malayalam", _("Malayalam"), "മലയാളം", "UTF-8", "IN"),
			"mn": ("Mongolian", _("Mongolian"), "Монгол хэл", "UTF-8", "MN"),
			"mr": ("Marathi", _("Marathi"), "मराठी", "UTF-8", "IN"),
			"ms": ("Malay", _("Malay"), "Bahasa Melayu, بهاس ملايو", "UTF-8", "MY"),
			"mt": ("Maltese", _("Maltese"), "Malti", "UTF-8", "MT"),
			"my": ("Burmese", _("Burmese"), "ဗမာစာ", "UTF-8", "MM"),
			"na": ("Nauru", _("Nauru"), "Dorerin Naoero", "UTF-8"),
			"nb": ("Norwegian Bokml", _("Norwegian Bokml"), "Norsk Bokmål", "ISO-8859-15", "NO"),
			"nd": ("North Ndebele", _("North Ndebele"), "isiNdebele", "UTF-8"),
			"ne": ("Nepali", _("Nepali"), "नेपाली", "UTF-8", "NP"),
			"ng": ("Ndonga", _("Ndonga"), "Owambo", "UTF-8"),
			"nl": ("Dutch / Flemish", _("Dutch / Flemish"), "Nederlands / Vlaams", "ISO-8859-15", "NL", "AW", "BE"),
			"nn": ("Norwegian Nynorsk", _("Norwegian Nynorsk"), "Norsk Nynorsk", "UTF-8", "NO"),
			"no": ("Norwegian", _("Norwegian"), "Norsk", "ISO-8859-15", "NO"),
			"nr": ("South Ndebele", _("South Ndebele"), "isiNdebele", "UTF-8", "ZA"),
			"nv": ("Navajo / Navaho", _("Navajo / Navaho"), "Diné bizaad", "UTF-8"),
			"ny": ("Chichewa / Chewa / Nyanja", _("Chichewa / Chewa / Nyanja"), "ChiCheŵa / Chinyanja", "UTF-8"),
			"oc": ("Occitan", _("Occitan"), "Occitan / Lenga D'òc", "UTF-8", "FR"),
			"oj": ("Ojibwa", _("Ojibwa"), "ᐊᓂᔑᓈᐯᒧᐎᓐ", "UTF-8"),
			"om": ("Oromo", _("Oromo"), "Afaan Oromoo", "UTF-8", "ET", "KE"),
			"or": ("Oriya", _("Oriya"), "ଓଡ଼ିଆ", "UTF-8", "IN"),
			"os": ("Ossetian / Ossetic", _("Ossetian / Ossetic"), "Ирон Æвзаг", "UTF-8", "RU"),
			"pa": ("Panjabi / Punjabi", _("Panjabi / Punjabi"), "ਪੰਜਾਬੀ, پنجابی", "UTF-8", "IN", "PK"),
			"pi": ("Pali", _("Pali"), "पालि, पाळि", "UTF-8"),
			"pl": ("Polish", _("Polish"), "Język Polski, Polszczyzna", "ISO-8859-15", "PL"),
			"ps": ("Pushto / Pashto", _("Pushto / Pashto"), "پښتو", "UTF-8", "AF"),
			"pt": ("Portuguese", _("Portuguese"), "Português", "ISO-8859-15", "PT", "BR"),
			"qu": ("Quechua", _("Quechua"), "Runa Simi, Kichwa", "UTF-8"),
			"rm": ("Romansh", _("Romansh"), "Rumantsch Grischun", "UTF-8"),
			"rn": ("Rundi", _("Rundi"), "Ikirundi", "UTF-8"),
			"ro": ("Romanian", _("Romanian"), "Română", "ISO-8859-15", "RO"),
			"ru": ("Russian", _("Russian"), "Русский", "ISO-8859-15", "RU", "UA"),
			"rw": ("Kinyarwanda", _("Kinyarwanda"), "Ikinyarwanda", "UTF-8", "RW"),
			"sa": ("Sanskrit", _("Sanskrit"), "संस्कृतम्", "UTF-8", "IN"),
			"sb": ("Sorbian", _("Sorbian"), "Sorbian", "UTF-8"),  # Not in Wikipedia.
			"sc": ("Sardinian", _("Sardinian"), "Sardu", "UTF-8", "IT"),
			"sd": ("Sindhi", _("Sindhi"), "सिन्धी, سنڌي، سندھی", "UTF-8", "IN"),
			"se": ("Northern Sami", _("Northern Sami"), "Davvisámegiella", "UTF-8", "NO"),
			"sg": ("Sango", _("Sango"), "Yângâ tî sängö", "UTF-8"),
			"si": ("Sinhala / Sinhalese", _("Sinhala / Sinhalese"), "සිංහල", "UTF-8", "LK"),
			"sk": ("Slovak", _("Slovak"), "Slovenčina / Slovenský Jazyk", "ISO-8859-15", "SK"),
			"sl": ("Slovenian", _("Slovenian"), "Slovenski Jezik / Slovenščina", "ISO-8859-15", "SI"),
			"sm": ("Samoan", _("Samoan"), "Gagana Fa'a Samoa", "UTF-8", "WS"),
			"sn": ("Shona", _("Shona"), "chiShona", "UTF-8"),
			"so": ("Somali", _("Somali"), "Soomaaliga, af Soomaali", "UTF-8", "DJ", "ET", "KE", "SO"),
			"sq": ("Albanian", _("Albanian"), "Shqip", "UTF-8", "AL", "KV", "MK"),
			"sr": ("Serbian", _("Serbian"), "Српски Језик", "ISO-8859-15", "RS", "ME"),
			"ss": ("Swati", _("Swati"), "SiSwati", "UTF-8", "ZA"),
			"st": ("Sotho, Southern", _("Sotho, Southern"), "Sesotho", "UTF-8", "ZA"),
			"su": ("Sundanese", _("Sundanese"), "Basa Sunda", "UTF-8"),
			"sv": ("Swedish", _("Swedish"), "Svenska", "ISO-8859-15", "SE", "FI"),
			"sw": ("Swahili", _("Swahili"), "Kiswahili", "UTF-8", "KE", "TZ"),
			"ta": ("Tamil", _("Tamil"), "தமிழ்", "UTF-8", "IN", "LK"),
			"te": ("Telugu", _("Telugu"), "తెలుగు", "UTF-8", "IN"),
			"tg": ("Tajik", _("Tajik"), "тоҷикӣ, toçikī, تاجیکی", "UTF-8", "TJ"),
			"th": ("Thai", _("Thai"), "ไทย", "ISO-8859-15", "TH"),
			"ti": ("Tigrinya", _("Tigrinya"), "ትግርኛ", "UTF-8", "ER", "ET"),
			"tk": ("Turkmen", _("Turkmen"), "Türkmen, Түркмен", "UTF-8", "TM"),
			"tl": ("Tagalog", _("Tagalog"), "Wikang Tagalog", "UTF-8", "PH"),
			"tn": ("Tswana", _("Tswana"), "Setswana", "UTF-8", "ZA"),
			"to": ("Tonga", _("Tonga"), "Faka Tonga", "UTF-8", "TO"),
			"tr": ("Turkish", _("Turkish"), "Türkçe", "ISO-8859-15", "TR", "CY"),
			"ts": ("Tsonga", _("Tsonga"), "Xitsonga", "UTF-8", "ZA"),
			"tt": ("Tatar", _("Tatar"), "Татар теле, Tatar tele", "UTF-8", "RU"),
			"tw": ("Twi", _("Twi"), "Twi", "UTF-8"),
			"ty": ("Tahitian", _("Tahitian"), "Reo Tahiti", "UTF-8"),
			"ug": ("Uighur / Uyghur", _("Uighur / Uyghur"), "ئۇيغۇرچە‎ / Uyghurche", "UTF-8", "CN"),
			"uk": ("Ukrainian", _("Ukrainian"), "Українська", "ISO-8859-15", "UA"),
			"ur": ("Urdu", _("Urdu"), "اردو", "UTF-8", "IN", "PK"),
			"uz": ("Uzbek", _("Uzbek"), "Oʻzbek, Ўзбек, أۇزبېك", "UTF-8", "UZ"),
			"ve": ("Venda", _("Venda"), "Tshivenḓa", "UTF-8", "ZA"),
			"vi": ("Vietnamese", _("Vietnamese"), "Tiếng Việt", "UTF-8", "VN"),
			"vo": ("Volapük", _("Volapük"), "Volapük", "UTF-8"),
			"wa": ("Walloon", _("Walloon"), "Walon", "UTF-8", "BE"),
			"wo": ("Wolof", _("Wolof"), "Wollof", "UTF-8", "SN"),
			"xh": ("Xhosa", _("Xhosa"), "isiXhosa", "UTF-8", "ZA"),
			"yi": ("Yiddish", _("Yiddish"), "ייִדיש", "UTF-8", "US"),
			"yo": ("Yoruba", _("Yoruba"), "Yorùbá", "UTF-8", "NG"),
			"za": ("Zhuang / Chuang", _("Zhuang / Chuang"), "Saɯ cueŋƅ / Saw cuengh", "UTF-8"),
			"zh": ("Chinese", _("Chinese"), "中文", "UTF-8", "CN", "HK", "SG", "TW"),
			"zu": ("Zulu", _("Zulu"), "isiZulu", "UTF-8", "ZA")
		}
		self.countryData = {
			# https://www.worldatlas.com/aatlas/ctycodes.htm
			"AD": ("Andorra", _("Andorra"), "d'Andorra"),
			"AE": ("United Arab Emirates", _("United Arab Emirates"), "الإمارات العربية المتحدة‎ al-ʾImārāt al-ʿArabīyyah al-Muttaḥidah"),
			"AF": ("Afghanistan", _("Afghanistan"), "افغانستان"),
			"AG": ("Antigua and Barbuda", _("Antigua and Barbuda"), "Antigua and Barbuda"),
			"AI": ("Anguilla", _("Anguilla"), "Anguilla"),
			"AL": ("Albania", _("Albania"), "Shqipëri"),
			"AM": ("Armenia", _("Armenia"), "Հայաստան"),
			"AO": ("Angola", _("Angola"), "Angola"),
			"AQ": ("Antarctica", _("Antarctica"), "Antarctica"),
			"AR": ("Argentina", _("Argentina"), "Argentina"),
			"AS": ("American Samoa", _("American Samoa"), "Amerika Sāmoa"),
			"AT": ("Austria", _("Austria"), "Österreich"),
			"AU": ("Australia", _("Australia"), "Australia"),
			"AW": ("Aruba", _("Aruba"), "Aruba"),
			"AZ": ("Azerbaijan", _("Azerbaijan"), "Azərbaycan"),
			"BA": ("Bosnia and Herzegovina", _("Bosnia and Herzegovina"), "Bosna i Hercegovina"),
			"BB": ("Barbados", _("Barbados"), "Barbados"),
			"BD": ("Bangladesh", _("Bangladesh"), "বাংলাদেশ"),
			"BE": ("Belgium", _("Belgium"), "België"),
			"BF": ("Burkina Faso", _("Burkina Faso"), "Buʁkina Faso"),
			"BG": ("Bulgaria", _("Bulgaria"), "България"),
			"BH": ("Bahrain", _("Bahrain"), "البحرين‎"),
			"BI": ("Burundi", _("Burundi"), "y'Uburundi"),
			"BJ": ("Benin", _("Benin"), "Bénin"),
			"BL": ("Saint-Barthélemy", _("Saint-Barthélemy"), "Saint-Barthélemy"),
			"BM": ("Bermuda", _("Bermuda"), "Bermuda"),
			"BN": ("Brunei Darussalam", _("Brunei Darussalam"), "Negara Brunei Darussalam"),
			"BO": ("Bolivia", _("Bolivia"), "Mborivia"),
			"BQ": ("Bonaire", _("Bonaire"), "Bonaire"),
			"BR": ("Brazil", _("Brazil"), "Brasil"),
			"BS": ("Bahamas", _("Bahamas"), "Bahamas"),
			"BT": ("Bhutan", _("Bhutan"), "འབྲུག་རྒྱལ་ཁབ་"),
			"BV": ("Bouvet Island", _("Bouvet Island"), "Bouvetøya"),
			"BW": ("Botswana", _("Botswana"), "Botswana"),
			"BY": ("Belarus", _("Belarus"), "Беларусь"),
			"BZ": ("Belize", _("Belize"), "Belize"),
			"CA": ("Canada", _("Canada"), "Canada"),
			"CC": ("Cocos (Keeling) Islands", _("Cocos (Keeling) Islands"), "Cocos (Keeling) Islands"),
			"CD": ("Democratic Republic of the Congo", _("Democratic Republic of the Congo"), "République démocratique du Congo"),
			"CF": ("Central African Republic", _("Central African Republic"), "Ködörösêse tî Bêafrîka"),
			"CG": ("Congo", _("Congo"), "Congo"),
			"CH": ("Switzerland", _("Switzerland"), "Suisse"),
			"CI": ("Cote d'Ivoire / Ivory Coast", _("Cote d'Ivoire / Ivory Coast"), "Côte d'Ivoire"),
			"CK": ("Cook Islands", _("Cook Islands"), "Kūki 'Āirani"),
			"CL": ("Chile", _("Chile"), "Chile"),
			"CM": ("Cameroon", _("Cameroon"), "Cameroun"),
			"CN": ("China", _("China"), "中国"),
			"CO": ("Colombia", _("Colombia"), "Colombia"),
			"CR": ("Costa Rica", _("Costa Rica"), "Costa Rica"),
			"CU": ("Cuba", _("Cuba"), "Cuba"),
			"CV": ("Cape Verde", _("Cape Verde"), "Cabo Verde"),
			"CW": ("Curacao", _("Curacao"), "Kòrsou"),
			"CX": ("Christmas Island", _("Christmas Island"), "聖誕島 / Wilayah Pulau Krismas"),
			"CY": ("Cyprus", _("Cyprus"), "Κύπρος"),
			"CZ": ("Czech Republic", _("Czech Republic"), "Česká Republika"),
			"DE": ("Germany", _("Germany"), "Deutschland"),
			"DJ": ("Djibouti", _("Djibouti"), "جيبوتي‎"),
			"DK": ("Denmark", _("Denmark"), "Danmark"),
			"DM": ("Dominica", _("Dominica"), "Dominique"),
			"DO": ("Dominican Republic", _("Dominican Republic"), "República Dominicana"),
			"DZ": ("Algeria", _("Algeria"), "الجزائر‎"),
			"EC": ("Ecuador", _("Ecuador"), "Ikwayur"),
			"EE": ("Estonia", _("Estonia"), "Eesti"),
			"EG": ("Egypt", _("Egypt"), "ِصر‎"),
			"EH": ("Western Sahara", _("Western Sahara"), "الصحراء الغربية"),
			"ER": ("Eritrea", _("Eritrea"), "ኤርትራ"),
			"ES": ("Spain", _("Spain"), "España"),
			"ET": ("Ethiopia", _("Ethiopia"), "ኢትዮጵያ"),
			"FI": ("Finland", _("Finland"), "Suomi"),
			"FJ": ("Fiji", _("Fiji"), "Viti"),
			"FK": ("Falkland Islands (Malvinas)", _("Falkland Islands (Malvinas)"), "Islas Malvinas"),
			"FM": ("Micronesia, Federated States of", _("Micronesia, Federated States of"), "Micronesia, Federated States of"),
			"FO": ("Faroe Islands", _("Faroe Islands"), "Føroyar"),
			"FR": ("France", _("France"), "Française"),
			"GA": ("Gabon", _("Gabon"), "Gabonaise"),
			"GB": ("United Kingdom", _("United Kingdom"), "United Kingdom"),
			"GD": ("Grenada", _("Grenada"), "Grenada"),
			"GE": ("Georgia", _("Georgia"), "საქართველო"),
			"GF": ("French Guiana", _("French Guiana"), "Guyane"),
			"GG": ("Guernsey", _("Guernsey"), "Guernési"),
			"GH": ("Ghana", _("Ghana"), "Ghana"),
			"GI": ("Gibraltar", _("Gibraltar"), "جبل طارق"),
			"GL": ("Greenland", _("Greenland"), "Grønland"),
			"GM": ("Gambia", _("Gambia"), "Gambia"),
			"GN": ("Guinea", _("Guinea"), "Guinée"),
			"GP": ("Guadeloupe", _("Guadeloupe"), "Gwadloup"),
			"GQ": ("Equatorial Guinea", _("Equatorial Guinea"), "Guinea Ecuatorial"),
			"GR": ("Greece", _("Greece"), "Ελληνική Δημοκρατία"),
			"GS": ("South Georgia and the South Sandwich Islands", _("South Georgia and the South Sandwich Islands"), "South Georgia and the South Sandwich Islands"),
			"GT": ("Guatemala", _("Guatemala"), "Guatemala"),
			"GU": ("Guam", _("Guam"), "Guåhån"),
			"GW": ("Guinea-Bissau", _("Guinea-Bissau"), "Guiné-Bissau"),
			"GY": ("Guyana", _("Guyana"), "Guyana"),
			"HK": ("Hong Kong", _("Hong Kong"), "香港"),
			"HM": ("Heard Island and McDonald Islands", _("Heard Island and McDonald Islands"), "Heard Island and McDonald Islands"),
			"HN": ("Honduras", _("Honduras"), "Honduras"),
			"HR": ("Croatia", _("Croatia"), "Hrvatska"),
			"HT": ("Haiti", _("Haiti"), "Haïti"),
			"HU": ("Hungary", _("Hungary"), "Magyarország"),
			"ID": ("Indonesia", _("Indonesia"), "Indonesia"),
			"IE": ("Ireland", _("Ireland"), "Éire"),
			"IL": ("Israel", _("Israel"), "ישראל"),
			"IM": ("Isle of Man", _("Isle of Man"), "Mannin"),
			"IN": ("India", _("India"), "Bhārat"),
			"IO": ("British Indian Ocean Territory", _("British Indian Ocean Territory"), "British Indian Ocean Territory"),
			"IQ": ("Iraq", _("Iraq"), "ٱلْعِرَاق‎"),
			"IR": ("Iran, Islamic Republic of", _("Iran, Islamic Republic of"), "جمهوری اسلامی ایران"),
			"IS": ("Iceland", _("Iceland"), "Ísland"),
			"IT": ("Italy", _("Italy"), "Italia"),
			"JE": ("Jersey", _("Jersey"), "Jèrri"),
			"JM": ("Jamaica", _("Jamaica"), "Jumieka"),
			"JO": ("Jordan", _("Jordan"), "الْأُرْدُنّ‎"),
			"JP": ("Japan", _("Japan"), "日本"),
			"KE": ("Kenya", _("Kenya"), "Kenya"),
			"KG": ("Kyrgyzstan", _("Kyrgyzstan"), "Kırğızstan"),
			"KH": ("Cambodia", _("Cambodia"), "កម្ពុជា"),
			"KI": ("Kiribati", _("Kiribati"), "Kiribati"),
			"KM": ("Comoros", _("Comoros"), "جزر القمر‎"),
			"KN": ("Saint Kitts and Nevis", _("Saint Kitts and Nevis"), "Saint Kitts and Nevis"),
			"KP": ("Korea, Democratic People's Republic of", _("Korea, Democratic People's Republic of"), "조선"),
			"KR": ("Korea, Republic of", _("Korea, Republic of"), "한국"),
			"KW": ("Kuwait", _("Kuwait"), "الكويت‎"),
			"KY": ("Cayman Islands", _("Cayman Islands"), "Cayman Islands"),
			"KZ": ("Kazakhstan", _("Kazakhstan"), "Қазақстан"),
			"LA": ("Lao People's Democratic Republic", _("Lao People's Democratic Republic"), "ລາວ"),
			"LB": ("Lebanon", _("Lebanon"), "لبنان‎"),
			"LC": ("Saint Lucia", _("Saint Lucia"), "Sainte-Lucie"),
			"LI": ("Liechtenstein", _("Liechtenstein"), "Liechtenstein"),
			"LK": ("Sri Lanka", _("Sri Lanka"), "ශ්‍රී ලංකා Śrī Laṃkā"),
			"LR": ("Liberia", _("Liberia"), "Liberia"),
			"LS": ("Lesotho", _("Lesotho"), "Lesotho"),
			"LT": ("Lithuania", _("Lithuania"), "Lietuva"),
			"LU": ("Luxembourg", _("Luxembourg"), "Lëtzebuerg"),
			"LV": ("Latvia", _("Latvia"), "Latvija"),
			"LY": ("Libya", _("Libya"), "ليبيا‎"),
			"MA": ("Morocco", _("Morocco"), "المغرب‎"),
			"MC": ("Monaco", _("Monaco"), "Monaco"),
			"MD": ("Moldova, Republic of", _("Moldova, Republic of"), "Republica Moldova"),
			"ME": ("Montenegro", _("Montenegro"), "Црна Гора"),
			"MF": ("Saint Martin (French part)", _("Saint Martin (French part)"), "Saint-Martin"),
			"MG": ("Madagascar", _("Madagascar"), "Madagasikara"),
			"MH": ("Marshall Islands", _("Marshall Islands"), "Aolepān Aorōkin M̧ajeļ"),
			"MK": ("Macedonia, Former Yugoslav Republic of", _("Macedonia, Former Yugoslav Republic of"), "Република Северна Македонија"),
			"ML": ("Mali", _("Mali"), "Mali"),
			"MM": ("Myanmar", _("Myanmar"), "မြန်မာ"),
			"MN": ("Mongolia", _("Mongolia"), "Монгол Улс"),
			"MO": ("Macao", _("Macao"), "澳門"),
			"MP": ("Northern Mariana Islands", _("Northern Mariana Islands"), "Northern Mariana Islands"),
			"MQ": ("Martinique", _("Martinique"), "Matnik / Matinik"),
			"MR": ("Mauritania", _("Mauritania"), "موريتانيا‎"),
			"MS": ("Montserrat", _("Montserrat"), "Montserrat"),
			"MT": ("Malta", _("Malta"), "Malta"),
			"MU": ("Mauritius", _("Mauritius"), "Maurice"),
			"MV": ("Maldives", _("Maldives"), "ދިވެހިރާއްޖެ"),
			"MW": ("Malawi", _("Malawi"), "Malaŵi"),
			"MX": ("Mexico", _("Mexico"), "Mēxihco"),
			"MY": ("Malaysia", _("Malaysia"), "Məlejsiə"),
			"MZ": ("Mozambique", _("Mozambique"), "Moçambique"),
			"NA": ("Namibia", _("Namibia"), "Namibia"),
			"NC": ("New Caledonia", _("New Caledonia"), "Nouvelle-Calédonie"),
			"NE": ("Niger", _("Niger"), "Niger"),
			"NF": ("Norfolk Island", _("Norfolk Island"), "Norf'k Ailen"),
			"NG": ("Nigeria", _("Nigeria"), "Nijeriya"),
			"NI": ("Nicaragua", _("Nicaragua"), "Nicaragua"),
			"NL": ("Netherlands", _("Netherlands"), "Nederland"),
			"NO": ("Norway", _("Norway"), "Norge / Noreg"),
			"NP": ("Nepal", _("Nepal"), "नेपाल"),
			"NR": ("Nauru", _("Nauru"), "Naoero"),
			"NU": ("Niue", _("Niue"), "Niuē"),
			"NZ": ("New Zealand", _("New Zealand"), "New Zealand"),
			"OM": ("Oman", _("Oman"), "عمان‎"),
			"PA": ("Panama", _("Panama"), "Panamá"),
			"PE": ("Peru", _("Peru"), "Perú"),
			"PF": ("French Polynesia", _("French Polynesia"), "Polynésie française"),
			"PG": ("Papua New Guinea", _("Papua New Guinea"), "Papua Niugini"),
			"PH": ("Philippines", _("Philippines"), "Pilipinas"),
			"PK": ("Pakistan", _("Pakistan"), "اِسلامی جمہوریہ پاكِستان"),
			"PL": ("Poland", _("Poland"), "Polska"),
			"PM": ("Saint Pierre and Miquelon", _("Saint Pierre and Miquelon"), "Saint-Pierre-et-Miquelon"),
			"PN": ("Pitcairn", _("Pitcairn"), "Pitkern Ailen"),
			"PR": ("Puerto Rico", _("Puerto Rico"), "Puerto Rico"),
			"PS": ("Palestine, State of", _("Palestine, State of"), "فلسطين‎"),
			"PT": ("Portugal", _("Portugal"), "Portuguesa"),
			"PW": ("Palau", _("Palau"), "Belau"),
			"PY": ("Paraguay", _("Paraguay"), "Paraguái"),
			"QA": ("Qatar", _("Qatar"), "قطر‎"),
			"RE": ("Réunion", _("Réunion"), "La Réunion"),
			"RO": ("Romania", _("Romania"), "România"),
			"RS": ("Serbia", _("Serbia"), "Србија"),
			"RU": ("Russian Federation", _("Russian Federation"), "Росси́йская Федера́ция"),
			"RW": ("Rwanda", _("Rwanda"), "Rwanda"),
			"SA": ("Saudi Arabia", _("Saudi Arabia"), "المملكة العربية السعودية"),
			"SB": ("Solomon Islands", _("Solomon Islands"), "Solomon Aelan"),
			"SC": ("Seychelles", _("Seychelles"), "Seychelles"),
			"SD": ("Sudan", _("Sudan"), "السودان‎ as-Sūdān"),
			"SE": ("Sweden", _("Sweden"), "Sverige"),
			"SG": ("Singapore", _("Singapore"), "Singapore"),
			"SH": ("Saint Helena", _("Saint Helena"), "Saint Helena"),
			"SI": ("Slovenia", _("Slovenia"), "Slovenija"),
			"SJ": ("Svalbard and Jan Mayen", _("Svalbard and Jan Mayen"), "Svalbard og Jan Mayen"),
			"SK": ("Slovakia", _("Slovakia"), "Slovensko"),
			"SL": ("Sierra Leone", _("Sierra Leone"), "Sierra Leone"),
			"SM": ("San Marino", _("San Marino"), "San Marino"),
			"SN": ("Senegal", _("Senegal"), "Sénégal"),
			"SO": ("Somalia", _("Somalia"), "Soomaaliya"),
			"SR": ("Suriname", _("Suriname"), "Suriname"),
			"SS": ("South Sudan", _("South Sudan"), "South Sudan"),
			"ST": ("Sao Tome and Principe", _("Sao Tome and Principe"), "São Tomé e Principe"),
			"SV": ("El Salvador", _("El Salvador"), "el salβaˈðoɾ"),
			"SX": ("Sint Maarten", _("Sint Maarten"), "Sint Maarten"),
			"SY": ("Syria", _("Syria"), "سوريا‎"),
			"SZ": ("Swaziland / Eswatini", _("Swaziland / Eswatini"), "eSwatini"),
			"TC": ("Turks and Caicos Islands", _("Turks and Caicos Islands"), "Turks and Caicos Islands"),
			"TD": ("Chad", _("Chad"), "تشاد‎"),
			"TF": ("French Southern Territories", _("French Southern Territories"), "Terres australes et antarctiques françaises"),
			"TG": ("Togo", _("Togo"), "Togolaise"),
			"TH": ("Thailand", _("Thailand"), "ราชอาณาจักรไทย"),
			"TJ": ("Tajikistan", _("Tajikistan"), "Тоҷикистон"),
			"TK": ("Tokelau", _("Tokelau"), "Tokelau"),
			"TL": ("Timor-Leste / East Timor", _("Timor-Leste / East Timor"), "Timór Lorosa'e"),
			"TM": ("Turkmenistan", _("Turkmenistan"), "Türkmenistan"),
			"TN": ("Tunisia", _("Tunisia"), "الجمهورية التونسية"),
			"TO": ("Tonga", _("Tonga"), "Tonga"),
			"TR": ("Turkey", _("Turkey"), "Türkiye"),
			"TT": ("Trinidad and Tobago", _("Trinidad and Tobago"), "Trinidad and Tobago"),
			"TV": ("Tuvalu", _("Tuvalu"), "Tuvalu"),
			"TW": ("Taiwan", _("Taiwan"), "中華民國"),
			"TZ": ("Tanzania", _("Tanzania"), "Tanzania"),
			"UA": ("Ukraine", _("Ukraine"), "Україна"),
			"UG": ("Uganda", _("Uganda"), "Jamhuri ya Uganda"),
			"UM": ("United States Minor Outlying Islands", _("United States Minor Outlying Islands"), "United States Minor Outlying Islands"),
			"US": ("United States", _("United States"), "United States"),
			"UY": ("Uruguay", _("Uruguay"), "Uruguay"),
			"UZ": ("Uzbekistan", _("Uzbekistan"), "Oʻzbekiston"),
			"VA": ("Holy See (Vatican City State)", _("Holy See (Vatican City State)"), "Santa Sede (Stato della Città del Vaticano)"),
			"VC": ("Saint Vincent and the Grenadines", _("Saint Vincent and the Grenadines"), "Saint Vincent and the Grenadines"),
			"VE": ("Venezuela", _("Venezuela"), "Venezuela"),
			"VG": ("British Virgin Islands", _("British Virgin Islands"), "British Virgin Islands"),
			"VI": ("US Virgin Islands", _("US Virgin Islands"), "US Virgin Islands"),
			"VN": ("Viet Nam", _("Viet Nam"), "Việt Nam"),
			"VU": ("Vanuatu", _("Vanuatu"), "Vanuatu"),
			"WF": ("Wallis and Futuna", _("Wallis and Futuna"), "Wallis-et-Futuna"),
			"WS": ("Samoa", _("Samoa"), "Sāmoa"),
			"YE": ("Yemen", _("Yemen"), "ٱلْيَمَن‎"),
			"YT": ("Mayotte", _("Mayotte"), "Mayotte"),
			"ZA": ("South Africa", _("South Africa"), "South Africa"),
			"ZM": ("Zambia", _("Zambia"), "Zambia"),
			"ZW": ("Zimbabwe", _("Zimbabwe"), "Zimbabwe")
		}
		self.categories = [
			("LC_ALL", locale.LC_ALL),
			("LC_ADDRESS", None),
			("LC_COLLATE", locale.LC_COLLATE),
			("LC_CTYPE", locale.LC_CTYPE),
			("LC_DATE", None),
			("LC_IDENTIFICATION", None),
			("LC_MEASUREMENT", None),
			("LC_MESSAGES", locale.LC_MESSAGES),
			("LC_MONETARY", locale.LC_MONETARY),
			("LC_NAME", None),
			("LC_NUMERIC", locale.LC_NUMERIC),
			("LC_PAPER", None),
			("LC_TELEPHONE", None),
			("LC_TIME", locale.LC_TIME)
		]
		self.languagePath = resolveFilename(SCOPE_LANGUAGE)
		gettext.install("enigma2", self.languagePath, unicode=0, codeset="utf-8")
		gettext.bindtextdomain("enigma2", self.languagePath)
		gettext.textdomain("enigma2")
		self.availablePackages = []
		self.installedPackages = []
		self.packageDirectories = []
		self.localeList = ["en_US"]
		self.activeLocale = "en_US"
		self.catalog = None
		self.callbacks = []
		self.languageListSelection = []  # For PluginBrowser
		self.InitLang()

	def InitLang(self):
		self.availablePackages = self.getAvailablePackages()
		self.installedPackages = self.getInstalledPackages()
		self.packageDirectories = self.getPackageDirectories()
		if self.packageDirectories != self.installedPackages:
			print "[Language] Warning: Installed language packages and language directory contents do not match!"
		uniqueLocales = set(["en_US"])
		for package in self.installedPackages:
			# print "[Language] DEBUG: Package='%s'" % package
			locales = self.packageToLocales(package)
			self.languageListSelection.append((locales[0], self.languageData[self.getLanguage(locales[0])][self.LANG_NAME]))  # For PluginBrowser
			for loc in locales:
				# print "[Language] DEBUG: Locale='%s'" % loc
				uniqueLocales.add(loc)
		self.localeList = sorted(list(uniqueLocales))

	def activateLanguage(self, lang, runCallbacks=True):
		# These two lines are a hack to keep old code working even though the old calling code probably uses a locale and not a language!
		if len(lang) > 3:
			return self.activateLocale(lang, runCallbacks=runCallbacks)
		try:
			loc = "%s_%s" % (lang, self.languageData[lang][self.LANG_COUNTRYCODE])
		except IndexError:
			loc = "en_US"
		# print "[Language] Language '%s' is being activated as locale '%s'." % (lang, loc)
		return self.activateLocale(loc, runCallbacks=runCallbacks)

	def activateLocale(self, loc, runCallbacks=True):
		if loc not in self.localeList:
			print "[Language] Selected locale '%s' is not installed or does not exist!" % loc
		else:
			if loc == self.activeLocale:
				print "[Language] Language '%s', locale '%s' is already active." % (self.getLanguage(loc), loc)
			else:
				# print "[Language] Activating language '%s', locale '%s'." % (self.getLanguage(loc), loc)
				self.activeLocale = loc
				self.catalog = gettext.translation("enigma2", self.languagePath, languages=[loc], fallback=True)
				self.catalog.install(names=("ngettext", "pgettext"))
				localeError = None
				for category in self.categories:
					# This should be checked against a unified Operating System locale installation.
					environ[category[self.CAT_ENVIRONMENT]] = "%s.UTF-8" % loc
					if category[self.CAT_PYTHON] is not None:
						try:  # Try and set the Python locale to the current locale.
							locale.setlocale(category[self.CAT_PYTHON], (loc, "UTF-8"))
						except locale.Error:
							try:  # If unavailable, try for the Python locale to the language base locale.
								locales = self.packageToLocales(self.getLanguage(loc))
								locale.setlocale(category[self.CAT_PYTHON], (locales[0], "UTF-8"))
								replacement = locales[0]
							except locale.Error:  # If unavailable fall back to the US English locale.
								locale.setlocale(category[self.CAT_PYTHON], ("en_US", "UTF-8"))
								replacement = "en_US"
							if localeError is None:
								localeError = replacement
								# print "[Language] Warning: Locale '%s' is not available in Python, using locale '%s' instead." % (loc, replacement)
				environ["LANG"] = "%s.UTF-8" % loc
				environ["LANGUAGE"] = "%s.UTF-8" % loc
				environ["GST_SUBTITLE_ENCODING"] = self.getGStreamerSubtitleEncoding()
				if runCallbacks:
					for method in self.callbacks:
						if method:
							method()

	def addCallback(self, callback):
		self.callbacks.append(callback)

	def getActiveCatalog(self):
		return self.catalog

	def getAvailablePackages(self):
		command = ["opkg", "find", "enigma2-locale-*"]
		availablePackages = set()
		try:
			process = Popen(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
			packageText, errorText = process.communicate()
			if errorText:
				print "[Language] Error: %s (getLanguagePackages)" % errorText
			else:
				for language in packageText.split("\n"):
					if language and "meta" not in language:
						availablePackages.add(language[15:].split(" ")[0])
				availablePackages = sorted(list(availablePackages))
		except (IOError, OSError) as err:
			# print "[Language] Error %d: getLanguagePackages - %s ('%s')" % (err.errno, err.strerror, command[0])
			availablePackages = []
		# print "[Language] DEBUG: %d languages available." % len(availablePackages)
		# print "[Language] DEBUG: Available language modules:\n%s" % availablePackages
		return availablePackages

	def getInstalledPackages(self):
		command = ["opkg", "status", "enigma2-locale-*"]
		installedPackages = []
		try:
			process = Popen(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
			packageText, errorText = process.communicate()
			if errorText:
				print "[Language] Error: %s (getInstalledPackages)" % errorText
			else:
				for package in packageText.split("\n\n"):
					if package.startswith("Package: enigma2-locale-") and "meta" not in package:
						list = []
						for data in package.split("\n"):
							if data.startswith("Package: "):
								installedPackages.append(data[24:])
								break
				installedPackages = sorted(installedPackages)
		except (IOError, OSError) as err:
			print "[Language] Error %d: getInstalledPackages - %s ('%s')" % (err.errno, err.strerror, command[0])
		# print "[Language] DEBUG: %d installed languages." % len(installedPackages)
		# print "[Language] DEBUG: Installed language modules:\n%s" % installedPackages
		return installedPackages

	def getPackageDirectories(self):
		# Adapt language directory entries to match the package format.
		packageDirectories = [dir.replace("_", "-").lower() for dir in sorted(listdir(self.languagePath))]
		# print "[Language] DEBUG: %d installed language directories." % len(packageDirectories)
		# print "[Language] DEBUG: Installed language directories:\n%s" % packageDirectories
		return packageDirectories

	def packageToLocales(self, package):
		loc = package.replace("-", "_")
		data = self.splitLocale(loc)
		locales = []
		if data[1]:
			locales.append("%s_%s" % (data[0], data[1].upper()))
		else:
			for country in self.languageData.get(data[0], tuple([None] * self.LANG_MAX))[self.LANG_COUNTRYCODE:]:
				locales.append("%s_%s" % (data[0], country))
		return locales

	def splitLocale(self, loc):
		data = loc.split("_")
		if len(data) < 2:
			data.append(None)
		return data

	def splitPackage(self, package):
		data = package.split("-")
		if len(data) < 2:
			data.append(None)
		else:
			data[1] = data[1].upper()
		return data

	def getCountry(self, loc=None):
		if loc is None:
			loc = self.getLocale()
		return self.splitLocale(loc)[1]

	def getCountryName(self, loc=None):
		return self.countryData.get(self.getCountry(loc), tuple([None] * self.COUNTRY_MAX))[self.COUNTRY_NAME]

	def getCountryNative(self, loc=None):
		return self.countryData.get(self.getCountry(loc), tuple([None] * self.COUNTRY_MAX))[self.COUNTRY_NATIVE]

	def getLanguage(self, loc=None):
		if loc is None:
			loc = self.getLocale()
		return self.splitLocale(loc)[0]

	def getLanguageName(self, loc=None):
		return self.languageData.get(self.getLanguage(loc), tuple([None] * self.LANG_MAX))[self.LANG_NAME]

	def getLanguageNative(self, loc=None):
		return self.languageData.get(self.getLanguage(loc), tuple([None] * self.LANG_MAX))[self.LANG_NATIVE]

	def getLocale(self):
		return "en_US" if self.activeLocale is None else self.activeLocale

	def getLanguageList(self):
		languageList = set()
		for loc in self.localeList:
			languageList.add(self.getLanguage(loc))
		languageList = sorted(languageList)
		# print "[Language] DEBUG: %d installed languages." % len(languageList)
		# print "[Language] DEBUG: Installed languages:\n%s" % languageList
		return languageList

	def getLocaleList(self):
		return self.localeList

	def getPackage(self, loc=None):
		if loc is None:
			loc = self.getLocale()
		lang = self.getLanguage(loc)
		pack = loc.replace("_", "-").lower()
		if pack in self.availablePackages:
			package = pack
		elif lang in self.availablePackages:
			package = lang
		else:
			package = None
		return package

	def getGStreamerSubtitleEncoding(self, loc=None):
		try:
			return self.languageData[self.getLanguage(loc)][self.LANG_ENCODING]
		except IndexError:
			return "ISO-8859-15"

	def getLanguageListSelection(self):  # For PluginBrowser
		return self.languageListSelection

	def deleteLanguagePackages(self, packageList):
		return self.runPackageManager(cmdList=["opkg", "remove", "--autoremove", "--force-depends", "enigma2-locale-%s"], packageList=packageList, action=_("deleted"))

	def installLanguagePackages(self, packageList):
		return self.runPackageManager(cmdList=["opkg", "install", "enigma2-locale-%s"], packageList=packageList, action=_("installed"))

	def runPackageManager(self, cmdList=None, packageList=None, action=""):
		status = []
		if cmdList is not None and packageList is not None:
			for package in packageList:
				cmdList = [cmd % package if "%s" in cmd else cmd for cmd in cmdList]
				lang = self.splitPackage(package)[0]
				try:
					process = Popen(cmdList, stdout=PIPE, stderr=PIPE, universal_newlines=True)
					packageText, errorText = process.communicate()
					if errorText:
						# print "[Language] Package manager error: %s" % errorText
						status.append(_("Error: Language %s (%s) not %s!") % (self.languageData[lang][self.LANG_NAME], self.languageData[lang][self.LANG_NATIVE], action))
					else:
						status.append(_("Language %s (%s) %s.") % (self.languageData[lang][self.LANG_NAME], self.languageData[lang][self.LANG_NATIVE], action))
					# print "[Language] DEBUG: Package manager exit status 1 = %d" % process.returncode
				except (IOError, OSError) as err:
					# print "[Language] Package manager error %d: %s ('%s')" % (err.errno, err.strerror, command[0])
					status.append(_("Error: Language %s (%s) not %s!") % (self.languageData[lang][self.LANG_NAME], self.languageData[lang][self.LANG_NATIVE], action))
					# print "[Language] DEBUG: Package manager exit status 2 = %d" % process.returncode
			self.InitLang()
		return status

language = Language()
