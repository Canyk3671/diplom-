import numpy as np
from typing import List, Tuple

class BimatrixGame:
    """Представление биматричной игры с матрицами A (игрок 1) и B (игрок 2)."""
    def __init__(self, A: List[List[float]], B: List[List[float]]):
        self.A = np.array(A, dtype=float)
        self.B = np.array(B, dtype=float)
        if self.A.shape != self.B.shape:
            raise ValueError("Матрицы должны быть одного размера")
        self.shape = self.A.shape  # (m, n)

    @property
    def payoff_matrices(self) -> Tuple[np.ndarray, np.ndarray]:
        return self.A, self.B

    def __repr__(self):
        return f"BimatrixGame(shape={self.shape})"