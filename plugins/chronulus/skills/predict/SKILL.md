---
name: predict
description: >
  Best practices for using the Chronulus MCP server to produce reusable, calibrated
  probability estimates for high-value, intelligence, and prediction-market-style
  questions (Kalshi, Polymarket, and similar) in sports, elections, politics, culture,
  crypto, commodities, climate, economics, mentions, finance, and tech & science.
  Handles binary markets ("will A beat B?", "will X happen by date D?", "will Y exceed
  a threshold?") and markets with more than two outcomes: a 3-way soccer line, an
  ordinal ladder (cut/hold/hike), or an exclusive-winner field (awards, tournaments,
  multi-candidate races). Use whenever setting up or running Chronulus predictions in
  Claude.ai or Claude Code. Covers reusing one session + agent per category and bet
  type, dual-framing (run each question twice with the framing swapped, average
  the Beta parameters) to cancel order bias, batching, Dirichlet reconciliation,
  and per-category guides, with detailed sport workflows (football, soccer, tennis,
  volleyball, basketball, e-sports).
---

# Chronulus Probability Prediction

This skill turns the Chronulus MCP tools into a repeatable pipeline for probability
estimates on prediction-market-type questions, starting from the simplest case — a binary
question ("will Team A beat Team B?", "will the bill pass by June 30?", "will CPI print
above 0.3%?") — and extending to any market with more than two mutually exclusive
outcomes (a draw, an ordinal ladder, an exclusive-winner field). Set up once per
category + bet type, then reuse for every question of that kind for as long as you're
tracking that market.

## Start here: find your category

Before designing a session, open the reference for the market's category. Each has the
market shapes, a session template, input fields, an evidence checklist and the
pitfalls specific to that kind of market. Where a sport or subcategory has its own file,
read it too — it overrides the generic templates below.

| Category | Reference | Subcategory guides |
|---|---|---|
| Sports | [references/sports/index.md](references/sports/index.md) | [football](references/sports/football.md), [soccer](references/sports/soccer.md), [tennis](references/sports/tennis.md), [volleyball](references/sports/volleyball.md), [basketball](references/sports/basketball.md), [e-sports](references/sports/esports.md) (CS2, LoL, Dota 2, Valorant) |
| Elections | [references/elections/index.md](references/elections/index.md) | to be added |
| Politics and policy | [references/politics/index.md](references/politics/index.md) | to be added |
| Culture and entertainment | [references/culture/index.md](references/culture/index.md) | to be added |
| Crypto | [references/crypto/index.md](references/crypto/index.md) | to be added |
| Commodities | [references/commodities/index.md](references/commodities/index.md) | to be added |
| Climate and weather | [references/climate/index.md](references/climate/index.md) | to be added |
| Economics | [references/economics/index.md](references/economics/index.md) | to be added |
| Mentions | [references/mentions/index.md](references/mentions/index.md) | to be added |
| Finance | [references/finance/index.md](references/finance/index.md) | to be added |
| Tech and science | [references/tech-science/index.md](references/tech-science/index.md) | to be added |

If the market fits no category, use the generic templates in this file. If a category
has no subcategory guide yet, use its index plus this file, and copy the structure of the
closest sport file when you need a detailed schema.

**Pick the schema first.** Two input schemas cover almost everything:

- **Matchup schema** (Step 2): exactly two competing sides and one must win — a game, a
  match, a series. `side1_*` / `side2_*` fields, SUBJECT and OBJECT.
- **Proposition schema** ("Beyond binary" below, and "Questions that aren't matchups"):
  everything else — thresholds, "by date" events, draws, multi-outcome markets,
  exclusive-winner fields. `proposition` / `negation` fields.

Whichever schema you use, the dual-framing, batching and reconciliation mechanics below
are identical.

It assumes the Chronulus MCP server is connected. The tools referenced below
(`create_chronulus_session`, `create_prediction_agent_and_get_predictions`,
`reuse_prediction_agent_and_get_prediction`,
`batch_reuse_prediction_agents_and_get_predictions`, `render_prediction_scorecard`,
`render_debiased_prediction_scorecard`, `get_risk_assessment_scorecard`,
`debias_beta_params`, `reconcile_ordinal_outcome_dirichlet`,
`reconcile_exclusive_outcome_dirichlet`, `render_ordinal_dirichlet_scorecard`,
`render_exclusive_dirichlet_scorecard`) come from that server.

## The core idea: set up once, reuse forever

A Chronulus `Session` (situation + task) and the `BinaryPredictor` agent built on top
of it are **reusable across every matchup of the same kind** — you do not create a new
session or agent for each game. Set both up on the *first* matchup you predict, then
reuse them for every later one:

| Step | Tool | When |
|---|---|---|
| 1. Create the session | `create_chronulus_session` | Once, ever, per **(category/subcategory, bet type)** pair — e.g. once for "NBA moneyline", a separate one for "NBA spread cover", another for "US CPI release thresholds" |
| 2. Create the agent + get the first prediction | `create_prediction_agent_and_get_predictions` | Once, on the very first matchup — this is also where `input_data_model` (your field schema) gets fixed |
| 3. Get every later prediction | `reuse_prediction_agent_and_get_prediction` | Every subsequent matchup, and every subsequent *framing* (see Dual-Framing below) — pass the same `agent_id`, new `input_data` |
| 3b. Get many predictions at once | `batch_reuse_prediction_agents_and_get_predictions` | Whenever you need two or more predictions (both framings of a matchup, a slate of games, every outcome of a multi-outcome market) — same agents, run concurrently in one call (see Batching below) |

Only start a **new** session + agent when:
- You're predicting a genuinely different bet type (moneyline vs. spread-cover vs.
  total vs. series-winner are different tasks — each gets its own session, exactly like
  the ATP example this skill is modeled on keeps "match winner", "straight sets", and
  "one set" as separate sessions).
- You're switching sports, leagues, or market categories in a way that changes what evidence matters.
- You need to add/remove/rename a field in `input_data_model` — the schema is locked in
  once the agent is created, so a schema change means a new agent (you can keep the same
  `session_id` if the situation/task still apply).

Everything else — which two teams, the date, the venue, injuries, current form — is
just a new `input_data` payload passed to the *same* agent.

## Step 1 — Session setup

Write `situation` and `task` in terms of the generic roles **SUBJECT** and **OBJECT**,
not specific teams — this is what makes the session reusable across every matchup of
this type. Model it on this template:

```
name: "<Sport/League> <Bet Type> Predictor"
    e.g. "NBA Moneyline Predictor", "EPL Match Winner Predictor", "NFL Playoff Series Winner Predictor"

situation: >
    I am a professional forecaster who evaluates <sport> matchups. I want
    independent, well-calibrated win-probability estimates I can use as a signal for
    bet sizing and for comparing against market prices.

task: >
    Predict the probability that the SUBJECT (team or player) wins <the specific binary
    event — the match outright / covers the spread / wins the series / etc.> against the
    OBJECT (team or player), given the information provided.
```

Keep `task` scoped to exactly one binary event. If you also want spread-cover or
totals predictions, that is a *different* task and needs its own session — don't
overload one session with multiple bet types.

## Step 2 — Design the input_data_model once

`input_data_model` is a list of `SimpleInputField` objects (`name`, `description`,
`type`: `'str'`). Every value is a single string, so join several items into one string.
There is currently no image/PDF field type on this
tool — if a user hands you a screenshot, box score image, or PDF, **extract or
summarize its relevant content to text yourself** and pass that text as a string field.
Total input size across all fields is capped at 10MB, so summarize rather than paste
raw dumps of long documents.

Design the schema **generically enough to cover every future matchup** in this sport +
bet type — you can't add fields later without a new agent. A solid default schema,
modeled on the ATP tennis match-winner predictor this pattern comes from (the
per-sport files under `references/sports/` extend it with sport-specific fields):

**Event-level fields** (describe the contest itself):
- `competition` — league/competition and season (e.g. "2026 NBA Regular Season")
- `matchup_stage` — round, week, or stage (e.g. "Conference Semifinals, Game 5")
- `venue` — venue, city, and whether it's a true home game, true road game, or neutral site
- `event_datetime` — scheduled date/time (with timezone)
- `format_notes` — anything about the format/stakes that could matter (elimination game,
  rivalry game, tanking incentives, rest-the-starters situations)
- `head2head` — historical head-to-head record/context between the two sides
- `situational_context` — weather (outdoor sports), rest days/travel/back-to-backs,
  officiating tendencies, or other external factors relevant to this sport

**Side-level fields** — duplicate this block once for `side1_*` (SUBJECT) and once for
`side2_*` (OBJECT):
- `side1_name` / `side2_name` — full name of the team or player(s)
- `side1_standing` / `side2_standing` — current record, ranking, or standing
- `side1_recent_form` / `side2_recent_form` — recent results, streaks, scoring/efficiency trends
- `side1_key_availability` / `side2_key_availability` — injury report / key player(s) availability
- `side1_matchup_stats` / `side2_matchup_stats` — the statistical profile that matters for
  this sport (e.g. offensive/defensive efficiency and pace for basketball; serve/return
  stats and surface record for tennis; xG and set-piece record for soccer) — tailor this
  to the sport, but keep the *field names* identical between side1 and side2
- `side1_motivation` / `side2_motivation` — situational motivators (must-win, already
  clinched/eliminated, revenge game, short rest)

Adapt field count and specifics to the sport — a hockey predictor might add
`side1_goalie_starter` / `side2_goalie_starter`; a soccer predictor might add
`side1_lineup_selection` / `side2_lineup_selection`. The shape (event fields once,
symmetric side1/side2 fields) is what matters, because it's what makes the dual-framing
swap in the next section mechanical.

When writing the side-level field descriptions, you should avoid using "side 1" and "side 2". Instead you should refer to them only as "the SUBJECT" or "the OBJECT". This keeps Chronulus from anchoring them to a spatial or visual "side" of any data or tables you may provide.  


## Data collection: don't guess, don't leave gaps

Chronulus's experts can only be as good as what you feed them. Before calling the
prediction tool:

- **Research every field, don't fabricate.** Pull current standings, injury reports,
  recent form, and head-to-head record from real sources (web search/fetch, a
  connected stats provider, or the user directly) rather than relying on background
  knowledge that may be stale.
- **If a field genuinely has no data, say so explicitly** instead of inventing a value
  or leaving it blank — e.g. `"No injury report available as of prediction time."`
  A clear "not available" note lets the experts reason around a gap; a fabricated
  value or an empty string produces a confidently wrong prediction.
- **Keep side1 and side2 fields evidentially parallel.** If you report a stat for one
  side, report the same stat (or an explicit "not available") for the other.
- Confirm today's date/game date before pulling "recent form" so you don't quote stats
  from the wrong week.

## Step 3 — Run the prediction, then reuse

First matchup:

```
create_prediction_agent_and_get_predictions(
    session_id=<from step 1>,
    input_data_model=[...the schema above...],
    input_data={...this game's values, side1 = whichever side you're framing as SUBJECT...},
    num_experts=5,
)
```

This returns `agent_id`, `request_id`, `beta_params` (`alpha`, `beta`), `expert_opinions`,
`probability`, and `billing` (what the call cost; see Cost and balance below). Save
`agent_id`.

Every later matchup (and every later framing — see below):

```
reuse_prediction_agent_and_get_prediction(
    agent_id=<saved agent_id>,
    input_data={...new game's values...},
    num_experts=5,
)
```

`num_experts=5` is a reasonable default for a market you're actually going to act
on; drop to 3 while iterating on your schema/wording to save cost, and consider more
for high-stakes decisions.

## Dual-framing: cancel evidence order bias before trusting the number

A single call may be biased. Like a human respondent, the model is susceptible to cognitive order / framing bias 
depending on which side occupies the `side1`/SUBJECT slot. **Never quote or act on a
single framing's raw probability.** For every matchup, call the agent twice, swapping
which side's data fills the `side1_*` vs `side2_*` fields, then average. Only those
two evidence blocks trade places (names included); the event-level fields — venue, date,
format, head-to-head, situational context — stay identical in both calls, because
re-ordering them is error-prone and is not what the bias comes from:

```
# Frame 1: Team A's data → side1_*, Team B's data → side2_*
pred_orig = reuse_prediction_agent_and_get_prediction(agent_id, input_data=frame1, num_experts=5)

# Frame 2: swap — Team B's data → side1_*, Team A's data → side2_*
pred_rev  = reuse_prediction_agent_and_get_prediction(agent_id, input_data=frame2, num_experts=5)

alpha1, beta1 = pred_orig["beta_params"]["alpha"], pred_orig["beta_params"]["beta"]
alpha2, beta2 = pred_rev["beta_params"]["alpha"],  pred_rev["beta_params"]["beta"]

# Frame 2's Beta is an estimate from the perspective of the COMPLEMENT event (B was
# the SUBJECT, so it describes "B wins", i.e. "A does not"). Flip it back to A's view:
# alpha1 = evidence for A (A was side1/SUBJECT in frame 1)
# beta2  = evidence against B, i.e. for A (B was side1/SUBJECT in frame 2)
alpha_star_A = (alpha1 + beta2) * 0.5
beta_star_A  = (beta1  + alpha2) * 0.5

prob_A = alpha_star_A / (alpha_star_A + beta_star_A)   # de-biased P(A wins)
prob_B = 1 - prob_A
```

Both calls use the **same `agent_id`** — the schema doesn't change, only which side's
data occupies which slot. This is the number to report, size a bet with, or compare
against a market line — never a single framing's raw `probability` field.

**To show the user this debiased result, call `render_debiased_prediction_scorecard`
instead of computing and describing it yourself in text:**

```
render_debiased_prediction_scorecard(
    original_request_id=pred_orig["request_id"],
    reversed_request_id=pred_rev["request_id"],
    subject_label="Team A",   # or player/hypothesis name — whatever occupied side1 in frame1
    object_label="Team B",
    title="Team A vs Team B — Moneyline",
)
```

This tool does the same `alpha1+beta2` / `beta1+alpha2` averaging internally and renders
the debiased consensus alongside a "Framing Check" card showing each raw framing's
probability and the gap between them — the bias being corrected for, made visible. It
is a general-purpose tool (not sports-specific), so it's the right tool any time you've
run this dual-framing pattern, not just for sports matchups. The card shows the first
expert's opinions for each framing, not the whole panel, to stay small enough to display;
`render_prediction_scorecard` shows every expert of a single framing.

The render tool's output is a visual card, not a value returned to the conversation. When
you need the debiased numbers yourself — to quote the probability, reason about it, or
compare it with a market — **call `debias_beta_params` instead of averaging by hand**:

```
debias_beta_params(items={
    "game1": {
        "original_alpha": pred_orig["beta_params"]["alpha"], "original_beta": pred_orig["beta_params"]["beta"],
        "reversed_alpha": pred_rev["beta_params"]["alpha"],  "reversed_beta": pred_rev["beta_params"]["beta"],
    },
})   # -> {"game1": {"alpha": alpha_star, "beta": beta_star, "probability": prob_A}}
```

`items` is `{label: pair}` and the result is keyed by the same labels. It takes any number of
pairs, so put every pair you need — a whole slate of games, or every outcome of a
multi-outcome market — in **one call**.

It computes exactly the formula above, so the numbers match the card. Pass each call's
`beta_params` exactly as returned: the reversed Beta is already an estimate from the
complement event's perspective, and the tool does the flipping back to the original
outcome's perspective, so never swap alpha and beta yourself first. The formula is worth
understanding, but it is easy to swap the wrong two parameters or to average probabilities
instead of Betas, so let the tool do the arithmetic.

## Batching: run many predictions in one call

`reuse_prediction_agent_and_get_prediction` handles one prediction per call. Whenever you
need **two or more** — both framings of a matchup, a whole slate of games, or every
outcome of a multi-outcome market — use `batch_reuse_prediction_agents_and_get_predictions`
instead. It queues everything up front, runs the predictions concurrently, waits for all
of them, and returns one dict, so a batch takes about as long as its slowest prediction
instead of the sum of all of them. It is the same operation as
`reuse_prediction_agent_and_get_prediction`, just many at once.

Pass `items` as `{item_key: {agent_id, input_data, num_experts}}`. The `item_key` is any
unique string you choose, so you can tie each result back to what it is for — name it
after the task (e.g. `"lal_vs_bos:orig"`, `"lal_vs_bos:rev"`). Items can use different
agents, so you can create several prediction agents first (one per category / bet type) and
batch across all of them in a single call.

```
results = batch_reuse_prediction_agents_and_get_predictions(items={
    "lal_vs_bos:orig": {"agent_id": agent_id, "input_data": frame1, "num_experts": 5},
    "lal_vs_bos:rev":  {"agent_id": agent_id, "input_data": frame2, "num_experts": 5},
})

orig, rev = results["lal_vs_bos:orig"], results["lal_vs_bos:rev"]
# each success has the same fields as reuse_prediction_agent_and_get_prediction:
#   agent_id, request_id, beta_params, expert_opinions, probability, billing
# and results["billing"] is the total cost of the whole batch
```

The result for each key is exactly what a single call would have returned, so everything
downstream is unchanged — apply the same dual-framing averaging, or hand
`orig["request_id"]` / `rev["request_id"]` straight to `render_debiased_prediction_scorecard`.

Rules to know before you batch:

- **The batch is capped at 32 experts in total.** The `num_experts` of all items must add
  up to at most 32, and each item needs at least 2. Budget before you build the batch:
  e.g. one dual-framed matchup at 5 experts is 10 experts, so three matchups (30) fit in one
  call but a fourth does not. A batch over the cap is rejected outright — nothing is queued.
  For bigger jobs, split them across several calls (keep both framings of a matchup, and all
  outcomes of one multi-outcome market, in the *same* call), or lower `num_experts`.
- **Check every item before using it.** One item failing does not affect the others — a
  failed item comes back as `{"error": "..."}` in place of its result, while the rest still
  complete. Look for the `"error"` key on each result, fix and re-run just the failed items,
  and never average a framing pair if either half failed.
- **Never use `"error"` or `"billing"` as an `item_key`.** A top-level `"error"` key in the
  response means the whole batch was rejected (over the expert cap, empty, or a reserved
  key), and a top-level `"billing"` key is the total cost of the batch.
- **`agent_id`s must be real.** Use the `agent_id` returned by
  `create_prediction_agent_and_get_predictions`; do not invent one. Each item's `input_data`
  must follow *that item's* agent's `input_data_model`.
- A single prediction on its own (no framing pair, no slate) is still just
  `reuse_prediction_agent_and_get_prediction`.

## Questions that aren't matchups

Most non-sports markets have no pair of sides: "will X happen by D?", "will the value
exceed T?", "will exactly one of these candidates win?". Use the **proposition schema**
from "Beyond binary" below even when there are only two outcomes. The agent keeps one
fixed input model, and each call carries two fields:

- `proposition` — the SUBJECT statement whose probability is being assessed, written as
  a complete, checkable sentence with its threshold, date, source and timezone.
- `negation` — the OBJECT statement, the exact logical complement of the proposition
  (everything that makes the market resolve No, including edge cases like ties,
  cancellation or a missed deadline).

What dual-framing flips depends on the question. Like a human respondent, the model is
susceptible to cognitive order / framing bias depending on which side occupies the
`side1`/SUBJECT slot, so you flip the *order the agent sees things in*:

- **Two competing sides, each with its own evidence** (a match where a draw or other
  outcomes are possible): keep the `side1_*` / `side2_*` evidence blocks next to
  `proposition` / `negation` and flip the evidence exactly as in a matchup. See "Beyond
  binary" below.
- **No competing sides** (a threshold, a date, one candidate, one word in a speech):
  there are no two evidence sets to reorder, so the only thing left to flip is the two
  statements. Swap `proposition` ↔ `negation` between the calls.

Either way the same averaging formula applies. Around those fields, build the input
model from the category reference: an event block (what, when, resolution criteria,
`as_of_date`) and an evidence block (the category's key facts).

Four habits make these questions work:

1. **Put the resolution rule in the text.** The market pays on its rules, not on the
   headline: the source, the timestamp, which print counts, whether a tie or void
   applies. Copy the rule into `resolution_criteria` and into the proposition/negation.
2. **State the `as_of_date`.** Probabilities age; the agent should know how current the
   evidence is and how much time remains.
3. **Give numeric questions a numeric baseline.** For thresholds on prices, indices,
   weather or macro data, compute a baseline yourself (a volatility model, an official
   forecast, the consensus) and pass it as labeled evidence. The experts adjust for
   what the baseline misses; they should not invent the base level.
4. **Mutually exclusive or not?** An exclusive set (one winner among K) or an ordinal
   ladder gets reconciled with the Dirichlet tools. A set of independent yes/no
   questions (several words in a speech, several thresholds that can all hold) does
   *not* — each is its own dual-framed binary, and they need not sum to 1.

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
- If `partial` is true, some experts finished and were already charged. Do not resubmit the whole request (that charges them again); use the completed results or run a new request for the missing part.
- Always quote the `request_id` when you tell the user a request failed.
- In a batch, check every item for an `"error"` key; a failed item carries the same `code`, `request_id`, `charged` and `retryable` fields. One item failing for `INSUFFICIENT_FUNDS` means the rest will too, so stop submitting more.
- When you run both framings of a dual-framing pair, don't average or debias a pair where either call failed.

**Never present a result with no expert opinions as a prediction.** If a call returns without any expert opinions, treat it as a failed call, not a result, and ask the user to check their account balance before retrying.

## Cost and balance

Every successful prediction result has a `billing` object next to `request_id`. It is a
record of what the call cost for the user, not something to draw.

```
pred["billing"]
# {"request_id": "...", "cost_usd": "0.063102", "charged_count": 2, "total_count": 2,
#  "estimated": false}
```

- **Report `cost_usd` exactly as given.** It is in USD with six decimals and is what was
  actually charged, across all of the call's experts. State it in your own text (or in a
  table the user asked for); the scorecards do not show it, so don't try to add it to one.
- **`charged_count` of `total_count`** counts predictions (one per expert), so a request that
  is only partly complete shows fewer charged than requested.
- **`estimated: true`** means the request is still running, so `cost_usd` is not final.
  `estimated_cost_usd` is then an estimate for the whole request, not a limit: the final
  cost can come out higher, so say so rather than quoting it as a promise.
- **Never estimate or invent a cost.** Don't derive one from the number of experts or from
  token counts, and don't guess the cost of a dual-framed pair. If `billing`
  is missing, tell the user the cost isn't available for that call.
- **A batch has its own total.** `results["billing"]` is the exact sum for the whole batch
  (with `request_count`, the number of calls it covers); each successful item also has its
  own `billing`. For a dual-framed matchup, report the cost of the pair as the sum of the
  two framings (the batch total, if they were one batch).
- **The balance is not in `billing`**, because it changes with every request. When the
  user asks what is left, or before a large batch, call `get_chronulus_balance()`: it
  returns `balance_usd` (available now), `reserved_usd` (held for requests still running),
  and the auto-reload settings (`auto_reload_enabled`, `auto_reload_threshold_usd`, and
  `auto_reload_amount_usd`, the amount added each time a reload happens).

## Interpreting the result

- `alpha + beta` is a pseudo-sample-size: Beta(8,2) and Beta(1.6,0.4) both imply
  `prob = 0.8`, but the first reflects a tight expert consensus and the second wide
  disagreement. Report both the probability and this spread when the spread is wide.
- To compare against a market price/line, put both on the same 0–100 scale:
  `edge = prob_A * 100 - market_implied_prob_A_cents`. A positive edge means Chronulus
  thinks the market is underpricing A. Don't feed the market price into `input_data` as
  a predictive input — it anchors the panel and defeats the point of an independent
  estimate; only use it afterward, for comparison.
  Prices come in different units — Kalshi quotes a Yes contract in cents (1–99) that pays
  $1, Polymarket quotes shares in dollars (0–1) that pay $1 — so convert to a probability
  before comparing. Compare against a price you could actually trade at (the ask when
  buying Yes, the bid when selling), net of fees, not the last-trade or midpoint, and
  check the market's rules text: the contract resolves on its own wording, which can
  differ from the headline question.
- Use `render_debiased_prediction_scorecard` (see Dual-framing above) for the
  bias-corrected result you actually report on a matchup. `render_prediction_scorecard`
  renders a single, un-debiased framing — reach for it only when inspecting one framing
  on its own (e.g. while debugging a schema), not as the user-facing result for a
  matchup. Periodically call `get_risk_assessment_scorecard(session_id)` to review
  calibration and risk across everything predicted under this session so far.

## Beyond binary: markets with more than two outcomes

Everything above assumes a strict binary — exactly two mutually exclusive results.
Plenty of real markets aren't: a soccer match can end in a **draw**, a central bank
decision has more than two rate-change sizes, a horse race has a whole field of
**exclusive winners**. This section generalizes the same dual-framing technique to
those markets.

**The pattern this generalizes from:** the reference implementation for this is a
3-outcome soccer match result — win / draw / loss. Instead of one binary proposition
per matchup (as above), it defines *three* binary propositions for the same match —
"Team A wins outright", "Team B wins outright", "the match ends in a draw" — dual-frames
and debiases **each one independently** exactly as in the previous section, and then
reconciles the three resulting Betas into a single Dirichlet distribution so the three
probabilities are internally consistent (sum to 1, not just three separate numbers that
happen to roughly do so). A draw is also structurally different from the two win
outcomes — it sits "between" them — so the reconciliation can enforce that a draw is
never the least likely of the three, which is a real constraint on soccer scorelines,
not just a modeling convenience. The rest of this section generalizes that exact
pattern — one binary proposition per outcome, debiased independently, then reconciled
— from 3 outcomes to any K, and from soccer to any market with the same shape.

### 1. Recognize which shape you have

- **Ordinal** — outcomes sit along a meaningful scale, and outcomes next to each other
  are structurally more likely to move together. Win/draw/loss is the 3-outcome case
  (a draw sits between the two win outcomes); a rate-decision market with outcomes
  `[cut > 25bps, cut 25bps, hold, hike 25bps, hike > 25bps]` is a 5-outcome case. Use
  `reconcile_ordinal_outcome_dirichlet` / `render_ordinal_dirichlet_scorecard`.
- **Exclusive-winner, unordered** — exactly one of K candidates wins, and no candidate
  sits "between" any others (a horse race, a golf tournament field, a boat race, a
  multi-candidate election). Use `reconcile_exclusive_outcome_dirichlet` /
  `render_exclusive_dirichlet_scorecard`.

Both tools take the same shape of input — a list of `{label, alpha, beta, weight}`,
one entry per outcome — and both default to `method="pool"` (robust linear opinion
pooling) with `method="ls"` (joint least-squares) available when you want the fit to
actively reconcile disagreement between outcomes rather than just average around it.
For the ordinal tool, `method="ls"` also supports `enforce_interior_floor` (default
`True`), which is the generalized version of "a draw is never the least likely
outcome" — every outcome that has a neighbor on both sides (a draw between win/loss;
`hold` between the two cuts and two hikes) is constrained to not be less likely than
BOTH of its immediate neighbors.

