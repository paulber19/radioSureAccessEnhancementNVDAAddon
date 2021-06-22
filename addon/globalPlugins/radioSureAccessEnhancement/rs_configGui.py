# globalPlugins\radioSureAccessEnhancement\rs_configGui.py
# a part of radioSureAccessEnhancement add-on
# Copyright 2019,paulber19
# This file is covered by the GNU General Public License.

# manage add-on configuration dialog
import addonHandler
import wx
import gui
from gui.settingsDialogs import MultiCategorySettingsDialog, SettingsPanel
import os
import sys
import core
import queueHandler
_curAddon = addonHandler.getCodeAddon()
_addonSummary = _curAddon.manifest['summary']
path = os.path.join(_curAddon.path, "shared")
sys.path.append(path)
from rs_addonConfigManager import _addonConfigManager  # noqa:E402  # noqa:E402
from rs_NVDAStrings import NVDAString  # noqa:E402
del sys.path[-1]
addonHandler.initTranslation()


def askForNVDARestart():
	if gui.messageBox(
		# Translators: A message asking the user if they wish to restart NVDA
		_("Some Changes have been made . You must save the configuration and restart NVDA for these changes to take effect. Would you like to do it now?"),  # noqa:E501
		"%s - %s" % (_addonSummary, NVDAString("Restart NVDA")),
		wx.YES | wx.NO | wx.ICON_WARNING) == wx.YES:
		_addonConfigManager.saveSettings(True)
		queueHandler.queueFunction(queueHandler.eventQueue, core.restart)
		return
	gui.messageBox(
		# Translators: A message  to user
		_("Don't forget to save the configuration for the changes to take effect !"),
		"%s - %s" % (_addonSummary, NVDAString("Warning")),
		wx.OK | wx.ICON_WARNING)


class OptionsSettingsPanel(SettingsPanel):
	# Translators: This is the label for the Audacity settings  dialog.
	title = _("Options")

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in Options Settings panel.
		labelText = _("Desactivate progress &bars update")
		self.desactivateProgressBarsUpdateBox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.desactivateProgressBarsUpdateBox.SetValue(
			_addonConfigManager.toggleDesactivateProgressBarsUpdateOption(False))
		# Translators: This is the label for a group of editing options
		# in Options settings panel.
		groupText = _("Random playing")
		group = gui.guiHelper.BoxSizerHelper(
			self,
			sizer=wx.StaticBoxSizer(
				wx.StaticBox(self, label=groupText),
				wx.VERTICAL))
		sHelper.addItem(group)
		# Translators: This is the label for a choice in the Options settings panel.
		labelText = _("&Maximum stations to check:")
		choice = [x for x in reversed(list(range(1, 11)))]
		self.maxStationsToCheckBox = group.addLabeledControl(
			labelText,
			wx.Choice,
			choices=[str(x) for x in choice])
		self.maxStationsToCheckBox.SetSelection(
			choice.index(_addonConfigManager.getMaxStationsToCheck()))
		# Translators: This is the label for a choice in the Options settings panel.
		labelText = _("&Maximum delay for waiting connexion (in seconds):")
		choice = [x for x in reversed(list(range(1, 16)))]
		self.maxDelayForConnexionBox = group.addLabeledControl(
			labelText,
			wx.Choice,
			choices=[str(x) for x in choice])
		self.maxDelayForConnexionBox.SetSelection(
			choice.index(_addonConfigManager.getMaxDelayForConnexion()))
		# Translators: This is the label for a checkbox in Options Settings panel.
		labelText = _("&Skip stations without connexion")
		self.skipStationsWithoutConnexionBox = group.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.skipStationsWithoutConnexionBox.SetValue(
			_addonConfigManager.toggleSkipStationsWithoutConnexionOption(False))
		# translators: label for a button in Options settings panel.
		labelText = _("&Clear history of stations without connexion")
		clearHistoryButton = wx.Button(self, label=labelText)
		group.addItem(clearHistoryButton)
		clearHistoryButton.Bind(wx.EVT_BUTTON, self.onClearHistoryButton)
		# Translators: This is the label for a checkbox in Options Settings panel.
		labelText = _("""&Use "shift+control" instead of "alt+control" for input gestures""")  # noqa:E501
		self.useShiftControlGesturesCheckbox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.useShiftControlGesturesCheckbox.SetValue(
			_addonConfigManager.toggleUseShiftControlGesturesOption(False))

	def onClearHistoryButton(self, evt):
		if gui.messageBox(
			# Translators:  message to ask the user
			# if  he wants to clear  stations's history.
			_("Are you sure you want  to clearthe history of stations without connexion?"),  # noqa:E501
			# Translators: title of message box.
			_("Warning"),
			wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) == wx.YES:
			_addonConfigManager.clearBadStationsHistory()

	def postInit(self):
		self.AutomaticSelectionChangeReportBox.SetFocus()

	def saveSettingChanges(self):
		self.restartNVDA = False
		if self.desactivateProgressBarsUpdateBox.IsChecked() != _addonConfigManager .toggleDesactivateProgressBarsUpdateOption(False):  # noqa:E501
			_addonConfigManager .toggleDesactivateProgressBarsUpdateOption(True)
		value = self.maxStationsToCheckBox.GetStringSelection()
		_addonConfigManager.setMaxStationsToCheck(int(value))
		value = self.maxDelayForConnexionBox.GetStringSelection()
		_addonConfigManager.setMaxDelayForConnexion(int(value))
		if self.skipStationsWithoutConnexionBox.IsChecked() != _addonConfigManager .toggleSkipStationsWithoutConnexionOption(False):  # noqa:E501
			_addonConfigManager .toggleSkipStationsWithoutConnexionOption(True)
		if self.useShiftControlGesturesCheckbox.IsChecked() != _addonConfigManager .toggleUseShiftControlGesturesOption(False):  # noqa:E501
			self.restartNVDA = True
			_addonConfigManager .toggleUseShiftControlGesturesOption(True)  # noqa:E501

	def postSave(self):
		if self.restartNVDA:
			askForNVDARestart()

	def onSave(self):
		self.saveSettingChanges()


