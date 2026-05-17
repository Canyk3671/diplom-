"""
Ручная реализация алгоритма Лемке–Хоусона по учебнику Колобашкиной (раздел 3.4).
Адаптирована для интеграции в веб-приложение: возвращает пошаговые данные
в виде сериализуемых структур для рендера в Jinja2-шаблоне.

Обозначения (как в учебнике):
  x  — стратегия столбцового игрока B (n компонент)
  y  — стратегия строчного игрока A   (m компонент, первые m из n)
  A*0 = [A1^T | In]  —  n строк × (m+n) столбцов
  B*0 = [B1   | Im]  —  m строк × (n+m) столбцов
  x0[i*-1] = 1/b,   y0[0] = 1/a  — оба вектора длины n
"""

from fractions import Fraction as F
from app.models.game import BimatrixGame


# ─────────────────────────── Вспомогательные функции ────────────────────────

def _f(x) -> F:
    return F(x).limit_denominator(100000) if not isinstance(x, F) else x

def _fstr(x) -> str:
    f = _f(x)
    return str(f.numerator) if f.denominator == 1 else str(f)

def _pivot(tbl, pr, pc):
    """Одно симплекс-преобразование таблицы."""
    nr, nc = len(tbl), len(tbl[0])
    pv = tbl[pr][pc]
    if pv == 0:
        raise ValueError(f"Разрешающий элемент = 0 (стр.{pr+1}, ст.{pc+1})")
    new = [[F(0)] * nc for _ in range(nr)]
    for j in range(nc):
        new[pr][j] = _f(tbl[pr][j]) / pv
    for i in range(nr):
        if i == pr:
            continue
        fac = tbl[i][pc]
        for j in range(nc):
            new[i][j] = _f(tbl[i][j]) - fac * new[pr][j]
    return new

def _compute_lam_mu(row, num_main, num_base, bot_main, bot_base):
    """
    Вычисляет λⱼ или μᵢ для одной строки таблицы.
    Правило: ratio = -числитель/знаменатель, берём ТОЛЬКО ratio > 0.
    Возвращает (значение, метка-источник, кандидаты_star, кандидаты_dstar).
    """
    a_part = row[:num_main]
    q_part = row[num_main:]
    cand_star, cand_dstar = [], []

    for k in range(num_main):
        if a_part[k] == 0 or bot_main[k] == 0:
            continue
        ratio = -bot_main[k] / a_part[k]
        if ratio <= 0:
            continue
        (cand_star if a_part[k] < 0 else cand_dstar).append(ratio)

    for r in range(num_base):
        if q_part[r] == 0 or bot_base[r] == 0:
            continue
        ratio = -bot_base[r] / q_part[r]
        if ratio <= 0:
            continue
        (cand_star if q_part[r] < 0 else cand_dstar).append(ratio)

    ls = min(cand_star)  if cand_star  else F(0)
    ld = max(cand_dstar) if cand_dstar else F(0)

    # Источник (метка столбца, давшего min/max)
    def find_src(target, part_a, part_b, main_lbls, base_lbls, sign):
        for k in range(num_main):
            if part_a[k] == 0 or bot_main[k] == 0:
                continue
            ratio = -bot_main[k] / part_a[k]
            if ratio == target and ((sign < 0 and part_a[k] < 0) or (sign > 0 and part_a[k] > 0)):
                return main_lbls[k]
        for r in range(num_base):
            if part_b[r] == 0 or bot_base[r] == 0:
                continue
            ratio = -bot_base[r] / part_b[r]
            if ratio == target and ((sign < 0 and part_b[r] < 0) or (sign > 0 and part_b[r] > 0)):
                return base_lbls[r]
        return ""

    val = ls if ls != 0 else ld
    return val, cand_star, cand_dstar

def _check_eq(q_y, p_x, m, n):
    """Проверка условий равновесия (Способ В)."""
    all_lbl = q_y + p_x
    af = {int(l[1:]) for l in all_lbl if l[0] in "af"}
    be = {int(l[1:]) for l in all_lbl if l[0] in "be"}
    return (af == set(range(1, m + 1))) and (be == set(range(1, n + 1)) and len(be) == n)

def _table_to_str(rows, row_lbls, col_lbls, bottom=None, bot_lbl="",
                  lam=None, lam_src=None):
    """Сериализует таблицу в dict для шаблона."""
    return {
        "col_labels": col_lbls,
        "row_labels": row_lbls,
        "rows": [[_fstr(v) for v in row] for row in rows],
        "bottom": [_fstr(v) for v in bottom] if bottom is not None else None,
        "bottom_label": bot_lbl,
        "lambda_col": [_fstr(v) for v in lam] if lam is not None else None,
        "lambda_src": lam_src,
    }


