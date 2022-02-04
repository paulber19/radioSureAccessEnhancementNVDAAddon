# globalPlugins\radioSureAccessEnhancement\rs_globalPlugin.py
# a part of radioSureAccessEnhancement add-on
# Copyright (C) 2019-2022 Paulber19
# This file is covered by the GNU General Public License.


import addonHandler
import globalPluginHandler
import gui
import wx
import os
import sys
addon = addonHandler.getCodeAddon()
path = os.path.join(addon.path, "shared")
sys.path.append(path)
from rs_addonConfigManager import _addonConfigManager
del sys.path[-1]
addonHandler.initTranslation()


class RadioSureGlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super(RadioSureGlobalPlugin, self).__init__(*args, **kwargs)
		self.installSettingsMenu()
		from . updateHandler import autoUpdateCheck
		if _addonConfigManager.toggleAutoUpdateCheck(False):
			autoUpdateCheck(releaseToDev=_addonConfigManager.toggleUpdateReleaseVersionsToDevVersions(False))

	def installSettingsMenu(self):
		self.preferencesMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
		from .rs_configGui import AddonSettingsDialog
		self.menu = self.preferencesMenu.Append(
			wx.ID_ANY,
			AddonSettingsDialog.title + " ...",
			"")
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onMenu, self.menu)

	def deleteSettingsMenu(self):
		try:
			self.preferencesMenu.Remove(self.menu)
		except Exception:
			pass

	def terminate(self):
		self.deleteSettingsMenu()
		super(RadioSureGlobalPlugin, self).terminate()

	def onMenu(self, evt):
		from .rs_configGui import AddonSettingsDialog
		wx.CallAfter(gui.mainFrame._popupSettingsDialog, AddonSettingsDialog)
