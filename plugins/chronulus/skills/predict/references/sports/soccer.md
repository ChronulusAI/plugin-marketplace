# Soccer (association football)

Covers leagues (EPL, La Liga, Serie A, Bundesliga, MLS, ...), domestic cups, European
club competitions and international tournaments. Start with [index.md](index.md) for
shared rules. Soccer is the canonical **3-outcome** market, so most of the work here
uses the "Beyond binary" section of `SKILL.md`.

## Markets

| Market | Shape / schema | Session name |
|---|---|---|
| Full-time result: home / draw / away | ordinal, 3 outcomes, proposition/negation | "Soccer Match Result Predictor" |
| To advance / win the tie (two-legged ties, knockout rounds) | binary, matchup or proposition | "Soccer Knockout Advance Predictor" |
| Draw no bet | binary conditional on no draw; derive it from the 3-way result rather than asking directly | none |
| Both teams to score | binary, proposition/negation | "Soccer BTTS Predictor" |
| Total goals over/under | binary, proposition/negation | "Soccer Total Goals Predictor" |
| Tournament / league / top-scorer winner | exclusive-winner | one session per competition |

If the market is "Team A wins" (a Yes/No contract on one outcome), it is not a
two-way market: a draw makes "does not win" include the draw. Price it with the 3-way
result and use the single outcome's reconciled probability.

## Session template (3-way result)

```
name: "Soccer Match Result Predictor"
situation: >
    I am a professional forecaster who evaluates association football matches. I want
    independent, well-calibrated probabilities for each full-time result.
task: >
    Predict the probability that the SUBJECT proposition is true, as opposed to the OBJECT
    proposition (its logical negation), for a match decided over 90
    minutes plus stoppage time (extra time and penalties are not included).
```

Keep the `side1_*` / `side2_*` evidence blocks and add the `proposition` / `negation`
fields, with three outcome propositions per match, each dual-framed as in the worked
example in `SKILL.md`. In the reversed call the two evidence blocks trade places (home
team's information in `side2_*`, away team's in `side1_*`) and the statements are the
exact complements; event-level fields do not change. Do not ask "away team wins" as the
reversed question for the home-win outcome, since the draw sits between them. Order for the ordinal tool:
`[home_win, draw, away_win]`, so that the draw is the interior outcome. Keep this order
consistent in every match, and label by home/away rather than by "favorite".

## Event and team fields beyond the base schema

- `competition_context` — league table positions, group stage vs knockout, first or
  second leg, aggregate score, away-goals rule if any (many competitions no longer use it).
- `*_expected_goals_profile` — xG for and against over a stated window, shots, set-piece
  share, and how much of the record is finishing luck.
- `*_lineup_selection` — confirmed or predicted XI, formation, absentees by position.
  Goalkeeper and center-forward absences matter most.
- `*_squad_availability` — injuries, suspensions, international-duty returns.
- `*_schedule_load` — days since last match, midweek European games, travel.
- `*_motivation` — title race, relegation, qualification at stake, already safe.
- `*_venue_status` — home / away / neutral, and for neutral finals name the nominal
  home side if the rules do.
- `*_manager_context` — new manager (first matches), tactical changes, rotation habits.

## Evidence checklist

1. Predicted or confirmed lineups, usually released about an hour before kickoff.
2. xG-based team ratings over a decent window (8-15 matches), not table position.
3. Injuries and suspensions, plus rotation risk when a big match follows.
4. Fixture congestion and travel (mid-week continental matches, long away trips).
5. Competition context: a second leg, aggregate score, dead rubbers, final-day matters.
6. Home advantage is real but varies by league and has shrunk in some; do not hard-code it.

## Pitfalls

- **Draw handling.** Draw probabilities are typically a quarter to a third of
  outcomes in balanced matches and lower in lopsided ones. If your reconciled draw
  probability is far outside what the league's history suggests, inspect the draw
  proposition's expert opinions before trusting it. Use `method="pool"` by default and
  consider `method="ls"` with the interior floor if the three Betas disagree.
- **Regulation vs. advancing.** "Wins the match" in a knockout tie may resolve on
  regulation, after extra time, or after penalties. Pick the shape to match the rule:
  3-way result for 90 minutes; binary for to-advance.
- **Two legs.** Treat each leg as its own match with the aggregate score in context,
  and price "to advance" as its own binary session.
- **Lineup uncertainty.** If lineups are not out, say so in the field and expect wider
  Betas; re-run after lineups are confirmed if the market is still open.
- **Cup upsets and rotations.** Domestic cup games against lower-league opponents see
  heavy rotation; capture that in `*_lineup_selection`, not just in form.
- **Women's, youth and lower leagues.** Data is thinner. Say what you could not find
  instead of borrowing men's top-flight numbers.
- **Competition format.** Know whether the market is on a single match, a group-stage
  outcome or the whole tournament; they are different sessions.

## Workflow

1. Create the session once.
2. Build the agent on the first outcome of the first match with the matchup schema
   plus the proposition/negation fields.
3. For each match, run one batch of 3 outcomes × 2 framings × 2 experts = 12 experts
   (the 32 cap allows two matches per batch). The reversed calls flip the evidence blocks.
4. Debias all three outcomes in one `debias_beta_params` call, then `render_ordinal_dirichlet_scorecard`
   with the three `alpha`/`beta` pairs in `[home_win, draw, away_win]` order; use
   `reconcile_ordinal_outcome_dirichlet` instead when you need the numbers in the
   conversation. Keep each outcome's request ids: the card's per-outcome "Show
   order-debiased scorecard" button asks for `render_debiased_prediction_scorecard`.
5. Compare each reconciled probability to the corresponding tradable price. Remember
   prediction-market single-outcome contracts pay on one outcome only.
