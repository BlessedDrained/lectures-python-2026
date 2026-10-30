from itertools import groupby


def read_orders(path):
    """Лениво читает заказы из файла: на каждой строке user,amount."""
    with open(path, encoding='utf-8') as f:
        return (line.strip().split(',') for line in f if line.strip())


def totals_by_user(orders):
    """Сумма заказов по каждому пользователю."""
    result = {}
    for user, group in groupby(orders, key=lambda o: o[0]):
        result[user] = sum(float(amount) for _, amount in group)
    return result


def has_large_orders(orders, threshold=1000):
    """Есть ли хотя бы один заказ дороже threshold."""
    large = (o for o in orders if float(o[1]) > threshold)
    return bool(large)


def vip_over_limit(totals, vip_users, vip_limits):
    """VIP-клиенты, превысивший свой лимит."""
    return [u for u, limit in zip(vip_users, vip_limits) if totals.get(u, 0) > limit]


def last_orders(path, n=5):
    """Последние n строк файла заказов."""
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    return [line.strip() for line in lines[-n:]]


def build_report(path, vip_users, vip_limits):
    orders = read_orders(path)
    count = sum(1 for _ in orders)
    totals = totals_by_user(orders)
    return {
        'orders': count,
        'totals': totals,
        'has_large': has_large_orders(orders),
        'vip_over_limit': vip_over_limit(totals, vip_users, vip_limits),
        'last': last_orders(path, 3),
    }
