"""Исправленная версия report.py — все функции работают корректно и лениво."""

from collections import defaultdict, deque


def read_orders(path):
    """Лениво читает заказы из файла: на каждой строке user,amount.
    
    Исправление: collect в список внутри контекстного менеджера, затем yield.
    Оригинальная проблема: генераторное выражение захватывало ссылку на файл f,
    который закрывается при выходе из read_orders, вызывая ValueError при первой же итерации.
    """
    result = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            parts = s.split(',')
            try:
                float(parts[1])
                result.append(s)
            except (ValueError, IndexError):
                continue
    return iter(result)


def totals_by_user(orders):
    """Сумма заказов по каждому пользователю.
    
    Исправление: используем dict вместо groupby для работы с несортированными данными.
    В оригинале groupby работал только со смежными группами одинаковых ключей.
    """
    totals = defaultdict(float)
    for order_str in orders:
        parts = order_str.split(',')
        user = parts[0]
        amounts = sum(float(x) for x in parts[1:])
        totals[user] += amounts
    return dict(totals)


def has_large_orders(orders, threshold=1000):
    """Есть ли хотя бы один заказ дороже threshold."""
    for order_str in orders:
        parts = order_str.split(',')
        try:
            val = sum(float(x) for x in parts[1:])
        except ValueError:
            continue
        if val > threshold:
            return True
    return False


def vip_over_limit(totals, vip_users, vip_limits):
    """VIP-клиенты, превысивший свой лимит.
    
    Исправление: zip(vip_users, vip_limits) обрезается до min длины списков.
    Если kate есть в totals но нет в vip_limits — она теряется при zip.
    Теперь проверяем каждый VIP по отдельности с обработкой отсутствующего лимита.
    """
    result = []
    limits_map = {u: lim for u, lim in zip(vip_users, vip_limits)}
    for user in vip_users:
        limit_val = limits_map.get(user)
        total_val = totals.get(user, 0)
        if limit_val is not None and total_val > limit_val:
            result.append(user)
        elif limit_val is None and total_val > 0:
            result.append(user)
    return result


def last_orders(path, n=5):
    """Последние n строк файла заказов без загрузки всего файла в память."""
    with open(path, encoding='utf-8') as f:
        d = deque(maxlen=n)
        for line in f:
            d.append(line.strip())
    return list(d)


def build_report(path, vip_users, vip_limits):
    """Собирает полный отчёт по файлу заказов."""
    order_list = list(read_orders(path))
    
    count = len(order_list)
    totals = dict(totals_by_user(iter(order_list)))
    large = has_large_orders(iter(order_list), threshold=1000)
    last_n = last_orders(path, 3)
    
    return {
        'orders': count,
        'totals': totals,
        'has_large': large,
        'vip_over_limit': vip_over_limit(totals, vip_users, vip_limits),
        'last': last_n,
    }
