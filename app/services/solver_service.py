import time
import numpy as np
from app.models.game import BimatrixGame
from app.algorithms.lemke_howson_nashpy import lemke_howson_nashpy, lemke_howson_nashpy_all_labels
from app.algorithms.support_enumeration import support_enumeration
from app.algorithms.validation import get_game_properties
from app.algorithms.saddle_point import find_saddle_point
from app.algorithms.graphic_2x2 import solve_graphic
from app.algorithms.support_enumeration_hand import find_all_equilibria_hand

class SolverService:
    @staticmethod
    def _add_payoffs(result, A, B):
        if 'equilibrium' in result and result.get('success'):
            r = np.array(result['equilibrium']['row_strategy'])
            c = np.array(result['equilibrium']['col_strategy'])
            result['payoff_A'] = float(r @ A @ c)
            result['payoff_B'] = float(r @ B @ c)
        if 'equilibria' in result:
            for eq in result['equilibria']:
                r = np.array(eq['row_strategy'])
                c = np.array(eq['col_strategy'])
                eq['payoff_A'] = float(r @ A @ c)
                eq['payoff_B'] = float(r @ B @ c)

    @staticmethod
    def solve(game: BimatrixGame, method: str, **kwargs) -> dict:
        start_time = time.perf_counter()

        # Проверка на седловую точку для всех методов
        saddle_result = find_saddle_point(game)

        if method == 'lemke_howson':
            label = kwargs.get('initial_label', 0)
            result = lemke_howson_nashpy(game, initial_dropped_label=label)
            result['method'] = 'lemke_howson'
            if result.get('success'):
                SolverService._add_payoffs(result, game.A, game.B)

        elif method == 'lemke_howson_all':
            result_list = lemke_howson_nashpy_all_labels(game)
            # Берём все уникальные равновесия
            equilibria = []
            seen = set()
            for r in result_list:
                if r['success']:
                    eq = r['equilibrium']
                    key = (tuple(round(x, 8) for x in eq['row_strategy']),
                           tuple(round(x, 8) for x in eq['col_strategy']))
                    if key not in seen:
                        seen.add(key)
                        equilibria.append(eq)
            result = {
                'method': 'lemke_howson_all',
                'success': len(equilibria) > 0,
                'equilibria': equilibria,
                'count': len(equilibria)
            }
            SolverService._add_payoffs(result, game.A, game.B)

        elif method == 'support_enumeration':
            result = support_enumeration(game)
            result['method'] = 'support_enumeration'
            if result.get('success'):
                SolverService._add_payoffs(result, game.A, game.B)

        elif method == 'support_enumeration_hand':
            result = find_all_equilibria_hand(game)
            result['method'] = 'support_enumeration_hand'
            if result.get('success'):
                SolverService._add_payoffs(result, game.A, game.B)

        elif method == 'graphic_2x2':
            result = solve_graphic(game)
            result['method'] = 'graphic_2x2'

        elif method == 'lemke_howson_manual':
            result = {
                'method': 'lemke_howson_manual',
                'success': False,
                'error': 'Ручная реализация Лемке–Хаусона пока не готова.'
            }

        else:
            raise ValueError(f"Неизвестный метод: {method}")

        elapsed = time.perf_counter() - start_time
        result['time_sec'] = round(elapsed, 6)
        result['saddle_point'] = saddle_result
        result['game_properties'] = get_game_properties(game)

        return result