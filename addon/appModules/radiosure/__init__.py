#appModules\radioSure\__init__.py
# a part of radioSureAccessEnhancement add-on
#Copyright (C) 2019, Paulber19
#This file is covered by the GNU General Public License.
# Released under GPL 2


import addonHandler
addonHandler.initTranslation()
import gui
from logHandler import log
import appModuleHandler,ctypes,NVDAObjects,globalCommands,speech
from scriptHandler import getLastScriptRepeatCount
from speech import speakSpelling
import ui
import eventHandler
import winUser
from winUser import getWindow,getControlID,setFocus,sendMessage,mouse_event,MOUSEEVENTF_LEFTDOWN,MOUSEEVENTF_LEFTUP,setCursorPos,getWindowText
from winUser import VK_DOWN,VK_UP,VK_SPACE,VK_NEXT,VK_PRIOR, VK_LEFT, VK_RIGHT
#from win32con import ff,WM_KEYDOWN,WM_SETFOCUS
import controlTypes
from NVDAObjects.IAccessible import IAccessible
from  NVDAObjects import NVDAObject
import api
import os
import wx
import time
import speech
from keyboardHandler import KeyboardInputGesture, trappedKeys
import sys
_curAddon = addonHandler.getCodeAddon()
path = os.path.join(_curAddon.path, "shared")
sys.path.append(path)
from rs_py3Compatibility import _unicode
del sys.path[-1]

# winUser constants
WM_KEYUP                        = 0x0101
WM_KEYDOWN =                      0x0100
WM_SETFOCUS                     = 0x0007



_addonSummary = _curAddon.manifest['summary']
_addonVersion = _curAddon.manifest['version']
_addonName = _curAddon.manifest['name']
_scriptCategory = _unicode(_addonSummary)

#pour getWindow function
firstWindow =0
nextWindow=2
firstChild =5


ctrlIdsDic = {
		"searchEdit" : 1001,
		"favButton" : 1024,
		"optionsButton": 1041,
		"volume" : 1006,
		"nextButton" : 1039,
		"backButton" : 1038,
		"playButton" : 1000,
		"pauseButton" : 1017,
		"recButton" : 1051,
		"expandButton" : 1076,
		"topButton":1077,
		"exitButton" : 1,
		"stationsList" : 1016,
		"searchCombo" : 1019,
		"muteButton" : 1027,
		"copyURLButton":1046,
		"stateInfo":1007,
		"liveInfo" : 1046,
		"stationName" : 1026,
		"buffer":1009
}
# to find main window, class and control id of first child window
firstChildWindow = (("msctls_trackbar32",1006), ("SysListView32",1016))

def getTopWindow(obj = None):
	if obj == None:
		obj = api.getFocusObject()

	i= 10
	while i and obj:
		i=i-1
		if winUser.getClassName(obj.windowHandle) == "#32770":
			return obj.windowHandle
			
		try:
			obj = obj.parent
		except:
			return None
		
	return None

def inMainWindow(hFocus = None):
	if not hFocus :
		obj = api.getFocusObject()
		
	hTop = getTopWindow(obj)
	if hTop == None:
		log.warning("error, pas de top window")
		return False
		

	hFirstChild = winUser.getWindow(hTop,firstChild)
	id = winUser.getControlID(hFirstChild)
	className = winUser.getClassName(hFirstChild)
	if (className,id) in firstChildWindow:
		return True

	return False

def findWindow(window):
	h = getWindow(getTopWindow(), firstChild)
	id=ctrlIdsDic [window]
	i= 70
	while i:
		i= i-1
		if getControlID(h) == id:
			return h
			
		h=getWindow (h,nextWindow)
	return None

def clickButton (window):
	h = findWindow(window)
	if not h:
		return  None

	obj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,0)
	oldSpeechMode = speech.speechMode
	speech.speechMode = speech.speechMode_off
	obj.IAccessibleObject.accDoDefaultAction (0)
	eventHandler.queueEvent("gainFocus",obj)
	time.sleep(0.1)
	api.processPendingEvents()
	speech.speechMode = oldSpeechMode
	return obj.name


