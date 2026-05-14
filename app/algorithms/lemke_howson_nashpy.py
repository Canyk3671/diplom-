import nashpy as nash
import numpy as np
from typing import Tuple, List
from app.models.game import BimatrixGame
from app.algorithms.utils import format_equilibrium

def lemke_howson_nashpy(game: BimatrixGame, initial_dropped_label: int = 0) -> dict:
    A, B = game.payoff_matrices
    game_nash = nash.Game(A, B)
    try:
        # Nashpy возвращает кортеж (row_strategy, col_strategy)
        eq = game_nash.lemke_howson(initial_dropped_label=initial_dropped_label)
        return {
            "success": True,
            "equilibrium": format_equilibrium(eq),
            "initial_label": initial_dropped_label
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "initial_label": initial_dropped_label
        }

def lemke_howson_nashpy_all_labels(game: BimatrixGame) -> List[dict]:
    """
    Запускает LH со всеми возможными начальными метками (0..m+n-1)
    и возвращает список уникальных равновесий.
    """
    m, n = game.shape
    results = []
    seen = set()
    for label in range(m + n):
        res = lemke_howson_nashpy(game, initial_dropped_label=label)
        if res["success"]:
            # Ключ уникальности: строковое представление стратегий с округлением
            key = (
                tuple(round(x, 8) for x in res["equilibrium"]["row_strategy"]),
                tuple(round(x, 8) for x in res["equilibrium"]["col_strategy"])
            )
            if key not in seen:
                seen.add(key)
                results.append(res)
        else:
            # Даже с ошибкой можно сохранить для отладки
            results.append(res)
    return results