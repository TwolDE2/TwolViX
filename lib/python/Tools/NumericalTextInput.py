from builtins import range
import sys
import six
from enigma import eTimer
from Components.Language import language


MAP_SEARCH_UPCASE = "SearchUpper"  # NOTE: Legacy interface for previous and deprecated versions of NumericalTextInput.
MAP_SEARCH = "SearchLower"

MODES = {
	"DEFAULT": 0,
	"DEFAULTUPPER": 1,
	"DEFAULTLOWER": 2,
	"HEX": 6,
	"HEXUPPER": 7,
	"HEXLOWER": 8,
	"HEXFAST": 9,
	"HEXFASTUPPER": 10,
	"HEXFASTLOWER": 11,
	"HEXFASTLOGICAL": 12,
	"HEXFASTLOGICALUPPER": 13,
	"HEXFASTLOGICALLOWER": 14,
	"SEARCH": 3,
	"SEARCHUPPER": 4,
	"SEARCHLOWER": 5
}
if sys.version_info >= (3, 0):
	PUNCTUATION0 = "0,?!'\"\\()<>[]{}~^`|"
	PUNCTUATION1 = "1 .:;+-*/=_@#$%&"

	MAPPINGS = (
		# Text, TextUpper, TextLower, Search, SearchUpper, SearchLower, Hex, HexUpper, HexLower, HexFast, HexFastUpper, HexFastLower, HexLogical, HexLogicalUpper, HexLogicalLower
		(PUNCTUATION0, PUNCTUATION0, PUNCTUATION0, "%_0", "%_0", "%_0", "0", "0", "0", "0", "0", "0", "0Aa", "0A", "0a"),
		(PUNCTUATION1, PUNCTUATION1, PUNCTUATION1, " 1", " 1", " 1", "1AaBbCc", "1ABC", "1abc", "1Aa", "1A", "1a", "1Bb", "1B", "1b"),
		("abc2ABC", "ABC2", "abc2", "abc2ABC", "ABC2", "abc2", "2DdEeFf", "2DEF", "2def", "2Bb", "2B", "2b", "2Cc", "2C", "2c"),
		("def3DEF", "DEF3", "def3", "def3DEF", "DEF3", "def3", "3", "3", "3", "3Cc", "3C", "3c", "3Dd", "3D", "3d"),
		("ghi4GHI", "GHI4", "ghi4", "ghi4GHI", "GHI4", "ghi4", "4", "4", "4", "4Dd", "4D", "4d", "4Ee", "4E", "4e"),
		("jkl5JKL", "JKL5", "jkl5", "jkl5JKL", "JKL5", "jkl5", "5", "5", "5", "5Ee", "5E", "5e", "5Ff", "5F", "5f"),
		("mno6MNO", "MNO6", "mno6", "mno6MNO", "MNO6", "mno6", "6", "6", "6", "6Ff", "6F", "6f", "6", "6", "6"),
		("pqrs7PQRS", "PQRS7", "pqrs7", "pqrs7PQRS", "PQRS7", "pqrs7", "7", "7", "7", "7", "7", "7", "7", "7", "7"),
		("tuv8TUV", "TUV8", "tuv8", "tuv8TUV", "TUV8", "tuv8", "8", "8", "8", "8", "8", "8", "8", "8", "8"),
		("wxyz9WXYZ", "WXYZ9", "wxyz9", "wxyz9WXYZ", "WXYZ9", "wxyz9", "9", "9", "9", "9", "9", "9", "9", "9", "9")
	)

	LOCALES = {
		"cs_CZ": (
			(None, None, None),
			(None, None, None),
			("abc2\u00E1\u010DABC\u00C1\u010C", "ABC2\u00C1\u010C", "abc2\u00E1\u010D"),
			("def3\u010F\u00E9\u011BDEF\u010E\u00C9\u011A", "DEF3\u010E\u00C9\u011A", "def3\u010F\u00E9\u011B"),
			("ghi4\u00EDGHI\u00CD", "GHI4\u00CD", "ghi4\u00ED"),
			(None, None, None),
			("mno6\u0148\u00F3MNO\u0147\u00D3", "MNO6\u0147\u00D3", "mno6\u0148\u00F3"),
			("pqrs7\u0159\u0161PQRS\u0158\u0160", "PQRS7\u0158\u0160", "pqrs7\u0159\u0161"),
			("tuv8\u0165\u00FA\u016FTUV\u0164\u00DA\u016E", "TUV8\u0164\u00DA\u016E", "tuv8\u0165\u00FA\u016F"),
			("wxyz9\u00FD\u017EWXYZ\u00DD\u017D", "WXYZ9\u00DD\u017D", "wxyz9\u00FD\u017E")
		),
		"de_DE": (
			(None, None, None),
			(None, None, None),
			("abc\u00E4\u00E0\u00E5\u01012ABC\u00C4\u00C0\u00C5\u0100", "ABC\u00C42", "abc\u00E42"),
			("def\u0111\u00E9\u01133DEF\u0110\u00C9\u0112", "DEF\u0110\u00C9\u01123", "def\u0111\u00E9\u01133"),
			(None, None, None),
			(None, None, None),
			("mno\u00F66MNO\u00D6", "MNO\u00D66", "mno\u00F66"),
			("pqrs\u00DF7PQRS", "PQRS7", "pqrs\u00DF7"),
			("tuv\u00FC8TUV\u00DC", "TUV\u00DC8", "tuv\u00FC8"),
			(None, None, None)
		),
		"es_ES": (
			(None, None, None),
			(None, None, None),
			("abc\u00E1\u00E0\u00E72ABC\u00C1\u00C0\u00C7", "ABC\u00C1\u00C0\u00C72", "abc\u00E1\u00E0\u00E72"),
			("def\u00E9\u00E83DEF\u00C9\u00C8", "DEF\u00C9\u00C83", "def\u00E9\u00E83"),
			("ghi\u00ED\u00EF4GHI\u00CD\u00CF", "GHI\u00CD\u00CF4", "ghi\u00ED\u00EF4"),
			(None, None, None),
			("mno\u00F1\u00F3\u00F26MNO\u00D1\u00D3\u00D2", "MNO\u00D1\u00D3\u00D26", "mno\u00F1\u00F3\u00F26"),
			(None, None, None),
			("tuv\u00FA\u00FC8TUV\u00DA\u00DC", "TUV\u00DA\u00DC8", "tuv\u00FA\u00FC8"),
			(None, None, None)
		),
		"et_EE": (
			(None, None, None),
			(None, None, None),
			("abc\u00E42ABC\u00C4", "ABC\u00C42", "abc\u00E42"),
			(None, None, None),
			(None, None, None),
			(None, None, None),
			("mno\u00F5\u00F66MNO\u00D5\u00D6", "MNO\u00D5\u00D66", "mno\u00F5\u00F66"),
			("pqrs\u01617PQRS\u0160", "PQRS\u01607", "pqrs\u01617"),
			("tuv\u00FC8TUV\u00DC", "TUV\u00DC8", "tuv\u00FC8"),
			("wxyz\u017E9WXYZ\u017D", "WXYZ\u017D9", "wxyz\u017E9")
		),
		"fa_IR": (
			("\u06F0" + PUNCTUATION0, "\u06F0" + PUNCTUATION0, "\u06F0" + PUNCTUATION0),
			("\u06F1" + PUNCTUATION1, "\u06F1" + PUNCTUATION1, "\u06F1" + PUNCTUATION1),
			("\u0628\u067E\u062A\u0629\u062B\u06F2abc2DEF", "\u0628\u067E\u062A\u0629\u062B\u06F2ABC2", "\u0628\u067E\u062A\u0629\u062B\u06F2abc2"),
			("\u0627\u0623\u0625\u0622\u0624\u0626\u0621\u06F3def3DEF", "\u0627\u0623\u0625\u0622\u0624\u0626\u0621\u06FDEF3", "\u0627\u0623\u0625\u0622\u0624\u0626\u0621\u06F3def3"),
			("\u0633\u0634\u0635\u0636\u06F4ghi4GHI", "\u0633\u0634\u0635\u0636\u06F4GHI4", "\u0633\u0634\u0635\u0636\u06F4ghi4"),
			("\u062F\u0630\u0631\u0632\u0698\u06F5jkl5JKL", "\u062F\u0630\u0631\u0632\u0698\u06F5JKL5", "\u062F\u0630\u0631\u0632\u0698\u06F5jkl5"),
			("\u062C\u0686\u062D\u062E\u06F6mno6MNO", "\u062C\u0686\u062D\u062E\u06F6MNO6", "\u062C\u0686\u062D\u062E\u06F6mno6"),
			("\u0646\u0648\u0647\u06CC\u06F7pqrs7PQRS", "\u0646\u0648\u0647\u06CC\u06F7PQRS7", "\u0646\u0648\u0647\u06CC\u06F7pqrs7"),
			("\u0641\u0642\u06A9\u06AF\u0644\u0645\u0643\u06F8tuv8TUV", "\u0641\u0642\u06A9\u06AF\u0644\u0645\u0643\u06F8TUV8", "\u0641\u0642\u06A9\u06AF\u0644\u0645\u0643\u06F8tuv8"),
			("\u0637\u0638\u0639\u063A\u06F9wxyz9WXYZ", "\u0637\u0638\u0639\u063A\u06F9WXYZ9", "\u0637\u0638\u0639\u063A\u06F9wxyz9"),
		),
		"fi_FI": (
			(None, None, None),
			(None, None, None),
			("abc\u00E4\u00E5\u00E1\u00E2\u010D2ABC\u00C4\u00C5\u00C1\u00C2\u010C", "ABC\u00C4\u00C5\u00C1\u00C2\u010C2", "abc\u00E4\u00E5\u00E1\u00E2\u010D2"),
			("def\u00E9\u01113DEF\u00C9\u0110", "DEF\u00C9\u01103", "def\u00E9\u01113"),
			("ghi\u01E7\u01E54GHI\u01E6\u01E4", "GHI\u01E6\u01E44", "ghi\u01E7\u01E54"),
			("jkl\u01E95JKL\u01E8", "JKL\u01E85", "jkl\u01E95"),
			("mno\u00F6\u00F8\u014B\u00F56MNO\u00D6\u00D8\u014A\u00D5", "MNO\u00D6\u00D8\u014A\u00D56", "mno\u00F6\u00F8\u014B\u00F56"),
			("pqrs\u01617PQRS\u0160", "PQRS\u01607", "pqrs\u01617"),
			("tuv\u00FC\u01678TUV\u00DC\u0166", "TUV\u00DC\u01668", "tuv\u00FC\u01678"),
			("wxyz\u017E\u0292\u01EF9WXYZ\u017D\u01B7\u01EE", "WXYZ\u017D\u01B7\u01EE9", "wxyz\u017E\u0292\u01EF9")
		),
		"lv_LV": (
			(None, None, None),
			(None, None, None),
			("a\u0101bc\u010D2A\u0100BC\u010C", "A\u0100BC\u010C2", "a\u0101bc\u010D2"),
			("de\u0113f3DE\u0112F", "DE\u0112F3", "de\u0113f3"),
			("g\u0123hi\u012B4G\u0122HI\u012A", "G\u0122HI\u012A4", "g\u0123hi\u012B4"),
			("jk\u0137l\u013C5JK\u0136L\u013B", "JK\u0136L\u013B5", "jk\u0137l\u013C5"),
			("mn\u0146o6MN\u0145O", "MN\u0145O6", "mn\u0146o6"),
			("prs\u01617qPRS\u0160Q", "PRS\u01607Q", "prs\u01617q"),
			("tu\u016Bv8TU\u016AV", "TU\u016AV8", "tu\u016Bv8"),
			("z\u017E9wxyWXYZ\u017D", "Z\u017D9WXY", "z\u017E9wxy")
		),
		"nl_NL": (
			(None, None, None),
			(None, None, None),
			(None, None, None),
			("def\u00EB3DEF\u00CB", "DEF\u00CB3", "def\u00EB3"),
			("ghi\u00EF4GHI\u00CF", "GHI\u00CF4", "ghi\u00EF4"),
			(None, None, None),
			(None, None, None),
			(None, None, None),
			(None, None, None),
			(None, None, None),
		),
		"pl_PL": (
			(None, None, None),
			(None, None, None),
			("abc\u0105\u01072ABC\u0104\u0106", "ABC\u0104\u01062", "abc\u0105\u01072"),
			("def\u01193DEF\u0118", "DEF\u01183", "def\u01193"),
			(None, None, None),
			("jkl\u01425JKL\u0141", "JKL\u01415", "jkl\u01425"),
			("mno\u0144\u00F36MNO\u0143\u00D3", "MNO\u0143\u00D36", "mno\u0144\u00F36"),
			("pqrs\u015B7PQRS\u015A", "PQRS\u015A7", "pqrs\u015B7"),
			(None, None, None),
			("wxyz\u017A\u017C9WXYZ\u0179\u017B", "WXYZ\u0179\u017B9", "wxyz\u017A\u017C9")
		),
		"ru_RU": (
			(None, None, None),
			(None, None, None),
			("\u0430\u0431\u0432\u0433abc2\u0410\u0411\u0412\u0413ABC", "\u0410\u0411\u0412\u0413ABC2", "\u0430\u0431\u0432\u0433abc2"),
			("\u0434\u0435\u0451\u0436\u0437def3\u0414\u0415\u0431\u0416\u0417DEF", "\u0414\u0415\u0431\u0416\u0417DEF3", "\u0434\u0435\u0451\u0436\u0437def3"),
			("\u0438\u0439\u043A\u043Bghi4\u0418\u0419\u041A\u041BGHI", "\u0418\u0419\u041A\u041BGHI4", "\u0438\u0439\u043A\u043Bghi4"),
			("\u043C\u043D\u043E\u043Fjkl5\u041C\u041D\u041E\u041FJKL", "\u041C\u041D\u041E\u041FJKL5", "\u043C\u043D\u043E\u043Fjkl5"),
			("\u0440\u0441\u0442\u0443mno6\u0420\u0421\u0422\u0423MNO", "\u0420\u0421\u0422\u0423MNO6", "\u0440\u0441\u0442\u0443mno6"),
			("\u0444\u0445\u0446\u0447pqrs7\u0424\u0425\u0426\u0427PQRS", "\u0424\u0425\u0426\u0427PQRS7", "\u0444\u0445\u0446\u0447pqrs7"),
			("\u0448\u0449\u044A\u044Btuv8\u0428\u0429\u042C\u042BTUV", "\u0428\u0429\u042A\u042BTUV8", "\u0448\u0449\u044A\u044Btuv8"),
			("\u044C\u044D\u044E\u044Fwxyz9\u042C\u042D\u042E\u042FWXYZ", "\u042C\u042D\u042E\u042FWXYZ9", "\u044C\u044D\u044E\u044Fwxyz9")
		),
		"sv_SE": (
			(None, None, None),
			(None, None, None),
			("abc\u00E5\u00E4\u00E0\u00E6\u00E1\u010D2ABC\u00C5\u00C4\u00C0\u00C6\u00C1\u010C", "ABC\u00C5\u00C4\u00C0\u00C6\u00C1\u010C2", "abc\u00E5\u00E4\u00E0\u00E6\u00E1\u010D2"),
			("def\u00E9\u01113DEF\u00C9\u0110", "DEF\u00C9\u01103", "def\u00E9\u01113"),
			("ghi\u00EF4GHI\u00CF", "GHI\u00CF4", "ghi\u00EF4"),
			(None, None, None),
			("mno\u00F6\u00F8\u014B6MNO\u00D6\u00D8\u014A", "MNO\u00D6\u00D8\u014A6", "mno\u00F6\u00F8\u014B6"),
			("pqrs\u01617PQRS\u0160", "PQRS\u01607", "pqrs\u01617"),
			("tuv\u00FC\u01678TUV\u00DC\u0166", "TUV\u00DC\u01668", "tuv\u00FC\u01678"),
			("wxyz\u017E9WXYZ\u017D", "WXYZ\u017D9", "wxyz\u017E9")
		),
		"sk_SK": (
			(None, None, None),
			(None, None, None),
			("abc\u00E1\u010D\u00E42ABC\u00C1\u010C\u00C4", "ABC\u00C1\u010C\u00C42", "abc\u00E1\u010D\u00E42"),
			("def\u010F\u00E93DEF\u010E\u00C9", "DEF\u010E\u00C93", "def\u010F\u00E93"),
			("ghi\u00ED4GHI\u00CD", "GHI\u00CD4", "ghiGHI\u00CD4"),
			("jkl\u013A\u013E5JKL\u0139\u013D", "JKL\u0139\u013D5", "jkl\u013A\u013E5"),
			("mno\u0148\u00F3\u00F4\u00F6\u01516MNO\u0147\u00D3\u00D4\u00D6\u0150", "MNO\u0147\u00D3\u00D4\u00D6\u01506", "mno\u0148\u00F3\u00F4\u00F6\u01516"),
			("pqrs\u0155\u01617PQRS\u0154\u0160", "PQRS\u0154\u01607", "pqrs\u0155\u01617"),
			("tuv\u0165\u00FA\u00FC\u01718TUV\u0164\u00DA\u00DC\u0170", "TUV\u0164\u00DA\u00DC\u01708", "tuv\u0165\u00FA\u00FC\u01718"),
			("wxyz\u00FD\u017E9WXYZ\u00DD\u017D", "WXYZ\u00DD\u017D9", "wxyz\u00FD\u017E9")
		),
		"uk_UA": (
			(None, None, None),
			(None, None, None),
			("\u0430\u0431\u0432\u0433\u0491abc2\u0410\u0411\u0412\u0413\u0490ABC", "\u0410\u0411\u0412\u0413\u0490ABC2", "\u0430\u0431\u0432\u0433\u0491abc2"),
			("\u0434\u0435\u0454\u0436\u0437def3\u0414\u0415\u0404\u0416\u0417DEF", "\u0414\u0415\u0404\u0416\u0417\u0401DEF3", "\u0434\u0435\u0454\u0436\u0437def3"),
			("\u0438\u0456\u0457\u0439\u043A\u043Bghi4\u0418\u0406\u0407\u0419\u041A\u041BGHI", "\u0418\u0406\u0407\u0419\u041A\u041BGHI4", "\u0438\u0456\u0457\u0439\u043A\u043Bghi4"),
			("\u043C\u043D\u043E\u043Fjkl5\u041C\u041D\u041E\u041FJKL", "\u041C\u041D\u041E\u041FDJKL5", "\u043C\u043D\u043E\u043Fjkl5"),
			("\u0440\u0441\u0442\u0443mno6\u0420\u0421\u0422\u0423MNO", "\u0420\u0421\u0422\u0423MNO6", "\u0440\u0441\u0442\u0443mno6"),
			("\u0444\u0445\u0446\u0447pqrs7\u0424\u0425\u0426\u0427PQRS", "\u0424\u0425\u0426\u0427PQRS7", "\u0444\u0445\u0446\u0447pqrs7"),
			("\u0448\u0449tuv8\u0428\u0429TUV", "\u0428\u0429TUV8", "\u0448\u0449tuv8"),
			("\u044E\u044F\u044Cwxyz9\u042E\u042F\u042CWXYZ", "\u042E\u042F\u042CWXYZ9", "\u044E\u044F\u044Cwxyz9")
		)
	}