def clickButtonWithoutMoving (window):
	oldSpeechMode = speech.speechMode
	speech.speechMode = speech.speechMode_off
	currentObj = api.getFocusObject()
	name = clickButton (window)
	currentObj.setFocus()
	eventHandler.queueEvent("gainFocus",currentObj)
	time.sleep(0.1)
	api.processPendingEvents()
	speech.speechMode = oldSpeechMode
	return name



	
def getVolume ():
	h = findWindow("volume")
	if h:
		return str (sendMessage (h,1024,0,0))
		
	return ""
def getStationName():
	h = findWindow("stationName")

	if not h:
		return ""
		
	return  winUser.getWindowText(h)


def sayStationName():
	ui.message(getStationName())
	
def getStationState():
	h = findWindow("stateInfo")
	if not h:
		return ""
		
	return getWindowText(h)

def sayStationState():
	text = _("{name} {state}").format(name= getStationName(), state= getStationState())	
	ui.message(text)
	
def getPlayInfos():
# others informations in live field
	h = findWindow("liveInfo")
	text = ""
	if h:
		text=getWindowText (h)
	return _("{name} {state} {live}") .format(name = getStationName(), state = getStationState(), live = text) 

def modifyVolume (vkKey):
	h=findWindow("volume")
	sendMessage(h,WM_KEYDOWN,vkKey,0)
	sendMessage (h,WM_KEYUP,vkKey,0)
	ui.message (_("{0}%") .format(getVolume()))
class Button(NVDAObject):
	
	def script_activate(self, gesture):
		try:
			self.doAction()
			if self.windowControlID == ctrlIdsDic ["favButton"]:
				eventHandler.queueEvent("gainFocus",self)
				time.sleep(0.1)
				api.processPendingEvents()
				KeyboardInputGesture.fromName("downArrow").send()
		except:
			gesture.send()


	__gestures = {
		"kb:space":"activate",
		"kb:enter":"activate",
		"kb:return":"activate",
	}

