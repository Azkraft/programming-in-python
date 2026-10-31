class MyDict:
    """Упрощённый словарь на основе хеш-таблицы с цепочками.

    Внутри используются только списки и кортежи (dict/set не используются).
    """

    def __init__(self, size=8):
        self._buckets = [[] for _ in range(size)]
        self._len = 0

    def _index(self, key):
        return hash(key) % len(self._buckets)

    def _resize(self):
        old_buckets = self._buckets
        self._buckets = [[] for _ in range(len(old_buckets) * 2)]
        self._len = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self[key] = value

    def __setitem__(self, key, value):
        idx = self._index(key)
        for i, (k, v) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx][i] = (key, value)
                return
        self._buckets[idx].append((key, value))
        self._len += 1
        if self._len > len(self._buckets) * 2 / 3:
            self._resize()

    def __getitem__(self, key):
        idx = self._index(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        raise KeyError(key)

    def __delitem__(self, key):
        idx = self._index(key)
        for i, (k, v) in enumerate(self._buckets[idx]):
            if k == key:
                del self._buckets[idx][i]
                self._len -= 1
                return
        raise KeyError(key)

    def __contains__(self, key):
        idx = self._index(key)
        return any(k == key for k, _ in self._buckets[idx])

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def stats(self):
        longest = max((len(b) for b in self._buckets), default=0)
        return (len(self._buckets), self._len, longest)

    def __repr__(self):
        items = []
        for bucket in self._buckets:
            for k, v in bucket:
                items.append(f"{k!r}: {v!r}")
        return "MyDict({" + ", ".join(items) + "})"


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
    assert size == 999 and size <= buckets * 2 / 3
    print(d.stats())


    e = MyDict()
    assert len(e) == 0
    assert e.get('x') is None and e.get('x', 5) == 5
    assert e.stats() == (8, 0, 0)
    for bad in (lambda: e['x'], lambda: e.__delitem__('x')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    d2 = MyDict()
    d2[1] = 'a'
    d2[1] = 'b'                 # обновление существующего ключа не увеличивает длину
    assert len(d2) == 1 and d2[1] == 'b'
    d2[(1, 2)] = 'par'          # кортеж в качестве ключа
    assert d2[(1, 2)] == 'par'
    big = MyDict()
    for i in range(300):
        big[i] = i
    b2, s2, _ = big.stats()
    assert s2 == 300 and b2 > 8 and s2 <= b2 * 2 / 3   # таблица перестроилась

# 1. При увеличении таблицы номера корзин меняются, потому что индекс корзины
#    вычисляется как hash(key) % len(self._buckets); при удвоении числа корзин
#    остаток от деления для того же ключа может стать другим, поэтому все пары
#    раскладываются заново.
# 2. Для 1000 строковых ключей stats() показывает примерно (2048, 999, 4)
#    — хеши строк распределяются равномерно. Если все ключи возвращают хеш 42,
#    все пары попадают в одну корзину: вставка 1000 ключей по времени O(n^2), longest == 1000.
