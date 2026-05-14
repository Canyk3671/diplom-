import nashpy as nash
import numpy as np
from typing import List
from app.models.game import BimatrixGame
from app.algorithms.utils import format_equilibrium

def support_enumeration(game: BimatrixGame) -> dict:
    """
    Возвращает все равновесия Нэша, найденные методом перебора опор.
    """
    A, B = game.payoff_matrices
    game_nash = nash.Game(A, B)
    try:
        equilibria = list(game_nash.support_enumeration())
        formatted = [format_equilibrium(eq) for eq in equilibria]
        return {
            "success": True,
            "equilibria": formatted,
            "count": len(formatted)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "equilibria": []
        }