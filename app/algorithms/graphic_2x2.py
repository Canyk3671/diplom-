import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from fractions import Fraction
from app.models.game import BimatrixGame


def solve_graphic(game: BimatrixGame) -> dict:
    A, B = game.payoff_matrices
    if A.shape != (2, 2):
        return {'success': False, 'error': 'Графический метод только для игр 2×2'}

    a11, a12, a21, a22 = A.flatten()
    b11, b12, b21, b22 = B.flatten()

    # Обозначения из учебника Колобашкиной
    a1 = a11 - a12 - a21 + a22  # C
    a2 = a22 - a12               # alpha
    b1 = b11 - b12 - b21 + b22  # D
    b2 = b22 - b21               # beta

    result = {'success': True, 'pure_equilibria': [], 'mixed_equilibria': []}

    # Чистые равновесия
    for i in range(2):
        for j in range(2):
            if np.isclose(A[i, j], np.max(A[:, j])) and np.isclose(B[i, j], np.max(B[i, :])):
                result['pure_equilibria'].append({
                    'row': i, 'col': j,
                    'payoff_A': float(A[i, j]),
                    'payoff_B': float(B[i, j])
                })

    # Особый случай: a1=0 и b1=0 — весь квадрат
    if abs(a1) < 1e-10 and abs(b1) < 1e-10:
        result['mixed_equilibria'].append({
            'p': 0.5, 'q': 0.5,
            'p_frac': 'любое p ∈ [0,1]', 'q_frac': 'любое q ∈ [0,1]',
            'payoff_A': float(a11*0.25 + a12*0.25 + a21*0.25 + a22*0.25),
            'payoff_B': float(b11*0.25 + b12*0.25 + b21*0.25 + b22*0.25)
        })
        result['is_full_square'] = True

    # Особый случай: a1=0 или b1=0
    elif abs(a1) < 1e-10 or abs(b1) < 1e-10:
        p_test = b2 / b1 if abs(b1) > 1e-10 else 0.5
        q_test = a2 / a1 if abs(a1) > 1e-10 else 0.5
        p_test = np.clip(p_test, 0, 1)
        q_test = np.clip(q_test, 0, 1)
        payoff_A = a11*p_test*q_test + a12*p_test*(1-q_test) + a21*(1-p_test)*q_test + a22*(1-p_test)*(1-q_test)
        payoff_B = b11*p_test*q_test + b12*p_test*(1-q_test) + b21*(1-p_test)*q_test + b22*(1-p_test)*(1-q_test)
        result['mixed_equilibria'].append({
            'p': float(p_test), 'q': float(q_test),
            'p_frac': f"{p_test:.3f}", 'q_frac': f"{q_test:.3f}",
            'payoff_A': float(payoff_A), 'payoff_B': float(payoff_B)
        })

    # Обычный случай: a1≠0 и b1≠0
    if abs(a1) > 1e-10 and abs(b1) > 1e-10:
        p_star = b2 / b1
        q_star = a2 / a1
        if 0 <= p_star <= 1 and 0 <= q_star <= 1:
            payoff_A = a11*p_star*q_star + a12*p_star*(1-q_star) + a21*(1-p_star)*q_star + a22*(1-p_star)*(1-q_star)
            payoff_B = b11*p_star*q_star + b12*p_star*(1-q_star) + b21*(1-p_star)*q_star + b22*(1-p_star)*(1-q_star)
            result['mixed_equilibria'].append({
                'p': float(p_star), 'q': float(q_star),
                'p_frac': f"{p_star:.3f}", 'q_frac': f"{q_star:.3f}",
                'payoff_A': float(payoff_A), 'payoff_B': float(payoff_B)
            })

    result['plot'] = _generate_plot(a1, a2, b1, b2, result)
    return result


def _generate_plot(a1, a2, b1, b2, result):
    """Зигзаги K и L по учебнику Колобашкиной."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel('x (вероятность 1-й стратегии игрока A)')
    ax.set_ylabel('y (вероятность 1-й стратегии игрока B)')
    ax.set_title('Множества K и L')
    ax.grid(True, linestyle='--', alpha=0.3)

    # a = a2 / a1, b = b2 / b1
    a = a2 / a1 if abs(a1) > 1e-10 else 0.5
    b = b2 / b1 if abs(b1) > 1e-10 else 0.5
    a = np.clip(a, 0, 1)
    b = np.clip(b, 0, 1)

    # Множество K (игрок A) — зелёный зигзаг
    if abs(a1) < 1e-10:
        ax.axvline(x=0, color='green', linewidth=2)
        ax.axvline(x=1, color='green', linewidth=2)
    elif a1 > 0:
        # x=0 при y <= a, затем вертикально до x=1 при y >= a
        ax.plot([0, 0], [0, a], 'green', linewidth=2)       # x=0, y ≤ a
        ax.plot([0, 1], [a, a], 'green', linewidth=2)       # 0 < x < 1, y = a
        ax.plot([1, 1], [a, 1], 'green', linewidth=2)       # x=1, y ≥ a
    else:  # a1 < 0
        ax.plot([0, 0], [a, 1], 'green', linewidth=2)       # x=0, y ≥ a
        ax.plot([0, 1], [a, a], 'green', linewidth=2)       # 0 < x < 1, y = a
        ax.plot([1, 1], [0, a], 'green', linewidth=2)       # x=1, y ≤ a

    # Множество L (игрок B) — синий зигзаг
    if abs(b1) < 1e-10:
        ax.axhline(y=0, color='blue', linewidth=2)
        ax.axhline(y=1, color='blue', linewidth=2)
    elif b1 > 0:
        ax.plot([0, b], [0, 0], 'blue', linewidth=2)        # y=0, x ≤ b
        ax.plot([b, b], [0, 1], 'blue', linewidth=2)        # 0 < y < 1, x = b
        ax.plot([b, 1], [1, 1], 'blue', linewidth=2)        # y=1, x ≥ b
    else:  # b1 < 0
        ax.plot([b, 1], [0, 0], 'blue', linewidth=2)        # y=0, x ≥ b
        ax.plot([b, b], [0, 1], 'blue', linewidth=2)        # 0 < y < 1, x = b
        ax.plot([0, b], [1, 1], 'blue', linewidth=2)        # y=1, x ≤ b

    # Точки равновесий (пересечения K и L)
    equilibria_points = []
    for eq in result['pure_equilibria']:
        equilibria_points.append((eq['row'], eq['col']))
    for eq in result['mixed_equilibria']:
        if not result.get('is_full_square'):
            equilibria_points.append((eq['p'], eq['q']))

    for pt in equilibria_points:
        ax.plot(pt[0], pt[1], 'o', markersize=10, markerfacecolor='red',
                markeredgecolor='black')

    # Особый случай — весь квадрат
    if result.get('is_full_square'):
        ax.fill_between([0, 1], 0, 1, alpha=0.15, color='red')
        ax.plot(0.5, 0.5, 'X', markersize=12, markerfacecolor='red', markeredgecolor='black')

    # Легенда
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='green', linewidth=2, label='K (игрок A)'),
        Line2D([0], [0], color='blue', linewidth=2, label='L (игрок B)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red',
               markeredgecolor='black', markersize=10, label='Равновесие')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64