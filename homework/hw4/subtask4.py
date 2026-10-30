import functools


def memoize(func):
    """Декоратор с кэшированием результатов через замыкание."""
    cache = {}
    h = [0]
    m = [0]

    def make_key(args, kwds):
        key = args
        if kwds:
            key += (object(),) + tuple(sorted(kwds.items()))
        return key

    class MemoWrapper:
        @property
        def hits(self_):
            return h[0]

        @property
        def misses(self_):
            return m[0]

        def cache_clear(self_):
            nonlocal cache
            cache.clear()
            h[0] = 0
            m[0] = 0

        def __call__(self_, *args, **kwargs):
            key = make_key(args, kwargs)
            try:
                hash(key)
            except TypeError:
                return func(*args, **kwargs)
            if key in cache:
                h[0] += 1
                return cache[key]
            result = func(*args, **kwargs)
            m[0] += 1
            try:
                cache[key] = result
            except TypeError:
                pass
            return result

    wrapped = MemoWrapper()
    functools.update_wrapper(wrapped, func)

    return wrapped


if __name__ == '__main__':
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)
    assert sq(3) == 9 and sq(3) == 9 and sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square' and sq.__doc__ == 'Возводит в степень.'
    total = memoize(sum)
    assert total([1, 2, 3]) == 6 and total([1, 2, 3]) == 6
    assert (total.hits, total.misses) == (0, 0)
    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3