else:
	PUNCTUATION0 = u"0,?!'\"\\()<>[]{}~^`|"
	PUNCTUATION1 = u"1 .:;+-*/=_@#$%&"

	MAPPINGS = (
		# Text, TextUpper, TextLower, Search, SearchUpper, SearchLower, Hex, HexUpper, HexLower, HexFast, HexFastUpper, HexFastLower, HexLogical, HexLogicalUpper, HexLogicalLower
		(PUNCTUATION0, PUNCTUATION0, PUNCTUATION0, u"%_0", u"%_0", u"%_0", u"0", u"0", u"0", u"0", u"0", u"0", u"0Aa", u"0A", u"0a"),
		(PUNCTUATION1, PUNCTUATION1, PUNCTUATION1, u" 1", u" 1", u" 1", u"1AaBbCc", u"1ABC", u"1abc", u"1Aa", u"1A", u"1a", u"1Bb", u"1B", u"1b"),
		(u"abc2ABC", u"ABC2", u"abc2", u"abc2ABC", u"ABC2", u"abc2", u"2DdEeFf", u"2DEF", u"2def", u"2Bb", u"2B", u"2b", u"2Cc", u"2C", u"2c"),
		(u"def3DEF", u"DEF3", u"def3", u"def3DEF", u"DEF3", u"def3", u"3", u"3", u"3", u"3Cc", u"3C", u"3c", u"3Dd", u"3D", u"3d"),
		(u"ghi4GHI", u"GHI4", u"ghi4", u"ghi4GHI", u"GHI4", u"ghi4", u"4", u"4", u"4", u"4Dd", u"4D", u"4d", u"4Ee", u"4E", u"4e"),
		(u"jkl5JKL", u"JKL5", u"jkl5", u"jkl5JKL", u"JKL5", u"jkl5", u"5", u"5", u"5", u"5Ee", u"5E", u"5e", u"5Ff", u"5F", u"5f"),
		(u"mno6MNO", u"MNO6", u"mno6", u"mno6MNO", u"MNO6", u"mno6", u"6", u"6", u"6", u"6Ff", u"6F", u"6f", u"6", u"6", u"6"),
		(u"pqrs7PQRS", u"PQRS7", u"pqrs7", u"pqrs7PQRS", u"PQRS7", u"pqrs7", u"7", u"7", u"7", u"7", u"7", u"7", u"7", u"7", u"7"),
		(u"tuv8TUV", u"TUV8", u"tuv8", u"tuv8TUV", u"TUV8", u"tuv8", u"8", u"8", u"8", u"8", u"8", u"8", u"8", u"8", u"8"),
		(u"wxyz9WXYZ", u"WXYZ9", u"wxyz9", u"wxyz9WXYZ", u"WXYZ9", u"wxyz9", u"9", u"9", u"9", u"9", u"9", u"9", u"9", u"9", u"9")
	)

	LOCALES = {
		"cs_CZ": (
			(None, None, None),
			(None, None, None),
			(u"abc2\u00E1\u010DABC\u00C1\u010C", u"ABC2\u00C1\u010C", u"abc2\u00E1\u010D"),
			(u"def3\u010F\u00E9\u011BDEF\u010E\u00C9\u011A", u"DEF3\u010E\u00C9\u011A", u"def3\u010F\u00E9\u011B"),
			(u"ghi4\u00EDGHI\u00CD", u"GHI4\u00CD", u"ghi4\u00ED"),
			(None, None, None),
			(u"mno6\u0148\u00F3MNO\u0147\u00D3", u"MNO6\u0147\u00D3", u"mno6\u0148\u00F3"),
			(u"pqrs7\u0159\u0161PQRS\u0158\u0160", u"PQRS7\u0158\u0160", u"pqrs7\u0159\u0161"),
			(u"tuv8\u0165\u00FA\u016FTUV\u0164\u00DA\u016E", u"TUV8\u0164\u00DA\u016E", u"tuv8\u0165\u00FA\u016F"),
			(u"wxyz9\u00FD\u017EWXYZ\u00DD\u017D", u"WXYZ9\u00DD\u017D", u"wxyz9\u00FD\u017E")
		),
		"de_DE": (
			(None, None, None),
			(None, None, None),
			(u"abc\u00E4\u00E0\u00E5\u01012ABC\u00C4\u00C0\u00C5\u0100", u"ABC\u00C42", u"abc\u00E42"),
			(u"def\u0111\u00E9\u01133DEF\u0110\u00C9\u0112", u"DEF\u0110\u00C9\u01123", u"def\u0111\u00E9\u01133"),
			(None, None, None),
			(None, None, None),
			(u"mno\u00F66MNO\u00D6", u"MNO\u00D66", u"mno\u00F66"),
			(u"pqrs\u00DF7PQRS", u"PQRS7", u"pqrs\u00DF7"),
			(u"tuv\u00FC8TUV\u00DC", u"TUV\u00DC8", u"tuv\u00FC8"),
			(None, None, None)
		),
		"es_ES": (
			(None, None, None),
			(None, None, None),
			(u"abc\u00E1\u00E0\u00E72ABC\u00C1\u00C0\u00C7", u"ABC\u00C1\u00C0\u00C72", u"abc\u00E1\u00E0\u00E72"),
			(u"def\u00E9\u00E83DEF\u00C9\u00C8", u"DEF\u00C9\u00C83", u"def\u00E9\u00E83"),
			(u"ghi\u00ED\u00EF4GHI\u00CD\u00CF", u"GHI\u00CD\u00CF4", u"ghi\u00ED\u00EF4"),
			(None, None, None),
			(u"mno\u00F1\u00F3\u00F26MNO\u00D1\u00D3\u00D2", u"MNO\u00D1\u00D3\u00D26", u"mno\u00F1\u00F3\u00F26"),
			(None, None, None),
			(u"tuv\u00FA\u00FC8TUV\u00DA\u00DC", u"TUV\u00DA\u00DC8", u"tuv\u00FA\u00FC8"),
			(None, None, None)
		),
		"et_EE": (
			(None, None, None),
			(None, None, None),
			(u"abc\u00E42ABC\u00C4", u"ABC\u00C42", u"abc\u00E42"),
			(None, None, None),
			(None, None, None),
			(None, None, None),
			(u"mno\u00F5\u00F66MNO\u00D5\u00D6", u"MNO\u00D5\u00D66", u"mno\u00F5\u00F66"),
			(u"pqrs\u01617PQRS\u0160", u"PQRS\u01607", u"pqrs\u01617"),
			(u"tuv\u00FC8TUV\u00DC", u"TUV\u00DC8", u"tuv\u00FC8"),
			(u"wxyz\u017E9WXYZ\u017D", u"WXYZ\u017D9", u"wxyz\u017E9")
		),
		"fa_IR": (
			(u"\u06F0" + PUNCTUATION0, u"\u06F0" + PUNCTUATION0, u"\u06F0" + PUNCTUATION0),
			(u"\u06F1" + PUNCTUATION1, u"\u06F1" + PUNCTUATION1, u"\u06F1" + PUNCTUATION1),
			(u"\u0628\u067E\u062A\u0629\u062B\u06F2abc2DEF", u"\u0628\u067E\u062A\u0629\u062B\u06F2ABC2", u"\u0628\u067E\u062A\u0629\u062B\u06F2abc2"),
			(u"\u0627\u0623\u0625\u0622\u0624\u0626\u0621\u06F3def3DEF", u"\u0627\u0623\u0625\u0622\u0624\u0626\u0621\u06FDEF3", u"\u0627\u0623\u0625\u0622\u0624\u0626\u0621\u06F3def3"),
			(u"\u0633\u0634\u0635\u0636\u06F4ghi4GHI", u"\u0633\u0634\u0635\u0636\u06F4GHI4", u"\u0633\u0634\u0635\u0636\u06F4ghi4"),
			(u"\u062F\u0630\u0631\u0632\u0698\u06F5jkl5JKL", u"\u062F\u0630\u0631\u0632\u0698\u06F5JKL5", U"\u062F\u0630\u0631\u0632\u0698\u06F5jkl5"),
			(u"\u062C\u0686\u062D\u062E\u06F6mno6MNO", u"\u062C\u0686\u062D\u062E\u06F6MNO6", u"\u062C\u0686\u062D\u062E\u06F6mno6"),
			(u"\u0646\u0648\u0647\u06CC\u06F7pqrs7PQRS", u"\u0646\u0648\u0647\u06CC\u06F7PQRS7", u"\u0646\u0648\u0647\u06CC\u06F7pqrs7"),
			(u"\u0641\u0642\u06A9\u06AF\u0644\u0645\u0643\u06F8tuv8TUV", u"\u0641\u0642\u06A9\u06AF\u0644\u0645\u0643\u06F8TUV8", u"\u0641\u0642\u06A9\u06AF\u0644\u0645\u0643\u06F8tuv8"),
			(u"\u0637\u0638\u0639\u063A\u06F9wxyz9WXYZ", u"\u0637\u0638\u0639\u063A\u06F9WXYZ9", u"\u0637\u0638\u0639\u063A\u06F9wxyz9"),
		),
		"fi_FI": (
			(None, None, None),
			(None, None, None),
			(u"abc\u00E4\u00E5\u00E1\u00E2\u010D2ABC\u00C4\u00C5\u00C1\u00C2\u010C", u"ABC\u00C4\u00C5\u00C1\u00C2\u010C2", u"abc\u00E4\u00E5\u00E1\u00E2\u010D2"),
			(u"def\u00E9\u01113DEF\u00C9\u0110", u"DEF\u00C9\u01103", u"def\u00E9\u01113"),
			(u"ghi\u01E7\u01E54GHI\u01E6\u01E4", u"GHI\u01E6\u01E44", u"ghi\u01E7\u01E54"),
			(u"jkl\u01E95JKL\u01E8", u"JKL\u01E85", u"jkl\u01E95"),
			(u"mno\u00F6\u00F8\u014B\u00F56MNO\u00D6\u00D8\u014A\u00D5", u"MNO\u00D6\u00D8\u014A\u00D56", u"mno\u00F6\u00F8\u014B\u00F56"),
			(u"pqrs\u01617PQRS\u0160", u"PQRS\u01607", u"pqrs\u01617"),
			(u"tuv\u00FC\u01678TUV\u00DC\u0166", u"TUV\u00DC\u01668", u"tuv\u00FC\u01678"),
			(u"wxyz\u017E\u0292\u01EF9WXYZ\u017D\u01B7\u01EE", u"WXYZ\u017D\u01B7\u01EE9", u"wxyz\u017E\u0292\u01EF9")
		),
		"lv_LV": (
			(None, None, None),
			(None, None, None),
			(u"a\u0101bc\u010D2A\u0100BC\u010C", u"A\u0100BC\u010C2", u"a\u0101bc\u010D2"),
			(u"de\u0113f3DE\u0112F", u"DE\u0112F3", u"de\u0113f3"),
			(u"g\u0123hi\u012B4G\u0122HI\u012A", u"G\u0122HI\u012A4", u"g\u0123hi\u012B4"),
			(u"jk\u0137l\u013C5JK\u0136L\u013B", u"JK\u0136L\u013B5", u"jk\u0137l\u013C5"),
			(u"mn\u0146o6MN\u0145O", u"MN\u0145O6", u"mn\u0146o6"),
			(u"prs\u01617qPRS\u0160Q", u"PRS\u01607Q", u"prs\u01617q"),
			(u"tu\u016Bv8TU\u016AV", u"TU\u016AV8", u"tu\u016Bv8"),
			(u"z\u017E9wxyWXYZ\u017D", u"Z\u017D9WXY", u"z\u017E9wxy")
		),
		"nl_NL": (
			(None, None, None),
			(None, None, None),
			(None, None, None),
			(u"def\u00EB3DEF\u00CB", u"DEF\u00CB3", u"def\u00EB3"),
			(u"ghi\u00EF4GHI\u00CF", u"GHI\u00CF4", u"ghi\u00EF4"),
			(None, None, None),
			(None, None, None),
			(None, None, None),
			(None, None, None),
			(None, None, None),
		),
		"pl_PL": (
			(None, None, None),
			(None, None, None),
			(u"abc\u0105\u01072ABC\u0104\u0106", u"ABC\u0104\u01062", u"abc\u0105\u01072"),
			(u"def\u01193DEF\u0118", u"DEF\u01183", u"def\u01193"),
			(None, None, None),
			(u"jkl\u01425JKL\u0141", u"JKL\u01415", u"jkl\u01425"),
			(u"mno\u0144\u00F36MNO\u0143\u00D3", u"MNO\u0143\u00D36", u"mno\u0144\u00F36"),
			(u"pqrs\u015B7PQRS\u015A", u"PQRS\u015A7", u"pqrs\u015B7"),
			(None, None, None),
			(u"wxyz\u017A\u017C9WXYZ\u0179\u017B", u"WXYZ\u0179\u017B9", u"wxyz\u017A\u017C9")
		),
		"ru_RU": (
			(None, None, None),
			(None, None, None),
			(u"\u0430\u0431\u0432\u0433abc2\u0410\u0411\u0412\u0413ABC", u"\u0410\u0411\u0412\u0413ABC2", u"\u0430\u0431\u0432\u0433abc2"),
			(u"\u0434\u0435\u0451\u0436\u0437def3\u0414\u0415\u0431\u0416\u0417DEF", u"\u0414\u0415\u0431\u0416\u0417DEF3", u"\u0434\u0435\u0451\u0436\u0437def3"),
			(u"\u0438\u0439\u043A\u043Bghi4\u0418\u0419\u041A\u041BGHI", u"\u0418\u0419\u041A\u041BGHI4", u"\u0438\u0439\u043A\u043Bghi4"),
			(u"\u043C\u043D\u043E\u043Fjkl5\u041C\u041D\u041E\u041FJKL", u"\u041C\u041D\u041E\u041FJKL5", u"\u043C\u043D\u043E\u043Fjkl5"),
			(u"\u0440\u0441\u0442\u0443mno6\u0420\u0421\u0422\u0423MNO", u"\u0420\u0421\u0422\u0423MNO6", u"\u0440\u0441\u0442\u0443mno6"),
			(u"\u0444\u0445\u0446\u0447pqrs7\u0424\u0425\u0426\u0427PQRS", u"\u0424\u0425\u0426\u0427PQRS7", u"\u0444\u0445\u0446\u0447pqrs7"),
			(u"\u0448\u0449\u044A\u044Btuv8\u0428\u0429\u042C\u042BTUV", u"\u0428\u0429\u042A\u042BTUV8", u"\u0448\u0449\u044A\u044Btuv8"),
			(u"\u044C\u044D\u044E\u044Fwxyz9\u042C\u042D\u042E\u042FWXYZ", u"\u042C\u042D\u042E\u042FWXYZ9", u"\u044C\u044D\u044E\u044Fwxyz9")
		),
		"sv_SE": (
			(None, None, None),
			(None, None, None),
			(u"abc\u00E5\u00E4\u00E0\u00E6\u00E1\u010D2ABC\u00C5\u00C4\u00C0\u00C6\u00C1\u010C", u"ABC\u00C5\u00C4\u00C0\u00C6\u00C1\u010C2", u"abc\u00E5\u00E4\u00E0\u00E6\u00E1\u010D2"),
			(u"def\u00E9\u01113DEF\u00C9\u0110", u"DEF\u00C9\u01103", u"def\u00E9\u01113"),
			(u"ghi\u00EF4GHI\u00CF", u"GHI\u00CF4", u"ghi\u00EF4"),
			(None, None, None),
			(u"mno\u00F6\u00F8\u014B6MNO\u00D6\u00D8\u014A", u"MNO\u00D6\u00D8\u014A6", u"mno\u00F6\u00F8\u014B6"),
			(u"pqrs\u01617PQRS\u0160", u"PQRS\u01607", u"pqrs\u01617"),
			(u"tuv\u00FC\u01678TUV\u00DC\u0166", u"TUV\u00DC\u01668", u"tuv\u00FC\u01678"),
			(u"wxyz\u017E9WXYZ\u017D", u"WXYZ\u017D9", u"wxyz\u017E9")
		),
		"sk_SK": (
			(None, None, None),
			(None, None, None),
			(u"abc\u00E1\u010D\u00E42ABC\u00C1\u010C\u00C4", u"ABC\u00C1\u010C\u00C42", u"abc\u00E1\u010D\u00E42"),
			(u"def\u010F\u00E93DEF\u010E\u00C9", u"DEF\u010E\u00C93", u"def\u010F\u00E93"),
			(u"ghi\u00ED4GHI\u00CD", u"GHI\u00CD4", u"ghiGHI\u00CD4"),
			(u"jkl\u013A\u013E5JKL\u0139\u013D", u"JKL\u0139\u013D5", u"jkl\u013A\u013E5"),
			(u"mno\u0148\u00F3\u00F4\u00F6\u01516MNO\u0147\u00D3\u00D4\u00D6\u0150", u"MNO\u0147\u00D3\u00D4\u00D6\u01506", u"mno\u0148\u00F3\u00F4\u00F6\u01516"),
			(u"pqrs\u0155\u01617PQRS\u0154\u0160", u"PQRS\u0154\u01607", u"pqrs\u0155\u01617"),
			(u"tuv\u0165\u00FA\u00FC\u01718TUV\u0164\u00DA\u00DC\u0170", u"TUV\u0164\u00DA\u00DC\u01708", u"tuv\u0165\u00FA\u00FC\u01718"),
			(u"wxyz\u00FD\u017E9WXYZ\u00DD\u017D", u"WXYZ\u00DD\u017D9", u"wxyz\u00FD\u017E9")
		),
		"uk_UA": (
			(None, None, None),
			(None, None, None),
			(u"\u0430\u0431\u0432\u0433\u0491abc2\u0410\u0411\u0412\u0413\u0490ABC", u"\u0410\u0411\u0412\u0413\u0490ABC2", u"\u0430\u0431\u0432\u0433\u0491abc2"),
			(u"\u0434\u0435\u0454\u0436\u0437def3\u0414\u0415\u0404\u0416\u0417DEF", u"\u0414\u0415\u0404\u0416\u0417\u0401DEF3", u"\u0434\u0435\u0454\u0436\u0437def3"),
			(u"\u0438\u0456\u0457\u0439\u043A\u043Bghi4\u0418\u0406\u0407\u0419\u041A\u041BGHI", u"\u0418\u0406\u0407\u0419\u041A\u041BGHI4", u"\u0438\u0456\u0457\u0439\u043A\u043Bghi4"),
			(u"\u043C\u043D\u043E\u043Fjkl5\u041C\u041D\u041E\u041FJKL", u"\u041C\u041D\u041E\u041FDJKL5", u"\u043C\u043D\u043E\u043Fjkl5"),
			(u"\u0440\u0441\u0442\u0443mno6\u0420\u0421\u0422\u0423MNO", u"\u0420\u0421\u0422\u0423MNO6", u"\u0440\u0441\u0442\u0443mno6"),
			(u"\u0444\u0445\u0446\u0447pqrs7\u0424\u0425\u0426\u0427PQRS", u"\u0424\u0425\u0426\u0427PQRS7", u"\u0444\u0445\u0446\u0447pqrs7"),
			(u"\u0448\u0449tuv8\u0428\u0429TUV", u"\u0428\u0429TUV8", u"\u0448\u0449tuv8"),
			(u"\u044E\u044F\u044Cwxyz9\u042E\u042F\u042CWXYZ", u"\u042E\u042F\u042CWXYZ9", u"\u044E\u044F\u044Cwxyz9")
		)
	}


