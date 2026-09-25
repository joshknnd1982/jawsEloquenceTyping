"""Apply JAWS-style Eloquence feedback while reading, typing, and navigating by character.

Background
----------
JAWS and NVDA can both drive the same underlying ETI-Eloquence engine, so
differences in "tone" are not a different synthesizer - they come from how
each screen reader hands text to it. During ordinary reading (say-all, line
reading) at NVDA's default "Some" symbol level, terminal punctuation such as
. ! ? , ; : is NOT converted to a spoken word - the raw character is passed
straight through to Eloquence, which applies its own native pause/pitch
prosody. That already matches JAWS closely, provided NVDA's symbol/punctuation
level is set to "Some" (matching JAWS's own Punctuation Level) and the same
Eloquence voice/variant (e.g. "Reed") is selected in both.

Where the two products audibly diverge is isolated character announcements -
typed character echo, and arrow-key character navigation - where NVDA speaks
a symbol's NAME (and its names do not always match JAWS's wording, e.g. NVDA
says "dot" for "." where JAWS says "period"). This add-on intercepts exactly
those isolated announcements and, instead of NVDA's flat spoken name, sends
Eloquence a short string built from a JAWS-style word plus the REAL character
(e.g. "period." or "question?"), so Eloquence's own native prosody engine
supplies the pause/rising/falling cadence, the same way it does for JAWS.

Each fix below is independently toggleable in NVDA's Settings dialog (NVDA
menu > Preferences > Settings > JAWS Eloquence Typing), since only the
capital-letter and question-mark handling has been validated by ear against
real JAWS; the rest follow the same pattern but are new and worth checking.
This add-on never writes to NVDA's own configuration - only its own settings.
"""

import config
import globalPluginHandler
import gui
import speech
import synthDriverHandler
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel
from speech.commands import CharacterModeCommand, EndUtteranceCommand, PitchCommand
from speech.extensions import filter_speechSequence
import addonHandler

addonHandler.initTranslation()

# Maps NVDA's default spoken word for an isolated punctuation character to:
#   (the real character, the config key that enables the fix, the JAWS-style
#   word to send instead of NVDA's own word)
# Order matters only for the settings panel layout below.
_PUNCT_BY_SPOKEN_WORD = {
	"question": (
		"?",
		"enableQuestionMarkFix",
		"question",
		# Translators: label of a checkbox in JAWS Eloquence Typing's settings.
		_('Question marks (?) - native rising "question" cadence'),
	),
	"dot": (
		".",
		"enablePeriodFix",
		"period",
		# Translators: label of a checkbox in JAWS Eloquence Typing's settings.
		_('Periods (.) - say "period" (JAWS wording) with native falling cadence'),
	),
	"bang": (
		"!",
		"enableExclamationFix",
		"exclaim",
		# Translators: label of a checkbox in JAWS Eloquence Typing's settings.
		_('Exclamation points (!) - say "exclaim" (JAWS wording) with native emphasis'),
	),
	"comma": (
		",",
		"enableCommaFix",
		"comma",
		# Translators: label of a checkbox in JAWS Eloquence Typing's settings.
		_("Commas (,) - native pause cadence"),
	),
	"semi": (
		";",
		"enableSemicolonFix",
		"semicolon",
		# Translators: label of a checkbox in JAWS Eloquence Typing's settings.
		_('Semicolons (;) - say "semicolon" (JAWS wording) with native pause'),
	),
	"colon": (
		":",
		"enableColonFix",
		"colon",
		# Translators: label of a checkbox in JAWS Eloquence Typing's settings.
		_("Colons (:) - native pause cadence"),
	),
}

confspec = {
	"enableCapitalPitchOffset": "boolean(default=true)",
	"capitalPitchOffset": "integer(default=20,min=-50,max=50)",
	"enableQuestionMarkFix": "boolean(default=true)",
	"enablePeriodFix": "boolean(default=true)",
	"enableExclamationFix": "boolean(default=true)",
	"enableCommaFix": "boolean(default=true)",
	"enableSemicolonFix": "boolean(default=true)",
	"enableColonFix": "boolean(default=true)",
}
config.conf.spec["jawsEloquenceTyping"] = confspec


