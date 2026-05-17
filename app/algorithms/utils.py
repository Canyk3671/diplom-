from fractions import Fraction
import numpy as np
from typing import Tuple


def float_to_frac(x: float, max_denom: int = 1000) -> str:
    """Конвертирует float в строку-дробь p/q или целое."""
    if abs(x) < 1e-9:
        return "0"
    f = Fraction(x).limit_denominator(max_denom)
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def strategy_to_fracs(strategy: list, max_denom: int = 1000) -> list:
    """Конвертирует список float в список строк-дробей."""
    return [float_to_frac(v, max_denom) for v in strategy]


def is_best_response(A: np.ndarray, B: np.ndarray,
                     row_strategy: np.ndarray, col_strategy: np.ndarray,
                     tol: float = 1e-8) -> bool:
    payoffs_row = A @ col_strategy
    payoffs_col = row_strategy @ B
    best_row = np.max(payoffs_row)
    best_col = np.max(payoffs_col)
    cur_row = row_strategy @ payoffs_row
    cur_col = payoffs_col @ col_strategy
    return (best_row - cur_row <= tol) and (best_col - cur_col <= tol)


def format_equilibrium(equilibrium: Tuple[np.ndarray, np.ndarray]) -> dict:
    row = equilibrium[0].tolist()
    col = equilibrium[1].tolist()
    return {
        "row_strategy":       row,
        "col_strategy":       col,
        "row_strategy_frac":  strategy_to_fracs(row),
        "col_strategy_frac":  strategy_to_fracs(col),
    }