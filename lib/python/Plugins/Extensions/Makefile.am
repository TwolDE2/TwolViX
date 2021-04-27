installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = TuxboxPlugins CutListEditor PicturePlayer MediaScanner SocketMMI DVDBurn MediaPlayer

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if VUSOLO4K
SUBDIRS += QuadPip
endif

if VUULTIMO4K
SUBDIRS += QuadPip
endif

if GB7252
SUBDIRS += QuadPip
endif

if VUUNO4K
SUBDIRS += QuadPip
endif

if VUUNO4KSE
SUBDIRS += QuadPip
endif

if VUDUO4K
SUBDIRS += QuadPip
endif

if VUDUO4KSE
SUBDIRS += QuadPip
endif

install_PYTHON = __init__.py
