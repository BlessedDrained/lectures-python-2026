class MyDict:
    """Упрощённый словарь на основе хеш-таблицы с цепочками коллизий."""

    def __init__(self, size=8):
        self._size = max(size, 1)
        self._buckets = [[] for _ in range(self._size)]
        self._len = 0

    @staticmethod
    def _find(bucket, key):
        for i, (k, _) in enumerate(bucket):
            if k == key:
                return i
        return -1

    def _resize(self):
        old_buckets = self._buckets
        new_size = self._size * 2
        self._size = new_size
        self._buckets = [[] for _ in range(new_size)]
        self._len = 0
        for bucket in old_buckets:
            for key, value in bucket:
                idx = hash(key) % self._size
                self._buckets[idx].append((key, value))
                self._len += 1

    def _ensure_capacity(self):
        if self._len > self._size * 2 // 3:
            self._resize()

    def __setitem__(self, key, value):
        idx = hash(key) % self._size
        bucket = self._buckets[idx]
        pos = self._find(bucket, key)
        if pos >= 0:
            bucket[pos] = (key, value)
        else:
            bucket.append((key, value))
            self._len += 1
            self._ensure_capacity()

    def __getitem__(self, key):
        idx = hash(key) % self._size
        bucket = self._buckets[idx]
        pos = self._find(bucket, key)
        if pos < 0:
            raise KeyError(key)
        return bucket[pos][1]

    def __delitem__(self, key):
        idx = hash(key) % self._size
        bucket = self._buckets[idx]
        pos = self._find(bucket, key)
        if pos < 0:
            raise KeyError(key)
        del bucket[pos]
        self._len -= 1

    def __contains__(self, key):
        idx = hash(key) % self._size
        return self._find(self._buckets[idx], key) >= 0

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __len__(self):
        return self._len

    def stats(self):
        longest = max((len(b) for b in self._buckets), default=0)
        return (self._size, self._len, longest)

    def __repr__(self):
        pairs = {}
        ordered_keys = []
        for bucket in self._buckets:
            for k, v in bucket:
                if k not in pairs:
                    pairs[k] = v
                    ordered_keys.append(k)
        inner = ', '.join(f'{k!r}: {v!r}' for k, v in zip(ordered_keys[:20], [pairs[k] for k in ordered_keys[:20]]))
        suffix = ' ...' if len(pairs) > 20 else ''
        return f'MyDict({{{inner}{suffix}}})'


if __name__ == '__main__':
    d = MyDict()
    for i in range(1000):
        d[f'key{i}'] = i
    assert len(d) == 1000
    assert d['key42'] == 42
    assert 'key7' in d and 'nope' not in d
    d['key42'] = -1
    assert d['key42'] == -1 and len(d) == 1000
    del d['key42']
    assert 'key42' not in d and len(d) == 999
    assert d.get('nope') is None and d.get('nope', 0) == 0
    for bad in (lambda: d['nope'], lambda: d.__delitem__('nope')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    buckets, size, longest = d.stats()
    assert size == 999 and size <= buckets * 2 // 3
    print(d.stats())