### 2. Elicit one binary proposition per outcome, not one per matchup

Keep the matchup schema from Step 2 above — the event-level fields and the `side1_*` /
`side2_*` evidence blocks — and add two statement fields, so the same agent can be asked
about any outcome of the match, not just "does side1 win":

- **Event-level fields** (competition, venue, `event_datetime`, format and stakes,
  head-to-head, situational context): identical in every call.
- **Evidence blocks**: `side1_*` (the SUBJECT) and `side2_*` (the OBJECT), with the same
  field names in both — name, form, availability, matchup stats, motivation. Same guidance
  as Step 2 above.
- `proposition` — "The SUBJECT proposition whose probability is being assessed"
- `negation` — "The OBJECT proposition — the logical negation of the SUBJECT proposition"

This is still **one session + one agent for the whole market** (e.g. one agent for
"soccer match outcome", not three). Per call, three things vary: which competitor's
evidence sits in the SUBJECT slot, the `proposition` and the `negation`. A 3-outcome
soccer match is three outcomes, each run in two framings (6 calls per matchup):

| Call | Evidence in `side1_*` / `side2_*` | proposition | negation |
|---|---|---|---|
| Team A win, orig | A / B | "Team A wins the match outright (not tied or defeated at full time)" | "Team A does not win outright (Team B wins, or the match ends in a draw)" |
| Team A win, rev | **B / A** | "Team A does not win outright (Team B wins, or the match ends in a draw)" | "Team A wins the match outright (not tied or defeated at full time)" |
| Team B win, orig | A / B | "Team B wins the match outright (not tied or defeated at full time)" | "Team B does not win outright (Team A wins, or the match ends in a draw)" |
| Team B win, rev | **B / A** | "Team B does not win outright (Team A wins, or the match ends in a draw)" | "Team B wins the match outright (not tied or defeated at full time)" |
| Draw, orig | A / B | "The match ends in a draw at full time" | "The match does not end in a draw (Team A or Team B wins outright)" |
| Draw, rev | **B / A** | "The match does not end in a draw (Team A or Team B wins outright)" | "The match ends in a draw at full time" |

