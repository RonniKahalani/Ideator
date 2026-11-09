# Ideator

![](img/grok-ideator-overview.jpg)
By [Learning Is Living](http://learningisliving.dk), Denmark | [X](https://x.com/RonniKahalani) | [LinkedIn](https://www.linkedin.com/in/kahalani)

## What Ideator is
An AI-Agent (Grok Bot) acting like an automated hybrid between a creative director and a high-performance product development team, who eats complex problems for breakfast, researches the problem domain, creates cheap testable ideas, drops an ideation report and visual board, ready and eager to facilitate test plans, well before lunch.

### A problem solving task runs in one of two modes
- `ask` -  User is asked for decisions and selections in each phase.
- `auto` - No interruptions, it does all the decisionmaking by itself.

### The problem solving proccess explained visually
These [UML](https://www.omg.org/uml) diagrams explains exactly how it works
- [State Machine](STATEMACHINE.md)
- [Sequence](SEQUENCE.md)

### When problem solving tasks are completed
A final ideation report is created, consisting of:
- [Visual Board](img/board.png) | [Markdown](samples/community-library-visitors.md) | [Web page](https://htmlpreview.github.io/?https://github.com/RonniKahalani/Ideator/blob/main/samples/community-library-visitors.html)

Want to read on? (recommended) or [get your own Ideator bot](#get-your-own-ideator-bot), right now?

## What Ideator does
- Takes a problem statement, research related challenges and generates testable ideas.
- Cuts traditional research- and test time (costs), from weeks to minutes.

### Follows well-known design processes and principles
- [Design Thinking](https://grokipedia.com/page/Design_thinking)
    - Helps tackling complex problems by prioritizing empathy for end-users, collaborative ideation, rapid prototyping, and continuous testing to generate innovative solutions.
- [Double Diamond](https://docs.google.com/presentation/d/1YpWFWuR4q4RbrE0vdfk1FYzsovVbZlOvFg2C3JraDE0/edit?usp=sharing)
    - A visual framework representing the design and innovation process, with its 4 phases (discover, define, develop, deliver).
- [Google Design Sprint](https://grokipedia.com/page/Design_sprint)
    - A five-day process for answering critical business questions through design, prototyping, and testing ideas with customers.
- [Pretotyping](PRETOTYPE.md)
    - Small fake-it tests to prove whether people really want your idea, before anyone starts building an expensive prototype.
- [The Startup Way](https://www.thestartupway.com)
    - Build - Measure - Learn, YODA, MVP testing, pivot or persevere.

### Research problems and related challenges
* Research the web for real evidence about your problem.
* Explores complaints, reviews, forum threads, articles and how competitors handle it.  
* Turns that evidence into challenges, each tied to a research source.
* Anything it can’t source is labeled a hypothesis.
* It never invents sources, quotes or numbers.  
* Rates and ranks the challenges.
* You can limit the number of research sources, via the **sources** [knob](KNOBS.md).

### Generate and conceptualize ideas
* Generates ideas for selected challenges, then scores and ranks the ideas.  
* Mixes the best ideas into concepts.
* You can limit the number of ideas per challenge, via the **ideas** [knob](KNOBS.md).

### Pretotype user tests
* Writes pretotype tests with a hypothesis, a success number, a deadline, and go or no-go rules.  
* Drafts the materials a person needs to run each recommended first test, such as fake-door copy, email or SMS scripts and survey questions.
* It only prepares them; it never sends, publishes or posts anything.
* You can limit the number of pretotype tests across concepts, via the **pretotypes** [knob](KNOBS.md).

### Generate reports
When a problem task completes a report is made with 3 possible deliveries
* [Visual Board](img/board.png) (.png).
* [Markdown](samples/community-library-visitors.md) (.md - default) or [Web page](https://htmlpreview.github.io/?https://github.com/RonniKahalani/Ideator/blob/main/samples/community-library-visitors.html) (.html) report.
* If the **format** [knob](KNOBS.md) equals **both**, then both report formats will be created.

## Workload and processing time

The workload, data and time needed for the realtime web research- and visual board image tasks consumes credits and takes time.

An average problem statement report can take 10-20 minutes, or more, depending on the workload set in the [knob settings](KNOBS.md).

## Get your own Ideator bot
- Are Grok Bots new to you? [Get them Grok Bots running](GROKBOT.md).

- Already using Grok Bots? [Get Ideator Grok Bot](https://forms.gle/EEa9tBV2Xqge5KNr9).

## Further details
- [Grok Bots](GROKBOT.md)
- [Business Case](BUSINESSCASE.md)
- [Phases](PHASES.md)
- [Knobs / Parameters](KNOBS.md)
- [Scoring & Rating](SCORING.md)
- [State Machine Diagram](STATEMACHINE.md)
- [Sequence Diagram](SEQUENCE.md)
- [Dependencies](DEPENDENCIES.md)
- [How to use it](HOWTO.md)
- [Human vs. AI](COMPARE.md)
- [Pretotyping](PRETOTYPE.md)
- [Marketplace](MARKET.md)
- [Future](FUTURE.md)

## Closing line

In short, you get 
- Research-backed findings with source links.
- Scored and ranked challenges and ideas.
- Concepts with testable pretotype plans and materials.
- Visual board and report of the whole run.

Later, after you report back on the pretotype test results, Ideator can
- Add a go, no-go or iterate decision to the same file.
- Set up a check-in once you tell it a start date.

## Contact
- [Discussion](https://github.com/RonniKahalani/Ideator/discussions).
- Discord Invite: [Grok Bot Ideation](https://discord.gg/6CNgtzuPPH).
- [Learning Is Living](https://learningisliving.dk/about/contact).