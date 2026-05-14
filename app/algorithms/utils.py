import numpy as np
from typing import Tuple

def is_best_response(A: np.ndarray, B: np.ndarray,
                     row_strategy: np.ndarray, col_strategy: np.ndarray,
                     tol: float = 1e-8) -> bool:
    """Проверяет, является ли пара стратегий равновесием Нэша."""
    # Ожидаемые выигрыши при фиксированной стратегии противника
    payoffs_row = A @ col_strategy
    payoffs_col = row_strategy @ B

    # Максимально возможный выигрыш при одностороннем отклонении
    best_row_payoff = np.max(payoffs_row)
    best_col_payoff = np.max(payoffs_col)

    # Текущий выигрыш (смешанная стратегия)
    current_row_payoff = row_strategy @ payoffs_row
    current_col_payoff = payoffs_col @ col_strategy

    # Допуск на численную погрешность
    return (best_row_payoff - current_row_payoff <= tol and
            best_col_payoff - current_col_payoff <= tol)

def format_equilibrium(equilibrium: Tuple[np.ndarray, np.ndarray]) -> dict:
    """Преобразует кортеж (row_strategy, col_strategy) в словарь для JSON."""
    return {
        "row_strategy": equilibrium[0].tolist(),
        "col_strategy": equilibrium[1].tolist()
    }