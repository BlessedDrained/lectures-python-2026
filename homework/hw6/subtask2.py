"""Класс DateRange реализует протокол контейнера и итератора для дат, аналогично range() для чисел.

Отличие от варианта с __iter__, возвращающим self: здесь __iter__ создаёт новый объект-итератор при каждом вызове, что позволяет безопасно перебирать один и тот же диапазон несколько раз (вложенные циклы). Если бы __iter__ возвращал self, внутренний счётчик сбрасывался бы только вручную, а вложенный цикл по тому же объекту выдавал бы пустой результат после первой итерации.
"""


from datetime import date, timedelta


class DateRange:
    """Протокол итерации + протокол контейнера для последовательности дат."""

    def __init__(self, start, stop, step=1):
        if not isinstance(step, int) or step <= 0:
            raise ValueError('step must be a positive integer')
        self._start = start
        self._stop = stop
        self._step = step

    class _Iterator:
        def __init__(self, start, stop, step):
            self.current = start
            self.stop = stop
            self.step = step

        def __next__(self):
            if self.current >= self.stop:
                raise StopIteration
            val = self.current
            self.current += timedelta(days=self.step)
            return val

    def __iter__(self):
        return self._Iterator(self._start, self._stop, self._step)

    def __len__(self):
        diff = (self._stop - self._start).days
        if diff <= 0:
            return 0
        return (diff + self._step - 1) // self._step

    def __getitem__(self, index):
        length = len(self)
        if length == 0:
            raise IndexError('DateRange index out of range')
        if isinstance(index, slice):
            return self[index]
        effective_index = index if index >= 0 else length + index
        if effective_index < 0 or effective_index >= length:
            raise IndexError('DateRange index out of range')
        offset_days = effective_index * self._step
        result_date = self._start + timedelta(days=offset_days)
        return result_date

    def __contains__(self, item):
        if not isinstance(item, date):
            return False
        day_diff = (item - self._start).days
        if day_diff < 0 or day_diff >= (self._stop - self._start).days:
            return False
        return day_diff % self._step == 0

    def __reversed__(self):
        last_offset = ((len(self) - 1) * self._step) if len(self) > 0 else 0
        current = self._start + timedelta(days=last_offset)
        step_back = timedelta(days=-self._step)
        while True:
            yield current
            next_val = current + step_back
            if next_val < self._start:
                break
            current = next_val

    def __repr__(self):
        return 'DateRange(' + self._start.__repr__() + ', ' + self._stop.__repr__() + ', ' + str(self._step) + ')'

    def __eq__(self, other):
        if type(other) is DateRange:
            return (self._start, self._stop, self._step) == \
                   (other._start, other._stop, other._step)
        return NotImplemented


if __name__ == '__main__':
    from datetime import date as dt

    r = DateRange(dt(2026, 10, 1), dt(2026, 10, 11), 3)
    assert list(r) == [dt(2026, 10, 1), dt(2026, 10, 4), dt(2026, 10, 7), dt(2026, 10, 10)]
    assert list(r) == list(r)
    assert sum(1 for a in r for b in r) == 16
    assert len(r) == 4
    assert len(DateRange(dt(2026, 1, 1), dt(2026, 1, 1))) == 0
    assert len(DateRange(dt(2026, 1, 5), dt(2026, 1, 1))) == 0
    assert r[0] == dt(2026, 10, 1) and r[-1] == dt(2026, 10, 10)
    try:
        r[4]
        assert False, 'ожидали IndexError'
    except IndexError:
        pass
    assert dt(2026, 10, 7) in r
    assert dt(2026, 10, 8) not in r and dt(2026, 10, 13) not in r
    assert list(reversed(r))[0] == dt(2026, 10, 10)

    import datetime
    expected_repr = f'DateRange({datetime.date(2026, 10, 1)!r}, {datetime.date(2026, 10, 11)!r}, 3)'
    actual_repr = repr(r)
    print(f'repr: {actual_repr}')
    print(f'expected: {expected_repr}')

    assert DateRange(dt(2026, 1, 1), dt(2026, 1, 3)) == \
           DateRange(dt(2026, 1, 1), dt(2026, 1, 3))

    big = DateRange(dt(1, 1, 1), dt(9999, 12, 31))
    assert dt(2026, 10, 17) in big and len(big) == 3652058
