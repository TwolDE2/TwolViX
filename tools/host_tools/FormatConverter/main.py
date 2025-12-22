#!/usr/bin/python
from os import system as ossystem

from datasource import genericdatasource
from satxml import satxml
from lamedb import lamedb
from input import inputChoices

maindata = genericdatasource()

sources = [satxml, lamedb]

datasources = [maindata]

for source in sources:
	datasources.append(source())

for source in datasources:
	source.setDatasources(datasources)

while True:
	ossystem("/usr/bin/clear")
	data = []
	for index in list(range(len(datasources))):
		data.append(datasources[index].getName() + (" (%d sats)" % len(datasources[index].transponderlist.keys())))
	index = inputChoices(data, "q", "quit")
	if index is None:
		break

	while True:
		print(datasources[index].getStatus())
		data = []
		for action in datasources[index].getCapabilities():
			data.append(action[0])
		action = inputChoices(data)
		if action is None:
			break

		datasources[index].getCapabilities()[action][1]()
