# Kit
This feature enables Ideator to download updates, from a remote GitHub folder, to a local folder on the bot cloud node.

Used update resources, locally on the bot, with updated versions of custom scripts, data, prompts, skills, rules and alike.

## Example use case
Ideator depends on the script [sheet_builder.py](kit/sheet_builder.py) script.

- It needs it locally on the bot cloud node, to build  Google Sheet reports. 
- The script [sheet_builder.py](kit/sheet_builder.py) gets downloaded, the very first a problem related chat message is sent. 

If the sheet design changes
- This script has to change too and be made available for the bot to download. Otherwise the report will be created by the older version of [sheet_builder.py](kit/sheet_builder.py).

## How it works
When giving a problem task, the bot checks for updates from a kit repo, defined by `kit` [knob](KNOBS.md).

- Downloads new and updated files locally, on the bot cloud machine.
- If local- and repo file size differs, download it.

## Changing the kit repo
The deafult `kit` value is https://github.com/RonniKahalani/Ideator/tree/main/kit

You can set your own kit repo url via the `kit` [knob](KNOBS.md).
