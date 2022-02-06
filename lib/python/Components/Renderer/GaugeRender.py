<<<<<<< HEAD
from __future__ import absolute_import
=======
from Components.VariableValue import VariableValue
from Components.Renderer.Renderer import Renderer
>>>>>>> 92e1086... Remove __future__ as this should not be needed for Python3

from enigma import eGauge

from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue


class GaugeRender(VariableValue, Renderer):
	def __init__(self):
		Renderer.__init__(self)
		VariableValue.__init__(self)

	GUI_WIDGET = eGauge

	def changed(self, what):
		if what[0] == self.CHANGED_CLEAR:
			return

		value = self.source.value
		if value is None:
			value = 0
		self.setValue(value)

	GUI_WIDGET = eGauge

	def postWidgetCreate(self, instance):
		instance.setValue(0)

	def setValue(self, value):
		#self.instance.setValue(5)
		if self.instance is not None:
			self.instance.setValue(value)

	#value = property(setValue)
