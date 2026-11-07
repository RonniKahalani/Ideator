# Knobs (adjustable parameters)

All knobs are optional. The problem statement is the only required input. Knobs apply to that run only.

| Knob | Default | What it controls |
| :---- | :---- | :---- |
| **ideas** | 5 | Number of ideas generated per picked challenge. |
| **pretotypes** | 4 | Total number of pretotype tests designed, split across the picked concepts. |
| **sources** | 5 | Number of distinct research sources found and cited. |
| **country** | United States | The target launch country for the product or service. It shapes the research sources, the cultural fit of the ideas, and the language of the pretotype materials. Ideator infers it from the problem or research if you do not set it. |
| **language** | English | The language of the report and all output prose. Quotes from sources stay in their original language with a translation. |
| **format** | both | The output file type: `markdown` (a .md file), `page` (one self-contained page/HTML file with the same content and order) or `both` a markdown and page. |
| **mode** | auto | The Generation type: auto or ask. |

## Using knobs
Append your preferred knob values to the problem statement message.
Ending the message with the preferred knobs:
-  **ideas**: 3
- **sources**: 3
- **country**: Denmark
- **language**: English
- **format**: page
- **mode**: ask