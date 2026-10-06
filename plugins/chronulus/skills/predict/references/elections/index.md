# Election markets

Winner of a race, party control, vote-share and margin thresholds, turnout, primaries
and referendums. Start with the generic templates in `SKILL.md`; this file adds what is
specific to elections.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Two-candidate race winner | binary | proposition/negation (or matchup with candidates as SUBJECT/OBJECT) |
| Multi-candidate race, primary, or any "exactly one wins" field | exclusive-winner, K outcomes | proposition/negation, one Beta per candidate → `render_exclusive_dirichlet_scorecard` |
| Party control (chamber control, seat count buckets) | ordinal buckets (or binary on a threshold) | proposition/negation → `render_ordinal_dirichlet_scorecard` |
| Vote share, margin, turnout above a threshold | binary on a threshold | proposition/negation with the threshold in the text |
| Runoff happens / no candidate above 50% | binary | proposition/negation |
| Referendum / ballot measure passes | binary | proposition/negation |

Candidates in an election are not a "SUBJECT vs OBJECT" matchup in the sense of
`SKILL.md` Step 2, because there are often more than two. Default to
proposition/negation and dual-frame by swapping the two statements; there are no two
evidence blocks to flip. If a race does reduce to two candidates with their own evidence
blocks, flip the evidence as in a matchup.

## Session template

```
name: "<Jurisdiction/Level> <Office> Winner Predictor"   # e.g. "US Senate General Election Winner Predictor"
situation: >
    I am a professional forecaster who evaluates elections. I want independent,
    well-calibrated probabilities to compare against prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), about the stated race, using the
    evidence provided and the resolution rules stated.
```

One session per (election type, level), such as "US Senate general", "US presidential
primary", "UK parliamentary constituency". Reuse it across races of that type.

## Input fields

Event fields: `election_name_and_date`, `office_and_jurisdiction`, `electoral_system`
(plurality, ranked-choice, runoff, proportional, electoral college), `candidates_and_parties`,
`resolution_criteria` (source and timing, see Pitfalls), `proposition`, `negation`.

Evidence fields:
- `polling_summary` — recent polls with dates, sample, population (adults, registered,
  likely voters) and pollster quality; an average or trend is better than one poll.
  Say how many polls there are and how recent.
- `fundamentals` — incumbency, partisan lean of the jurisdiction, past results,
  approval rating of the incumbent or the president, economic conditions, candidate
  quality and scandals.
- `campaign_state` — fundraising and ad spending, endorsements, turnout operations,
  debate performance, ballot-access issues, withdrawals.
- `rules_and_logistics` — voter ID, mail voting, runoff thresholds, recount thresholds,
  certification timeline.
- `expert_ratings` — nonpartisan race ratings (e.g. Cook, Sabato, Inside Elections)
  and model forecasts that are not market prices. Label them as external opinions.
- `historical_context` — how similar races resolved, polling error in past cycles.

## Evidence checklist

1. A polling average with date and quality notes, and the direction of the trend.
2. Fundamentals that predate the polls: partisan lean, incumbency, midterm penalty.
3. Primary-election specifics: endorsement strength, field size, ranked-choice rules,
   turnout skew, and polling scarcity.
4. Rules that define the event, such as recount law, runoffs, and certification dates.
5. For international elections: electoral system quirks, coalition arithmetic, and
   local poll reliability.

## Pitfalls

- **Resolution source and timing.** Markets resolve on an official source (certified
  results, an AP call, a named authority) and a deadline. A race that is called late or
  is recounted can resolve differently from what the "winner" is on election night.
  Put the exact source and the timing into the proposition.
- **Correlated polling error.** A polling miss tends to hit many races in the same
  direction. Do not treat 20 Senate races as 20 independent draws; reconcile
  chamber-control markets from the race-level numbers with that in mind and run a separate
  chamber-level session for control markets.
- **Polls vs fundamentals.** Early in a cycle, fundamentals deserve more weight; closer
  to election day, polls dominate. State the date.
- **Do not input market prices or model outputs that are built from them.** Other
  forecasts are fine as labeled external opinions; market-derived probabilities are not.
- **Thin polling.** Primaries, down-ballot races and small countries have few or low-quality
  polls. Say so; wide Betas are correct here.
- **Candidate lists change.** Withdrawals and ballot-access fights can change the
  exclusive-winner set after you built it; rebuild the candidate list before each run.

## Subcategories (guides to be added)

US president (general and primary), US Senate, US House and chamber control, governors,
non-US national elections, referendums and ballot measures. Until a subcategory file
exists, use this file plus `SKILL.md`.