# ─────────────────────────── Главная функция ────────────────────────────────

def lemke_howson_hand(game: BimatrixGame) -> dict:
    """
    Ручная реализация алгоритма Лемке–Хоусона по Колобашкиной.

    Возвращает dict:
      success    : bool
      equilibrium: {"row_strategy": [...], "col_strategy": [...]}
      HA, HB     : float — цены игры
      steps      : list[dict] — пошаговые данные для шаблона
      error      : str (при success=False)
    """
    A_raw, B_raw = game.A.tolist(), game.B.tolist()
    A = [[_f(v) for v in row] for row in A_raw]
    B = [[_f(v) for v in row] for row in B_raw]
    m, n = len(A), len(A[0])

    steps = []  # пошаговые блоки для шаблона

    def add_step(phase, title, text="", tables=None, formula=""):
        steps.append({
            "phase": phase,
            "title": title,
            "text": text,
            "tables": tables or [],
            "formula": formula,
        })

    # ── БЛОК I: A¹, B¹ ───────────────────────────────────────────────────
    all_vals = [A[i][j] for i in range(m) for j in range(n)] + \
               [B[i][j] for i in range(m) for j in range(n)]
    d = int(max(all_vals)) + 1
    A1 = [[_f(d) - A[i][j] for j in range(n)] for i in range(m)]
    B1 = [[_f(d) - B[i][j] for j in range(n)] for i in range(m)]

    col_n = [f"B{j+1}" for j in range(n)]
    row_m = [f"A{i+1}" for i in range(m)]
    add_step("I", "Вычисление матриц A¹ и B¹",
             f"d = max(aᵢⱼ, bᵢⱼ) + 1 = {int(max(all_vals))} + 1 = {d}; "
             f"A¹ = d·E − A;  B¹ = d·E − B",
             tables=[
                 _table_to_str(A1, row_m, col_n),
                 _table_to_str(B1, row_m, col_n),
             ],
             formula=f"d = {d}")

    # Метки
    a_lbl = [f"a{i+1}" for i in range(m)]
    e_lbl = [f"e{j+1}" for j in range(n)]
    b_lbl = [f"b{j+1}" for j in range(n)]
    f_lbl = [f"f{i+1}" for i in range(m)]

    result = None

    for it in range(m):
        iter_steps = []

        # ── A*0 = [A1^T | In] ────────────────────────────────────────────
        A1T  = [[A1[i][k] for i in range(m)] for k in range(n)]
        In   = [[_f(1) if r == c else _f(0) for c in range(n)] for r in range(n)]
        A0   = [A1T[k] + In[k] for k in range(n)]
        col_A0  = a_lbl + e_lbl
        basis_A = list(e_lbl)

        # ── y⁰: min в it-м столбце A¹, 1/a на позиции 0 ─────────────────
        col_A1_it = [A1[i][it] for i in range(m)]
        a_min  = min(col_A1_it)
        i_star = col_A1_it.index(a_min)
        y0 = [_f(0)] * n
        y0[0] = _f(1) / a_min

        # ── B*0 = [B1 | Im] ──────────────────────────────────────────────
        Im   = [[_f(1) if r == c else _f(0) for c in range(m)] for r in range(m)]
        B0   = [B1[i] + Im[i] for i in range(m)]
        col_B0  = b_lbl + f_lbl
        basis_B = list(f_lbl)

        # ── x⁰: min в i*-й строке B¹, 1/b на позиции i* ─────────────────
        row_istar = B1[i_star]
        b_min  = min(row_istar)
        j_star = row_istar.index(b_min)
        x0 = [_f(0)] * n
        x0[i_star] = _f(1) / b_min

        iter_steps.append({
            "title": f"Шаг 3–6. Таблицы A*₀ и B*₀, начальные x⁰ и y⁰",
            "text": (
                f"Столбец {it+1} матрицы A¹: [{', '.join(_fstr(v) for v in col_A1_it)}]  "
                f"→  a = {_fstr(a_min)},  i* = {i_star+1}\n"
                f"y⁰ = [{', '.join(_fstr(v) for v in y0)}]  (1/a на первой позиции)\n\n"
                f"Строка i*={i_star+1} матрицы B¹: [{', '.join(_fstr(v) for v in row_istar)}]  "
                f"→  b = {_fstr(b_min)},  j* = {j_star+1}\n"
                f"x⁰ = [{', '.join(_fstr(v) for v in x0)}]  (1/b на позиции i*={i_star+1})"
            ),
            "tables": [
                _table_to_str(A0, list(basis_A), col_A0),
                _table_to_str(B0, list(basis_B), col_B0),
            ],
        })

        # ── Шаг 7: начальная проверка равновесия ─────────────────────────
        q_y0 = list(basis_A)
        q_y0[0] = f"a{i_star+1}"
        p_x0 = list(basis_B)
        p_x0[i_star] = f"b{j_star+1}"

        eq0 = _check_eq(q_y0, p_x0, m, n)
        iter_steps.append({
            "title": "Шаг 7. Проверка начального (x⁰, y⁰) на равновесие (Способ В)",
            "text": (
                f"A*₀: выводим e1 → вводим a{i_star+1}  ⟹  q(y⁰) = ({', '.join(q_y0)})\n"
                f"B*₀: выводим f{i_star+1} → вводим b{j_star+1}  ⟹  p(x⁰) = ({', '.join(p_x0)})\n"
                f"{'✓ Начальная пара уже является равновесием!' if eq0 else '✗ Не равновесие → переходим к замене базисов'}"
            ),
            "tables": [],
        })

        if eq0:
            x_til, y_til = list(x0), list(y0)
        else:
            # ── Шаг 8: A*0 → A*1 ─────────────────────────────────────────
            prow_A, pcol_A = 0, i_star
            A1t = _pivot(A0, prow_A, pcol_A)
            bas_A1 = list(q_y0)

            # ── Шаг 9: xᵢ = столбец i(A*0) · y⁰ ────────────────────────
            x_vals = [sum(A0[r][i] * y0[r] for r in range(n)) for i in range(m)]
            x_m1   = [xi - _f(1) for xi in x_vals]
            bot_A1 = x_m1 + list(y0)

            x_calc_text = "\n".join(
                f"x{i+1} = [{', '.join(_fstr(A0[r][i]) for r in range(n))}] · "
                f"[{', '.join(_fstr(v) for v in y0)}] = {_fstr(x_vals[i])}"
                for i in range(m)
            )

            # ── Шаг 10: λⱼ ───────────────────────────────────────────────
            lam_vals, lam_src_list = [], []
            lam_details = []
            for j in range(n):
                val, cs, cd = _compute_lam_mu(A1t[j], m, n, x_m1, y0)
                # определяем источник
                src = ""
                target_val = min(cs) if cs else (max(cd) if cd else _f(0))
                # ищем источник по совпадению ratio
                row = A1t[j]
                a_part, q_part = row[:m], row[m:]
                for k in range(m):
                    if a_part[k] == 0 or x_m1[k] == 0: continue
                    ratio = -x_m1[k] / a_part[k]
                    if ratio == target_val and ratio > 0:
                        src = a_lbl[k]; break
                if not src:
                    for r in range(n):
                        if q_part[r] == 0 or y0[r] == 0: continue
                        ratio = -y0[r] / q_part[r]
                        if ratio == target_val and ratio > 0:
                            src = e_lbl[r]; break
                lam_vals.append(val)
                lam_src_list.append(f"({src})" if src else "")
                lam_details.append(
                    f"j={j+1}: λ*={_fstr(min(cs)) if cs else '0'}, "
                    f"λ**={_fstr(max(cd)) if cd else '0'}  → λ{j+1}={_fstr(val)} [{src}]"
                )

            iter_steps.append({
                "title": "Шаги 8–10. A*₀ → A*₁, вычисление xᵢ и λⱼ",
                "text": (
                    f"Разрешающий элемент: строка 1, столбец a{i_star+1} = {_fstr(A0[prow_A][pcol_A])}\n\n"
                    f"xᵢ = (столбец aᵢ в A*₀) · y⁰:\n{x_calc_text}\n"
                    f"(xᵢ−1) = [{', '.join(_fstr(v) for v in x_m1)}]\n\n"
                    f"λⱼ (только ratio > 0):\n" + "\n".join(lam_details)
                ),
                "tables": [
                    _table_to_str(A1t, bas_A1, col_A0,
                                  bottom=bot_A1, bot_lbl="xᵢ−1|y⁰",
                                  lam=lam_vals, lam_src=lam_src_list),
                ],
            })

            # ── Шаг 11: B*0 → B*1, μᵢ ───────────────────────────────────
            prow_B, pcol_B = i_star, j_star
            B1t = _pivot(B0, prow_B, pcol_B)
            bas_B1 = list(p_x0)

            h_vals = [sum(B0[k][j] * x0[k] for k in range(m)) for j in range(n)]
            h_m1   = [hj - _f(1) for hj in h_vals]
            x0_m   = x0[:m]
            bot_B1 = h_m1 + list(x0_m)

            mu_vals, mu_src_list = [], []
            mu_details = []
            for i in range(m):
                val, cs, cd = _compute_lam_mu(B1t[i], n, m, h_m1, x0_m)
                src = ""
                target_val = min(cs) if cs else (max(cd) if cd else _f(0))
                row = B1t[i]
                b_part, p_part = row[:n], row[n:]
                for k in range(n):
                    if b_part[k] == 0 or h_m1[k] == 0: continue
                    ratio = -h_m1[k] / b_part[k]
                    if ratio == target_val and ratio > 0:
                        src = b_lbl[k]; break
                if not src:
                    for s in range(m):
                        if p_part[s] == 0 or x0_m[s] == 0: continue
                        ratio = -x0_m[s] / p_part[s]
                        if ratio == target_val and ratio > 0:
                            src = f_lbl[s]; break
                mu_vals.append(val)
                mu_src_list.append(f"({src})" if src else "")
                mu_details.append(
                    f"i={i+1}: μ*={_fstr(min(cs)) if cs else '0'}, "
                    f"μ**={_fstr(max(cd)) if cd else '0'}  → μ{i+1}={_fstr(val)} [{src}]"
                )

            h_calc_text = "\n".join(
                f"h{j+1} = [{', '.join(_fstr(B0[k][j]) for k in range(m))}] · "
                f"[{', '.join(_fstr(v) for v in x0_m)}] = {_fstr(h_vals[j])}"
                for j in range(n)
            )

            iter_steps.append({
                "title": "Шаг 11. B*₀ → B*₁, вычисление hⱼ и μᵢ",
                "text": (
                    f"Разрешающий элемент: строка {i_star+1}, столбец b{j_star+1} = {_fstr(B0[prow_B][pcol_B])}\n\n"
                    f"hⱼ = (столбец j в B*₀) · x⁰[:m]:\n{h_calc_text}\n"
                    f"(hⱼ−1) = [{', '.join(_fstr(v) for v in h_m1)}]\n\n"
                    f"μᵢ (только ratio > 0):\n" + "\n".join(mu_details)
                ),
                "tables": [
                    _table_to_str(B1t, bas_B1, col_B0,
                                  bottom=bot_B1, bot_lbl="hⱼ−1|x⁰",
                                  lam=mu_vals, lam_src=mu_src_list),
                ],
            })

            # ── Шаги 12–14: кандидаты и проверка равновесия ──────────────
            Q = [A1t[j][m:] for j in range(n)]
            P = [B1t[i][n:] for i in range(m)]

            x_cands = []
            for i in range(m):
                pi_n = [P[i][k] if k < m else _f(0) for k in range(n)]
                xi = [x0[k] + mu_vals[i] * pi_n[k] for k in range(n)]
                x_cands.append(xi)

            y_cands = []
            for j in range(n):
                yj = [y0[r] + lam_vals[j] * Q[j][r] for r in range(n)]
                y_cands.append(yj)

            cands_text = (
                "\n".join(
                    f"x̃{i+1} = x⁰ + {_fstr(mu_vals[i])} · p{i+1} = "
                    f"[{', '.join(_fstr(v) for v in x_cands[i])}]"
                    for i in range(m)
                ) + "\n" +
                "\n".join(
                    f"ỹ{j+1} = y⁰ + {_fstr(lam_vals[j])} · q{j+1} = "
                    f"[{', '.join(_fstr(v) for v in y_cands[j])}]"
                    for j in range(n)
                )
            )

            found = False
            eq_check_lines = []
            for i in range(m):
                for j in range(n):
                    q_yj = list(q_y0)
                    if lam_vals[j] != 0 and lam_src_list[j]:
                        src_lbl = lam_src_list[j].strip("()")
                        out = bas_A1[j]
                        if out in q_yj:
                            q_yj[q_yj.index(out)] = src_lbl

                    p_xi = list(p_x0)
                    if mu_vals[i] != 0 and mu_src_list[i]:
                        src_lbl = mu_src_list[i].strip("()")
                        out = bas_B1[i]
                        if out in p_xi:
                            p_xi[p_xi.index(out)] = src_lbl

                    ok = _check_eq(q_yj, p_xi, m, n)
                    all_lbl = q_yj + p_xi
                    af = sorted({int(l[1:]) for l in all_lbl if l[0] in "af"})
                    be = sorted({int(l[1:]) for l in all_lbl if l[0] in "be"})
                    eq_check_lines.append(
                        f"(x̃{i+1}, ỹ{j+1}): q(y)=({', '.join(q_yj)})  p(x)=({', '.join(p_xi)})  "
                        f"(a,f)={af}→1..{m}:{'✓' if af==list(range(1,m+1)) else '✗'}  "
                        f"(b,e)={be}→1..{n}:{'✓' if be==list(range(1,n+1)) and len(be)==n else '✗'}  "
                        f"{'⟹ РАВНОВЕСИЕ!' if ok else ''}"
                    )
                    if ok:
                        x_til = x_cands[i]
                        y_til = y_cands[j]
                        found = True
                        break
                if found:
                    break

            iter_steps.append({
                "title": "Шаги 12–14. Кандидаты на равновесие и проверка",
                "text": cands_text + "\n\nПроверка пар:\n" + "\n".join(eq_check_lines),
                "tables": [],
            })

            if not found:
                steps.append({
                    "phase": f"Итерация {it+1}",
                    "title": f"Итерация {it+1}: равновесие не найдено",
                    "text": "Переходим к следующей строке матрицы A¹ᵀ.",
                    "tables": [],
                    "sub_steps": iter_steps,
                })
                continue

        # ── Шаг 15: нормировка ───────────────────────────────────────────
        sum_x = sum(x_til)
        sum_y = sum(y_til)
        if sum_x == 0 or sum_y == 0:
            continue

        x_star_frac = [v / sum_x for v in x_til]
        y_star_frac = [v / sum_y for v in y_til]
        HB = _f(d) - _f(1) / sum_x
        HA = _f(d) - _f(1) / sum_y

        norm_text = (
            f"x̃ = [{', '.join(_fstr(v) for v in x_til)}]  →  Σx̃ = {_fstr(sum_x)}\n"
            f"ỹ = [{', '.join(_fstr(v) for v in y_til)}]  →  Σỹ = {_fstr(sum_y)}\n\n"
            f"x* = [{', '.join(_fstr(v) for v in x_star_frac)}]\n"
            f"y* = [{', '.join(_fstr(v) for v in y_star_frac[:m])}]\n\n"
            f"H_B = {d} − 1/{_fstr(sum_x)} = {_fstr(HB)}  ≈ {float(HB):.6f}\n"
            f"H_A = {d} − 1/{_fstr(sum_y)} = {_fstr(HA)}  ≈ {float(HA):.6f}"
        )

        iter_steps.append({
            "title": "Шаг 15. Нормировка → x*, y*, цены игры H_A, H_B",
            "text": norm_text,
            "tables": [],
        })

        steps.append({
            "phase": f"Итерация {it+1}",
            "title": f"Итерация {it+1} (столбец {it+1} матрицы A¹)",
            "text": "",
            "tables": [],
            "sub_steps": iter_steps,
        })

        # В обозначениях Колобашкиной (нестандартных!):
        #   x_til — стратегия строчного игрока A (n компонент, первые m значимы)
        #   y_til — стратегия столбцового игрока B (n компонент)
        # В формате проекта:
        #   row_strategy = стратегия A (строчного) = x_star_frac[:m]
        #   col_strategy = стратегия B (столбцового) = y_star_frac (n компонент)
        row_strategy = [float(v) for v in x_star_frac[:m]]   # игрок A
        col_strategy = [float(v) for v in y_star_frac]       # игрок B

        result = {
            "success": True,
            "equilibrium": {
                "row_strategy": row_strategy,
                "col_strategy": col_strategy,
            },
            "HA": float(HA),
            "HB": float(HB),
            "HA_str": _fstr(HA),
            "HB_str": _fstr(HB),
            "d": d,
            "iteration": it + 1,
            "steps": steps,
            "row_strategy_str": [_fstr(v) for v in x_star_frac[:m]],
            "col_strategy_str": [_fstr(v) for v in y_star_frac],
        }
        break

    if result is None:
        return {
            "success": False,
            "error": "Алгоритм не нашёл равновесия (возможно вырожденная игра).",
            "steps": steps,
        }

    return result