# For more information about using NumericalTextInput see /doc/NUMERICALTEXTINPUT
#
class NumericalTextInput:
	def __init__(self, nextFunc=None, handleTimeout=True, search=False, mapping=None, mode=None):
		self.nextFunction = nextFunc
		if handleTimeout:
			self.timer = eTimer()
			self.timer.callback.append(self.timeout)
		else:
			self.timer = None
		if mapping and isinstance(mapping, (list, tuple)):
			self.mapping = mapping
		else:
			if mode is None:
				if search:  # NOTE: This will be removed when deprecated "search" is removed and "mode" is widely adopted.
					mode = "Search"
				if isinstance(mapping, str):  # NOTE: Legacy interface for previous and deprecated versions of NumericalTextInput.
					mode = mapping
			index = MODES.get(str(mode).upper(), 0)
			self.mapping = []
			for num in list(range(0, 10)):
				self.mapping.append((MAPPINGS[num][index]))
			locale = LOCALES.get(language.getLanguage(), None)
			if locale is not None and index in list(range(0, 6)):
				index = index % 3
				for num in list(range(0, 10)):
					if locale[num][index] is not None:
						self.mapping[num] = locale[num][index]
			self.mapping = tuple(self.mapping)
		# The key mapping lists naturally restricts character input to
		# the listed characters, this restriction is not enforced for
		# external keyboard input!
		self.useableChars = "".join(self.mapping)  # This limits data entry to only characters in the mapping lists.
		# print("[NumericalTextInput] DEBUG: Mode='%s', Index=%d, Character set: '%s'" % (mode, index, "".join(sorted(self.useableChars))))
		self.lastKey = -1
		self.pos = -1

	def timeout(self):
		if self.lastKey != -1:
			self.nextChar()

	def nextChar(self):
		self.nextKey()
		if self.nextFunction:
			self.nextFunction()

	def nextKey(self):
		if self.timer is not None:
			self.timer.stop()
		self.lastKey = -1

	def getKey(self, num):
		if self.lastKey != num:
			if self.lastKey != -1:
				self.nextChar()
			self.lastKey = num
			self.pos = -1
		if self.timer is not None:
			self.timer.start(1000, True)
		length = len(self.mapping[num])
		cnt = length
		while True:
			self.pos += 1
			if self.pos >= length:
				self.pos = 0
			if not self.useableChars or self.useableChars.find(self.mapping[num][self.pos]) != -1:
				break
			cnt -= 1
			if cnt == 0:
				return None
		return self.mapping[num][self.pos]

	def setUseableChars(self, useable):
		self.useableChars = six.text_type(useable)

