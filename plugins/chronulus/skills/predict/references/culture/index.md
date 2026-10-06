# Culture and entertainment markets

Awards (Oscars, Grammys, Emmys, Golden Globes), box office, charts and streaming
rankings, TV and reality-show outcomes, review scores, social-media milestones, and
celebrity or pop-culture events. Start with the generic templates in `SKILL.md`; this
file adds what is specific to these markets.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Award category winner | exclusive-winner over nominees | proposition/negation per nominee → `render_exclusive_dirichlet_scorecard` |
| Box office, chart position, rating, follower count above a threshold | binary on a threshold | proposition/negation |
| Chart rank buckets | ordinal | proposition/negation per bucket |
| Competition show winner, "who goes home" | exclusive-winner | proposition/negation per contestant |
| Event occurs by date (release, announcement, appearance) | binary | proposition/negation |

## Session template

```
name: "<Domain> Predictor"       # e.g. "Academy Awards Category Winner Predictor"
situation: >
    I am a professional forecaster who evaluates entertainment and culture outcomes. I
    want independent, well-calibrated probabilities to compare against prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), using the evidence provided and the
    resolution rules stated.
```

Use one session per (award body or metric type): "Oscars winner", "domestic opening
weekend box office", "Billboard Hot 100 number one", "Rotten Tomatoes score", and so on.

## Input fields

Event fields: `event_name_and_date`, `resolution_criteria` (which source, which metric,
which timestamp), `proposition`, `negation`.

Evidence fields vary by domain; the common set is:
- `candidates_and_context` — nominees or contenders with the relevant facts.
- `precursor_results` — earlier outcomes that predict this one (guild awards and
  critics' prizes before the Oscars; tracking numbers and presales before a box office
  weekend; first-week streaming data before a chart).
- `voting_or_scoring_mechanics` — who votes, how (preferential ballot for Best Picture,
  plurality elsewhere), eligibility, and how a metric is computed.
- `momentum_and_narrative` — campaigns, controversies, reviews, social signals, with dates.
- `comparable_history` — how similar contenders or releases did.

## Evidence checklist

1. The exact metric and its source (which box office tracker, which chart week, which
   review aggregator and whether the score is fresh or locked).
2. Precursor outcomes with sample sizes and track record of how well they have predicted.
3. Voting body composition and the ballot system: a preferential ballot favors broadly
   liked candidates over passionate-minority ones.
4. Recent information release: embargoes, screenings, leaks, and schedule changes.
5. For thresholds, the trajectory of the metric (daily, weekend-to-weekend), not just its
   current level.

## Pitfalls

- **Resolution timing and source.** Box office numbers are estimates until finalized;
  chart weeks run on a schedule; review scores move after release. Name the source and
  the time of measurement in the proposition.
- **Winners are not always favorites.** Upsets and split outcomes are common in
  small voting bodies. Keep the exclusive-winner set complete and let the reconciliation
  tool normalize it.
- **Narrative bias.** Press coverage overstates momentum. Weight precursor data and
  voting mechanics above buzz.
- **Leaks and spoilers.** Pre-announced results may exist; if the answer is already
  public, the market is not a forecast. Check before spending experts.
- **Quantitative thresholds** (box office, streams) should be anchored to a numeric
  projection, then adjusted. Provide the projection and its basis rather than asking the
  experts to invent the base level.
- **Do not include market prices** in the inputs.

## Subcategories (guides to be added)

Film awards, music awards, TV awards, box office, music charts and streaming, reality and
competition TV, social media and creators, celebrity events. Until a subcategory file
exists, use this file plus `SKILL.md`.
