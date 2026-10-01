# JAWS-style Eloquence typing

An [NVDA](https://www.nvaccess.org/) screen reader add-on that makes typing,
reading and character-navigation feedback with the Eloquence synthesizer
sound more like JAWS.

* Author: Codex, created for jcoff
* Version: 2.5.2
* Compatibility: NVDA 2024.1 through 2026.1
* Download: grab the `.nvda-addon` file from the
  [releases page](https://github.com/joshknnd1982/jawsEloquenceTyping/releases)

All behavior is runtime-only: the add-on never modifies or saves NVDA's own
configuration. Character echo must already be enabled in NVDA's Keyboard
settings.

## Why this only touches isolated characters

JAWS and NVDA can both drive the same ETI-Eloquence engine, so differences in
tone come from how each screen reader hands text to it, not from a different
synthesizer. During ordinary reading at NVDA's "Some" punctuation level,
terminal punctuation passes straight through to Eloquence, which already
supplies its own native pause and pitch cadence.

Where the two diverge is isolated character announcements: typed character
echo and arrow-key character navigation. There NVDA speaks a symbol's name,
and some of its names differ from JAWS's wording (NVDA says "dot" where JAWS
says "period"). This add-on intercepts exactly those announcements.

## What it does

* **Capital letters** are indicated with a pitch offset (default +20,
  adjustable) instead of saying "cap" or playing a beep.
* **Question marks** are sent as "question?" so Eloquence's native rising
  cadence is heard.
* **Periods** are sent as "period." (JAWS's wording, rather than "dot").
* **Exclamation points** are sent as "exclaim!" (rather than "bang").
* **Commas** are sent as "comma,".
* **Semicolons** are sent as "semicolon;" (rather than "semi").
* **Colons** are sent as "colon:".

Each is applied to typed character echo and to left/right arrow character
navigation.

## Settings

Open the NVDA menu, then Preferences, Settings, JAWS Eloquence Typing, to turn
any of the above on or off individually and to adjust the capital-letter pitch
offset. Only the capital-letter and question-mark behavior has been checked by
ear against real JAWS. If any of the others doesn't sound right, turn it off;
NVDA's own behavior for that character is left untouched when disabled.

For the closest overall match to JAWS, use the same Eloquence voice and
variant in both, and set NVDA's Symbol/Punctuation level to match JAWS's
Punctuation Level.

## Updates

The add-on checks for updates. Once a day, a little after NVDA starts, the add-on asks its GitHub repository, [github.com/joshknnd1982/jawsEloquenceTyping](https://github.com/joshknnd1982/jawsEloquenceTyping), whether a newer version has been released, and says nothing unless there is one. When there is, a dialog shows what's new in a box you can read line by line, and offers to download and install it. The download must match the release's SHA-256 checksum. Then NVDA asks you to confirm the installation and offers to restart. Your settings are kept.

To check yourself, open the NVDA menu, choose **Tools**, then **Check for add-on updates**, and choose **JAWS-style Eloquence typing...**. Or press **Check for updates now** in the add-on's settings: NVDA menu, Preferences, Settings, **JAWS Eloquence Typing**. You can also assign a gesture to **Checks for JAWS-style Eloquence typing updates** in NVDA's Input Gestures dialog, under **JAWS-style Eloquence typing**. To stop the daily check, clear **Check for JAWS-style Eloquence typing updates automatically** in the same settings panel.

## Installation

1. Download the latest `jawsEloquenceTyping-x.y.z.nvda-addon` file from the
   [releases page](https://github.com/joshknnd1982/jawsEloquenceTyping/releases).
2. Press enter on the downloaded file and confirm the installation in NVDA.
3. Restart NVDA when prompted.

## Building from source

Requires Python 3. From the repository root:

```bash
python build.py
```

This produces `jawsEloquenceTyping-2.5.2.nvda-addon` and its `.sha256` checksum
file in the repository root. Upload both to the GitHub release: the update check
reads the release's tag, such as `v2.5.2`, and checks the download against the
checksum.

## Repository layout

```
addon/
  manifest.ini                  Add-on metadata (name, version, NVDA compatibility)
  globalPlugins/
    jawsEloquenceTyping/
      __init__.py               The global plugin
      updater.py                The GitHub update check, shared by all of
                                joshknnd1982's add-ons; keep it identical
  doc/
    en/
      readme.html               User documentation bundled with the add-on
build.py                        Builds the .nvda-addon package
```

## License

MIT License. See [LICENSE](LICENSE).
