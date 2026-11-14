# Report
A problem task ends with a report
- [Google Sheet Report Sample](https://docs.google.com/spreadsheets/d/1HZpJBYYJQtU06iVmak6Kp8x2TslsaGx1/edit?usp=drive_link&ouid=106568148712124039315&rtpof=true&sd=true).
- Use `template` [knob](KNOBS.md) to select another template sheet.

## Why Google Sheet?
Initially, the report generator, made a visual board (png), a markdown- and html report. It was inefficient and sucked data integration-wise.

It it now a single spreadsheet file (xlsx):
- Easy, fast and known data integration-, manipulation- and visualization formats.
- Everyone knows how to use a spreadsheet.
- Google Drive is one of the most used plaforms for sharing documents.
here's why Ideator writes its report as a Google Sheet:

- It fits the content of a Double Diamond run is mostly tables: sources, sub-problems, scored ideas, concepts, pretotypes and the run knobs. rows and columns hold all of that naturally.
- Scores stay live, concept averages are real formulas, so if you change a score, the ranking updates by itself.
- You can sort and filter, freeze panes and filters let you rank ideas, filter by concept, or hide columns without rebuilding anything.
- One tab per phase, each step gets its own tab, plus a Tab guide, so a client or a colleague can jump straight to the part they care about.
- Every report looks the same, each run copies the template, so reports match across projects and are easy to compare.
- It's private but easy to share. It lands owner-only in your own Drive, and sharing is just a normal Google share whenever you decide.
- People can work on it together, comments, suggestions and editing in the same sheet suit a workshop or client review.
- It's easy to check if the Drive and Sheets connections can read the sheet back, so every run gets verified against what was built.
- No extra software, it opens in a browser, exports to Excel or CSV, and works on any device.
- It's easy to reuse. You can copy tabs into proposals and decks, or chart them, without converting anything first.

## Tabs in the report

### Introduction
- A company branded tab defined in the template used.

### Tab guide
- Information about the different tabs in the sheet.

### Run knobs
- Lists the values of the knobs/parameters for this report.

### Problem
- States the problem the report covers and some run status.

### Key results
- A quick overview of the key ideas.

### Sources
- Lists the research sources used in this report.

### Sticky notes
- Lists post-it info for the different challenges behind the problem.

### Challenges
- Lists all the challenges with a score and visualizes the selected challenges to generate ideas for.

### Define picks
- Lists challenge selections and reasons.

### Scoring weights
-Lists all the scoring weights.

### Ideas
- List all the ideas generated.

### Concepts
- Lists ideas combined into concepts.

### Pretotype test
- Lists all the pretotyping tests.

### Materials
- Lists materials made for the pretotype tests.

### First tests
- Lists the first tests to run.

### Board content
- Lists data to generate a visual board of the ideation process.