How to read the table:

- **The flip is the evidence.** In the reversed call the two evidence blocks trade
  places: B's name and information go into `side1_*`, A's into `side2_*`. Event-level
  fields stay exactly as they were.
- **The statements follow the evidence.** The SUBJECT slot now holds the other competitor,
  so the SUBJECT statement must describe that side of the question: the exact complement
  of the original proposition. That is why the reversed proposition is the original
  negation (and the reverse). The negated wording is a consequence of the flip, not the
  goal of it.
- **The reversed Beta describes the complement.** Because the reversed proposition is the
  exact complement of the original, the reversed call's `alpha` is evidence for the
  complement event (against your outcome) and its `beta` is evidence against it (for your
  outcome). That is why `debias_beta_params` pairs `original_alpha` with `reversed_beta`.
- **Keep the reversed statement the exact complement.** Do not write "Team B wins" as the
  reversed question for the Team A win outcome: once a draw is possible, "B wins" is not
  the complement of "A wins", and averaging the two would absorb the draw's probability.

For an ordinal market with more categories (e.g. the rate-decision ladder), the same idea
applies with one proposition/negation pair per category. When the outcomes have no
competing sides at all (a threshold ladder, a candidate field), there is no evidence to
flip: swap `proposition` and `negation` only.

### 3. Debias each outcome independently

