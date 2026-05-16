import numpy as np
from app.models.game import BimatrixGame


def find_saddle_point(game: BimatrixGame) -> dict:
    """Поиск седловой точки (равновесия в чистых стратегиях)."""
    A, B = game.payoff_matrices
    saddle_points = []

    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            # A[i,j] должно быть максимумом в своём столбце
            # B[i,j] должно быть максимумом в своей строке
            if A[i, j] == np.max(A[:, j]) and B[i, j] == np.max(B[i, :]):
                saddle_points.append({
                    'row': i,
                    'col': j,
                    'payoff_A': float(A[i, j]),
                    'payoff_B': float(B[i, j])
                })

    return {
        'has_saddle_point': len(saddle_points) > 0,
        'saddle_points': saddle_points,
        'count': len(saddle_points)
    }