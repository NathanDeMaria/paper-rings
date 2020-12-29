from typing import Dict, List, Tuple
import numpy as np


SeasonRatings = List[Tuple[str, float]]
Ratings = List[Tuple[int, SeasonRatings]]


class LeagueFitResult:
    """
    For translating the results of a trace
    into human readable ratings.
    """

    def __init__(
        self,
        offense_success_probs: np.ndarray,
        defense_success_probs: np.ndarray,
        team_season_indices: Dict[int, Dict[str, int]],
    ):
        self._offense_success_probs = offense_success_probs
        self._defense_success_probs = defense_success_probs
        self._team_season_indices = team_season_indices

    @property
    def offensive_ratings(self) -> Ratings:
        """
        Lookup of the median offensive rating for each team/season
        """
        success_medians = np.median(self._offense_success_probs, axis=0)
        return [
            (season, _get_team_ratings(success_medians, season_indices))
            for season, season_indices in self._team_season_indices.items()
        ]

    @property
    def defensive_ratings(self) -> Ratings:
        """
        Lookup of the median defensive rating for each team/season
        """
        success_medians = np.median(self._defense_success_probs, axis=0)
        return [
            (season, _get_team_ratings(success_medians, season_indices))
            for season, season_indices in self._team_season_indices.items()
        ]


def _get_team_ratings(
    success_medians: np.ndarray, team_indices: Dict[str, int]
) -> SeasonRatings:
    team_probs = [(t, float(success_medians[i])) for t, i in team_indices.items()]
    return sorted(team_probs, key=lambda p: p[1], reverse=True)