For **each** outcome, run the exact dual-framing formula from the section above —
completely independently per outcome, before any reconciliation happens:

```
# Repeat this block once per outcome (e.g. once for "Team A win", once for "Team B win", once for "Draw").
# `match` = the event-level fields, identical in both calls. sides(first, second) fills
# side1_* from `first` and side2_* from `second` — the reversed call flips them.
pred_orig = reuse_prediction_agent_and_get_prediction(agent_id, input_data={**match, **sides(a, b), "proposition": prop, "negation": neg}, num_experts=2)
pred_rev  = reuse_prediction_agent_and_get_prediction(agent_id, input_data={**match, **sides(b, a), "proposition": neg,  "negation": prop}, num_experts=2)

alpha_star = (pred_orig["beta_params"]["alpha"] + pred_rev["beta_params"]["beta"])  * 0.5
beta_star  = (pred_orig["beta_params"]["beta"]  + pred_rev["beta_params"]["alpha"]) * 0.5
```

Rather than making these 2K calls one at a time, run them as **one batch** with
`batch_reuse_prediction_agents_and_get_predictions` (keys like `"<outcome>:orig"` /
`"<outcome>:rev"`) — see Batching above. For multi-outcome predictions, use **2 experts per
framing**. Against the 32-expert cap that is 2K items × 2 experts, so up to 8 outcomes fit in
one batch (e.g. 3 outcomes × 2 framings × 2 experts = 12).

