#globalPlugins\radioSureAccessEnhancement\rs_configGui.py
# a part of radioSureAccessEnhancement add-on
# Copyright 2019,paulber19
#This file is covered by the GNU General Public License.

# manage add-on configuration dialog

import addonHandler
addonHandler.initTranslation()
from logHandler import log
import wx
import gui
from gui.settingsDialogs import SettingsDialog
import os
import sys
_curAddon = addonHandler.getCodeAddon()
_addonSummary = _curAddon.manifest['summary']
path = os.path.join(_curAddon.path, "shared")
sys.path.append(path)
from rs_addonConfigManager import _addonConfigManager
del sys.path[-1]


class RadioSureSettingsDialog(SettingsDialog):
	# Translators: This is the label for the RadioSure settings  dialog.
	title = _("%s - settings")%_addonSummary
	
	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a group of editing options in the RadioSure settings panel.
		groupText = _("Update")
		group = gui.guiHelper.BoxSizerHelper(self, sizer=wx.StaticBoxSizer(wx.StaticBox(self, label=groupText), wx.VERTICAL))
		sHelper.addItem(group)
		# Translators: This is the label for a checkbox in the RadioSure SettingsDialog.
		labelText = _("Automatically check for &updates ")
		self.autoCheckForUpdatesCheckBox=group.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.autoCheckForUpdatesCheckBox.SetValue(_addonConfigManager.toggleAutoUpdateCheck(False))
		# Translators: This is the label for a checkbox in the RadioSure settings panel.
		labelText = _("Update also release versions to &developpement versions")
		self.updateReleaseVersionsToDevVersionsCheckBox=group.addItem (wx.CheckBox(self,wx.ID_ANY, label= labelText))
		self.updateReleaseVersionsToDevVersionsCheckBox.SetValue(_addonConfigManager.toggleUpdateReleaseVersionsToDevVersions     (False))
		# translators: label for a button in RadioSure settings panel.
		labelText = _("&Check for update")
		checkForUpdateButton= wx.Button(self, label=labelText)
		group.addItem (checkForUpdateButton)
		checkForUpdateButton.Bind(wx.EVT_BUTTON,self.onCheckForUpdate)
	
	def onCheckForUpdate(self, evt):
		from .updateHandler import addonUpdateCheck
		releaseToDevVersion = self.updateReleaseVersionsToDevVersionsCheckBox.IsChecked() # or toggleUpdateReleaseVersionsToDevVersionsGeneralOptions(False)
		wx.CallAfter(addonUpdateCheck, auto = False, releaseToDev =releaseToDevVersion  )

		self.Close()
	
	def postInit(self):
		self.autoCheckForUpdatesCheckBox.SetFocus()
	
	def saveSettingChanges (self):
		if self.autoCheckForUpdatesCheckBox.IsChecked() != _addonConfigManager .toggleAutoUpdateCheck(False):
			_addonConfigManager .toggleAutoUpdateCheck(True)
		
		if self.updateReleaseVersionsToDevVersionsCheckBox.IsChecked() != _addonConfigManager .toggleUpdateReleaseVersionsToDevVersions     (False):
			_addonConfigManager .toggleUpdateReleaseVersionsToDevVersions     (True)
	
	def onOk(self,evt):
		self.saveSettingChanges()
		super(RadioSureSettingsDialog, self).onOk(evt)