class JAWSEloquenceTypingSettingsPanel(SettingsPanel):
	# Translators: title of the settings category in NVDA's Settings dialog.
	title = _("JAWS Eloquence Typing")

	def makeSettings(self, settingsSizer):
		helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		helper.addItem(
			wx.StaticText(
				self,
				label=_(
					"These only affect isolated character announcements (typed echo "
					"and arrow-key character navigation) while Eloquence is active. "
					"Normal reading is unaffected. For the closest match to JAWS, also "
					'set NVDA\'s own Symbol/Punctuation level to "Some" and use the '
					"same Eloquence voice/variant as JAWS."
				),
			)
		)

		capsSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.enableCapitalPitchCheckBox = wx.CheckBox(
			self,
			# Translators: label of a checkbox in JAWS Eloquence Typing's settings.
			label=_("Capital letters - pitch offset instead of saying \u201ccap\u201d"),
		)
		self.enableCapitalPitchCheckBox.SetValue(
			config.conf["jawsEloquenceTyping"]["enableCapitalPitchOffset"]
		)
		capsSizer.Add(self.enableCapitalPitchCheckBox, flag=wx.ALIGN_CENTER_VERTICAL)
		capsSizer.AddSpacer(guiHelper.SPACE_BETWEEN_ASSOCIATED_CONTROL_HORIZONTAL)
		# Translators: label of a numeric control in JAWS Eloquence Typing's settings.
		capsSizer.Add(wx.StaticText(self, label=_("Pitch offset:")), flag=wx.ALIGN_CENTER_VERTICAL)
		capsSizer.AddSpacer(guiHelper.SPACE_BETWEEN_ASSOCIATED_CONTROL_HORIZONTAL)
		self.capitalPitchOffsetCtrl = wx.SpinCtrl(self, min=-50, max=50)
		self.capitalPitchOffsetCtrl.SetValue(
			config.conf["jawsEloquenceTyping"]["capitalPitchOffset"]
		)
		capsSizer.Add(self.capitalPitchOffsetCtrl)
		helper.addItem(capsSizer)

		self._punctCheckBoxes = {}
		for symbol, confKey, _word, label in _PUNCT_BY_SPOKEN_WORD.values():
			checkBox = helper.addItem(wx.CheckBox(self, label=label))
			checkBox.SetValue(config.conf["jawsEloquenceTyping"][confKey])
			self._punctCheckBoxes[confKey] = checkBox

	def onSave(self):
		config.conf["jawsEloquenceTyping"]["enableCapitalPitchOffset"] = (
			self.enableCapitalPitchCheckBox.GetValue()
		)
		config.conf["jawsEloquenceTyping"]["capitalPitchOffset"] = (
			self.capitalPitchOffsetCtrl.GetValue()
		)
		for confKey, checkBox in self._punctCheckBoxes.items():
			config.conf["jawsEloquenceTyping"][confKey] = checkBox.GetValue()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Provide runtime-only JAWS-style feedback without changing NVDA's own settings."""

	def __init__(self):
		super().__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(
			JAWSEloquenceTypingSettingsPanel
		)
		filter_speechSequence.register(self._filterSpeechSequence)

	def terminate(self):
		try:
			filter_speechSequence.unregister(self._filterSpeechSequence)
		except (AttributeError, RuntimeError):
			pass
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(
				JAWSEloquenceTypingSettingsPanel
			)
		except (AttributeError, ValueError):
			pass
		super().terminate()

	def _getEloquenceSynthIfActive(self):
		try:
			synth = synthDriverHandler.getSynth()
		except Exception:
			return None
		if not synth or synth.name.lower() != "eloquence":
			return None
		return synth

	def _filterSpeechSequence(self, speechSequence):
		"""Adjust standalone punctuation and capitals for Eloquence."""
		textItems = [item for item in speechSequence if isinstance(item, str) and item.strip()]
		endsUtterance = any(isinstance(item, EndUtteranceCommand) for item in speechSequence)
		if not endsUtterance or len(textItems) != 1:
			return speechSequence
		word = textItems[0].strip()

		isCapital = len(word) == 1 and word.isalpha() and word.isupper()
		punctInfo = _PUNCT_BY_SPOKEN_WORD.get(word)
		if not (isCapital or punctInfo):
			return speechSequence

		conf = config.conf["jawsEloquenceTyping"]
		if isCapital and not conf["enableCapitalPitchOffset"]:
			return speechSequence
		if punctInfo and not conf[punctInfo[1]]:
			return speechSequence

		synth = self._getEloquenceSynthIfActive()
		if not synth:
			return speechSequence

		if punctInfo:
			symbol, _confKey, replacementWord, _label = punctInfo
			result = []
			replaced = False
			for item in speechSequence:
				if not replaced and isinstance(item, str) and item.strip() == word:
					leading = item[: len(item) - len(item.lstrip())]
					trailing = item[len(item.rstrip()) :]
					result.append(f"{leading}{replacementWord}{symbol}{trailing}")
					replaced = True
				else:
					result.append(item)
			return result

		# Capital letter: replace NVDA's configured capital pitch command when present.
		offset = conf["capitalPitchOffset"]
		result = []
		pitchReplaced = False
		for item in speechSequence:
			if isinstance(item, PitchCommand) and not item.isDefault and not pitchReplaced:
				result.append(PitchCommand(offset=offset))
				pitchReplaced = True
			else:
				result.append(item)
		if pitchReplaced:
			return result

		# Add a pitch wrapper when NVDA did not generate one itself.
		result = []
		for item in speechSequence:
			if isinstance(item, str) and item.strip() == word:
				result.extend([PitchCommand(offset=offset), item, PitchCommand()])
			else:
				result.append(item)
		return result

	def event_typedCharacter(self, obj, nextHandler, ch):
		"""Speak a typed punctuation/capital character with JAWS-style cadence."""
		conf = config.conf["jawsEloquenceTyping"]
		characterEcho = config.conf["keyboard"]["speakTypedCharacters"]
		isCapital = len(ch) == 1 and ch.isalpha() and ch.isupper()
		punctFix = None
		for spokenWord, info in _PUNCT_BY_SPOKEN_WORD.items():
			symbol, confKey, replacementWord, _label = info
			if ch == symbol:
				punctFix = info
				break

		wantsCapitalFix = isCapital and conf["enableCapitalPitchOffset"]
		wantsPunctFix = punctFix is not None and conf[punctFix[1]]

		if not (wantsCapitalFix or wantsPunctFix) or not characterEcho:
			nextHandler()
			return
		synth = self._getEloquenceSynthIfActive()
		if not synth:
			nextHandler()
			return

		# Preserve all of NVDA's normal typed-character and typed-word handling.
		# Cancel only the just-queued flat echo before speaking our replacement.
		# Crucially, this add-on never writes to config.conf.
		nextHandler()
		speech.cancelSpeech()

		if wantsPunctFix:
			symbol, _confKey, replacementWord, _label = punctFix
			# Send one uninterrupted word plus real punctuation directly to
			# Eloquence. NVDA's high-level speech processing would replace the
			# character with its spoken name before the synthesizer could use
			# it for natural prosody.
			synth.speak([f"{replacementWord}{symbol}"])
		else:
			offset = conf["capitalPitchOffset"]
			# Indicate typed capitals with a pitch offset only.
			speech.speak([
				PitchCommand(offset=offset),
				CharacterModeCommand(True),
				ch,
				CharacterModeCommand(False),
				PitchCommand(),
			])
