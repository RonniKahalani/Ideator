# Kit

When sharing a bot template, custom scripts are not included.

The kit idea is a way to update local bot features and data, from a remote GitHub folder.

Enables maintaining behavior and resources, ex. scripts, data, prompts, skills, rules and alike.

## Example use case

Ideator needs script `sheet_builder.py` to build the Google Sheet. 

When the sheet design changes, this script has to change too and be made available for the bot to download, before its next problem task.

This kit featue can also be used to make new data and instructions available for the bot via the automatic download feature.

## How it works
When giving a problem task, the bot checks for updates from a kit repo, defined by `kit` [knob](KNOBS.md).

- Downloads new and updated files locally, on the bot cloud machine.
- If local- and repo file size differs, do download.

## Changing the kit repo
The deafult `kit` value is https://github.com/RonniKahalani/Ideator/tree/main/kit

You can set your own kit repo url via the `kit` [knob](KNOBS.md).
