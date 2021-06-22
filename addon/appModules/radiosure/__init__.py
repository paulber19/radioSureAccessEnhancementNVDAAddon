# appModules\radioSure\__init__.py
# a part of radioSureAccessEnhancement add-on
# Copyright (C) 2019-2021, Paulber19
# This file is covered by the GNU General Public License.
# Released under GPL 2


import addonHandler
import gui
import config
from logHandler import log
import NVDAObjects
from scriptHandler import getLastScriptRepeatCount
from speech import speakSpelling
import ui
import speech
import eventHandler
import queueHandler
import winUser
from winUser import getWindow, getControlID
from winUser import VK_DOWN, VK_UP, sendMessage
from winUser import VK_NEXT, VK_PRIOR, VK_LEFT, VK_RIGHT
import controlTypes
from NVDAObjects import NVDAObject
import review
import textInfos
import api
import os
import wx
import time
import tones
from keyboardHandler import KeyboardInputGesture
from oleacc import *  # noqa:F403
import sys
from .rs_utils import getSpeechMode, setSpeechMode, setSpeechMode_off
_curAddon = addonHandler.getCodeAddon()
debugToolsPath = os.path.join(_curAddon.path, "debugTools")
sys.path.append(debugToolsPath)
try:
	from appModuleDebug import AppModuleDebug as AppModule
	from appModuleDebug import printDebug, toggleDebugFlag
except ImportError:
	from appModuleHandler import AppModule as AppModule
	def prindDebug(msg): return
	def toggleDebugFlag(): return
del sys.path[-1]
path = os.path.join(_curAddon.path, "shared")
sys.path.append(path)
from rs_addonConfigManager import _addonConfigManager  # noqa:E402
del sys.path[-1]

addonHandler.initTranslation()
# winUser constants
WM_KEYUP = 0x0101
WM_KEYDOWN = 0x0100
WM_SETFOCUS = 0x0007

_addonSummary = _curAddon.manifest['summary']
_addonVersion = _curAddon.manifest['version']
_addonName = _curAddon.manifest['name']
_scriptCategory = str(_addonSummary)

# pour getWindow function
firstWindow = 0
nextWindow = 2
firstChild = 5


ctrlIdsDic = {
		"searchEdit": 1001,
		"favButton": 1024,
		"optionsButton": 1041,
		"volume": 1006,
		"nextButton": 1039,
		"backButton": 1038,
		"playButton": 1000,
		"pauseButton": 1017,
		"recButton": 1051,
		"expandButton": 1076,
		"topButton": 1077,
		"exitButton": 1,
		"stationsList": 1016,
		"searchCombo": 1019,
		"muteButton": 1027,
		"copyURLButton": 1046,
		"stateInfo": 1007,
		"liveInfo": 1046,
		"stationName": 1026,
		"buffer": 1009
}
# to find main window, class and control id of first child window
firstChildWindow = (("msctls_trackbar32", 1006), ("SysListView32", 1016))


def getTopWindow(obj=None):
	if obj is None:
		obj = api.getFocusObject()
	i = 10
	while i and obj:
		i = i-1
		if winUser.getClassName(obj.windowHandle) == "#32770":
			return obj.windowHandle
		try:
			obj = obj.parent
		except:  # noqa:E722
			return None
	return None


def getTopWindowNVDAObject(obj=None):
	if obj is None:
		obj = api.getFocusObject()
	i = 10
	while i and obj:
		if obj.parent and obj.parent.name == api.getDesktopObject().name:
			return obj
		if obj.parent:
			obj = obj.parent
		i = i-1
	return None


def findWindow(window):
	h = getWindow(getTopWindow(), firstChild)
	id = ctrlIdsDic[window]
	i = 70
	while i:
		i = i-1
		if getControlID(h) == id:
			return h
		h = getWindow(h, nextWindow)
	return None


def findWindowNVDAObject(window):
	h = getWindow(getTopWindow(), firstChild)
	id = ctrlIdsDic[window]
	i = 70
	while i:
		i = i-1
		if getControlID(h) == id:
			obj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h, -4, 0)
			return obj
		h = getWindow(h, nextWindow)
	return None


def clickButton(window):
	obj = findWindowNVDAObject(window)
	if obj is None:
		return None
	oldSpeechMode = getSpeechMode()
	setSpeechMode_off()
	obj.IAccessibleObject.accDoDefaultAction(0)
	eventHandler.queueEvent("gainFocus", obj)
	time.sleep(0.1)
	api.processPendingEvents()
	setSpeechMode(oldSpeechMode)
	return obj.name


