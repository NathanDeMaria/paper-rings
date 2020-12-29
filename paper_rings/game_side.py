from typing import NamedTuple


# pylint: disable=inherit-non-class
class GameSide(NamedTuple):
    """
    One side of the ball for a game
    """

    season: int
    offensive_team: str
    defensive_team: str
    successes: int
    attempts: int
