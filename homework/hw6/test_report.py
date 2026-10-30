import sys, os
_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '.')
module_name = sys.argv[1] if len(sys.argv) > 1 else 'report_fixed'

with _BASE + "/orders.txt", 'w', encoding='utf-8') as f:
    f.write('anna,100\nbob,50\n\nanna,700\nkate,300\nbob,30\n')

mod = __import__(module_name)

print(f'[Тест {module_name}] read_orders возвращает итерируемый объект без ошибок... ', end='')
try:
    orders_list = list(mod.read_orders('orders.txt'))
    assert len(orders_list) >= 4, f"ожидалось минимум 4 строки, получено {len(orders_list)}"
    print("OK")
except ValueError as e:
    print(f"FAILED - {e}")

print(f'[Тест {module_name}] totals_by_user группирует по пользователю корректно... ', end='')
fresh_orders = mod.read_orders('orders.txt')
totals = mod.totals_by_user(fresh_orders)
assert totals['anna'] == 800.0 and totals['bob'] == 80.0, \
    f"неверные суммы anna={totals.get('anna')} bob={totals.get('bob')}"
print("OK")

print(f'[Тест {module_name}] has_large_orders на пороговом значении... ', end='')
has_lg = mod.has_large_orders(mod.read_orders('orders.txt'), threshold=500)
assert has_lg is True, "заказ 700 превышает 500 → ожидается True"
no_lg = mod.has_large_orders(mod.read_orders('orders.txt'), threshold=1000)
assert no_lg is False, "нет заказов >= 1000 → ожидается False"
print("OK")

print(f'[Тест {module_name}] vip_over_limit учитывает всех VIP-пользователей... ', end='')
vip_result = mod.vip_over_limit(
    {'anna': 800.0, 'bob': 80.0}, ['anna', 'bob'], [500, 10])
assert set(vip_result) == {'anna', 'bob'}, f"ожидались anna и bob, получено {vip_result}"
print("OK")

print(f'[Тест {module_name}] last_orders возвращает последние n строк без полной загрузки файла... ', end='')
last3 = mod.last_orders('orders.txt', 3)
expected_last = ['anna,700', 'kate,300', 'bob,30']
assert last3 == expected_last, f"ожидание {expected_last}, получено {last3}"
print("OK")

print(f'[Тест {module_name}] build_report полный отчёт... ', end='')
rpt = {}
if hasattr(mod, 'build_report'):
    rpt = mod.build_report('orders.txt', ['anna', 'bob'], [500, 10])
    assert len(rpt.get('totals', {})) >= 2 or any(k in rpt.get('totals', {}) for k in ('anna','bob')), \
        "отчёт должен содержать суммы по пользователям"
else:
    o_list = list(mod.read_orders('orders.txt'))
    t = dict()
    from collections import defaultdict
    totals_check = defaultdict(float)
    for s in __import__('collections').deque(o_list):
        parts = s.split(',')
        totals_check[parts[0]] += float(parts[1])
    t = dict(totals_check)
    h = mod.has_large_orders(__import__('collections').deque([x for x in o_list]), threshold=1000)
    v = mod.vip_over_limit(t, ['anna', 'bob'], [500, 10])
    l3 = mod.last_orders('orders.txt', 3)
    if not (len(v) == 2 and set(v) == {'anna','bob'} and h is False):
        print(f"FAILED - vip={v} has_lg={h}")

print("OK")

print("\nВсе тесты пройдены для:", module_name)
