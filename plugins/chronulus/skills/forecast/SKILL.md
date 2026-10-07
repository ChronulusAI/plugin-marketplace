---
name: forecast
description: >
  Best practices for using the Chronulus MCP server to produce time-series
  forecasts with the NormalizedForecaster — demand, foot traffic, share of volume,
  seasonal weights, occupancy, or any quantity over a future horizon of hours, days or
  weeks, with no historical data required. Use whenever a user asks Claude to forecast,
  project, predict a trend over time, or plot a forecast with Chronulus in Claude.ai or
  Claude Code. Covers writing the session (situation + task), designing one reusable
  input_data_model, setting the horizon, reusing one agent across many items, rescaling
  the 0–1 forecast into real units with y_min/y_max (and invert_scale), showing the
  result with render_forecast_scorecard instead of hand-building a chart, and the
  optional on-demand risk scorecard.
---

# Chronulus Forecasting

This skill turns the Chronulus MCP tools into a repeatable forecasting
pipeline. A Chronulus forecast is **normalized**: the agent returns a value between 0
and 1 for every period in the horizon, plus a written explanation. Think of it as a
seasonal weight, a share, or a probability-like index. You then map it onto real units
with `y_min` / `y_max` when you know the plausible range. It does **not** need
historical data — it reasons from the description of the thing being forecast.

It assumes the Chronulus MCP server is connected. The tools referenced below
(`create_chronulus_session`, `create_forecasting_agent_and_get_forecast`,
`reuse_forecasting_agent_and_get_forecast`, `rescale_forecast`,
`render_forecast_scorecard`, `get_risk_assessment_scorecard`) are the server's tools;
if one is missing, say so rather than improvising a substitute.

## The core idea: one session, one agent, many items

A **session** describes the use case. An **agent** is created inside a session with a
fixed `input_data_model`. Both are reusable, so set them up once on the first item you
forecast and reuse them for every later item of the same kind:

| Step | Tool | When |
|---|---|---|
| 1. Create the session | `create_chronulus_session` | Once per forecasting use case |
| 2. Create the agent + first forecast | `create_forecasting_agent_and_get_forecast` | Once — this fixes the `input_data_model` |
| 3. Every later forecast | `reuse_forecasting_agent_and_get_forecast` | Each new item with the same data model — pass `agent_id` and new `input_data` |
| 4. Show it | `render_forecast_scorecard` | After each forecast the user should see |
| 4b. Get rescaled numbers | `rescale_forecast` | Only when you need the real-unit values themselves (analysis, tables, math) |

Start a **new** agent only when the schema must change (add, remove or rename a field).
You can keep the same `session_id` if the situation and task still apply. A different
quantity to forecast (units sold vs. foot traffic) is a different task and needs its
own session.

## Step 1 — Write the session

```
name:      short label for the use case, e.g. "Weekly Store Foot Traffic"
situation: the business or context — who you are, where, what drives the quantity,
           and why you need the forecast
task:      exactly what to forecast, in the units' direction ("higher = more ...")
```

Write `situation` and `task` about the **kind** of item, not one specific item, so the
session works for every item you'll forecast with it. Say which direction is "up": the
normalized value rises with whatever the task describes (more demand, more traffic,
higher share), and that is what you map to `y_max` later.

## Step 2 — Design the input_data_model once

`input_data_model` is a list of fields (`name`, `description`, `type` of `'str'`). Every
value is a single string, so join several items (for example a list of events) into one
string. Pick the characteristics that actually drive the quantity — brand,
price, location, category, promotions, seasonality notes, known events — and describe
each field in one sentence so the agent knows how to use it. There is no image or PDF
field type: if the user gives you a file, extract or summarize the relevant content
into text first. Total input is capped at 10MB, so summarize long documents.

Design it generically enough for every future item. Different items reuse the same
fields with different values (e.g. `brand` and `price` for any product).

## Data collection: don't guess, don't leave gaps