You now have one debiased `(alpha_star, beta_star)` pair per outcome — K pairs for a
K-outcome market. These are NOT yet a valid joint distribution: each was estimated
independently, so the K implied probabilities will generally not sum to 1. That's
exactly what the reconciliation tools are for.

Get every outcome's debiased pair in a single `debias_beta_params` call: one item per outcome,
labeled with the outcome's name and holding that outcome's two framings' `beta_params`. The
result is keyed by the same labels.
Both the `reconcile_*` and the `render_*_dirichlet_scorecard` tools take these debiased
`alpha`/`beta` values; none of them takes request ids or computes the debiasing for you.

### 4. Reconcile the per-outcome Betas into one Dirichlet

To **show the user** the result, pass the K debiased `alpha`/`beta` pairs from step 3 to the
`render_*` tool matching your market's shape (see step 1). It reconciles all K outcomes and
draws the result, with a per-outcome section showing the original vs. reconciled Beta and
the outcome's confidence intervals:

```
render_ordinal_dirichlet_scorecard(
    outcomes=[
        {"label": "team_a_win", "alpha": a_star_a_win, "beta": b_star_a_win},
        {"label": "tie",        "alpha": a_star_tie,   "beta": b_star_tie},   # order matters — tie is the interior outcome
        {"label": "team_b_win", "alpha": a_star_b_win, "beta": b_star_b_win},
    ],
    method="pool",
    title="Team A vs Team B — Match Result",
)
```

