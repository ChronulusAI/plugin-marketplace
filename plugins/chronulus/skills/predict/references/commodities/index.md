# Commodities markets

Oil, natural gas, gold, silver, copper, agricultural goods, and retail prices tied to
them (gasoline, eggs, food), plus supply-side events like OPEC decisions and inventory
reports. Start with the generic templates in `SKILL.md`; this file adds what is specific
to commodities.

## Where Chronulus fits

- **Price-threshold markets.** Like crypto, the baseline is a volatility calculation:
  the relevant futures price, time to expiry and implied volatility from options. Use
  the BinaryPredictor for what that baseline misses: supply disruptions, policy
  decisions, weather and inventory surprises. Pass the baseline as evidence.
- **Scheduled-report markets** (EIA inventories, USDA reports, OPEC+ meetings, retail
  price averages). Strong fit when you give the experts the consensus, the recent
  trend and the seasonality.
- **Retail prices** (national average gasoline, egg prices) move slowly and follow
  wholesale prices with a lag; the baseline is a trend projection from the latest print.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Settle or spot above a level on a date | binary on a threshold | proposition/negation, quant baseline in evidence |
| Price range buckets on a date | ordinal | proposition/negation per bucket |
| Monthly average or weekly print above a level | binary on a threshold | proposition/negation |
| OPEC+ / policy decision (cut, hold, raise) | ordinal ladder | proposition/negation per outcome |
| Inventory build vs draw | binary | proposition/negation, consensus in evidence |

## Session template

```
name: "<Commodity> <Market Type> Predictor"    # e.g. "WTI Crude Settlement Threshold Predictor"
situation: >
    I am a professional forecaster who evaluates commodity prices and supply events. I
    want independent, well-calibrated probabilities to compare against prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), using the evidence provided and the
    resolution rules stated, as of the date supplied.
```

One session per (commodity family, market type): "crude oil price threshold", "US
gasoline price", "gold price threshold", "weekly EIA inventory change".

## Input fields

Event fields: `commodity_and_contract`, `resolution_criteria` (contract month, price type,
source, date and time), `as_of_date`, `proposition`, `negation`.

Evidence fields:
- `price_and_curve` — current price, the relevant futures contract and curve shape
  (contango or backwardation), recent range, implied volatility.
- `quant_baseline` — your probability from a volatility model over the actual horizon.
- `supply_and_demand` — production, inventories versus the seasonal norm, demand
  indicators, and outages or disruptions.
- `policy_and_geopolitics` — OPEC+ decisions, sanctions, tariffs, strategic reserve moves.
- `weather_and_seasonality` — crop conditions, hurricane risk for Gulf production,
  heating or cooling demand.
- `scheduled_releases` — the dates of EIA, USDA, OPEC and exchange reports and the
  consensus for each.

## Evidence checklist

1. Exactly which contract or index resolves the market, and at what time and date.
2. The futures curve and an implied-volatility-based baseline.
3. Inventory levels relative to seasonal norms, and the consensus for the next report.
4. Policy and geopolitical calendar in the window.
5. For retail prices: the latest published value, its publication schedule, and the lag
   from wholesale.

## Pitfalls

- **Spot vs futures vs settlement.** A "price above X" market can resolve on the
  front-month settle, a spot index, or a retail average; they differ. Write the exact
  one.
- **Contract rolls.** Front-month changes at expiry; check the roll date near the
  market's deadline.
- **Seasonality.** Gasoline, natural gas and agricultural prices have strong seasonal
  patterns. Say which season it is and what the norm is.
- **Report revisions and publication lags.** Weekly and monthly data are revised or
  published on a schedule; state the first-print vs revised convention.
- **Unscheduled shocks.** A disruption can move prices a lot in a day; do not give
  extreme probabilities near the money.
- **Do not include market prices as probabilities** in the inputs; the futures price
  is a necessary input for the baseline, but not a forecast of the outcome to anchor on.

## Subcategories (guides to be added)

Crude oil and refined products, natural gas, precious metals, base metals, agriculture,
retail price indices, OPEC and policy decisions. Until a subcategory file exists, use this
file plus `SKILL.md`.