- **Research the fields; don't fabricate.** Use real sources (web search, files the
  user shared, the user directly) rather than stale background knowledge.
- **If a field truly has no data, say so** — `"No promotion calendar available."` —
  instead of inventing a value or leaving it blank.
- **Pin down dates.** Confirm today's date and the forecast start before writing
  anything about "recent" or "upcoming" conditions.
- Dates and datetimes in the results are already in the local timezone when location
  matters. Do not convert from UTC.

## Step 3 — Set the horizon and forecast

```
create_forecasting_agent_and_get_forecast(
    session_id=<from step 1>,
    input_data_model=[...],
    input_data={...this item's values...},
    forecast_start_dt_str="2026-11-01 00:00:00",   # first period, '%Y-%m-%d %H:%M:%S'
    time_scale="days",                               # 'hours', 'days' or 'weeks'
    horizon_len=60,                                  # number of periods (default 60 days)
)
```

Choose `time_scale` and `horizon_len` from what the user asked for ("next quarter, by
week" → `weeks`, 13). Keep the horizon as short as the decision needs. The result has
`agent_id`, `prediction_id`, `data` (one row per period, `y_hat` between 0 and 1) and
`explanation`. **Save `agent_id` and `prediction_id`.**

Every later item:

```
reuse_forecasting_agent_and_get_forecast(
    agent_id=<saved agent_id>,
    input_data={...new item's values, same field names...},
    forecast_start_dt_str=..., time_scale=..., horizon_len=...,
)
```

Each call runs one forecast and can take a while. There is no batch tool for
forecasts, so don't re-run an identical request; reuse the saved result.

## Step 4 — Show it with render_forecast_scorecard

Use `render_forecast_scorecard` to show the user the forecast. It plots the series and
puts the agent's explanation in a card below it, so **do not also build your own chart**
unless the tool is unavailable (then fall back to a time-series plot with labeled axes
and the explanation as a caption below it).

```
render_forecast_scorecard(
    prediction_id=<from the forecast result>,
    title="Foot traffic, Store 12, next 8 weeks",
    # optional — plot in real units instead of 0–1:
    y_min=0, y_max=4000, invert_scale=False,
    y_axis_label="Visitors per week",
)
```

- Pass `y_min` and `y_max` **together or not at all**. It rescales internally, so you
  do not need to call `rescale_forecast` first.
- Always pass `invert_scale` as an explicit `true` or `false`; never leave it as a
  placeholder.
- `y_axis_label` is a short label for the series ("Daily units sold").

## Rescaling: turning 0–1 into real units

The mapping is `value = (1 − y_hat if invert_scale else y_hat) × (y_max − y_min) + y_min`,
so `y_hat = 0` is `y_min` and `y_hat = 1` is `y_max`.

- **Get `y_min` and `y_max` from the user or from real data** — recent history of the
  item or a close comparable, a capacity limit, a known floor. If you must assume a
  range, say so and let the user correct it. Don't present a guessed range as fact.
- **Set `invert_scale` to true only when the target units run opposite to what the
  task describes.** If the task defined "higher = more demand" but you want the output
  in "days of inventory remaining" (where more demand means fewer days), invert.
- **Never rescale by hand.** Use `render_forecast_scorecard` or `rescale_forecast` so
  the user sees exactly what the platform computes.
- Use `rescale_forecast(prediction_id, y_min, y_max, invert_scale)` when you need the
  numbers themselves (a table, totals, comparisons). It returns `{dt, y_hat}` rows in
  real units.
- **If the user wants the data as a CSV, make it as an artifact. Use two columns, `ts` and `value`: `ts` from `date`/`datetime` (or `dt`
  from `rescale_forecast`) and `value` from `y_hat`. If the plot was rescaled, take the rows
  from `rescale_forecast` (same `y_min`, `y_max`, `invert_scale`) so the CSV matches the plot;
  otherwise use the forecast result's `data`, which is on the 0–1 scale. Copy every row exactly
  — don't round, drop, or re-derive values — and say which scale the values are on.
- Saving to CSV/TXT with `save_forecast` exists only in the local stdio server, not the
  hosted one.

## When a call fails

A failed call is reported as an error (the tool result has `isError` set), with a message, a `next_step`, and these fields: `code`, `request_id`, `charged` / `charged_usd`, `retryable`, `retry_after_action`, and `partial`. Read them before you do anything else. Amounts are in USD.

| `code` | What it means | What to do |
|---|---|---|
| `INSUFFICIENT_FUNDS` | The account's wallet balance is too low; nothing ran and nothing was charged. | **Stop.** Tell the user to add funds at https://console.chronulus.com/billing (quote `estimated_cost_usd` and `balance_usd` if present). Do not retry, change the inputs, or create a new session or agent before they confirm funds were added. |
| `NO_ACTIVE_SUBSCRIPTION`, `USAGE_LIMIT_EXCEEDED` | The account can't run requests right now. | Stop and tell the user; resubmit only after they fix the account. |
| `REQUEST_TOO_LARGE` | The inputs (or horizon) are too big. | Reduce the size and resubmit. Retrying unchanged fails again. |
| `RATE_LIMITED` | Too many requests. | Wait, then resubmit. |
| `GENERATION_FAILED`, `RESPONSE_CONVERSION_FAILED`, `INTERNAL_ERROR`, `UNEXPECTED_ERROR` | The service failed while running the request. | Resubmit once. If it fails again, give the user the `request_id`. |
| `EMPTY_RESULT` | The request finished with no results, usually because it was rejected before it ran. | Treat it as a failure, not a result. Ask the user to check their balance. |
| `INVALID_INPUT` | A value doesn't match the type declared for its field. Nothing ran and nothing was charged. | Read `fields` (each entry names the field, its declared type and what was passed), correct those values, then resubmit. Retrying unchanged fails again. |
| `REQUEST_NOT_QUEUED` | The request was not queued, so nothing ran. | Read the message, fix the cause, then resubmit. |

- Use `retryable` and `charged` to decide, not guesswork: `retryable: false` means do not resubmit as-is, and `retryable: null` means unknown, so read the message first.
- Always quote the `request_id` when you tell the user a request failed.

**Never present a result with no forecast values as a forecast.** If a call returns without any forecast values, treat it as a failed call, not a result, and ask the user to check their account balance before retrying.

## Interpreting the result

- The forecast is a **relative shape** until rescaled. Don't read 0.6 as "60 units".
- Quote the agent's explanation faithfully as the reasoning behind the series, and add
  your own notes (assumptions about `y_min`/`y_max`, data you couldn't find) after it,
  clearly separated.
- If the user asks about uncertainty, be honest that the output is a single central
  path with an explanation, not a prediction interval. Don't invent bands.

## Optional: the risk assessment scorecard

`get_risk_assessment_scorecard(session_id, as_json)` returns a responsible-forecasting
risk review for the session. It is created **the first time it is requested**, so the
first call for a session can take several seconds and later calls return quickly. Use
it only when the user asks about risk, ethics or responsible use — not by default.

## Quick reference

```
session_id = create_chronulus_session(name=..., situation=..., task=...)

first = create_forecasting_agent_and_get_forecast(
    session_id, input_data_model, input_data,
    forecast_start_dt_str="YYYY-MM-DD HH:MM:SS", time_scale="days", horizon_len=60)
agent_id, prediction_id = first["agent_id"], first["prediction_id"]

# next item, same data model
nxt = reuse_forecasting_agent_and_get_forecast(
    agent_id, input_data_2, forecast_start_dt_str=..., time_scale="days", horizon_len=60)

# show it (rescaled when you know the range)
render_forecast_scorecard(prediction_id, title=..., y_min=..., y_max=..., invert_scale=False,
                          y_axis_label=...)

# need the real-unit numbers themselves
rows = rescale_forecast(prediction_id, y_min=..., y_max=..., invert_scale=False)
```
