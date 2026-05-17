import nashpy as nash
import numpy as np
from typing import List
from app.models.game import BimatrixGame
from app.algorithms.utils import format_equilibrium


def support_enumeration(game: BimatrixGame) -> dict:
    A, B = game.payoff_matrices
    game_nash = nash.Game(A, B)
    try:
        equilibria = [format_equilibrium(eq) for eq in game_nash.support_enumeration()]
        return {"success": True, "equilibria": equilibria, "count": len(equilibria)}
    except Exception as e:
        return {"success": False, "error": str(e), "equilibria": []}