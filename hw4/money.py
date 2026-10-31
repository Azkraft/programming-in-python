class Money:
    """Деньги: целое число копеек + валюта."""

    __slots__ = ('amount', 'currency')

    def __init__(self, amount: int, currency: str):
        object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'currency', currency)

    def __setattr__(self, name, value):
        raise AttributeError(f"поле {name!r} нельзя менять после создания")

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("нельзя складывать разные валюты")
        return Money(self.amount + other.amount, self.currency)

    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"


def total_by_currency(payments):
    result = {}
    for p in payments:
        result[p.currency] = result.get(p.currency, Money(0, p.currency)) + p
    return result


if __name__ == '__main__':
    assert len({Money(100, 'RUB'), Money(100, 'RUB'), Money(100, 'USD')}) == 2
    prices = {Money(100, 'RUB'): 'сто рублей'}
    assert prices[Money(100, 'RUB')] == 'сто рублей'
    assert Money(100, 'RUB') + Money(50, 'RUB') == Money(150, 'RUB')
    for action in (lambda m: setattr(m, 'amount', 5), lambda m: setattr(m, 'extra', 1)):
        try:
            action(Money(1, 'RUB'))
            assert False, 'ожидали AttributeError'
        except AttributeError:
            pass
    try:
        Money(1, 'RUB') + Money(1, 'USD')
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    pays = [Money(100, 'RUB'), Money(5, 'USD'), Money(250, 'RUB')]
    assert total_by_currency(pays) == {'RUB': Money(350, 'RUB'), 'USD': Money(5, 'USD')}


    assert total_by_currency([]) == {}
    assert Money(0, 'RUB') + Money(0, 'RUB') == Money(0, 'RUB')
    assert Money(-50, 'RUB') + Money(100, 'RUB') == Money(50, 'RUB')
    assert (Money(100, 'RUB') == 'не деньги') is False   # сравнение с другим типом
    try:
        Money(1, 'RUB') + 10
        assert False, 'ожидали ValueError/TypeError'
    except (ValueError, TypeError):
        pass

# Если поля Money можно было бы менять после помещения объекта в множество или
# использования как ключа словаря, то при изменении amount/currency изменился бы
# хеш объекта. Тогда словарь/множество стали бы искать его в другой корзине и не
# находили бы существующую запись (как с объектом Point из лекции 4: после p.x =
# 100 проверка p in visited возвращает False). Нарушится контракт
# a == b => hash(a) == hash(b).
