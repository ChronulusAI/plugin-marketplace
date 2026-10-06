# Tennis (ATP / WTA)

Covers match winner, set-based markets and tournament winners at tour level. Start with
[index.md](index.md) for shared rules. Tennis is a clean binary sport: no draws, and a
player (not a team) is the subject, which makes the matchup schema a direct fit.

## Markets

| Market | Shape / schema | Session name |
|---|---|---|
| Match winner | binary, matchup schema | "ATP Match Winner Predictor" / "WTA Match Winner Predictor" |
| Wins in straight sets | binary, proposition/negation | "ATP Straight Sets Predictor" |
| Wins at least one set | binary, proposition/negation | "ATP One Set Predictor" |
| Total games / sets over-under, handicap | binary, proposition/negation | separate sessions |
| Tournament winner | exclusive-winner over the draw | one session per tournament |

ATP and WTA get separate sessions because best-of format, depth and variance differ.
Grand Slam men's matches are best of five sets; almost everything else is best of three.
Put the format in `format_notes` for every match, since it changes how likely the
favorite is to win.

## Session template (match winner)

```
name: "ATP Match Winner Predictor"
situation: >
    I am a professional forecaster who evaluates professional tennis matches. I want
    independent, well-calibrated win-probability estimates to compare against
    prediction-market prices.
task: >
    Predict the probability that the SUBJECT player wins the match against the OBJECT
    player, given the information provided. A match that ends by retirement or
    walkover is handled as the market's rules state: <state the rule>.
```

## Matchup fields beyond the base schema

Duplicate for SUBJECT and OBJECT unless noted:

- `*_ranking_and_rating` — ATP/WTA ranking, plus an opponent-adjusted rating such as
  Elo (overall and surface-specific) if you can source it.
- `*_surface_record` — win-loss on the match's surface over the last 12 months and
  career, with the surface named (hard indoor, hard outdoor, clay, grass).
- `*_serve_return_profile` — first-serve percentage, points won on first and second
  serve, hold and break rates, tiebreak record, ideally on this surface.
- `*_recent_form` — last 5-10 matches with opponent quality and scores, and results in
  the current tournament (sets dropped, time on court).
- `*_physical_status` — injuries, retirements, medical timeouts, travel and recovery
  between rounds, previous match length.
- `*_style_and_handedness` — playing style, handedness, and anything that matters for
  this specific matchup (a lefty's serve on the ad side, a big hitter vs a counterpuncher).
- `head2head` — overall and surface-specific, with a note on how old the meetings are.
- `surface_and_conditions` — court speed, altitude, indoor/outdoor, ball type, weather,
  day or night session, expected conditions at the scheduled time.
- `tournament_context` — round, seeding, prize money and points at stake, and whether
  this is a priority event for each player (a player may skip or underperform at
  smaller events or before a Slam).
- `format_notes` — best of three or five, final-set tiebreak rules, and the retirement
  or walkover rule in the market.

## Evidence checklist

1. Surface and format first: the same two players can be priced very differently on
   clay and grass.
2. Fitness and schedule: a five-setter yesterday, a late-night finish, travel across
   time zones or a recent injury layoff.
3. Surface-specific serve and return numbers, not just overall ones.
4. Head-to-head, but do not overweight a few meetings; check surface and date.
5. Tournament context: early rounds can be rotations of effort for top players; late
   rounds at a Slam carry full motivation.
6. Qualifiers and wildcards have thin data; say so explicitly.

## Pitfalls

- **Retirement and walkover rules.** Prediction markets differ on whether a retirement
  before or during the match voids the market, pays the player who advanced, or pays
  as a normal result. Read the rules and write the one in force into the task text.
- **Dual-framing is easy here, so do it every time.** There is no home venue, so
  the SUBJECT/OBJECT swap is just a field swap. Do not skip it because the favorite
  looks obvious; the order bias shows up most when one player is a strong favorite.
- **Best-of-three vs five.** Do not reuse one session across the two formats without
  naming the format in the proposition; if you want separate calibration, use a
  separate session for Grand Slam men's matches.
- **Ranking is a poor proxy.** Rankings lag form and ignore surface; use a rating that
  adjusts for opponent quality when you can.
- **Same-day and late scheduling changes.** Matches can be moved by weather, so check
  the order of play and the conditions at the match time.
- **Doubles and mixed.** Different sport for modeling purposes: pair chemistry and
  lineup changes matter, and data is thin. Use a separate session and make the
  SUBJECT/OBJECT the pairs.

## Workflow

1. Create the session once per tour and bet type.
2. Create the agent on the first match, reuse it for every other match.
3. For each match, batch both framings (`"<p1>_vs_<p2>:orig"` / `":rev"`) and a whole
   round of matches in one call if the 32-expert cap allows (3 matches at 5 experts).
4. `render_debiased_prediction_scorecard`, then compare against the tradable price.
5. For set-based questions (straight sets, at least one set) use separate sessions with
   proposition/negation text such as "The SUBJECT wins the match without losing a set"
   and its negation, keep the `side1_*` / `side2_*` evidence blocks, and dual-frame by
   flipping the evidence and using the exact complement as the reversed proposition.
6. For a tournament winner, treat the draw as an exclusive-winner field, but note that
   early-round probabilities depend on the bracket path; run the per-player
   propositions together and reconcile with `render_exclusive_dirichlet_scorecard`.
