def memoize(func):
    """Возвращает функцию с кэшем результатов на замыкании.

    Кэш живёт в объемлющей функции. Нехешируемые аргументы вызывают функцию без
    кэша и не учитываются в hits/misses. Сохраняет __name__ и __doc__.
    """

    cache = {}
    stats = {'hits': 0, 'misses': 0}

    def wrapper(*args, **kwargs):
        try:
            key = (args, tuple(sorted(kwargs.items())))
            hash(key)
        except TypeError:
            return func(*args, **kwargs)
        if key in cache:
            stats['hits'] += 1
            wrapper.hits = stats['hits']
            return cache[key]
        stats['misses'] += 1
        wrapper.misses = stats['misses']
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    def cache_clear():
        cache.clear()
        stats['hits'] = 0
        stats['misses'] = 0
        wrapper.hits = 0
        wrapper.misses = 0

    wrapper.hits = 0
    wrapper.misses = 0
    wrapper.cache_clear = cache_clear
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


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

    # эксперимент с рекурсией (fib, n = 30)
    import time

    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    # Вариант A: только локальная обёртка кэшируется, рекурсия внутри fib
    # вызывает исходную (не кэшированную) функцию по имени fib из Глобальной области.
    fast_fib = memoize(fib)
    start = time.perf_counter()
    r_a = fast_fib(30)
    t_a = time.perf_counter() - start
    print(f'Вариант A (fast_fib): fib(30)={r_a}, misses={fast_fib.misses}, время={t_a:.4f} сек')

    # Вариант B: глобальная fib заменена на кэшированную обёртку, рекурсивные
    # вызовы fib(n-1) и fib(n-2) идут через кэш.
    fib = memoize(fib)
    start = time.perf_counter()
    r_b = fib(30)
    t_b = time.perf_counter() - start
    print(f'Вариант B (fib): fib(30)={r_b}, misses={fib.misses}, время={t_b:.4f} сек')

# Эксперимент с рекурсией:
# fast_fib = memoize(fib) — внутри fib рекурсивный вызов fib(n - 1) идёт по имени
# fib из Глобальной области (LEGB: G), которая после memoize всё ещё ссылается на
# исходную (не memoized) fib, поэтому ускорения почти нет.
# fib = memoize(fib) — имя fib в глобальной области теперь ссылается на memoized
# обёртку, и рекурсивный вызов внутри неё (которая вызывает исходную fib) попадает
# в кэш, что ускоряет вычисления в тысячи раз.
