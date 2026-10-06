# Finance markets

Stock and index levels, earnings outcomes, IPOs, mergers and acquisitions, corporate
actions, volatility, bond yields, market-cap rankings, and company events. Start with the
generic templates in `SKILL.md`; this file adds what is specific to finance.

## Where Chronulus fits, and a caution

Liquid financial markets are the hardest place to claim an edge: public information is
priced quickly. Treat a large gap between a Chronulus probability and a liquid market
price as a reason to re-check your evidence and resolution rules before anything else.

- **Level and threshold markets** ("S&P 500 closes above X", "stock above Y on date D").
  Baseline from the current level, time to expiry and implied volatility; the
  BinaryPredictor adjusts for scheduled catalysts. Do not use it to predict short-term
  direction from news.
- **Event markets** (earnings beat, deal closes, IPO happens by date, index inclusion,
  regulatory approval). Better fits: they depend on process, calendars and base rates.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Close above/below a level on a date | binary on a threshold | proposition/negation, quant baseline in evidence |
| Close in a range (bucket markets) | ordinal | proposition/negation per bucket |
| Earnings beat/miss, guidance raised | binary | proposition/negation, consensus in evidence |
| Deal completes by date, IPO prices by date | binary | proposition/negation |
| Which company is largest by market cap on a date | exclusive-winner | proposition/negation per company |
| Yield or VIX above a level | binary on a threshold | proposition/negation |

## Session template

```
name: "<Domain> Predictor"       # e.g. "Earnings Beat Predictor", "Merger Completion Predictor"
situation: >
    I am a professional forecaster who evaluates financial events and market levels. I
    want independent, well-calibrated probabilities to compare against prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), using the evidence provided and the
    resolution rules stated, as of the date supplied.
```

One session per (domain, market type): "equity index close thresholds", "earnings
beats", "M&A completion", "IPO timing", "market-cap ranking".

## Input fields

Event fields: `security_or_event`, `resolution_criteria` (official close, source, date,
adjustments), `as_of_date`, `proposition`, `negation`.

Evidence fields:
- `market_snapshot` — current level, recent range, implied volatility, days to expiry.
- `quant_baseline` — the probability from your volatility model and how you got it.
- `catalysts_calendar` — earnings dates, central bank meetings, index rebalances,
  shareholder votes, regulatory deadlines.
- `fundamentals_and_expectations` — for earnings: consensus, guidance, the whisper
  number if sourced, beat history. For deals: terms, financing, shareholder approval.
- `process_status` — for M&A and IPOs: regulatory reviews, filings, conditions, timeline.
- `base_rates` — how often companies of this type beat consensus, how often deals of
  this kind close and how long they take.

## Evidence checklist

1. The exact price, source and time that resolve the market, including adjustments for
   dividends or splits and the trading calendar.
2. A volatility-based baseline for any level market.
3. For earnings: the consensus definition (adjusted vs GAAP) and the company's beat history.
4. For deals: regulatory path, outstanding conditions and the spread between offer and
   market price (as context, not as an input to the probability).
5. For IPOs and listings: filing status, quiet period, market conditions.

## Pitfalls

- **Efficient-market caution.** If the baseline and the market agree and your probability
  disagrees, assume you are missing something.
- **Resolution details.** Official close vs last trade, adjusted vs unadjusted, market
  holidays, early closes, and halts.
- **Earnings definitions.** A "beat" can mean EPS, revenue, or both; against the
  consensus from a named provider. Write the exact one.
- **Deal timelines slip.** Regulatory reviews, financing and litigation take longer
  than announced. Use base rates for this kind of deal.
- **Event risk near the threshold.** Earnings and macro releases fall in the window; widen
  the distribution rather than relying on a clean volatility number.
- **Not investment advice.** Probabilities are estimates for comparison with prices;
  say so when reporting, and do not present them as recommendations to the user.
- **Do not include prediction-market prices or option-implied probabilities** as evidence
  for the event; use them only to compare afterward.

## Subcategories (guides to be added)

Equity indices, single stocks, earnings, M&A and corporate actions, IPOs, rates and
yields, volatility. Until a subcategory file exists, use this file plus `SKILL.md`.
