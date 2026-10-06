# Basketball (NBA, WNBA, NCAA, EuroLeague)

Covers pro and college basketball, including international leagues. Start with
[index.md](index.md) for shared rules. Basketball has no ties and many possessions, so
the better team wins more often than in most sports; the biggest swing factor is who is
playing.

## Markets

| Market | Shape / schema | Session name |
|---|---|---|
| Moneyline (game winner) | binary, matchup schema | "NBA Moneyline Predictor", "NCAA Basketball Moneyline Predictor" |
| Spread cover | binary, proposition/negation: "SUBJECT wins by more than X" | separate session |
| Total points over/under | binary, proposition/negation | separate session |
| Series winner (best of 5 or 7) | binary, matchup schema + series state | "NBA Playoff Series Winner Predictor" |
| Player props | binary, proposition/negation | separate session, thin evidence |
| Season win totals, MVP, championship | exclusive-winner or binary threshold | one session per market |

Use separate sessions for each league: pace, depth, rest and officiating differ across
the NBA, WNBA, NCAA and EuroLeague.

## Session template (NBA moneyline)

```
name: "NBA Moneyline Predictor"
situation: >
    I am a professional forecaster who evaluates NBA games. I want independent,
    well-calibrated win-probability estimates to compare against prediction-market
    prices.
task: >
    Predict the probability that the SUBJECT team wins the game, including overtime,
    against the OBJECT team, given the information provided.
```

## Matchup fields beyond the base schema

Duplicate for SUBJECT and OBJECT:

- `*_availability_report` — official injury report status for every rotation player
  (out / doubtful / questionable / probable), minutes restrictions, and rest or
  load-management expectations. Say who the stars are and what their absence means.
- `*_efficiency_profile` — offensive and defensive rating or net rating, pace, effective
  field-goal percentage, turnover and rebounding rates, preferably on a recent window
  and with the full season for context, adjusted for opponent where possible.
- `*_lineup_data` — how the team performs with and without the key players on the floor
  if available, and the likely starting five.
- `*_schedule_spot` — days of rest, back-to-back, games in the last 5-7 days, travel,
  altitude, and the next game's importance.
- `*_venue_status` — home / away / neutral. Home-court is smaller than it used to be
  in the NBA but not zero; do not hard-code it.
- `*_motivation` — playoff seeding race, play-in, tanking, clinched seed, rest plans.
- `*_coaching_and_matchup_notes` — switching coverages, three-point reliance, size
  mismatches that matter against this opponent.
- `series_state` (series markets only) — games played, series score, who has home court,
  upcoming game location, injuries sustained during the series.

## Evidence checklist

1. Final injury report as close to tip-off as the market allows. Check it again: status
   changes during the day and the starting lineup is announced shortly before tip.
2. Net rating and pace over a recent window plus season; avoid raw record.
3. Rest, travel, back-to-back and altitude.
4. For college: conference strength, injuries, transfer-portal roster churn, venue and
   tournament seeding; one-and-done games have higher variance.
5. For series: previous games in the series, rotation shortening, adjustments, and home
   court sequence.
6. For international leagues: roster rules for imports, schedule overlap between
   domestic and continental competitions.

## Pitfalls

- **Star availability dominates.** A single star's absence moves a game more than most
  other inputs. Make that field concrete (who, status, expected minutes) and keep it
  parallel for the two sides.
- **Load management in the NBA.** "Questionable" often means "probably out" on second
  nights of back-to-backs and for veterans with minor injuries. Say what the team's
  pattern is.
- **Regular season vs playoffs.** Playoff rotations shorten and pace slows; do not reuse
  a regular-season agent's calibration for the playoffs without a separate session.
- **Series are not independent games.** Model the series winner as its own binary
  question with the series state in the event fields, rather than multiplying
  single-game probabilities by hand. Check the two against each other as a sanity test.
- **Spread and total lines** define the event, so write the number into the proposition.
  Do not pass the odds or the moneyline.
- **College sample size and variance.** Single-elimination tournaments reward
  matchups and hot shooting nights; probabilities for heavy favorites should rarely sit
  at the extremes. Note the neutral-site status.
- **Overtime.** Confirm that the market resolves on the final score including overtime.

## Workflow

1. Create the session once per (league, bet type).
2. Create the agent on the first game; reuse for every later game.
3. For each game, batch both framings (`"<away>@<home>:orig"` / `":rev"`), three games
   per batch at 5 experts.
4. `render_debiased_prediction_scorecard`, then compare with the tradable price.
5. For series winners, run the matchup schema with `series_state` populated, and
   re-run after each game as the state changes.
6. For spread or total markets, use proposition/negation with the exact line.
