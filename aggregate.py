import json
from enum import Enum, auto
import pandas as pd

from endgame.nfl.teams import PRO_FOOTBALL_REFERENCE_SHORT_NAMES, NflTeam


class Side(Enum):
    offense = auto()
    defense = auto()


def _get_team(team_name: str) -> NflTeam:
    """
    Awkward...these names don't translate exactly
    to any of the formats from EndGame, so here's a shim
    """
    if team_name == "LA":
        # Seems right? There's LA and LAC
        return NflTeam.rams
    elif team_name == "KC":
        return NflTeam.chiefs
    elif team_name == "NE":
        return NflTeam.patriots
    elif team_name == "GB":
        return NflTeam.packers
    elif team_name == "SF":
        return NflTeam.niners
    elif team_name == "LV":
        return NflTeam.raiders
    elif team_name == "NO":
        return NflTeam.saints
    elif team_name == "TB":
        return NflTeam.buccaneers
    return PRO_FOOTBALL_REFERENCE_SHORT_NAMES[team_name]


def _build_ratings():
    """
    Build a lookup for team/side/season/week ratings.
    """
    all_ratings = {}
    for week in range(8, 22):
        with open(f"{week}.json") as f:
            d = json.load(f)
        ratings = {}
        for side in Side:
            for year_ratings in d:
                side_year_ratings = {
                    year: {_get_team(team): rating for team, rating in ratings}
                    for year, ratings in year_ratings[side.name]
                }
                ratings[side] = {
                    **(ratings[side] if side in ratings else {}),
                    # Assumes there's only one year in year_ratings
                    **side_year_ratings,
                }
        all_ratings[week] = ratings
    return all_ratings


RATINGS = _build_ratings()


def get_rating(side: Side, year: int, team: NflTeam, last_week: int) -> float:
    # last_week is inclusive
    return RATINGS[last_week][side][year][team]


if __name__ == "__main__":
    # nfl.csv is from `endgame update nfl`
    games = pd.read_csv("nfl.csv")
    games = games[games.week > 8]

    ds = []
    for game in games.itertuples():
        home_team = NflTeam[game.home]
        away_team = NflTeam[game.away]
        home_off = get_rating(Side.offense, game.season, home_team, game.week - 1)
        home_def = get_rating(Side.defense, game.season, home_team, game.week - 1)
        away_off = get_rating(Side.offense, game.season, away_team, game.week - 1)
        away_def = get_rating(Side.defense, game.season, away_team, game.week - 1)
        d = dict(
            home_team=home_team,
            away_team=away_team,
            home_off=home_off,
            away_off=away_off,
            home_def=home_def,
            away_def=away_def,
            home_mov=game.home_score - game.away_score,
            home_score=game.home_score,
            away_score=game.away_score,
            week=game.week,
        )
        ds.append(d)
    ds = pd.DataFrame(ds)
    ds.to_csv("games_with_ratings.csv", index=False)