Each outcome's expanded section has a **"Show order-debiased scorecard"** button. Clicking
it sends you a message asking for that outcome's dual-framing scorecard. When you get it,
call `render_debiased_prediction_scorecard` with that outcome's `original_request_id` and
`reversed_request_id` (from the batch results — keep each outcome's two request ids on hand
for exactly this), `subject_label` set to the outcome's label and `object_label` set to
`"not <label>"`. That is where the experts' opinions for the outcome are shown.

The plain `reconcile_*` tools take the same `alpha`/`beta` pairs:

```
reconcile_ordinal_outcome_dirichlet(
    outcomes=[
        {"label": "team_a_win", "alpha": a_star_a_win, "beta": b_star_a_win},
        {"label": "tie",        "alpha": a_star_tie,   "beta": b_star_tie},
        {"label": "team_b_win", "alpha": a_star_b_win, "beta": b_star_b_win},
    ],
    method="pool",
)
```

For an ordinal market, **list the outcomes in order along the scale** — that order is
what defines each outcome's neighbors for the interior floor (e.g.
`[cut_gt_25bps, cut_25bps, hold, hike_25bps, hike_gt_25bps]`). For an exclusive-winner
field, order doesn't matter — list every candidate in whatever order you gathered
them (e.g. every horse in the race).

