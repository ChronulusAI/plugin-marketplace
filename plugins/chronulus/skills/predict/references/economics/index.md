# Economics markets

Inflation (CPI, PCE), jobs (payrolls, unemployment), GDP, Fed and other central bank
decisions, recession calls, jobless claims, retail sales, housing, and similar
macroeconomic releases. Start with the generic templates in `SKILL.md`; this file adds
what is specific to economics.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Release above/below a level (CPI MoM above 0.3%, unemployment at least 4.2%) | binary on a threshold | proposition/negation, consensus in evidence |
| Release in buckets | ordinal | proposition/negation per bucket → `render_ordinal_dirichlet_scorecard` |
| Central bank decision (cut by size / hold / hike by size) | ordinal ladder | proposition/negation per outcome, outcomes in scale order |
| Recession declared / GDP negative for a quarter | binary | proposition/negation |
| Level on a date (mortgage rates, gas prices, claims) | binary or ordinal | proposition/negation |

The rate-decision ladder is the worked ordinal example in `SKILL.md` (cut > 25 bps, cut
25 bps, hold, hike 25 bps, hike > 25 bps). Keep the outcomes in order along the scale.

## Session template

```
name: "<Indicator or Decision> Predictor"   # e.g. "US CPI Release Predictor", "FOMC Rate Decision Predictor"
situation: >
    I am a professional forecaster who evaluates macroeconomic releases and central bank
    decisions. I want independent, well-calibrated probabilities to compare against
    prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), using the evidence provided and the
    resolution rules stated, as of the date supplied.
```

One session per indicator or decision type: CPI, payrolls, unemployment rate, GDP,
FOMC decision, ECB decision, and so on. Bucket markets on the same release can share the
session and agent.

## Input fields

Event fields: `release_name_and_date`, `series_definition` (headline or core,
seasonally adjusted or not, month-over-month or year-over-year, units, rounding),
`resolution_criteria` (first print or revised, source), `as_of_date`, `proposition`, `negation`.

Evidence fields:
- `consensus_and_range` — the economist survey median, range and number of respondents,
  and the prior release.
- `nowcast_and_leading_indicators` — a public nowcast (an inflation nowcast for CPI, a
  GDP nowcast for GDP), claims, surveys such as ISM and regional Fed indices, private
  payroll and card-spending data.
- `component_detail` — what drives the headline: shelter, energy and food in CPI;
  sector payroll detail, hours, participation in jobs data.
- `revision_and_surprise_history` — how often and by how much recent releases
  deviated from consensus, and the typical revision.
- `policy_context` — recent central bank statements, dot plots or forward guidance,
  speeches, minutes, and the committee's reaction function.
- `base_effects_and_calendar` — one-off effects, strikes, weather, holidays, survey
  timing quirks.

## Evidence checklist

1. The exact series, units, and which print resolves the market.
2. The consensus and its distribution; typical surprise size in this series.
3. A nowcast or alternative data for the release, and component details.
4. For decisions: the central bank's own communication, which is usually the strongest
   evidence, plus the data since the last meeting.
5. Rounding and threshold alignment: a consensus equal to the threshold means the
   outcome is close to a coin flip, and rounding decides it.

## Pitfalls

- **Market-implied probabilities are market prices.** Rate-futures tools (such as CME
  FedWatch) are market-derived. Treat them as comparison targets, never as input
  evidence, exactly like a Kalshi or Polymarket price.
- **Series definition.** Headline vs core, SA vs NSA, MoM vs YoY, and rounding differ
  across markets; mismatches are the most common source of wrong answers.
- **First print vs revision.** Most markets resolve on the first print or a stated
  vintage. State it.
- **Consensus is not the answer.** A calibrated distribution around the consensus is
  the starting point, with width set by the series' historical surprise size.
- **Central bank signaling.** Meetings after a blackout period tend to follow the
  guidance that came before; a recent shift in communication matters more than data.
  Keep the ladder ordinal and let `method="pool"` smooth over disagreement.
- **Lag and calendar.** Release dates move (government shutdowns, schedule changes);
  check the calendar before assuming the data arrives in time for the market.

## Subcategories (guides to be added)

US inflation, US labor market, GDP and recession, Federal Reserve decisions, other
central banks, housing and consumer indicators. Until a subcategory file exists, use this
file plus `SKILL.md`.
