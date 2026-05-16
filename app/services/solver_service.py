import time
from app.models.game import BimatrixGame
from app.algorithms.lemke_howson_nashpy import lemke_howson_nashpy, lemke_howson_nashpy_all_labels
from app.algorithms.support_enumeration import support_enumeration
from app.algorithms.validation import get_game_properties
from app.algorithms.saddle_point import find_saddle_point
from app.algorithms.graphic_2x2 import solve_graphic

class SolverService:
    @staticmethod
    def solve(game: BimatrixGame, method: str, **kwargs) -> dict:
        start_time = time.perf_counter()

        # Проверка на седловую точку для всех методов
        saddle_result = find_saddle_point(game)

        if method == 'lemke_howson':
            label = kwargs.get('initial_label', 0)
            result = lemke_howson_nashpy(game, initial_dropped_label=label)
            result['method'] = 'lemke_howson'

        elif method == 'lemke_howson_all':
            result_list = lemke_howson_nashpy_all_labels(game)
            result = {
                'method': 'lemke_howson_all',
                'success': all(r['success'] for r in result_list),
                'equilibria': [r['equilibrium'] for r in result_list if r['success']],
                'errors': [r for r in result_list if not r['success']],
                'count': len([r for r in result_list if r['success']]),
                'details': result_list
            }

        elif method == 'support_enumeration':
            result = support_enumeration(game)
            result['method'] = 'support_enumeration'

        elif method == 'graphic_2x2':
            result = solve_graphic(game)
            result['method'] = 'graphic_2x2'

        elif method == 'lemke_howson_manual':
            result = {
                'method': 'lemke_howson_manual',
                'success': False,
                'error': 'Ручная реализация Лемке–Хаусона пока не готова. Идёт разработка по учебнику Колобашкиной.'
            }

        else:
            raise ValueError(f"Неизвестный метод: {method}")

        elapsed = time.perf_counter() - start_time
        result['time_sec'] = round(elapsed, 6)

        # Добавляем результаты проверок
        result['saddle_point'] = saddle_result
        result['game_properties'] = get_game_properties(game)

        return result