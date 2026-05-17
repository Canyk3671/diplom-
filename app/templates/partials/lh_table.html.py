{# partials/lh_table.html — рендер одной таблицы из пошагового вывода ЛХ    #}
{# Ожидает переменную tbl (или table при вызове через with):                  #}
{#   col_labels, row_labels, rows, bottom, bottom_label, lambda_col, lambda_src #}
{% set t = tbl if tbl is defined else table %}
{% if t %}
<div class="lh-table-wrap">
    <table class="lh-table">
        <thead>
            <tr>
                <th class="lh-th-lbl"></th>
                {% for cl in t.col_labels %}<th>{{ cl }}</th>{% endfor %}
                {% if t.lambda_col %}<th class="lh-th-lam">λ / μ</th>{% endif %}
            </tr>
        </thead>
        <tbody>
            {% for i in range(t.rows | length) %}
            <tr>
                <td class="lh-td-lbl">{{ t.row_labels[i] }}</td>
                {% for v in t.rows[i] %}<td>{{ v }}</td>{% endfor %}
                {% if t.lambda_col %}
                <td class="lh-td-lam">
                    {{ t.lambda_col[i] }}
                    {% if t.lambda_src %}{{ t.lambda_src[i] }}{% endif %}
                </td>
                {% endif %}
            </tr>
            {% endfor %}
            {% if t.bottom %}
            <tr class="lh-tr-bot">
                <td class="lh-td-lbl">{{ t.bottom_label }}</td>
                {% for v in t.bottom %}<td>{{ v }}</td>{% endfor %}
                {% if t.lambda_col %}<td></td>{% endif %}
            </tr>
            {% endif %}
        </tbody>
    </table>
</div>
{% endif %}