def clickButtonWithoutMoving(window):
	oldSpeechMode = setSpeechMode()
	setSpeechMode_off()
	currentObj = api.getFocusObject()
	name = clickButton(window)
	currentObj.setFocus()
	eventHandler.queueEvent("gainFocus", currentObj)
	time.sleep(0.1)
	api.processPendingEvents()
	setSpeechMode(oldSpeechMode)
	return name


def getStationName():
	obj = findWindowNVDAObject("stationName")
	if obj is None:
		return ""
	return obj.windowText


def sayStationName():
	ui.message(getStationName())


def getStationState():
	obj = findWindowNVDAObject("stateInfo")
	if obj is None:
		return ""
	return obj.windowText


def sayStationState():
	name = getStationName()
	state = getStationState()
	text = "%s %s" % (name, state)
	ui.message(text)


def getPlayInfos():
	# others informations in live field
	obj = findWindowNVDAObject("liveInfo")
	text = ""
	if obj:
		text = obj.windowText
	name = getStationName()
	state = getStationState()
	return "%s %s %s" % (name, state, text)


def getVolume():
	obj = findWindowNVDAObject("volume")
	if obj:
		return obj.value
	return ""


def modifyVolume(vkKey):
	h = findWindowNVDAObject("volume").windowHandle
	sendMessage(h, WM_KEYDOWN, vkKey, 0)
	sendMessage(h, WM_KEYUP, vkKey, 0)
	ui.message(_("%s percent") % getVolume())


class Button(NVDAObject):
	def script_activate(self, gesture):
		try:
			self.doAction()
			if self.windowControlID == ctrlIdsDic["favButton"]:
				eventHandler.queueEvent("gainFocus", self)
				time.sleep(0.1)
				api.processPendingEvents()
				KeyboardInputGesture.fromName("downArrow").send()
		except:  # noqa:E722
			gesture.send()

	__gestures = {
		"kb:space": "activate",
		"kb:enter": "activate",
		"kb:return": "activate",
	}