Use the plain `reconcile_*` tool instead of the `render_*` one when you need the
numeric result back in the conversation (to reason about it in text, or feed it
elsewhere); use `render_*` — which computes the same reconciliation internally, no
separate call needed — when the user wants to see the result.

### Worked example: soccer win/draw/loss, end to end

```
# One-time setup — same agent handles all three outcomes and both framings
session_id = create_chronulus_session(name="Soccer Match Result Predictor", situation=..., task=...)
first = create_prediction_agent_and_get_predictions(session_id, input_data_model=<event fields + proposition/negation>, input_data=<match context + first proposition/negation>, num_experts=2)
agent_id = first["agent_id"]

# Dual-frame each of the three outcomes as ONE batch: 3 outcomes x 2 framings x 2 experts = 12 <= 32.
# match = event-level fields (identical in every call); sides(first, second) fills side1_* from
# `first` and side2_* from `second`. The reversed call flips the evidence and takes the exact
# complement statements, so its proposition is the original negation.
props = {
    "a_win": ("Team A wins the match outright...", "Team A does not win outright..."),
    "b_win": ("Team B wins the match outright...", "Team B does not win outright..."),
    "tie":   ("The match ends in a draw at full time", "The match does not end in a draw..."),
}
items = {}
for name, (prop_text, neg_text) in props.items():
    items[f"{name}:orig"] = {"agent_id": agent_id, "num_experts": 2,
                             "input_data": {**match, **sides(team_a, team_b), "proposition": prop_text, "negation": neg_text}}
    items[f"{name}:rev"]  = {"agent_id": agent_id, "num_experts": 2,
                             "input_data": {**match, **sides(team_b, team_a), "proposition": neg_text,  "negation": prop_text}}
results = batch_reuse_prediction_agents_and_get_predictions(items=items)
# check results[key] for an "error" key before using it; re-run any item that failed

# Debias all three outcomes with the tool (never by hand), in ONE call keyed by outcome name
def pair(name):
    orig, rev = results[f"{name}:orig"]["beta_params"], results[f"{name}:rev"]["beta_params"]
    return {"original_alpha": orig["alpha"], "original_beta": orig["beta"],
            "reversed_alpha": rev["alpha"],  "reversed_beta": rev["beta"]}

debiased = debias_beta_params(items={name: pair(name) for name in props})
# -> {"a_win": {"alpha", "beta", "probability"}, "b_win": {...}, "tie": {...}}
a_win, b_win, tie = debiased["a_win"], debiased["b_win"], debiased["tie"]

# Show the user the result: reconcile the three debiased Betas into one Dirichlet
render_ordinal_dirichlet_scorecard(
    outcomes=[
        {"label": "team_a_win", "alpha": a_win["alpha"], "beta": a_win["beta"]},
        {"label": "tie",        "alpha": tie["alpha"],   "beta": tie["beta"]},   # order matters — tie is the interior outcome
        {"label": "team_b_win", "alpha": b_win["alpha"], "beta": b_win["beta"]},
    ],
    method="pool",
    title="Team A vs Team B — Match Result",
)
# If the user clicks an outcome's "Show order-debiased scorecard" button, answer with:
# render_debiased_prediction_scorecard(
#     original_request_id=results["tie:orig"]["request_id"], reversed_request_id=results["tie:rev"]["request_id"],
#     subject_label="tie", object_label="not tie", title="Draw — debiased")
```

