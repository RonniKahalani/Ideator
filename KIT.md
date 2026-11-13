# Kit
This feature enables Ideator to download files, from a remote GitHub folder, to its cloud node.

Used to update resources, like scripts, data, prompts, skills, rules and alike.

## Example use case
Ideator depends on the script [sheet_builder.py](kit/sheet_builder.py).

- Ideator needs this script locally on its cloud node, to build Google Sheet reports. 
- The [sheet_builder.py](kit/sheet_builder.py) gets downloaded, at the very first problem related chat message. 

When the sheet design changes
- The script has to change too and be made available for  download. Otherwise the report will be created by the older version of [sheet_builder.py](kit/sheet_builder.py).

## How it works
When giving a problem task, the bot checks for updates from a kit repo, defined by `kit` [knob](KNOBS.md).

- Downloads new and updated files locally, on the bot cloud machine.
- If local- and repo file size differs, download it.

## Changing the kit repo
The deafult `kit` value is https://github.com/RonniKahalani/Ideator/tree/main/kit

You can set your own kit repo url via the `kit` [knob](KNOBS.md).
