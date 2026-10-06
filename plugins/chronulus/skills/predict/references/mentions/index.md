# Mentions markets

"Will X say Y?" markets: words or phrases spoken in a speech, press conference,
interview, earnings call, debate, broadcast or show; terms that appear in an
announcement or a document. Start with the generic templates in `SKILL.md`; this file
adds what is specific to mentions.

## Where Chronulus fits

A mention market is a frequency problem with a strict rule. The strongest input is a
**count you compute yourself**: how often the speaker said the phrase in comparable past
events. Chronulus has no transcript database, so research the transcripts, count, and
pass the counts as evidence. The BinaryPredictor then adjusts for the specifics of this
event: the agenda, the setting, the news cycle and the format.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Will the speaker say a given word or phrase during the event | binary | proposition/negation |
| Will the word appear at least N times | binary on a threshold | proposition/negation |
| A set of words in the same event (a "mention bingo" card) | K independent binaries, not mutually exclusive | one dual-framed binary per word; do **not** reconcile into a Dirichlet |
| Which word is said first | exclusive-winner | proposition/negation per word |

Note that several words in one event are **not** an exclusive set; each is its own
yes/no market, so use the binary tools, not the Dirichlet reconciliation.

## Session template

```
name: "<Speaker or Event Type> Mention Predictor"   # e.g. "Earnings Call Mention Predictor"
situation: >
    I am a professional forecaster who evaluates whether specific words or phrases are
    spoken at scheduled events. I want independent, well-calibrated probabilities to
    compare against prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), about the stated event, using the
    evidence provided and the exact resolution rules stated.
```

One session per event type (earnings calls, presidential remarks, press briefings, sports
broadcasts, award shows). Reuse across events and words.

## Input fields

Event fields: `event_and_speaker`, `scheduled_datetime_and_length`, `format` (prepared
remarks, Q&A, interview, panel), `resolution_criteria` (exact word and variants, who
counts as a speaker, source of truth), `proposition`, `negation`.

Evidence fields:
- `base_rate_counts` — in how many of the last N comparable events the phrase appeared,
  with the dates and the counts. State N and how the events were selected.
- `topic_and_agenda` — what the event is expected to cover; news cycle drivers that make
  the topic likely or unlikely.
- `speaker_patterns` — habits (repeated catchphrases, topics they avoid), and how they
  vary between prepared remarks and Q&A.
- `format_and_length` — scheduled length, whether there is Q&A, number of speakers,
  and whether the event could run short or be canceled.
- `recent_context` — what the speaker has said in recent days about the topic.

## Evidence checklist

1. Transcripts of the last 5-20 comparable events and a count for the exact phrase.
2. The wording rule: exact match, plural and tense variants, compound words, quotes.
3. The event's agenda and likelihood of Q&A.
4. The source that settles the market: a live broadcast, an official transcript, a
   captioning service. They differ.
5. Probability the event happens as scheduled at all.

## Pitfalls

- **Resolution wording is everything.** Does "tariff" count when the speaker says
  "tariffs"? Do quotes of someone else count? Is a transcript or the live audio the
  authority? Put the rule in the proposition text.
- **Base rates are only comparable if events are comparable.** Earnings calls differ by
  quarter and company situation; a different event type has different counts.
- **Event happens or not.** Cancellations, delays and early endings make No more likely.
  Include this explicitly.
- **Prepared vs unscripted.** Words in prepared remarks are close to deterministic once
  the text is public; unscripted portions follow base rates. If a prepared text or
  slides are available before the event, use them.
- **Small N.** With few comparable events, the Beta should be wide. Say how thin the
  count is.
- **Many words at once.** Use 2 experts per framing by default. Each word already has two
  framings, so 2 framings × 2 experts = 4 experts per word is plenty, and a large set of
  words is slow with more. A 32-expert batch fits 8 words; split a bigger set into
  several batches.
- **Do not include market prices** in the inputs.

## Subcategories (guides to be added)

Earnings calls, presidential and political remarks, press conferences and briefings,
sports broadcasts, award shows and TV events, interviews and podcasts. Until a
subcategory file exists, use this file plus `SKILL.md`.
