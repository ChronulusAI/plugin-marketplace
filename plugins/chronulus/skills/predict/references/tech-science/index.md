# Tech and science markets

Product and model launches, AI benchmarks and leaderboard rankings, company
announcements, space launches and missions, regulatory approvals (FDA, FCC),
clinical-trial results, scientific milestones, and technology adoption metrics. Start
with the generic templates in `SKILL.md`; this file adds what is specific to tech and
science.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Will X launch/release/be approved by date D | binary | proposition/negation |
| When will X happen (date buckets) | ordinal over buckets | proposition/negation per bucket |
| Which entity leads a ranking on a date (top model, top app, largest company) | exclusive-winner | proposition/negation per candidate |
| Score, rank or metric above a threshold | binary on a threshold | proposition/negation |
| Mission or test succeeds | binary | proposition/negation |

## Session template

```
name: "<Domain> Predictor"       # e.g. "AI Model Release Predictor", "FDA Approval Predictor"
situation: >
    I am a professional forecaster who evaluates technology and science events. I want
    independent, well-calibrated probabilities to compare against prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), using the evidence provided and the
    resolution rules stated, as of the date supplied.
```

One session per domain: AI releases, AI leaderboards, consumer hardware launches, space
launches, FDA decisions, clinical trials, and so on.

## Input fields

Event fields: `subject_and_event`, `resolution_criteria` (exact definition of "release",
"launch" or "approval"), `deadline`, `as_of_date`, `proposition`, `negation`.

Evidence fields:
- `official_schedule` — announced dates, regulatory calendars (decision dates for drug
  applications), launch manifests, event dates.
- `track_record` — how often this company, agency or program met past announced dates, how
  much slip is typical.
- `leading_indicators` — regulatory filings, certification databases, test sightings, job
  postings, supply-chain reports, leaks (labeled by reliability).
- `technical_readiness` — test results, pre-flight checks, trial data, benchmark scores,
  known open issues.
- `competitive_context` — competitors' releases, rankings, and the incentive to launch now.
- `external_constraints` — weather and range availability for launches, regulatory
  holds, supply limits, litigation.

## Evidence checklist

1. The exact event definition (announced vs available vs generally available; approved
   vs cleared; launched vs reached orbit; ranked first on which view of a leaderboard).
2. The calendar and what has to happen before the deadline.
3. The entity's record on hitting dates and its recent signals.
4. Readiness evidence: results, filings, tests.
5. For leaderboards: the exact leaderboard, its settings and snapshot time, and the scoring
   method and confidence intervals, since ties and small gaps are common.

## Pitfalls

- **Announced vs shipped.** Announcements, previews, limited access and general
  availability are different events. Quote the market's definition.
- **Optimism bias in schedules.** Launch dates and "coming soon" promises slip. Put the
  track record in the evidence, not only the latest statement.
- **Leaderboards.** Rankings move with new submissions and methodology changes; name
  the leaderboard, the category and the settings, and the time of measurement. With
  small score gaps use an exclusive-winner set so uncertainty is spread properly.
- **Regulatory decisions.** Decision-date calendars exist, but delays, extensions and
  complete-response outcomes occur; give the application's stage and any known issues,
  and look up base rates for the type of application and division.
- **Scientific claims.** Distinguish preprints from peer-reviewed results and
  announcements from replication; resolution usually depends on a named source.
- **Rumors.** Label by reliability and date; do not rely on a single leak.
- **Do not include market prices** in the inputs.

## Subcategories (guides to be added)

AI model releases and leaderboards, consumer technology launches, space launches and
missions, drug approvals and clinical trials, scientific milestones, and tech company
corporate events. Until a subcategory file exists, use this file plus `SKILL.md`.