class AppModule(AppModule):
	scriptCategory = _scriptCategory
	_stationsListName = _("Stations")
	_searchEditName = _("Search")

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		toggleDebugFlag()
		self.taskTimer = None
		self.badStations = _addonConfigManager.getBadStations()
		self.installGestures()

	def installGestures(self):
		if _addonConfigManager.toggleUseShiftControlGesturesOption(False):
			self.bindGestures(self._shiftControlGestures)
		else:
			self.bindGestures(self._altControlGestures)

	def event_NVDAObject_init(self, obj):
		if obj.windowControlID == ctrlIdsDic["searchEdit"]:
			obj.parent.name = self._searchEditName
		if obj.windowControlID == ctrlIdsDic["stationsList"]:
			obj.parent.name = self._stationsListName

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role == controlTypes.ROLE_BUTTON:
			clsList.insert(0, Button)

	def event_appModule_gainFocus(self):
		self.prevProgressBarOutputMode = config.conf["presentation"]["progressBarUpdates"]["progressBarOutputMode"]  # noqa:E501
		if _addonConfigManager.toggleDesactivateProgressBarsUpdateOption(False):
			config.conf["presentation"]["progressBarUpdates"]["progressBarOutputMode"] = "off"  # noqa:E501

	def event_appModule_loseFocus(self):
		config.conf["presentation"]["progressBarUpdates"]["progressBarOutputMode"] = self.prevProgressBarOutputMode  # noqa:E501

	def inMainWindow(self):
		foreground = api.getForegroundObject()
		child = foreground.firstChild
		if foreground.windowClassName == "#32770" and foreground.childCount and\
			(child.windowClassName, child.windowControlID) in firstChildWindow:
			return True
		return False

	def script_clickExitButton(self, gesture):
		def callback():
			h = winUser.getForegroundWindow()
			obj = api.getFocusObject()
			if gui.messageBox(
				# Translators: message to ask the user if he want quit RadioSure.
				_("Are you sure you want  to quit RadioSure?"),
				# Translators: dialog's title.
				_("Warning"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) == wx.YES:
				oldSpeechMode = getSpeechMode()
				setSpeechMode_off()
				winUser.setForegroundWindow(h)
				obj.setFocus()
				eventHandler.queueEvent("gainFocus", obj)
				time.sleep(0.1)
				api.processPendingEvents()
				clickButton("exitButton")
				setSpeechMode(oldSpeechMode)
			else:
				winUser.setForegroundWindow(h)
				time.sleep(0.5)
				obj.setFocus()
				eventHandler.queueEvent("gainFocus", obj)
		if not self.inMainWindow():
			gesture.send()
			return
		wx.CallAfter(callback)

	script_clickExitButton .__doc__ = _("Move focus to Exit button and click it to exit the application")  # noqa:E501

	def script_clickPlayButton(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		clickButtonWithoutMoving("playButton")
		sayStationState()

	script_clickPlayButton .__doc__ = _("Without moving focus, click on  Play button to play or stop the current station")  # noqa:E501

	def script_clickBackButton(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving("backButton")
		if name:
			ui.message(name)
		wx.CallLater(2000, sayStationName)

	script_clickBackButton .__doc__ = _("Without moving focus, click on Back button to play the prior played station")  # noqa:E501

	def script_clickNextButton(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving("nextButton")
		if name:
			ui.message(name)
		wx.CallLater(2000, sayStationName)

	script_clickNextButton .__doc__ = _("Without moving focus, click on  Next button to play the next played station")  # noqa:E501

	def script_clickRecButton(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving("recButton")
		if name:
			ui.message(name)

	script_clickRecButton .__doc__ = _("Without moving focus, click on  Rec button to start or stop record")  # noqa:E501

	def script_clickExpandButton(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		focus = api.getFocusObject()
		if getControlID(focus.windowHandle) in [ctrlIdsDic["stationsList"], ctrlIdsDic["searchEdit"]]:  # noqa:E501
			# focus in search edit box or stations list, we can't stay here
			name = clickButton("expandButton")
		else:
			name = clickButtonWithoutMoving("expandButton")
		if name:
			ui.message(name)
		# say if stations list is visible or not.
			time.sleep(1.0)
			h = findWindowNVDAObject("stationsList").windowHandle
			if not h or not winUser.isWindowVisible(h):
				ui.message(_("Search edit box and Stations list are not more visible"))
				obj = api.getFocusObject()
			else:
				# now set focus on stations list
				obj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h, -4, 0)
				obj.setFocus()
			eventHandler.queueEvent("gainFocus", obj)

	script_clickExpandButton .__doc__ = _("Without moving focus, click  on Expand button to  show or mask stations list")  # noqa:E501

	def script_clickOptionsButton(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		# clickButton("optionsButton")
		obj = findWindowNVDAObject("optionsButton")
		if obj is None:
			return None
		obj.IAccessibleObject.accDoDefaultAction(0)

	script_clickOptionsButton .__doc__ = _("Move focus to Options button and click it to open Options dialog")  # noqa:E501

	def script_clickFavButton(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		clickButton("favButton")
		obj = api.getFocusObject()
		eventHandler.queueEvent("gainFocus", obj)
		time.sleep(0.1)
		api.processPendingEvents()
		KeyboardInputGesture.fromName("downArrow").send()

	script_clickFavButton.__doc__ = _("Move focus to Fav button and click it to show the list of favorites station")  # noqa:E501

	def script_clickTopButton(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving("topButton")
		if name:
			ui.message(name)
	script_clickTopButton .__doc__ = _("Without moving focus, click on Top buttonto ???")  # noqa:E501

	def script_clickMuteButton(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving("muteButton")
		if name:
			ui.message(name)

	script_clickMuteButton .__doc__ = _("Without moving focus, click on Mute butt button to Mute volume on or off")  # noqa:E501

	def script_decreaseSlightlyVolume(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		modifyVolume(VK_DOWN)
	script_decreaseSlightlyVolume .__doc__ = _("Decrease slightly the volume(down 3%)")  # noqa:E501

	def script_increaseSlightlyVolume(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		modifyVolume(VK_UP)
	script_increaseSlightlyVolume .__doc__ = _("Increase slightly the volume(up 3%)")  # noqa:E501

	def script_decreaseVolume(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		modifyVolume(VK_LEFT)

	script_decreaseVolume .__doc__ = _("Decrease the volume(down 5%)")

	def script_increaseVolume(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		modifyVolume(VK_RIGHT)
	script_increaseVolume .__doc__ = _("Increase the volume(up 5%)")

	def script_increaseStronglyVolume(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		modifyVolume(VK_NEXT)
	script_increaseStronglyVolume.__doc__ = _("Increase strongly  the volume(up 20%)")  # noqa:E501

	def script_decreaseStronglyVolume(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		modifyVolume(VK_PRIOR)
	script_decreaseStronglyVolume.__doc__ = _("Decrease strongly the volume(down -20%)")  # noqa:E501

	def script_middleVolume(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		obj = findWindowNVDAObject("volume")
		if obj is None:
			returnh
		sendMessage(obj.windowHandle, 1029, False, 47)
		modifyVolume(VK_UP)
	script_middleVolume .__doc__ = _("Set volume to middle( 50%)")

	def script_sayVolume(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		volume = getVolume()
		if volume:
			ui.message(_("%s percent") % volume)

	script_sayVolume.__doc__ = _("Say volume")

	def script_sayStationInformations(self, gesture):
		def callback(repeatCount):
			text = getPlayInfos()
			if repeatCount:
				api.copyToClip(text)
				ui.message(_("Informations copied to clipboard"))
			else:
				ui.message(text)
		if not self.inMainWindow():
			gesture.send()
			return
		if self.taskTimer:
			self.taskTimer.Stop()
		wx.CallAfter(callback, getLastScriptRepeatCount())

	script_sayStationInformations.__doc__ = _("Say the name   of current station and the status line. Twice, copy these informations  to clipboard")  # noqa:E501

	def script_sayBuffer(self, gesture):
		def callback(repeatCount):
			self.taskTimer = None
			obj = findWindowNVDAObject("buffer")
			if obj is None or not self.inMainWindow():
				return
			text = obj.windowText
			if repeatCount:
				speakSpelling(text[text.find(":")+1:].strip())
			else:
				ui.message(text)
		if self.taskTimer:
			self.taskTimer.Stop()
		if not self.inMainWindow():
			gesture.send()
			return
		self.taskTimer = wx.CallLater(300, callback, getLastScriptRepeatCount())
	script_sayBuffer.__doc__ = _("Say buffer")

	def script_goToStationsList(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		obj = findWindowNVDAObject("stationsList")
		focus = api.getFocusObject()
		if obj == focus:
			ui.message(_("You are in stations list window"))
			return
		if obj is None or not winUser.isWindowVisible(obj.windowHandle):
			# try to  display stations list by pressing expand button
			clickButton("expandButton")
			time.sleep(1.0)
			obj = findWindowNVDAObject("stationsList")
			if obj is None or not winUser.isWindowVisible(obj.windowHandle):
				# impossible to display list
				ui.message(_("Stations list not found"))
				return
		# now set focus
		obj.setFocus()
		eventHandler.queueEvent("gainFocus", obj)

	script_goToStationsList.__doc__ = _("Move focus to stations list. IF stations list is not visible, click Expand button before.")  # noqa:E501

	def _getSearchEditComboBoxObject(self):
		foreground = api.getForegroundObject()
		for i in range(0, foreground.childCount):
			o = foreground.getChild(i)
			if o.windowControlID == 1019 and o.role == controlTypes.ROLE_COMBOBOX:
				return o
		return None

	def checkSearchEditComboBoxDisplay(self, setFocus=False):
		# check if  search edit combo box is shown.
		# If Not press "expand" buttonto show it.
		obj = findWindowNVDAObject("searchCombo")
		if obj is None or not winUser.isWindowVisible(obj.windowHandle):
			clickButton("expandButton")
			time.sleep(1.0)
			obj = findWindowNVDAObject("searchCombo")
			if obj is None or not winUser.isWindowVisible(obj.windowHandle):
				# impossible to display search edit box
				ui.message(_("Search edit box not found"))
				return False
		if setFocus:
			comboBox = self._getSearchEditComboBoxObject()
			comboBox.setFocus()
		return True

	def script_goToSearchEditBox(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		comboObj = findWindowNVDAObject("searchCombo")
		obj = api.getFocusObject()
		if comboObj == obj or comboObj.firstChild == obj:
			ui.message(_("You are in search edit field"))  # noqa:E501
			return
		if comboObj is None or not winUser.isWindowVisible(comboObj.windowHandle):
			# try to  display search edit box
			# and stations list by pressing expand button
			clickButton("expandButton")
			time.sleep(1.0)
			comboObj = findWindowNVDAObject("searchCombo")
			if comboObj is None or not winUser.isWindowVisible(comboObj.windowHandle):
				# impossible to display search edit box
				ui.message(_("Search edit box not found"))
				return
		# now set focus
		comboObj.setFocus()
	script_goToSearchEditBox.__doc__ = _("Move focus to search edit box. IF search edit box is not visible, click Expand button before.")  # noqa:E501

	def clickHeaderColumn(self, column):
		def callback(column):
			speech.cancelSpeech()
			comboBox = self._getSearchEditComboBoxObject()
			api.setNavigatorObject(comboBox)
			review.setCurrentMode("screen", updateReviewPosition=True)
			info = api.getReviewPosition().copy()
			info.collapse()
			info.expand(textInfos.UNIT_LINE)
			baseInfo = info.copy()
			info.collapse(True)
			api.setReviewPosition(info)
			curObject = api.getNavigatorObject()
			if curObject .role == controlTypes.ROLE_LISTITEM:
				info = baseInfo.copy()
				info.collapse()
				api.setReviewPosition(info)
				curObject = api.getNavigatorObject()

			columnHeaders = curObject.parent.children
			columnObj = columnHeaders[column-1]
			if columnObj is None:
				log.error("Cannot found stations list column object:%s" % column)
				return
			name = columnObj.name[1:] if columnObj.name[0] == "*" else columnObj.name
			speech.speakMessage(name)
			time.sleep(0.5)
			location = columnObj.location
			(l, t, w, h) = location
			i = int(l+w-10)
			j = int(t+h/2)
			import winUser
			winUser.setCursorPos(i, j)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN, 0, 0, None, None)
			winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP, 0, 0, None, None)
		if not self.checkSearchEditComboBoxDisplay(True):
			return
		wx.CallLater(800, callback, column)

	def checkStationsList(self):
		stationsListNVDAObject = findWindowNVDAObject("stationsList")
		if stationsListNVDAObject is None\
			or not winUser.isWindowVisible(stationsListNVDAObject.windowHandle):
			# try to  display stations list by pressing expand button
			clickButton("expandButton")
			time.sleep(1.0)
			stationsListNVDAObject = findWindowNVDAObject("stationsList")
			if stationsListNVDAObject is None\
				or not winUser.isWindowVisible(stationsListNVDAObject .windowHandle):
				# impossible to display list
				ui.message(_("Stations list not found"))
		if stationsListNVDAObject.childCount <= 2:
			# Translators: message to user
			# when there are none or one station in the list.
			ui.message(_("Not available because the station list is empty or has only one station"))  # noqa:E501
			return False
		return True

	def script_activate_titleSortMenu(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		if not self.checkStationsList():
			return
		self.clickHeaderColumn(column=1)
	script_activate_titleSortMenu.__doc__ = _("Activate context menu to sort stations list by title")  # noqa:E501

	def script_activate_countrySortMenu(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		if not self.checkStationsList():
			return
		self.clickHeaderColumn(column=2)
	script_activate_countrySortMenu.__doc__ = _("Activate context menu to sort stations list by country")  # noqa:E501

	def script_activate_genreSortMenu(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		if not self.checkStationsList():
			return
		self.clickHeaderColumn(column=3)
	script_activate_genreSortMenu.__doc__ = _("Activate context menu to sort stations list by genre")  # noqa:E501

	def script_activate_languageSortMenu(self, gesture):
		if not self.inMainWindow():
			gesture.send()
			return
		if not self.checkStationsList():
			return
		self.clickHeaderColumn(column=4)
	script_activate_languageSortMenu.__doc__ = _("Activate context menu to sort stations list by language")  # noqa:E501

	def startStation(self, stationsListObject):
		from random import randint
		i = 200
		while i:
			i -= 1
			stationID = randint(0, stationsListObject.childCount-2)
			obj = stationsListObject .getChild(stationID)
			if obj.name not in self.badStations:
				break
		oldSpeechMode = getSpeechMode()
		setSpeechMode_off()
		obj.setFocus()
		api.setFocusObject(obj)
		time.sleep(0.5)
		KeyboardInputGesture.fromName("control+space").send()
		time.sleep(0.2)
		KeyboardInputGesture.fromName("enter").send()
		api.processPendingEvents()
		setSpeechMode(oldSpeechMode)
		return obj

	def script_startStationRandomly(self, gesture):
		from . import rs_translations
		rs_translations.initialize()
		foreground = api.getForegroundObject()
		if foreground.name != "Radio? Sure!":
			clickButtonWithoutMoving("playButton")
		h = findWindow("stationsList")
		if not h or not winUser.isWindowVisible(h):
			# try to  display stations list by pressing expand button
			clickButton("expandButton")
			time.sleep(1.0)
			h = findWindow("stationsList")
			if not h or not winUser.isWindowVisible(h):
				# impossible to display list
				ui.message(_("Stations list not found"))
				return

		def callback(stationsListNVDAObject):
			from .rs_translations import getPlayingTranslation
			maxStationsToCheck = _addonConfigManager.getMaxStationsToCheck()
			stationCount = maxStationsToCheck
			while stationCount:
				stationCount -= 1
				station = self.startStation(stationsListNVDAObject)
				maxDelayForConnexion = _addonConfigManager.getMaxDelayForConnexion()
				while maxDelayForConnexion:
					maxDelayForConnexion -= 1
					time.sleep(1.0)
					infos = getPlayInfos()
					if getPlayingTranslation() in infos:
						# station is playing
						log.warning("playing: %s" % station.name)
						eventHandler.queueEvent("gainFocus", station)
						return
				# it's a bad station
				log.warning("no connexion: %s" % station.name)
				_addonConfigManager.recordBadStation(station.name)
				self.badStations.append(station.name)
				if stationCount == 0:
					# Translators: message to user there is none station with connexion.
					queueHandler.queueFunction(
						queueHandler.eventQueue,
						speech.speakMessage,
						# Translators: message to user
						_("None of the %s stations selected randomly could be connected") % maxStationsToCheck)  # noqa:E501
					eventHandler.queueEvent("gainFocus", station)
				else:
					if maxStationsToCheck - stationCount:
						tones.beep(500, 50)
		stationsListNVDAObject = NVDAObjects.IAccessible.getNVDAObjectFromEvent(
			h, -4, 0)
		if stationsListNVDAObject.childCount == 1:
			# no station in list
			# Translators: message to user there is no station in list.
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				speech.speakMessage,
				# Translators: message to user there is no stations in list.
				_("No station in list"))
			return
		# Translators: message to user when station search is starting.
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			speech.speakMessage,
			_("Station search running"))
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			callback,
			stationsListNVDAObject)

	script_startStationRandomly .__doc__ = _("Start a station randomly")

	def script_test(self, gesture):
		printDebug("test radiosure")
		print("radioSure test")
		ui.message("radioSure test")
		wx.CallAfter(self.script_startStationRandomly, gesture)

	__gestures = {
		"kb:control+alt+f10": "test",
		"kb:control+shift+upArrow": "increaseSlightlyVolume",
		"kb:control+shift+downArrow": "decreaseSlightlyVolume",
		"kb:control+shift+rightArrow": "increaseVolume",
		"kb:control+shift+leftArrow": "decreaseVolume",
		"kb:control+shift+pageUp": "increaseStronglyVolume",
		"kb:control+shift+pageDown": "decreaseStronglyVolume",
		"kb:control+shift+m": "middleVolume",
		"kb:alt+leftArrow": "clickBackButton",
		"kb:alt+rightArrow": "clickNextButton",
		"kb:control+e": "clickExpandButton",
		"kb:control+f": "clickFavButton",
		"kb:control+m": "clickMuteButton",
		"kb:control+o": "clickOptionsButton",
		"kb:control+p": "clickPlayButton",
		"kb:control+q": "clickExitButton",
		"kb:control+r": "clickRecButton",
		"kb:control+t": "clickTopButton",
		"kb:alt+v": "sayVolume",
		"kb:alt+i": "sayStationInformations",
		"kb:alt+b": "sayBuffer",
		}

	_altControlGestures = {
		"kb:alt+control+e": "goToSearchEditBox",
		"kb:alt+control+s": "goToStationsList",
		"kb:alt+control+t": "activate_titleSortMenu",
		"kb:alt+control+c": "activate_countrySortMenu",
		"kb:alt+control+g": "activate_genreSortMenu",
		"kb:alt+control+l": "activate_languageSortMenu",
		"kb:alt+control+r": "startStationRandomly",
		}

	_shiftControlGestures = {
		"kb:shift+control+e": "goToSearchEditBox",
		"kb:shift+control+s": "goToStationsList",
		"kb:shift+control+t": "activate_titleSortMenu",
		"kb:shift+control+c": "activate_countrySortMenu",
		"kb:shift+control+g": "activate_genreSortMenu",
		"kb:shift+control+l": "activate_languageSortMenu",
		"kb:shift+control+r": "startStationRandomly",
		}
