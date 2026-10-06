# Politics and policy markets

Non-election political events: legislation, executive actions, nominations and
confirmations, court decisions, approval-rating thresholds, government shutdowns,
tariffs and trade, diplomacy and geopolitical events. Start with the generic templates
in `SKILL.md`; this file adds what is specific to these markets.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Will X happen by date D (bill passes, order signed, person confirmed) | binary | proposition/negation |
| When will X happen (date buckets) | ordinal or exclusive over buckets | proposition/negation, one Beta per bucket |
| Approval or poll number above a threshold on a date | binary on a threshold | proposition/negation |
| Court ruling outcome | binary or exclusive (outcomes) | proposition/negation |
| Who will hold a role (nominee, leader) | exclusive-winner | proposition/negation per candidate |

There is almost never a SUBJECT/OBJECT pair. Use proposition/negation and dual-frame by
swapping them.

## Session template

```
name: "<Topic> Policy Event Predictor"    # e.g. "US Federal Legislation Passage Predictor"
situation: >
    I am a professional forecaster who evaluates political and policy events. I want
    independent, well-calibrated probabilities to compare against prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), using the evidence provided and the
    resolution rules stated, as of the date supplied.
```

One session per event type (federal legislation, executive orders, Supreme Court cases,
nominations, a particular conflict or negotiation). Reuse across events of that type.

## Input fields

Event fields: `event_description`, `resolution_criteria` (the exact trigger and the
authority that decides it), `deadline`, `as_of_date`, `proposition`, `negation`.

Evidence fields:
- `process_and_calendar` — the procedural path and where the event stands (committee,
  floor votes, conference, signing; filing and briefing dates for courts; comment periods
  for rules), and the remaining scheduled dates and deadlines.
- `actor_positions` — stated positions of the decision makers, whip counts or vote counts,
  public statements, and dissent within the coalition.
- `precedent_and_base_rates` — how often comparable events happened, how often deadlines
  slipped, and how this administration or body has behaved on similar issues.
- `external_pressures` — public opinion, markets, allies and adversaries, litigation,
  and what would force or block action.
- `recent_developments` — the last two weeks of news with dates.

## Evidence checklist

1. The exact resolution trigger: "announces" vs "signs" vs "takes effect" vs "is enforced".
2. The remaining timeline and what has to happen, in order, before the deadline.
3. Counts: votes, justices, delegates, signatures, with names where it matters.
4. Base rates: legislation and deadlines slip far more often than headlines suggest.
5. Statements vs actions: weight actions and procedure above rhetoric.

## Pitfalls

- **Status quo and deadline bias.** Most "by date X" markets resolve No because processes
  slip. The experts need the process and base rate, not only the news. For "when" markets,
  give the bucket propositions together and reconcile as an ordinal ladder.
- **Resolution wording.** Announced, signed, effective, and implemented differ. Quote
  the market's wording in the proposition.
- **Fast news.** Re-run when a material development lands; probabilities age quickly.
  State the `as_of_date` in the input.
- **Legal outcomes.** Court decisions turn on specific questions presented, panel makeup
  and oral-argument signals; give those rather than general ideology labels.
- **Geopolitics.** Distinguish stated intentions from verifiable events (a ceasefire
  announced vs holding), and name the source that will confirm it. Evidence is
  adversarial and noisy; prefer primary or multiple independent sources.
- **Do not include market prices** in the inputs.

## Subcategories (guides to be added)

US legislation, executive actions and tariffs, Supreme Court and federal courts,
nominations and cabinet changes, approval ratings, international conflicts and
diplomacy, non-US politics. Until a subcategory file exists, use this file plus `SKILL.md`.
