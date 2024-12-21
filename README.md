# Spell Card Maker

This utility generates spell cards based on the beautiful graphic designs
originally developed by nBeebz and friends ([see here][1]).

The cards are made from a spell definition input file that you can create or
customize. Included in this repository are starter files with the standard set
of 5E compatible spells taken from the System Reference Document released by
Wizards of the Coast LLC and available at
https://dnd.wizards.com/resources/systems-reference-document. Check out the
[spell_data](/spell_data) subfolder to view those starter files and the code
that generated them.

| ![][2] | ![][3] | ![][4] | ![][5] | ![][6] |
|--------|--------|--------|--------|--------|


## Requirements

You must install ImageMagick. Spell Card Maker uses the [Wand][7] library,
which is a Python binding to ImageMagick.

Follow the instructions for your OS:
* [Windows (64-bit)][8] *(Note: Typically it is not necessary to set the
  MAGICK_HOME environment variable.)*
* [Linux / Mac][9]


## Basic usage (Windows 64-bit)

1. Install ImageMagick as noted in the [Requirements](#requirements).
2. Grab the latest release of [SpellCardMaker.exe][10].
3. Download a copy of [spells.yaml](/spell_data/spells.yaml).
4. Place `SpellCardMaker.exe` and the `spells.yaml` input file in the same
directory.
5. Using a terminal such as Windows PowerShell, run one of the following
example commands in that directory.

Generate a single spell card from `spells.yaml`:
```commandline
./SpellCardMaker generate spells.yaml -s "Spell Name" -o .
```

Generate cards for every spell in `spells.yaml`:
```commandline
./SpellCardMaker generate spells.yaml -o "Output Directory"
```

To abort in-progress spell card generation, press `CTRL`+`C` on most systems
(keyboard interrupt) 


## Advanced usage

```commandline
./SpellCardMaker generate INPUT_FILE [-o OUTPUT_DIR] [-s SINGLE_SPELL] [-c CONFIG]
```

**INPUT_FILE** : _Required_ <br> A file with spell information. This can be either a CSV or a YAML
file. See the examples included in this repository (spells.csv and spells.yaml).
Example: `my_homebrew_spells.csv`

**OUTPUT_DIR** : _Optional_ <br> The folder to which spell card images are output, relative to the 
working directory (the location of the .exe). Cards are placed in a folder
called `output` by default if this option is not specified. Example: `-o "Spell 
Card Output"`. To output directly into the working directory, use `-o .`

**SINGLE_SPELL** : _Optional_ <br> A single spell to generate a card for. Example: `-s "Magic 
Missile"`. If this is not specified, cards are generated for every spell that is
included in the INPUT_FILE.

**CONFIG** : _Optional_ <br> A configuration file used to modify how spell cards are generated.
Example: `-c my_config.json`.


## Configuration

Spell Card Maker supports the use of a configuration file to change many aspects
of how spell cards are generated. For example, you can use a config file to 
modify spell school icons and colors, fonts used on the cards, or which classes
to include in the class list on the right side of the card.

To generate a default configuration file, use the following command:

```commandline
./SpellCardMaker make_config
```

You can then update the file as desired, and specify the config file by using
the `-c` option when running the [Generation](#advanced-usage) command.

Images and fonts in the configuration file are often defined using a relative
filepath. These files are bundled with the application by default, but you can
provide the files yourself by placing them in the working directory (alongside
SpellCardMaker.exe). The Spell Card Maker utility will always prefer to use
files that exist in the working directory before using the default bundled
files. For example, the icon used at the top of abjuration spell cards is
defined in the default config file as `resources/images/abjuration/icon.png`, as
you can see here:

```json
"school": {
    "abjuration": {
        "bg_color": "#6DC3D3",
        "fg_color": "#000000",
        "img": "resources/images/abjuration/icon.png"
    },
```

You can override this image by creating a `resources` folder in the working
directory along with the same sub-folders and icon filname
(`resources/images/abjuration/icon.png`), or you can create your own config file
to specify a new location for this image.


### Adding classes and schools

To add an additional class to the spell cards — or otherwise customize the class
list — you can edit the array of classes in the `general.classes` configuration
section.

For example, if you add "Artificer" to that list, the "Artificer" class appears
on the sidebar of all spell cards that are generated, and is highlighted for any
spell that lists the "Artificer" in its "classes" list in the spell data input
file.

<img align="right" src="/docs/images/Adding%20the%20Artificer.png" width="442">

```json
"general": {
    "classes": [
        "Artificer",
        "Bard",
        "Cleric",
        "Druid",
        "Paladin",
        "Ranger",
        "Sorcerer",
        "Warlock",
        "Wizard"
    ],
```

Similarly, it is fairly straightforward to add a new school of magic to the pool
for spell card generation. Simply add your new school to the `school`
configuration section with similar details as the existing schools in the
configuration file. Any spells with that school listed in the spell data input
file will be stylized appropriately.

```json
    "school": {
        "metamagic": {
            "bg_color": "#D47B25",
            "fg_color": "#000000",
            "img": "resources/images/metamagic/icon.png"
        },
```


## Building the app

[Pyinstaller][11] is used to build the app into a standalone executable for
release. If you would like to build the application for a non-Windows OS (or
make other customizations), it should be fairly straightforward to do so. The
included spec file (`SpellCardMaker.spec`) contains the required settings and
configuration for building the app. It should be as easy as installing
Pyinstaller and then running the following command from the project directory:

```commandline
pyinstaller SpellCardMaker.spec
```


[1]: https://www.reddit.com/r/DnD/comments/6fga8k/
[2]: /docs/images/Magic%20Missile.png
[3]: /docs/images/Misty%20Step.png
[4]: /docs/images/Locate%20Creature.png
[5]: /docs/images/Water%20Walk.png
[6]: /docs/images/Resurrection.png
[7]: https://docs.wand-py.org/en/0.6.13/
[8]: https://docs.wand-py.org/en/latest/guide/install.html#install-imagemagick-windows
[9]: https://docs.wand-py.org/en/latest/guide/install.html#install-imagemagick-debian
[10]: https://github.com/egocarib/Spell-Card-Maker/releases
[11]: https://pyinstaller.org/en/v6.11.1/
