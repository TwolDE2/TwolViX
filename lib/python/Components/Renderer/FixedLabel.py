<<<<<<< HEAD
from __future__ import absolute_import
=======
from Components.Renderer.Renderer import Renderer
>>>>>>> 92e1086... Remove __future__ as this should not be needed for Python3

from enigma import eLabel

from Components.Renderer.Renderer import Renderer


class FixedLabel(Renderer):
	GUI_WIDGET = eLabel
