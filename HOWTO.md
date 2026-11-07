# How to use Ideator

* Open a chat with Ideator and give it a problem statement. A good one says who has the problem, what goes wrong, and what you have seen that shows it.
* Append preferred [knobs](KNOBS.md) to the message and send it.
* The ideator states the problem and knob values, before it starts researching.
* In ask mode, you will be asked questions, regarding options and decisionmaking, at each phase.  
* In auto mode, you just wait for the final result (no interruptions) and Ideator will take all the necessary decisions on its own.  
* At the end you get the board PNG and the report file (Markdown or page) as attachments, with no other text in the chat.  
* Run the recommended first pretotypes yourself, then tell Ideator the start date. It sets a check-in for the day after each deadline, compares the results with the success number, and recommends go, no-go or iterate.

## Example problem statement

> Small community libraries see fewer and fewer visitors because young families think of them as quiet, old-fashioned places and do not know about the children's events, free tools and digital services they offer. (Knobs: **mode**:ask, **sources**:1,**ideas**:5, **format**:both)

## What to expect as a result

At the end of a run you typically get
- A board image.
- At least one report file format, Markdown (default) or a web page (HTML), if you set **format** knob to **page**.

Ideator's final chat message is one or two report file attachments and the board image (PNG). Everything else is in the report and documents every stage it has gone through. The used knobs values are listed inside the report, not in the chat.

The report is laid out in this order, both in the Markdown (.md) and in web page (HTML) format:

* Title  
* Key results.  
* Problem statement.  
* List of knob values used for the current report.  
* **Discover**
  * A research summary with source links, then the challenges behind your problem as sticky notes.  
  * Each challenge cites the source or finding it comes from, or is marked "hypothesis, no evidence found".  
* **Define**  
  * A table rating each challenge for possible and exciting, ranked by score, with the top 5 picked.  
* **Develop**  
  * The generated ideas, grouped by picked challenges.  
  * With the default 5 ideas per challenge.  
* **Deliver**  
  * A short scoring weights block.  
  * A table of every idea with its cheap, simple, base, evidence, uniqueness and weighted scores.  
  * Top 5 picks with one line each on why they outrank the next idea.  
  * Listing the concepts made by mixing the best ideas.  
* **Pretotypes**  
  * The pretotype tests. Each has a hypothesis, a measurable success number, a deadline, and go and no-go rules.  
  * One test per concept is marked as the recommended first test, and it comes with ready-to-use materials such as page copy, email or SMS scripts and survey questions, written in the language the country and language knobs call for.  
  * These are drafts for a person to run; nothing is sent.

## Sample reports

* [Visual Board](img/board.png) (image)
* [Markdown Report](samples/community-library-visitors.md) (simple text)  
* [Web Page Report](https://htmlpreview.github.io/?https://github.com/RonniKahalani/Ideator/blob/main/samples/community-library-visitors.html) (styled web page)