class UpdateSettingsPanel(SettingsPanel):
	# Translators: This is the label for the Advanced settings panel.
	title = _("Update")

	def __init__(self, parent):
		super(UpdateSettingsPanel, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: This is the label for a checkbox in the Update Settings panel.
		labelText = _("Automatically check for &updates ")
		self.autoCheckForUpdatesCheckBox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.autoCheckForUpdatesCheckBox.SetValue(
			_addonConfigManager.toggleAutoUpdateCheck(False))
		# Translators: This is the label for a checkbox in the Update settings panel.
		labelText = _("Update also release versions to &developpement versions")
		self.updateReleaseVersionsToDevVersionsCheckBox = sHelper.addItem(
			wx.CheckBox(self, wx.ID_ANY, label=labelText))
		self.updateReleaseVersionsToDevVersionsCheckBox.SetValue(
			_addonConfigManager.toggleUpdateReleaseVersionsToDevVersions(False))
		# translators: label for a button in Update settings panel.
		labelText = _("&Check for update")
		checkForUpdateButton = wx.Button(self, label=labelText)
		sHelper.addItem(checkForUpdateButton)
		checkForUpdateButton.Bind(wx.EVT_BUTTON, self.onCheckForUpdate)
		# translators: this is a label for a button in update settings panel.
		labelText = _("View &history")
		seeHistoryButton = wx.Button(self, label=labelText)
		sHelper.addItem(seeHistoryButton)
		seeHistoryButton.Bind(wx.EVT_BUTTON, self.onSeeHistory)

	def onCheckForUpdate(self, evt):
		from .updateHandler import addonUpdateCheck
		self.saveSettingChanges()
		releaseToDevVersion = self.updateReleaseVersionsToDevVersionsCheckBox.IsChecked()  # noqa:E501
		wx.CallAfter(addonUpdateCheck, auto=False, releaseToDev=releaseToDevVersion)
		self.Close()

	def onSeeHistory(self, evt):
		addon = addonHandler.getCodeAddon()
		from languageHandler import curLang
		theFile = os.path.join(addon.path, "doc", curLang, "changes.html")
		if not os.path.exists(theFile):
			lang = curLang.split("_")[0]
			theFile = os.path.join(addon.path, "doc", lang, "changes.html")
			if not os.path.exists(theFile):
				lang = "en"
				theFile = os.path.join(addon.path, "doc", lang, "changes.html")
		os.startfile(theFile)

	def saveSettingChanges(self):
		if self.autoCheckForUpdatesCheckBox.IsChecked() != _addonConfigManager .toggleAutoUpdateCheck(False):  # noqa:E501s
			_addonConfigManager .toggleAutoUpdateCheck(True)
		if self.updateReleaseVersionsToDevVersionsCheckBox.IsChecked() != _addonConfigManager .toggleUpdateReleaseVersionsToDevVersions(False):  # noqa:E501
			_addonConfigManager .toggleUpdateReleaseVersionsToDevVersions(True)

	def postSave(self):
		pass

	def onSave(self):
		self.saveSettingChanges()


class AddonSettingsDialog(MultiCategorySettingsDialog):
	# translators: title of the dialog.
	dialogTitle = _("Settings")
	title = "%s - %s" % (_curAddon.manifest["summary"], dialogTitle)
	INITIAL_SIZE = (1000, 480)
	# Min height required to show the OK, Cancel, Apply buttons
	MIN_SIZE = (470, 240)

	categoryClasses = [
		OptionsSettingsPanel,
		UpdateSettingsPanel,
		]

	def __init__(self, parent, initialCategory=None):
		super(AddonSettingsDialog, self).__init__(parent, initialCategory)
