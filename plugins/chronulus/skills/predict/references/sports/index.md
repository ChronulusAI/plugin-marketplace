# Sports markets

Sports is the best-fit category for the BinaryPredictor: contests are repeated,
well-documented, and resolve quickly, so one session + one agent per (sport, bet type)
pays for itself over hundreds of games. Read this file first, then the sport's own file.

## Sport guides

| Sport | File | Covers |
|---|---|---|
| American football (NFL, college) | [football.md](football.md) | moneyline, spread, total, futures |
| Soccer / association football | [soccer.md](soccer.md) | 3-way result, to-advance, BTTS, totals |
| Tennis (ATP / WTA) | [tennis.md](tennis.md) | match winner, set betting, tournament winner |
| Volleyball (indoor, beach) | [volleyball.md](volleyball.md) | match winner, set/total-sets |
| Basketball (NBA, WNBA, NCAA, EuroLeague) | [basketball.md](basketball.md) | moneyline, spread, total, series |
| E-sports (CS2, League of Legends, Dota 2, Valorant) | [esports.md](esports.md) | match winner, map winner, series |

A sport with no file yet (hockey, baseball, MMA, golf, motorsport, cricket, rugby, ...)
uses this file plus the generic templates in `SKILL.md`; copy the structure of the
closest sport file when you build its schema.

## Market shapes

| Market | Shape | Schema | Tools |
|---|---|---|---|
| Moneyline / match winner with no tie possible | binary | matchup (`side1_*`/`side2_*`) | dual-frame + `render_debiased_prediction_scorecard` |
| Moneyline with a draw possible (soccer 90-min, some hockey/NFL regulation lines) | ordinal, 3 outcomes | proposition/negation | one dual-framed Beta per outcome → `render_ordinal_dirichlet_scorecard` |
| Spread cover, total over/under, player prop, "wins by 2+ sets" | binary on a threshold | proposition/negation (the line is written into the proposition) | dual-frame |
| Series winner (best-of-N) | binary | matchup, with series state in event fields | dual-frame |
| Tournament / race / leaderboard winner | exclusive-winner, K outcomes | proposition/negation | `render_exclusive_dirichlet_scorecard` |

Rule of thumb: if the question is "does A beat B?" and exactly one of them must win,
use the matchup schema. If it is about a *threshold* or a *draw*, there is no natural
SUBJECT/OBJECT pair, so use proposition/negation. Different bet types are different
sessions (see "The core idea" in `SKILL.md`).

## What to gather for any sport

Use the event-level and side-level fields in `SKILL.md` Step 2 as the base, then add the
sport's own `matchup_stats`. Across sports, the evidence that moves a probability most is:

1. **Who is actually playing.** Confirmed lineups, starters, injuries, suspensions,
   rest decisions. Re-check as close to start time as the market allows; stale
   availability is the most common cause of a bad number.
2. **Rest, travel and schedule density.** Days of rest, back-to-backs, travel distance,
   congested fixtures, a big game right after.
3. **Strength estimate.** A rating or efficiency measure that adjusts for opponent
   quality (Elo/SRS/net rating/xG difference), not raw win-loss record.
4. **Venue.** Home/away/neutral, altitude, surface, roof/weather where it applies.
5. **Stakes.** Elimination, clinched seed, rivalry, dead rubber, rotation risk.
6. **Format rules that define resolution.** See the next section.

## Pitfalls that apply to every sport

- **Read the market's resolution rules before writing the proposition.** "Wins the
  match" can mean regulation only, include overtime, include extra time and penalties,
  or void on retirement/postponement. Write the exact rule into the proposition and
  negation text so the experts price the thing that actually pays.
- **Keep home/away attached to the team, not the slot.** When you swap SUBJECT and
  OBJECT for the second framing, move the venue designation with the team. If the venue
  field says "the SUBJECT is the home team" in framing 1, framing 2 must say it of
  whichever team now occupies the SUBJECT slot, or the pair describes two different
  games. Prefer side-level fields (`subject_venue_status`: home / away / neutral) over
  a single event-level sentence, so the swap is mechanical.
- **Do not put the market price, the sportsbook odds or an implied probability into
  `input_data`.** It anchors the panel. A spread or total *line* is a different thing:
  it has to appear in the proposition ("wins by more than 3.5") to define the event.
  Include the line, not the price on either side of it.
- **Compare against a no-vig number.** Sportsbook odds include margin. Convert both
  sides to implied probabilities and normalize them to sum to 1 before computing edge.
  Exchange-style prediction-market prices (Kalshi cents, Polymarket dollars) are already
  probabilities but still carry fees and a bid-ask spread; use the price you could
  actually trade at, and net out fees.
- **Do not trust a single framing**, even in sports where you "know" the favorite.
- **Pre-game vs live.** These skills model pre-game information. In-game prices move
  on events the schema does not see; do not reuse a pre-game agent for live markets
  without a separate session built for in-game state.
- **Small samples at the start of a season, in new leagues, after roster overhauls.**
  Say so in the field text ("6 games played; ratings are largely preseason priors").
