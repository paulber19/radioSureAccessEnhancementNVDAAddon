#appModules\radiosure\rs_translations.py
#A part of radioSureAccessEnhancement add-on
#Copyright (C) 2020, paulber19
#This file is covered by the GNU General Public License.


import addonHandler
addonHandler.initTranslation()
from logHandler import log
import os
import sys
import api
from . import psutil

_curAddon = addonHandler.getCodeAddon()
path = os.path.join(_curAddon.path, "shared")
sys.path.append(path)
from rs_py3Compatibility import py3
del sys.path[-1]

if py3:
	from .utilitiesPy3  import xmltodict
else:
	from .utilitiesPy2  import xmltodict
# dictionnary to store radiosure translations of current language
_translations = None

def getRadioSureFullPath():
	focus = api.getFocusObject()
	pid = focus.processID
	for p in psutil.process_iter():
		if p.pid == pid:
			radioSurePath =psutil.Process(pid).cmdline()[0]
			path = os.path.dirname(radioSurePath)
			return path if py3 else path.decode("mbcs")
	return None

def getTranslations():
	languageFilePath = getRadioSureLanguage()
	if py3:
		with open(languageFilePath, encoding="utf8") as fd:
			translations = xmltodict.parse(fd.read(), process_namespaces=True)
	else:
		with open(languageFilePath, ) as fd:
			translations = xmltodict.parse(fd.read(), process_namespaces=True)
	fd.close()
	return translations


def getRadioSureLanguage():
	radioSureDirPath = getRadioSureFullPath()
	if radioSureDirPath is None:
		log.error("Cannot retrive radioSure directory path")
		return
	radioSureXMLFilePath = os.path.join(radioSureDirPath, "RadioSure.xml")
	if py3:
		with open(radioSureXMLFilePath, encoding="utf8") as fd:
			radiosureXML = xmltodict.parse(fd.read(), process_namespaces=True)
	else:
		with open(radioSureXMLFilePath, ) as fd:
			radiosureXML = xmltodict.parse(fd.read(), process_namespaces=True)
	fd.close()
	try:
		languageFileName=  radiosureXML["XMLConfigSettings"]["General"]["Language"]
	except:
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
