# Crypto markets

Price thresholds for bitcoin, ether and other tokens, ETF approvals and flows, exchange
listings, protocol upgrades, hacks and outages, regulatory actions, and company or
treasury announcements. Start with the generic templates in `SKILL.md`; this file adds
what is specific to crypto.

## Where Chronulus fits

Split crypto markets into two kinds, because they need different tools:

- **Price-threshold markets** ("BTC above $X on date D", "ETH between $A and $B"). The
  answer is mostly a volatility calculation. Build a quantitative baseline from the
  current price, the time to expiry and an implied or realized volatility (a lognormal
  with fat-tail adjustments is a reasonable start) and treat that as your primary
  number. Use the BinaryPredictor for *adjustments*: scheduled catalysts, regime
  changes, flows and event risk that the volatility number does not capture. Do not
  ask the experts to guess short-horizon price direction from news alone.
- **Event markets** (ETF approved by date, token listed, upgrade ships, regulator acts,
  hack occurs, a company announces a purchase). These are a strong fit: they depend on
  process, calendars and base rates.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Price above/below a level at a time | binary on a threshold | proposition/negation; pass the quant baseline as evidence |
| Price range buckets at a time | ordinal over buckets | proposition/negation per bucket, reconcile with `render_ordinal_dirichlet_scorecard` |
| Touch a level any time before D | binary, path-dependent | proposition/negation; barrier probability is not terminal probability |
| Event by date | binary | proposition/negation |
| Which token/exchange/company does X first | exclusive-winner | proposition/negation per candidate |

## Session template

```
name: "<Subdomain> Crypto Event Predictor"   # e.g. "Crypto Regulatory Event Predictor"
situation: >
    I am a professional forecaster who evaluates cryptocurrency events and price
    levels. I want independent, well-calibrated probabilities to compare against
    prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), using the evidence provided and the
    resolution rules stated, as of the date supplied.
```

Use separate sessions for price thresholds, regulatory and legal events, protocol and
technical events, and company or institutional announcements.

## Input fields

Event fields: `asset_or_entity`, `resolution_criteria` (see Pitfalls), `as_of_date`,
`proposition`, `negation`.

Evidence fields:
- `market_snapshot` — spot price, recent range, realized and implied volatility, funding
  rates, open interest, time to expiry.
- `quant_baseline` — the probability from your own volatility model and how you
  computed it; label it as a baseline, not a market price.
- `catalysts_calendar` — scheduled events within the window (ETF deadlines, unlocks,
  upgrades, macro releases, court dates, protocol votes).
- `flows_and_positioning` — ETF flows, exchange balances, stablecoin supply, derivatives
  positioning, with dates.
- `regulatory_and_legal_state` — pending rules, litigation, agency statements.
- `protocol_state` — upgrade status on testnet, audit results, governance votes.

## Evidence checklist

1. The exact price source, time, and venue or index that resolves the market.
2. A volatility-based baseline over the actual horizon.
3. Scheduled catalysts in the window.
4. For regulatory events: the agency's calendar, filing deadlines and past behavior.
5. For technical events: testnet results, audit status, and the project's record on
   shipping dates.

## Pitfalls

- **Resolution source.** Prices differ by exchange and index, and markets resolve on a
  named source at a specific timestamp and timezone. A 24/7 market means weekends and
  holidays count. Put the exact source and time into the proposition.
- **Terminal vs touch.** "Above X at expiry" and "touches X before expiry" are different
  events with different probabilities; write which one it is.
- **Fat tails and jumps.** A lognormal underestimates extreme moves. Do not let a
  confident-looking Beta override a sensible tail allowance for far-from-the-money
  thresholds.
- **Anchoring on the spot price.** A price between two thresholds can look obviously
  one-sided; run the quant baseline to avoid being overconfident near the money.
- **Slipping launch dates.** Protocol upgrades and token launches are usually late.
  Include the project's history of delay.
- **Scams, manipulation and thin markets.** Low-cap tokens and obscure venues have
  unreliable prices; say so, and prefer not to forecast them.
- **Do not include prediction-market or options-market probabilities** in the inputs; use
  them afterward for comparison.

## Subcategories (guides to be added)

Major-asset price thresholds, ETF and institutional flows, regulation and litigation,
protocol and exchange events, stablecoins, and company announcements. Until a
subcategory file exists, use this file plus `SKILL.md`.
