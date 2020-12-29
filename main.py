"""
Generate a bunch of .json files containing the 
ratings for team offense/defenses up to a given week
"""

import json
import pandas as pd

from paper_rings import fit, GameSide


def _get_ratings(df: pd.DataFrame, season: int):
    games = []
    for (_, season, posteam, defteam), game in df[df.season == season].groupby(
        ["game_id", "season", "posteam", "defteam"]
    ):
        games.append(
            GameSide(
                season=season,
                offensive_team=posteam,
                defensive_team=defteam,
                successes=game.posteam_drive_success.sum(),
                attempts=len(game),
            )
        )

    league = fit(games)
    return dict(
        offense=league.offensive_ratings,
        defense=league.defensive_ratings,
    )


def main(drive_deltas_csv: str, until_week: int):
    drive_deltas = pd.read_csv(drive_deltas_csv)
    drive_deltas = drive_deltas[drive_deltas.week <= until_week]
    ratings = [
        _get_ratings(drive_deltas, season) for season in drive_deltas.season.unique()
    ]
    with open(f"{until_week}.json", "w") as f:
        json.dump(ratings, f)


if __name__ == "__main__":
    for w in range(8, 22):
        main("drive_deltas.csv", w)
