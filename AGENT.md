# Introduction to AGENT.md
Before running a problem task, Ideator looks for an AGENT.md instruction file, in its Ideator folder. If found it adapts to the instructions, if they are "legal".

## 10 ways AGENT.md adds value
Here are 10 ways an AGENT.md, in the kit folder, could add value:

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

## Current active AGENT.md
You find it in the kit folder: [AGENT.md](kit/AGENT.md)

## Order of priority
There are 3 levels, when handling ambiguity in setting the value of a [knob](KNOBS.md), ex. with the `ideas` knob.

### Priority
#### High
- When the knob value is supplied as part of the problem statement, in a chat, before a problem solving run.

#### Middle
- When instructed by an AGENT.md file, located in the Ideator folder and updated via the [kit feature](KIT.md).

#### Low
- When a knob default value is used implicitly.

### Priority example
A user or bot sends a  problem statement, with the `ideas` knob set to 6, wanting 6 ideas per challenge.

An AGENT.md instruction file is asking for 8 ideas, but is rejected because of the higher priority of the `ideas` knop being sent with the problem statement, in a chat.

### Privacy-, security- and illegal actions
There are actions that an AGENT.md will not be allowed do or request.

An AGENT.md cannot:
- Ask for a Google Sheet report to be shared automatically, for privacy reasons. The user (owner of the sheet document) has to share the reports manually. 
- Override the knob values sent with the problem statement.
