# chronulus

Claude Code / Claude.ai skills that teach Claude how to use the Chronulus MCP server. This plugin includes two skills: `predict` and `forecast`.

## `predict`

A skill that teaches Claude how to use the
[chronulus-mcp](https://github.com/ChronulusAI/chronulus-mcp) Chronulus MCP
server to build reusable, calibrated probability predictors for prediction-market
questions (Kalshi, Polymarket, and similar) — binary markets like "will A beat B?",
"will X happen by date D?" or "will Y exceed a threshold?", and markets with more than
two outcomes, like a soccer win/draw/loss line, an ordinal ladder (a rate-decision
market), or an exclusive-winner field (an award category, a tournament, a multi-candidate race).

### Category references

`skills/predict/references/` has one guide per broad market category, each with
the market shapes, a session template, input fields, an evidence checklist and the
pitfalls specific to that category:

| Category | Reference | Detailed subcategory guides |
|---|---|---|
| Sports | `sports/index.md` | football, soccer, tennis, volleyball, basketball, e-sports (CS2, League of Legends, Dota 2, Valorant) |
| Elections | `elections/index.md` | planned |
| Politics and policy | `politics/index.md` | planned |
| Culture and entertainment | `culture/index.md` | planned |
| Crypto | `crypto/index.md` | planned |
| Commodities | `commodities/index.md` | planned |
| Climate and weather | `climate/index.md` | planned |
| Economics | `economics/index.md` | planned |
| Mentions | `mentions/index.md` | planned |
| Finance | `finance/index.md` | planned |
| Tech and science | `tech-science/index.md` | planned |

## What it covers

- Setting up **one session + one agent per (category, bet type)** that gets reused across
  every future question, instead of recreating either per question.
- Two input schemas: a **matchup** schema (event-level fields plus symmetric
  `side1_*`/`side2_*` fields) for contests, and a **proposition/negation** schema for
  thresholds, "by date" events, draws and multi-outcome markets.
- Data-collection guidance: research instead of fabricate, explicit "not available"
  notes over blanks/guesses, and keeping evidence parallel between sides.
- The **dual-framing** technique — run every question twice with the framing swapped, then
  average the Beta parameters — to cancel directional framing bias before trusting or
  quoting a probability.
- **Batching:** running many predictions concurrently in one call with
  `batch_reuse_prediction_agents_and_get_predictions` — both framings of a question, a
  slate of games, or every outcome of a multi-outcome market — including the 32-expert
  batch cap and per-item error handling.
- **Beyond binary:** eliciting one dual-framed, debiased Beta per outcome (via a
  proposition/negation input schema instead of fixed sides) and reconciling them into
  a single Dirichlet with `reconcile_ordinal_outcome_dirichlet` /
  `reconcile_exclusive_outcome_dirichlet` and their `render_*_dirichlet_scorecard`
  counterparts — covering ordinal outcomes (a draw between two win outcomes, a "hold"
  between cuts and hikes) as well as unordered exclusive-winner fields.
- **Comparing against market prices:** unit conversion (Kalshi cents, Polymarket
  dollars), tradable prices net of fees, and keeping market prices out of the inputs.

## `forecast`

A skill for producing time-series forecasts with the Chronulus `NormalizedForecaster`: no
historical data required, a 0–1 normalized series plus the agent's explanation, over a
horizon of hours, days or weeks.

- Setting up **one session + one agent** per forecasting use case and reusing it across
  items that share an `input_data_model`.
- Writing the session `situation`/`task`, designing the input fields, and the same
  research-don't-fabricate data-collection rules.
- Setting `forecast_start_dt_str`, `time_scale` and `horizon_len`.
- **Showing the result** with `render_forecast_scorecard` (plot plus explanation tooltip)
  instead of hand-building a chart.
- **Rescaling** into real units with `y_min`/`y_max` and `invert_scale`, including the
  exact formula, and when to use `rescale_forecast` for the numbers themselves.
- The optional, on-demand risk assessment scorecard.

## Requirements

A Chronulus account. This plugin bundles a connection to the hosted Chronulus
MCP server at `https://mcp.chronulus.com/mcp` (the production deployment of
[chronulus-mcp](https://github.com/ChronulusAI/chronulus-mcp)) — no local install or
API key file needed. You'll be prompted to sign in via OAuth the first time a tool
from it is used.

## Installation

Install via this marketplace:

```
/plugin marketplace add ChronulusAI/plugin-marketplace
/plugin install chronulus
```

Run `/mcp` afterward to confirm the Chronulus server connected and to complete
sign-in.
