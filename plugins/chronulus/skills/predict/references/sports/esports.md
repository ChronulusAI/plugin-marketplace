# E-sports (CS2, League of Legends, Dota 2, Valorant)

Covers the major competitive titles. Start with [index.md](index.md) for shared rules.
E-sports are binary and series-based: no draws in a decided series, and the most
important information (rosters, patch, map pool, draft) changes quickly. Build **one
session per game title**; the evidence that matters differs too much to share one.

## Shared structure

### Markets

| Market | Shape / schema | Notes |
|---|---|---|
| Match / series winner (Bo1, Bo3, Bo5) | binary, matchup schema | format goes in `format_notes` |
| Map or game winner within a series | binary, matchup schema with series state | needs a separate session from the series winner |
| Handicap, total maps, exact score | binary, proposition/negation | e.g. "wins the series 2-0" |
| Tournament winner | exclusive-winner | bracket path matters |

A Bo1 is far more random than a Bo3 or Bo5. Do not reuse a calibration across formats
without stating the format in the proposition or `format_notes`.

### Session template

```
name: "<Game> Series Winner Predictor"      # e.g. "CS2 Series Winner Predictor"
situation: >
    I am a professional forecaster who evaluates professional <game> matches. I want
    independent, well-calibrated win-probability estimates to compare against
    prediction-market prices.
task: >
    Predict the probability that the SUBJECT team wins the series against the OBJECT
    team, given the information provided.
```

### Fields shared by all titles (duplicate per SUBJECT and OBJECT)

- `*_roster_status` — current five players or the full lineup, any stand-ins, and how
  many matches this exact roster has played together. Roster changes are the most
  common cause of stale ratings.
- `*_rating_and_ranking` — a recognized ranking or Elo-style rating and its date, with
  the region or tier of events it reflects.
- `*_recent_results` — last 10 series with opponent strength, scores, and the
  tournament (online vs LAN, tier).
- `*_current_event_context` — results so far at this event, maps/games played, fatigue
  across long group days, and travel or visa issues.
- `*_form_and_stability` — recent coaching changes, role swaps, team tension rumors
  only if reported by reliable sources.
- `head2head` — recent meetings, with dates and roster composition in each.
- `format_notes` — Bo1 / Bo3 / Bo5, side or map selection rules, the patch, LAN or
  online, whether it is a group stage match with qualification at stake.

### Pitfalls shared by all titles

- **Roster and patch recency.** Ratings reflect past rosters and past metas. A
  new player or a new patch makes older results less informative. Write the date of
  each result and the roster that produced it.
- **Online vs LAN.** Results can differ materially; say which each result was.
- **Regional strength.** Cross-region matchups at international events are hard to
  rate because there are few samples; say so and expect wider Betas.
- **Best-of format.** State it in the proposition and in `format_notes`.
- **Forfeits and technical losses.** Check the market rules for forfeits, technical
  losses and stand-ins; the rules vary by market.
- **Source quality.** Use the main community stat sites and official match pages, not
  rumors; if a roster claim is unconfirmed, label it as such.
- **Dual-framing** works like tennis: no home side, so flipping the SUBJECT and OBJECT
  evidence blocks is mechanical. Do it every time. If the event has side selection or home crowd, move that
  attribute with the team.

## CS2 (Counter-Strike 2)

Series are Bo1, Bo3 or Bo5, played on a map pool of seven maps with a ban-and-pick veto
before play. The veto determines the maps the series is played on, which is a large part
of who wins a Bo3.

Add fields:
- `*_map_pool` — win rate and recent results per map in the active pool, which maps the
  team prefers to pick and ban, and CT-side vs T-side round win rates on each.
- `*_player_form` — rating and impact stats for the five (and any star player), recent
  form with the current roster, and AWPer or star availability.
- `veto_and_map_context` — the order of bans and picks if known (otherwise say the
  veto has not happened yet), the format and who has the advantage in the veto.

Evidence: the map pool is the main structural edge. If you predict before the veto, the
predictor has to reason over likely maps; say so. After the veto, give it the actual maps
and rerun, which is usually a meaningful improvement for Bo3 series.

## League of Legends

Series are Bo1, Bo3 or Bo5; each game starts with a champion draft, and sides (blue and
red) matter. Patch changes shift which champions and roles are strong, so a team's
recent results can be partly about the previous patch.

Add fields:
- `*_role_players` — top, jungle, mid, bot and support players, any substitutes, and
  notable individual form or recent role changes.
- `*_draft_and_champion_pool` — signature champions, flexibility, and how they handle
  the current patch; tendencies in early game vs late game.
- `*_side_and_early_game_profile` — blue vs red side record, first-blood and
  first-dragon rates, gold difference at 15 minutes, objective control.
- `patch_and_meta_context` — current patch number and the main changes, and whether the
  team has played many games on it.
- `region_and_event_context` — region (LCK, LPL, LEC, LCS/LTA, etc.) and whether this
  is domestic or an international event; international events carry the largest
  uncertainty about cross-region strength.

Evidence: gold difference at 15 minutes, objective control, draft flexibility, and
recent games on the current patch are more informative than season win rate. For
international events, weight each region's recent international results.

## Dota 2

Series are Bo1, Bo3 or Bo5, and a game lasts a long time, so draft and strategy
matter. Rosters shift often, and patch-driven meta changes are common.

Add fields:
- `*_roster_and_roles` — five players with their positions, stand-ins, and how long this
  roster has played together.
- `*_draft_style` — hero pool depth, preferred strategies (early aggression vs late
  scaling), and performance on the current patch.
- `patch_and_meta_context` — current patch and any large balance changes, and how many
  recent games each team has on it.
- `event_context` — LAN or online, region, tier, and travel.

## Valorant

Series are Bo1, Bo3 or Bo5 on a rotating map pool with an agent-pick phase. Both map
selection and the attack/defense side split matter.

Add fields:
- `*_map_pool_and_sides` — map win rates and attack vs defense round win rates per
  map, and pick/ban tendencies.
- `*_agent_composition` — typical compositions per map, flexibility, and star players'
  agent pools.
- `*_roster_and_form` — five players, stand-ins, and recent form on LAN.
- `event_context` — VCT tier, region, and whether the match is international.

## Workflow

1. Create the session once per title (and per format class if you track both Bo1 and
   Bo3 heavily).
2. Create the agent on the first series; reuse it for every later series.
3. For each series, batch both framings (`"<a>_vs_<b>:orig"` / `":rev"`) with several
   series per call if the 32-expert cap allows (three at 5 experts).
4. Re-run after the veto or draft is known if it is available before the market closes;
   treat the pre-veto result as the earlier, wider estimate.
5. `render_debiased_prediction_scorecard`, then compare with the tradable price and
   report the Beta spread.
6. For map-level markets within a series, use the matchup schema with the map and
   series state populated, in a separate session.
