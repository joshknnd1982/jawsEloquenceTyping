# JAWS-style Eloquence typing

An [NVDA](https://www.nvaccess.org/) screen reader add-on that makes typing,
reading and character-navigation feedback with the Eloquence synthesizer
sound more like JAWS.

* Author: Codex, created for jcoff
* Version: 2.5.1
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

This produces `jawsEloquenceTyping-2.5.1.nvda-addon` in the repository root.

## Repository layout

```
addon/
  manifest.ini                  Add-on metadata (name, version, NVDA compatibility)
  globalPlugins/
    jawsEloquenceTyping.py      The global plugin
  doc/
    en/
      readme.html               User documentation bundled with the add-on
build.py                        Builds the .nvda-addon package
```
