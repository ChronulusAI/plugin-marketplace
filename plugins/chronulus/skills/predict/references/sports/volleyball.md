# Volleyball (indoor and beach)

Covers national-team events (Olympics, Nations League, world and continental
championships) and club leagues (e.g. Italy's SuperLega, Poland's PlusLiga, Brazil's
Superliga, Japan's SV.League, US collegiate). Start with [index.md](index.md) for shared
rules. Volleyball is a binary, set-based sport: no draws, and the match winner is
decided over a best-of-five (indoor, most senior competitions) or best-of-three (beach,
many youth and some league formats).

Data is thinner and less standardized than for the major sports. Treat that as the
central modeling constraint: say what you could not find, and expect wider Betas.

## Markets

| Market | Shape / schema | Session name |
|---|---|---|
| Match winner | binary, matchup schema | "Volleyball Match Winner Predictor" (one per league or event type) |
| Set handicap, total sets over/under, exact set score | binary, proposition/negation | separate sessions |
| Set winner (rare) | binary, matchup | separate session |
| Tournament / league winner | exclusive-winner | one session per competition |

Use separate sessions for men and women, and for national-team vs club play: roster
stability, depth and scheduling differ enough that one session would blur them.

## Session template (match winner)

```
name: "Volleyball Match Winner Predictor"
situation: >
    I am a professional forecaster who evaluates volleyball matches. I want
    independent, well-calibrated win-probability estimates to compare against
    prediction-market prices.
task: >
    Predict the probability that the SUBJECT team wins the match against the OBJECT
    team, given the information provided. The match is played to <best of five sets,
    25 points per set with the fifth set to 15, win by two> (adjust to the event).
```

State the format explicitly in the task or in `format_notes`; it is not uniform.

## Matchup fields beyond the base schema

Duplicate for SUBJECT and OBJECT:

- `*_rating_and_standing` — league standing or FIVB-style ranking, and an
  opponent-adjusted rating if you can source one; otherwise say it is unavailable.
- `*_attack_and_block` — attack efficiency, kill percentage, blocks per set, aces and
  service errors per set, side-out percentage if available.
- `*_reception_and_defense` — serve-receive quality, digs, errors; relevant against
  strong servers.
- `*_key_players` — outside hitters, opposite, setter, libero availability and
  form; the setter and primary scorers matter disproportionately.
- `*_lineup_and_rotation` — confirmed or expected starting six, any recent changes,
  foreign-player limits in leagues that cap them.
- `*_recent_form` — last 5-10 matches including set scores (straight sets vs five-setters
  tell you how dominant a win was).
- `*_physical_and_travel` — schedule load, travel, recent five-set matches,
  tournament fatigue in short events.
- `*_motivation` — qualification stakes, seeding, roster rotation in dead matches.
- `head2head` — recent meetings with set scores.
- `competition_context` — pool stage vs knockout, qualification scenarios, venue and
  home crowd (large for some club and national-team events).

## Evidence checklist

1. Starting lineups and any absences, especially setter and top-scoring attackers.
2. Recent set scores, not just wins and losses.
3. Format and stakes: pool matches in a tournament can see rotation once a team has
   qualified; knockout matches do not.
4. Serve and block efficiency, which swing sets more than raw win totals.
5. Home crowd and venue, particularly in club leagues with loud arenas.
6. For national teams, how complete the roster is: players often join late from clubs.

## Pitfalls

- **Set structure compounds an edge.** A modest per-set advantage becomes a large
  match-win probability in a best-of-five. Do not hand-adjust; just ensure the format
  is in the text so the experts reason about the right distribution.
- **Format varies by event.** Best-of-three vs five, golden-set rules in some beach
  and short-format events, and different scoring in the final set all change the
  distribution. One session per format.
- **Thin and inconsistent data.** League stats, lineups and injuries are often only
  available in local-language sources. If you can't find a field, write "not available"
  rather than guessing. Do not infer one league's numbers from another's.
- **Rotation in group stages.** Teams with a qualification already locked up can rest
  starters. Capture it in `*_motivation`.
- **Beach volleyball** is a pairs sport: pair chemistry, recent partner changes,
  weather and wind and sand conditions matter, and sample sizes are small. Use a separate
  session with the pairs as SUBJECT and OBJECT.
- **Mismatches.** Large rating gaps produce probabilities near the extremes; check the
  Beta's total (`alpha + beta`) before reading too much into a 95% estimate.

## Workflow

1. Create one session per (gender, league or event type, bet type).
2. Build the agent on the first match; reuse for every later match.
3. Batch both framings per match (`"<home>_vs_<away>:orig"` / `":rev"`), several
   matches per call if the 32-expert cap allows.
4. `render_debiased_prediction_scorecard` for the result, then compare with the
   tradable price.
5. For total-sets or exact-score markets, use proposition/negation text such as "The
   match goes the full five sets", keep the `side1_*` / `side2_*` evidence blocks, and for
   the second framing flip the evidence and use the exact complement as the proposition. If the market has several exact-score outcomes (3-0, 3-1, 3-2, 2-3, 1-3,
   0-3), treat them as one ordinal market in score order and reconcile with
   `render_ordinal_dirichlet_scorecard`.
