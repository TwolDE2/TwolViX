installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = TuxboxPlugins CutListEditor PicturePlayer MediaScanner SocketMMI DVDBurn MediaPlayer

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if VUSOLO4K
SUBDIRS += MiniTV QuadPip
endif

if VUULTIMO4K
SUBDIRS += MiniTV QuadPip
endif

if VUUNO4K
SUBDIRS += QuadPip
endif

install_PYTHON = __init__.py