class AppModule (appModuleHandler.AppModule):
	scriptCategory = _scriptCategory
	_stationsListName = _("Stations")
	_searchEditName = _("Search")
	
	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		self.taskTimer = None
	def event_NVDAObject_init(self, obj):
		if obj.windowControlID == ctrlIdsDic ["searchEdit"]:
			obj.parent.name = self._searchEditName
		if obj.windowControlID == ctrlIdsDic ["stationsList"]:
			obj.parent.name = self._stationsListName
	
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):		
		if obj.role == controlTypes.ROLE_BUTTON:
			clsList.insert(0, Button)
		

	
	def script_clickExitButton (self,gesture):
		def callback():
			h = winUser.getForegroundWindow()
			obj= api.getFocusObject()
			res = gui.messageBox(_("Are you sure you want  to quit RadioSure?"),_("Warning"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_WARNING) 
			if res == wx.YES:
				oldSpeechMode = speech.speechMode
				speech.speechMode = speech.speechMode_off
				winUser.setForegroundWindow(h)
				obj.setFocus()
				eventHandler.queueEvent("gainFocus",obj)
				time.sleep(0.1)
				api.processPendingEvents()
				clickButton ("exitButton")
				speech.speechMode = oldSpeechMode
			else:
				winUser.setForegroundWindow(h)
				time.sleep(0.5)
				obj.setFocus()
				eventHandler.queueEvent("gainFocus",obj)
		if not inMainWindow():
			gesture.send()
			return
		wx.CallAfter(callback)

	script_clickExitButton .__doc__ = _("Move focus to Exit button and click it to exit the application")



	def script_clickPlayButton (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		clickButtonWithoutMoving ("playButton")
		sayStationState()
		
	script_clickPlayButton .__doc__ = _("Without moving focus, click on  Play button to play or stop the current station")


	def script_clickBackButton (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving ("backButton")
		if name:
			ui.message(name)
		wx.CallLater(2000, sayStationName)
		
	script_clickBackButton .__doc__ = _("Without moving focus, click on Back button to play the prior played station")

	def script_clickNextButton (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving ("nextButton")
		if name:
			ui.message(name)
			
		wx.CallLater(2000, sayStationName)
		
	script_clickNextButton .__doc__ = _("Without moving focus, click on  Next button to play the next played station")

	def script_clickRecButton (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving ("recButton")
		if name:
			ui.message(name)

	script_clickRecButton .__doc__ = _("Without moving focus, click on  Rec button to start or stop record")


	def script_clickExpandButton (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		currentH = api.getFocusObject().windowHandle
		if getControlID(currentH) in [ctrlIdsDic ["stationsList"], ctrlIdsDic ["searchEdit"]]:
			#focus in search edit box or stations list, we can't stay here
			name = clickButton("expandButton")
		else:
			name = clickButtonWithoutMoving ("expandButton")
			
		if name:
			ui.message(name)
		#say if stations list is visible or not.
			time.sleep(1.0)
			h=findWindow("stationsList")
			if not h or not winUser.isWindowVisible(h):
				ui.message(_("Search edit box and Stations list are not more visible"))
				obj = api.getFocusObject()
			else:
				# now set focus on stations list
				obj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,0)
				obj.setFocus()
			
			eventHandler.queueEvent("gainFocus",obj)
			
	script_clickExpandButton .__doc__ = _("Without moving focus, click  on Expand button to  show or mask stations list")


	def script_clickOptionsButton (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		#clickButton ("optionsButton")
		h = findWindow("optionsButton")
		if not h:
			return  None
		obj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,0)
		obj.IAccessibleObject.accDoDefaultAction (0)
		
	script_clickOptionsButton .__doc__ = _("Move focus to Options button and click it to open Options dialog")
	
	def script_clickFavButton (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		clickButton ("favButton")
		obj = api.getFocusObject()
		eventHandler.queueEvent("gainFocus",obj)
		time.sleep(0.1)
		api.processPendingEvents()
		KeyboardInputGesture.fromName("downArrow").send()
		
		
	script_clickFavButton.__doc__ = _ ("Move focus to Fav button and click it to show the list of favorites station")



	def script_clickTopButton (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving ("topButton")
		if name:
			ui.message(name)
			
	script_clickTopButton .__doc__ = _("Without moving focus, click on Top buttonto ???")



	def script_clickMuteButton (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		name = clickButtonWithoutMoving ("muteButton")
		if name:
			ui.message(name)
			
	script_clickMuteButton .__doc__ = _("Without moving focus, click on Mute butt button to Mute volume on or off")

	def script_decreaseSlightlyVolume (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		modifyVolume (VK_DOWN)
	script_decreaseSlightlyVolume .__doc__ = _("Decrease slightly the volume (down 3%)")

	def script_increaseSlightlyVolume (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		modifyVolume (VK_UP)
	script_increaseSlightlyVolume .__doc__ = _("Increase slightly the volume (up 3%)")

	def script_decreaseVolume (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		modifyVolume (VK_LEFT)
		
	script_decreaseVolume .__doc__ = _("Decrease the volume (down 5%)")

	def script_increaseVolume (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		modifyVolume (VK_RIGHT)
	script_increaseVolume .__doc__ = _("Increase the volume (up 5%)")


	
	def script_increaseStronglyVolume(self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		modifyVolume(VK_NEXT)
	script_increaseStronglyVolume.__doc__ = _ ("Increase strongly  the volume (up 20%)")
	
	def script_decreaseStronglyVolume(self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		modifyVolume(VK_PRIOR)
		
	script_decreaseStronglyVolume.__doc__ = _("Decrease strongly the volume (down -20%)")



	def script_middleVolume (self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		h = findWindow("volume")
		if not h:
			returnh
			
		sendMessage(h,1029,False,47)
		modifyVolume(VK_UP)
	script_middleVolume .__doc__ = _("Set volume to middle( 50%)") 

	def script_sayVolume(self,gesture):
		if not inMainWindow():
			gesture.send()
			return
		volume =getVolume ()
		if volume :
			ui.message (_("{0}%") .format(volume))
	script_sayVolume.__doc__ = _("Say volume")

	def script_sayStationInformations(self,gesture):
		def callback (repeatCount):

			text=getPlayInfos()
			if repeatCount:
				api.copyToClip(text)
				ui.message(_("Informations copied to clipboard"))
			else:
				ui.message (text)
		
		if not inMainWindow():
			gesture.send()
			return
				
		if self.taskTimer:
			self.taskTimer.Stop()
			
		self.taskTimer = wx.CallLater(300, callback, getLastScriptRepeatCount() )
		
	script_sayStationInformations.__doc__ = _("Say the name   of current station and the status line. Twice, copy these informations  to clipboard")
	
	def  script_sayBuffer (self,gesture):
		def callback(repeatCount):
			self.taskTimer = None
			h = findWindow("buffer")
			if not h or not inMainWindow():
				return
			text=getWindowText (h)
			if repeatCount:
				speakSpelling (text[text.find(":")+1:].strip())
			else:
				ui.message (text)
				

		if self.taskTimer:
			self.taskTimer.Stop()
		if not inMainWindow():
			gesture.send()
			return
	
		self.taskTimer = wx.CallLater(300, callback, getLastScriptRepeatCount ())
	script_sayBuffer.__doc__ = _("Say buffer")
	
	def script_goToStationsList(self, gesture):
		if not inMainWindow():
			gesture.send()
			return
		h=findWindow("stationsList")
		currentH = api.getFocusObject().windowHandle
		if h == currentH:
			ui.message(_("You are in stations list window"))
			return
		id = getControlID(currentH)
		if id == ctrlIdsDic ["searchEdit"]:
			# on search edit box, so just type tab.
			ui.message(_stationsListName)
			KeyboardInputGesture.fromName("Tab").send()
			return


		if not h or not winUser.isWindowVisible(h):
			# try to  display stations list by pressing expand button
			clickButton ("expandButton")
			time.sleep(1.0)
			h=findWindow("stationsList")
			if not h or not winUser.isWindowVisible(h):
				# impossible to display list
				ui.message(_("Stations list not found"))
				return
	
		# now set focus
		obj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,0)
		obj.setFocus()
		eventHandler.queueEvent("gainFocus",obj)

		
	script_goToStationsList.__doc__ = _("Move focus to stations list. IF stations list is not visible, click Expand button before.")

	def script_goToSearchEditBox(self, gesture):
		if not inMainWindow():
			gesture.send()
			return
		h=findWindow("searchCombo")
		obj = api.getFocusObject()
		currentH = obj.windowHandle
		parentH = obj.parent.windowHandle
		if h == currentH or getWindow(h, firstChild) == currentH:

			ui.message(_("You are in search edit field"))
			return
		id = getControlID(currentH)
		if id == ctrlIdsDic ["stationsList"]:
			# on stations list box, so just type shift + tab.
			#ui.message(_stationsListName)
			KeyboardInputGesture.fromName("shift+Tab").send()
			return


		if not h or not winUser.isWindowVisible(h):
			# try to  display search edit box and stations list by pressing expand button
			clickButton ("expandButton")
			time.sleep(1.0)
			h=findWindow("searchCombo")
			if not h or not winUser.isWindowVisible(h):
				# impossible to display search edit box
				ui.message(_("Search edit box not found"))
				return
	
		# now set focus
		obj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,0)
		obj.setFocus()



		
	script_goToSearchEditBox.__doc__ = _("Move focus to search edit box. IF search edit box is not visible, click Expand button before.")


		
	def script_test(self, gesture):
		print ("test radioSure")
		ui.message("radioSure test")
		speech.speakMessage(str(api.getFocusObject().role))
	
	__gestures ={
		"kb:control+alt+f10":"test",
		#"kb:enter":"EnterKey",
		#"kb:return":"EnterKey",
		"kb:control+shift+upArrow":"increaseSlightlyVolume",
		"kb:control+shift+downArrow":"decreaseSlightlyVolume",
		"kb:control+shift+rightArrow":"increaseVolume",
		"kb:control+shift+leftArrow":"decreaseVolume",
		"kb:control+shift+pageUp":"increaseStronglyVolume",
		"kb:control+shift+pageDown":"decreaseStronglyVolume",
		"kb:control+shift+m":"middleVolume",
		"kb:control+leftArrow":"clickBackButton",
		"kb:control+rightArrow":"clickNextButton",
		"kb:control+e":"clickExpandButton",
		"kb:control+f":"clickFavButton",
		"kb:control+m":"clickMuteButton",
		"kb:control+o":"clickOptionsButton",
		"kb:control+p":"clickPlayButton",
		"kb:control+q":"clickExitButton",
		"kb:control+r":"clickRecButton",
		"kb:control+t":"clickTopButton",
		"kb:control+alt+e":"goToSearchEditBox",
		"kb:control+alt+s":"goToStationsList",
		"kb:alt+v":"sayVolume",
		"kb:alt+i":"sayStationInformations",
		"kb:alt+b":"sayBuffer"
		}

