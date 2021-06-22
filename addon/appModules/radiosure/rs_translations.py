# appModules\radiosure\rs_translations.py
# A part of radioSureAccessEnhancement add-on
# Copyright (C) 2020-2021, paulber19
# This file is covered by the GNU General Public License.

import addonHandler
from logHandler import log
import os
import sys
import api
from . import psutil

from .utilities import xmltodict

addonHandler.initTranslation()

# dictionnary to store radiosure translations of current language
_translations = None


def getRadioSureFullPath():
	focus = api.getFocusObject()
	pid = focus.processID
	for p in psutil.process_iter():
		if p.pid == pid:
			radioSurePath = psutil.Process(pid).cmdline()[0]
			path = os.path.dirname(radioSurePath)
			return path
	return None


def getTranslations():
	languageFilePath = getRadioSureLanguage()
	with open(languageFilePath, encoding="utf8") as fd:
		translations = xmltodict.parse(fd.read(), process_namespaces=True)
	fd.close()
	return translations


def getRadioSureLanguage():
	radioSureDirPath = getRadioSureFullPath()
	if radioSureDirPath is None:
		log.error("Cannot retrive radioSure directory path")
		return
	radioSureXMLFilePath = os.path.join(radioSureDirPath, "RadioSure.xml")
	with open(radioSureXMLFilePath, encoding="utf8") as fd:
		radiosureXML = xmltodict.parse(fd.read(), process_namespaces=True)
	fd.close()
	try:
		languageFileName = radiosureXML["XMLConfigSettings"]["General"]["Language"]
	except:  # noqa:E722
		languageFileName = "english.lng"
	languageFilePath = os.path.join(radioSureDirPath, "Lang", languageFileName)
	return languageFilePath


def getPlayingTranslation():
	playing = _translations["XMLConfigSettings"]["Radio"]["Playing"]
	return playing


def initialize():
	global _translations
	if _translations is None:
		_translations = getTranslations()
