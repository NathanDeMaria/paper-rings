import multiprocessing
from collections import defaultdict
from typing import DefaultDict, Dict, List
from pymc3 import Model, Beta, Binomial, sample, Potential


from .game_side import GameSide
from .fit_result import LeagueFitResult


OFFENSE_NAME = "offense"
DEFENSE_NAME = "defense"
DRIVE_RESULT_NAME = "drive_result"


def fit(game_sides: List[GameSide]) -> LeagueFitResult:
    """
    Fit a list of game results.
    Currently models each season as independent,
    so it'd probably be best to only run on later weeks.
    """
    team_season_indices: DefaultDict[int, Dict[str, int]] = defaultdict(dict)
    for i, (season, team) in enumerate(
        set((s.season, s.offensive_team) for s in game_sides)
    ):
        team_season_indices[int(season)][team] = i
    off_indices = [team_season_indices[g.season][g.offensive_team] for g in game_sides]
    def_indices = [team_season_indices[g.season][g.defensive_team] for g in game_sides]
    attempts = [g.attempts for g in game_sides]
    successes = [g.successes for g in game_sides]
    n_team_seasons = sum(len(t) for t in team_season_indices.values())

    teams = set.union(*(set(season.keys()) for season in team_season_indices.values()))
    seasons = sorted(team_season_indices.keys())

    with Model() as model:
        # TODO: include something for home field advantage?
        # offense_weights = Uniform(OFFENSE_WEIGHT_NAME, lower=0, upper=1)

        # team-specific model parameters
        # TODO: set them to priors that match baseline offense/defense
        offs = Beta(OFFENSE_NAME, alpha=1, beta=1, shape=n_team_seasons)
        defs = Beta(DEFENSE_NAME, alpha=1, beta=1, shape=n_team_seasons)

        # likelihood of observed data
        # ...b/c they totally are...
        # pylint: disable=unsubscriptable-object
        game_offs = offs[off_indices]
        # pylint: disable=unsubscriptable-object
        game_defs = defs[def_indices]

        # Find P(off and def), P(!off and !def), make p = P(off and def) / P(off and def land the same)
        # so, game_offs * game_defs / (game_offs * game_defs + ((1 - game_offs) * (1 - game_defs)))
        # sort like saying we sim combos of each independently, then throw out the "impossible" times
        # Will "weight" between offense and defense wind up in the SD of defensive betas? Or was explicitly modeling that useful?
        _ = Binomial(
            DRIVE_RESULT_NAME,
            p=(game_offs * game_defs)
            / (game_offs * game_defs + (1 - game_offs) * (1 - game_defs)),
            observed=successes,
            n=attempts,
        )

        season_diffs = []
        for team in teams:
            for previous_season, season in zip(seasons[:-1], seasons[1:]):
                previous_index = team_season_indices[previous_season].get(team)
                current_index = team_season_indices[season].get(team)

                # For if teams skipped a season
                # or more likely, they weren't in the initial seasons (ex: Houston)
                if previous_index is None or current_index is None:
                    continue
                season_diffs.append(offs[current_index] - offs[previous_index])
                season_diffs.append(defs[current_index] - defs[previous_index])

        _ = Potential("yoy_change", sum(season_diffs))
    with model:
        # TODO: mess with these, check how it goes
        trace = sample(10_000, tune=10_000, cores=multiprocessing.cpu_count())

    return LeagueFitResult(
        offense_success_probs=trace[OFFENSE_NAME],
        defense_success_probs=trace[DEFENSE_NAME],
        team_season_indices=team_season_indices,
    )
