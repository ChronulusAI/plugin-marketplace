# Climate and weather markets

Daily and monthly temperature highs and lows for specific cities, rain and snow
amounts, hurricane counts and landfalls, global temperature anomalies, wildfire and
other weather events, and sea-ice or climate indicators. Start with the generic
templates in `SKILL.md`; this file adds what is specific to weather and climate.

## Where Chronulus fits

For **short horizons** (days), weather forecast models and official forecasts beat
judgment. Do not ask the BinaryPredictor to out-forecast meteorology; instead give it
the best available forecast (the official point forecast, ensemble spread, model
disagreement) and ask for the probability that the stated threshold is met, with the
ensemble spread conveying uncertainty. For **long horizons** (seasonal and annual),
climatology and trend are the base, and the BinaryPredictor can integrate ENSO state,
seasonal outlooks and trend.

## Market shapes

| Market | Shape | Schema |
|---|---|---|
| Daily high/low above a temperature at a station | binary on a threshold | proposition/negation, forecast in evidence |
| Temperature range buckets | ordinal | proposition/negation per bucket → `render_ordinal_dirichlet_scorecard` |
| Monthly rainfall or snowfall above a level | binary on a threshold | proposition/negation |
| Number of named storms, hurricanes, landfalls above N | binary on a threshold or ordinal buckets | proposition/negation |
| Annual or monthly global temperature anomaly rank or threshold | binary or ordinal | proposition/negation |

## Session template

```
name: "<Metric> Weather Predictor"     # e.g. "Daily High Temperature Predictor"
situation: >
    I am a professional forecaster who evaluates weather and climate outcomes. I want
    independent, well-calibrated probabilities to compare against prediction-market prices.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), using the forecast and climatology
    provided and the resolution rules stated, as of the date supplied.
```

Use separate sessions for daily station markets, monthly totals, storm-season counts and
global anomaly markets.

## Input fields

Event fields: `location_and_station`, `metric_and_period`, `resolution_criteria` (source,
units, rounding, time window, see Pitfalls), `as_of_date`, `proposition`, `negation`.

Evidence fields:
- `official_forecast` — the forecast from the national weather service for the location
  and day, with its time of issue.
- `model_guidance` — the main model forecasts and their spread (global and regional,
  ensemble members), and any large disagreement.
- `observations_so_far` — for in-progress periods, the running max/min or accumulated
  total, and the remaining time.
- `climatology` — normals and the observed distribution for the date and station, and
  recent anomalies.
- `drivers` — ENSO and other climate patterns, sea-surface temperatures, soil moisture,
  and seasonal outlooks for long-horizon markets.
- `local_factors` — marine layer, urban heat, elevation, sea breeze, or snow-cover
  effects at the station.

## Evidence checklist

1. The exact station and source that resolves the market, and the exact window.
2. The latest official forecast and the ensemble spread.
3. Observations so far if the period has started.
4. Climatology and the recent anomaly.
5. For seasonal counts: current state of ENSO and basin conditions, activity to date.

## Pitfalls

- **Station and source.** Markets typically resolve on a specific station's official
  climate report. Use that station's data, not a city-wide or app forecast. Verify
  whether the day is measured in local standard time (daily climate reports generally
  are), because that changes which hours count during daylight saving time.
- **Units and rounding.** Whole degrees, Fahrenheit vs Celsius, and trace amounts of
  precipitation can decide a bucket. Write them into the proposition.
- **Forecast age.** Forecasts update several times a day; use the latest, state its
  time, and rerun if a newer one moves the number.
- **Edge-of-bucket risk.** If the forecast sits near a threshold, the probability is
  close to 50% by construction; do not let the experts produce a confident answer there.
- **Do not double count.** The official forecast already embeds model guidance; do not
  stack them as independent evidence.
- **Long-horizon markets** (hurricane counts, annual anomalies) lean on climatology and
  trend; outlook skill is modest, so Betas should be wide.

## Subcategories (guides to be added)

Daily station temperature, monthly precipitation and snowfall, hurricane and storm-season
counts, global temperature records, wildfire and extreme-event markets. Until a subcategory
file exists, use this file plus `SKILL.md`.
