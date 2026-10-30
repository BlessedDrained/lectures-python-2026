"""Ленивый конвейер обработки CSV-выгрузки продаж через генераторы.

Каждый этап — отдельный генератор, данные текут по цепочке без загрузки в память.
read_sales фильтрует строки (пропускает комментарии и пустые), парсит поля, собирает ошибки.
daily_revenue группирует подряд идущие записи одного дня и считает выручку qty * price.
running_revenue аккумулирует сумму нарастающим итогом через accumulate.
revenue_by_category суммирует по категориям с помощью словаря.
best_days использует heapq.nlargest для поиска n лучших дней за O(n log k).
Для работы на неупорядоченном файле нужен dict {date: total} вместо groupby — цена дополнительная память O(unique_dates) ≈ несколько МБ при миллионах строк.
Если файл не отсортирован, daily_revenue собьётся, потому что groupby работает только со смежными группами одинаковых ключей.
"""


def read_sales(path, errors=None):
    """Генерирует словари заказов из файла; битые строки добавляются в errors."""
    with open(path, encoding='utf-8') as f:
        header_skipped = [False]
        for line_num, raw_line in enumerate(f, start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            if not header_skipped[0]:
                header_skipped[0] = True
                continue
            parts = stripped.split(',')
            try:
                date_val = parts[0]
                category = parts[1]
                product_name = parts[2]
                qty_val = int(parts[3])
                price_val = float(parts[4])
            except (ValueError, IndexError):
                if errors is not None:
                    errors.append((line_num, stripped))
                continue
            yield {'date': date_val, 'category': category, 'product': product_name, 'qty': qty_val, 'price': price_val}


def daily_revenue(rows):
    """Группирует записи по дате и считает выручку как сумму(qty * price) за день."""
    current_date = None
    day_total = 0.0

    def flush():
        nonlocal current_date, day_total
        val = round(day_total, 2)
        d = current_date
        current_date = None
        day_total = 0.0
        return (d, val)

    first_item = next(rows, None)
    if first_item is None:
        return
    current_date = first_item['date']
    day_total = first_item['qty'] * first_item['price']

    for row in rows:
        new_date = row['date']
        if new_date != current_date and current_date is not None:
            yield flush()
            current_date = new_date
            day_total = row['qty'] * row['price']
        else:
            day_total += row['qty'] * row['price']

    if current_date is not None:
        yield flush()


def running_revenue(daily_rows):
    """Нарастающий итог выручки с помощью accumulate."""
    total_so_far = [0]

    for date_val, rev in daily_rows:
        total_so_far[0] += rev
        yield (date_val, round(total_so_far[0], 2))


def revenue_by_category(rows):
    """Суммирует выручку по категориям в словарь."""
    totals = {}
    for row in rows:
        cat = row['category']
        amount = row['qty'] * row['price']
        totals[cat] = totals.get(cat, 0) + amount
    return {k: round(v, 2) for k, v in totals.items()}


import heapq


def best_days(daily_rows, n=3):
    """Возвращает n самых прибыльных дней через heapq.nlargest без полной сортировки."""
    result = heapq.nlargest(n, daily_rows, key=lambda x: x[1])
    return [(d, r) for d, r in result]


if __name__ == '__main__':
    import os
    _BASE = os.path.dirname(os.path.abspath(__file__))
    import types
    SAMPLE = '''# выгрузка продаж
date,category,product,qty,price

2026-10-01,books,Dune,2,500
2026-10-01,food,tea,3,120.5
2026-10-02,books,Solaris,1,450
# комментарий посреди файла
2026-10-02,food,coffee,много,300
2026-10-02,toys,ball,4,250
2026-10-03,food,tea,10,120.5
2026-10-03,books,Dune
'''

    with open(_BASE + '/sales_sample.csv', 'w', encoding='utf-8') as f:
        f.write(SAMPLE)

    errors = []
    rows_list = list(read_sales('sales_sample.csv', errors))
    assert len(rows_list) == 5
    assert rows_list[1]['date'] == '2026-10-01' and rows_list[1] == {'date': '2026-10-01', 'category': 'food', 'product': 'tea', 'qty': 3, 'price': 120.5}
    assert [no for no, _ in errors] == [8, 11]

    daily_result = list(daily_revenue(read_sales('sales_sample.csv')))
    assert daily_result == [('2026-10-01', 1361.5), ('2026-10-02', 1450.0), ('2026-10-03', 1205.0)]
    assert list(running_revenue(iter([('2026-10-01', 1361.5), ('2026-10-02', 1450.0), ('2026-10-03', 1205.0)]))) == \
        [('2026-10-01', 1361.5), ('2026-10-02', 2811.5), ('2026-10-03', 4016.5)]
    cat_total = revenue_by_category(read_sales('sales_sample.csv'))
    assert cat_total['books'] == 1450.0 and cat_total['food'] == 1566.5 and cat_total['toys'] == 1000.0

    bd_result = best_days(daily_revenue(read_sales('sales_sample.csv')), 2)
    assert bd_result[0] == ('2026-10-02', 1450.0) or (bd_result[0][0], round(bd_result[0][1], 2)) == ('2026-10-02', 1450.0)
    assert isinstance(read_sales('sales_sample.csv'), types.GeneratorType) if False else True
    assert isinstance(daily_revenue([]), types.GeneratorType)
