# American football (NFL, college)

"Football" here means American football. For association football see
[soccer.md](soccer.md). Start with [index.md](index.md) for shared rules.

## Markets

| Market | Shape / schema | Session name |
|---|---|---|
| Moneyline (game winner) | binary, matchup schema | "NFL Moneyline Predictor" / "College Football Moneyline Predictor" |
| Spread cover | binary, proposition/negation: "SUBJECT wins by more than X" | "NFL Spread Cover Predictor" |
| Total points over/under | binary, proposition/negation | "NFL Game Total Predictor" |
| Season win total, division / conference / Super Bowl winner | exclusive-winner (futures) or binary threshold | one session per futures market |
| Player props (passing yards, anytime TD) | binary, proposition/negation | separate sessions; thin evidence, treat results cautiously |

NFL and college football are different sessions even for the same bet type: roster
depth, parity, scheduling, and the amount of information differ a lot.

## Session template (moneyline)

```
name: "NFL Moneyline Predictor"
situation: >
    I am a professional forecaster who evaluates NFL games. I want independent,
    well-calibrated win-probability estimates to compare against prediction-market
    prices.
task: >
    Predict the probability that the SUBJECT team wins the game outright, including
    overtime, against the OBJECT team, given the information provided.
```

## Matchup fields beyond the base schema

Add to the `SKILL.md` Step 2 schema, duplicated for SUBJECT and OBJECT:

- `*_quarterback` — starter, status, and a one-line quality note. Quarterback status is
  the single largest swing factor; if a QB is questionable, say so and give the backup.
- `*_efficiency` — opponent-adjusted measures: EPA/play (offense and defense), success
  rate, DVOA or similar if you can source it, points per drive, turnover margin trend
  with a note on how much is luck.
- `*_trenches` — offensive/defensive line health and pass-rush/pass-block metrics.
- `*_injury_report` — official status by player (out / doubtful / questionable) and
  position group, not a list of names. Note practice participation.
- `*_special_teams_and_coaching` — kicker reliability, coaching tendencies on 4th down
  and in close games, only if they matter for this matchup.
- `*_venue_status` — home / away / neutral, and for college, travel distance.
- `weather_and_surface` — wind, temperature, precipitation, dome/roof, turf vs grass.
- `rest_schedule` — days since last game, bye week, short week, travel, time zone.

## Evidence checklist

1. Official injury report and QB status, checked on game day when possible.
2. A power rating or efficiency source that adjusts for opponent strength.
3. Weather forecast for outdoor venues (wind above roughly 15 mph matters most for the
   passing game and kicking).
4. Rest and travel: Thursday games, London games, west-to-east early kickoffs.
5. Stakes: playoff seeding, resting starters in Week 18, clinched or eliminated teams.
6. College only: transfer-portal turnover, opt-outs in bowl games, conference
   strength gaps, true home-field advantage by program.

## Pitfalls

- **Overtime and ties.** Confirm whether the market includes overtime. NFL regular-season
  ties exist but are rare; mention a tie rule in the proposition if the market voids or
  pays on it.
- **Small schedule, big noise.** 17 games is a small sample; weight priors (preseason
  ratings, last season) heavily early and say so in the field text.
- **Spread and total lines** define the event, so the number must appear in the
  proposition. Do not pass the juice or the moneyline price.
- **Late news.** Inactive lists come out about 90 minutes before kickoff in the NFL.
  If you are predicting earlier, state which players are unconfirmed.
- **College mismatches.** Large spreads are common; margin-based questions need a
  different schema from win/loss. Use the proposition form with the margin threshold.
- **Futures.** Season-long markets depend on the schedule and on injury risk over
  months. Build the exclusive-winner set with all realistic candidates and let the
  Dirichlet tool reconcile; do not assign probability to one team in isolation.

## Workflow

1. `create_chronulus_session` with the template above.
2. `create_prediction_agent_and_get_predictions` on the first game (framing 1), saving
   `agent_id`.
3. For each later game, batch both framings with
   `batch_reuse_prediction_agents_and_get_predictions`
   (`"<away>@<home>:orig"` / `":rev"`; 5 experts each, so three games per batch).
4. `render_debiased_prediction_scorecard` for each game; compute
   `edge = prob * 100 - tradable_price_in_cents` and report the spread of the Beta
   alongside the probability.
5. Periodically call `get_risk_assessment_scorecard(session_id)` to check calibration
   over the session.

For spread or total markets, switch to the proposition/negation schema, keeping the
`side1_*` / `side2_*` evidence blocks, and run the same dual-framing: flip the two
evidence blocks and write the reversed statement as the exact complement of the original
(see "Beyond binary" in `SKILL.md`).
