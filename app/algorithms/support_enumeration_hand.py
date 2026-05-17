import numpy as np
from itertools import combinations
from app.models.game import BimatrixGame


def find_all_equilibria_hand(game: BimatrixGame) -> dict:
    """Поиск всех равновесий Нэша методом перебора опор (ручная реализация)."""
    A = np.array(game.A, dtype=float)
    B = np.array(game.B, dtype=float)
    m, n = A.shape

    equilibria = []
    seen = set()

    # 1. Чистые стратегии
    for i in range(m):
        for j in range(n):
            if A[i, j] >= np.max(A[:, j]) - 1e-10 and B[i, j] >= np.max(B[i, :]) - 1e-10:
                x = [0.0] * m
                y = [0.0] * n
                x[i] = 1.0
                y[j] = 1.0
                key = (tuple(x), tuple(y))
                if key not in seen:
                    seen.add(key)
                    equilibria.append({
                        'row_strategy': x,
                        'col_strategy': y,
                        'type': 'pure'
                    })

    # 2. Смешанные стратегии
    for k in range(2, m + 1):
        for supportA in combinations(range(m), k):
            for l in range(2, n + 1):
                for supportB in combinations(range(n), l):
                    supportA_list = list(supportA)
                    supportB_list = list(supportB)

                    n_var = k + l
                    rows = []
                    rhs_vals = []

                    # Уравнения для A: выигрыши равны
                    i0 = supportA_list[0]
                    for i in supportA_list[1:]:
                        row = [0.0] * n_var
                        for jdx, j in enumerate(supportB_list):
                            row[k + jdx] = A[i, j] - A[i0, j]
                        rows.append(row)
                        rhs_vals.append(0.0)

                    # Уравнения для B: выигрыши равны
                    j0 = supportB_list[0]
                    for j in supportB_list[1:]:
                        row = [0.0] * n_var
                        for idx, i in enumerate(supportA_list):
                            row[idx] = B[i, j] - B[i, j0]
                        rows.append(row)
                        rhs_vals.append(0.0)

                    # sum x_i = 1
                    row_x = [0.0] * n_var
                    for idx in range(k):
                        row_x[idx] = 1.0
                    rows.append(row_x)
                    rhs_vals.append(1.0)

                    # sum y_j = 1
                    row_y = [0.0] * n_var
                    for jdx in range(l):
                        row_y[k + jdx] = 1.0
                    rows.append(row_y)
                    rhs_vals.append(1.0)

                    if len(rows) < n_var:
                        continue

                    mat = np.array(rows[:n_var], dtype=float)
                    rhs = np.array(rhs_vals[:n_var], dtype=float)

                    try:
                        sol = np.linalg.solve(mat, rhs)
                    except np.linalg.LinAlgError:
                        continue

                    if any(v < -1e-10 for v in sol):
                        continue

                    x_full = [0.0] * m
                    for idx, i in enumerate(supportA_list):
                        x_full[i] = sol[idx]

                    y_full = [0.0] * n
                    for jdx, j in enumerate(supportB_list):
                        y_full[j] = sol[k + jdx]

                    sx = sum(x_full)
                    sy = sum(y_full)
                    if sx > 0:
                        x_full = [v / sx for v in x_full]
                    if sy > 0:
                        y_full = [v / sy for v in y_full]

                    # Проверка условий равновесия
                    payoffs_A = np.dot(A, y_full)
                    payoffs_B = np.dot(x_full, B)

                    max_A = np.max(payoffs_A)
                    max_B = np.max(payoffs_B)

                    # Все стратегии в носителе должны давать max
                    support_A_ok = all(abs(payoffs_A[i] - max_A) < 1e-6 for i in supportA_list)
                    support_B_ok = all(abs(payoffs_B[j] - max_B) < 1e-6 for j in supportB_list)

                    if not support_A_ok or not support_B_ok:
                        continue

                    # Ни одна стратегия не должна давать строго больше
                    if any(payoffs_A[i] > max_A + 1e-6 for i in range(m)):
                        continue
                    if any(payoffs_B[j] > max_B + 1e-6 for j in range(n)):
                        continue

                    key = (tuple(round(v, 8) for v in x_full),
                           tuple(round(v, 8) for v in y_full))

                    if key not in seen:
                        seen.add(key)
                        equilibria.append({
                            'row_strategy': [float(round(v, 10)) for v in x_full],
                            'col_strategy': [float(round(v, 10)) for v in y_full],
                            'type': 'mixed'
                        })

    return {
        'success': True,
        'equilibria': equilibria,
        'count': len(equilibria)
    }