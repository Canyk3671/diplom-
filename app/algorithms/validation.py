import numpy as np
from itertools import combinations
from app.models.game import BimatrixGame


def check_nondegeneracy(game: BimatrixGame) -> dict:
    A, B = game.payoff_matrices
    m, n = A.shape

    # Проверка через C и D для 2×2
    if m == 2 and n == 2:
        a11, a12, a21, a22 = A.flatten()
        b11, b12, b21, b22 = B.flatten()
        C = a11 - a12 - a21 + a22
        D = b11 - b12 - b21 + b22
        if abs(C) < 1e-10 or abs(D) < 1e-10:
            return {
                'is_nondegenerate': False,
                'degenerate_count': 1
            }

    degenerate_supports = []

    # Проверяем подматрицы размера >= 2
    for k in range(2, min(m, n) + 1):
        for rows in combinations(range(m), k):
            for cols in combinations(range(n), k):
                rows_list = list(rows)
                cols_list = list(cols)

                A_sub = A[np.ix_(rows_list, cols_list)]
                B_sub = B[np.ix_(rows_list, cols_list)]

                det_A = np.linalg.det(A_sub)
                det_B = np.linalg.det(B_sub)

                if abs(det_A) < 1e-10 or abs(det_B) < 1e-10:
                    degenerate_supports.append({
                        'rows': rows_list,
                        'cols': cols_list,
                        'det_A': round(float(det_A), 10),
                        'det_B': round(float(det_B), 10)
                    })

    return {
        'is_nondegenerate': len(degenerate_supports) == 0,
        'degenerate_count': len(degenerate_supports)
    }


def get_game_properties(game: BimatrixGame) -> dict:
    A, B = game.payoff_matrices
    m, n = A.shape

    is_zero_sum = bool(np.allclose(A + B, 0, atol=1e-10))

    is_symmetric = False
    if m == n:
        is_symmetric = bool(np.allclose(A, B.T, atol=1e-10))

    nondegeneracy = check_nondegeneracy(game)

    return {
        'shape': [m, n],
        'is_zero_sum': is_zero_sum,
        'is_symmetric': is_symmetric,
        'is_nondegenerate': nondegeneracy['is_nondegenerate']
    }