The same pipeline, with a `reconcile_exclusive_outcome_dirichlet` /
`render_exclusive_dirichlet_scorecard` swap and one debiased Beta per
candidate instead of per win/draw/loss outcome, is how you'd handle a horse race or a
tournament-winner field.

## Quick reference

```
# One-time setup (per category + bet type)
session_id = create_chronulus_session(name=..., situation=..., task=...)
first = create_prediction_agent_and_get_predictions(session_id, input_data_model, input_data_frame1, num_experts=5)
agent_id = first["agent_id"]

# Every matchup thereafter: two calls per game, same agent_id, sides swapped
pred_orig = reuse_prediction_agent_and_get_prediction(agent_id, input_data_frame1, num_experts=5)
pred_rev  = reuse_prediction_agent_and_get_prediction(agent_id, input_data_frame2, num_experts=5)

debiased = debias_beta_params(items={
    "game1": {"original_alpha": pred_orig["beta_params"]["alpha"], "original_beta": pred_orig["beta_params"]["beta"],
              "reversed_alpha": pred_rev["beta_params"]["alpha"],  "reversed_beta": pred_rev["beta_params"]["beta"]},
})   # -> {"game1": {"alpha", "beta", "probability"}}; probability is the debiased P(side1 subject)

# Or run both framings (and any number of other matchups) concurrently in one call —
# keys are yours; total num_experts across the batch must be <= 32 (min 2 per item)
results = batch_reuse_prediction_agents_and_get_predictions(items={
    "game1:orig": {"agent_id": agent_id, "input_data": input_data_frame1, "num_experts": 5},
    "game1:rev":  {"agent_id": agent_id, "input_data": input_data_frame2, "num_experts": 5},
})   # -> {item_key: result}; a failed item is {"error": ...}; never use "error" as a key

# Show the user the debiased result (does the same averaging internally)
render_debiased_prediction_scorecard(
    original_request_id=pred_orig["request_id"],
    reversed_request_id=pred_rev["request_id"],
    subject_label=..., object_label=..., title=...,
)
```

```
# Beyond binary (K > 2 outcomes): dual-frame each outcome (one batch), debias each, then render.
# Two competing sides: the reversed call flips the evidence (sides(b, a)). No sides: drop
# sides() and swap only proposition/negation.
results = batch_reuse_prediction_agents_and_get_predictions(items={
    f"{label}:orig": {"agent_id": agent_id, "num_experts": 2,
                      "input_data": {**match, **sides(a, b), "proposition": prop, "negation": neg}}
    for label, (prop, neg) in outcome_propositions.items()
} | {
    f"{label}:rev":  {"agent_id": agent_id, "num_experts": 2,
                      "input_data": {**match, **sides(b, a), "proposition": neg,  "negation": prop}}
    for label, (prop, neg) in outcome_propositions.items()
})   # 2 experts per framing; 2K items x num_experts must total <= 32

def pair(label):
    o, r = results[f"{label}:orig"]["beta_params"], results[f"{label}:rev"]["beta_params"]
    return {"original_alpha": o["alpha"], "original_beta": o["beta"],
            "reversed_alpha": r["alpha"],  "reversed_beta": r["beta"]}

# ONE debias_beta_params call for all K outcomes, keyed by outcome label
debiased = debias_beta_params(items={label: pair(label) for label in outcome_propositions})
outcomes = [{"label": label, "alpha": d["alpha"], "beta": d["beta"]} for label, d in debiased.items()]

# Ordinal (win/tie/loss, a rate-decision ladder, ...) — outcomes MUST be in scale order
render_ordinal_dirichlet_scorecard(outcomes=outcomes, method="pool", title=...)

# Exclusive-winner, unordered (horse race, tournament field, ...) — order doesn't matter
render_exclusive_dirichlet_scorecard(outcomes=outcomes, method="pool", title=...)

# Clicking an outcome's "Show order-debiased scorecard" button asks for that outcome's
# render_debiased_prediction_scorecard — keep each outcome's two request_ids from the batch results.
# For numbers instead of a visual, pass the same outcomes to reconcile_ordinal_outcome_dirichlet /
# reconcile_exclusive_outcome_dirichlet.
```
