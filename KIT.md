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

- Downloads new and updated files locally, on the bot cloud node.
- If local- and repo file size differs, download it.
- When a new AGENT.md file is downloaded, Ideator adds the instructions to its work.

## AGENT.md sample
Here are 10 ways an AGENT.md in the kit folder could add value:

### Studio house style
- Set the tone, wording and language rules for every report, like plain English, no jargon, or a client-friendly voice.

### Domain focus
- Tell Ideator to lean toward a sector, such as public spaces, healthcare or edtech, so research and ideas start from the right context.

### Trusted sources
- List preferred or banned source types, like English municipal data, academic papers first, or no blogs, so the sourced findings fit your standards.

### Custom scoring
- Add or reweight scoring criteria, such as sustainability, cost to pilot or accessibility, so the idea ranking matches how your studio actually decides.

### Hard constraints
- State limits every idea must respect, like "no new hardware", a budget ceiling, or GDPR rules, so you get fewer ideas that are dead on arrival.

### Pretotype preferences
- Steer which cheap tests it suggests, such as paper prototypes and landing pages but never paid ads, matched to what the studio can run.

### Client or project context
- Drop in background like who the stakeholders are, what was tried before, or the client's brand values, so the define phase starts informed.

### Extra report content
- Ask for extra sections or notes in the sheet, like a risks list, a next-steps column or a workshop agenda, without changing the builder.

### One change for every run
- Because it sits in the kit folder that's fetched before each run, editing one file updates every future report, and the git history shows when and why the rules changed.

### Per-team setups
- Different kit folder URLs can carry different AGENT.md files, so one Ideator can serve several clients or teams, each with its own rules, just by changing the kit knob.

### Current AGENT.md in kit folder, on main.
- [AGENT.md](kit/AGENT.md)

## Changing the kit repo
The deafult `kit` value is https://github.com/RonniKahalani/Ideator/tree/main/kit

You can set your own kit repo url via the `kit` [knob](KNOBS.md).
