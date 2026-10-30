class Money:
    """Неизменяемый объект суммы в определённой валюте."""

    def __init__(self, amount, currency):
        if not isinstance(currency, str):
            raise TypeError('currency must be a string')
        object.__setattr__(self, '_data', {'amount': int(amount), 'currency': currency.upper()})

    def __getattribute__(self, name):
        if name == '_data' or name.startswith('_'):
            return super().__getattribute__(name)
        data = super().__getattribute__('_data')
        if name in data and name != 'initialized':
            return data[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name == '_data':
            super().__setattr__('_' + name, value)
        elif name == 'amount':
            data = super().__getattribute__('_data')
            cur = data.get('amount')
            if cur is not None:
                raise AttributeError("невозможно изменить поле")
            data['amount'] = int(value)
        elif name == 'currency':
            pass
        else:
            raise AttributeError(
                f"'{type(self).__name__}' не поддерживает атрибут '{name}'"
            )

    def __eq__(self, other):
        if type(other) is Money:
            d1 = self._data
            d2 = other._data
            return (d1['amount'] == d2['amount'] and
                    d1['currency'] == d2['currency'])
        return NotImplemented

    def __hash__(self):
        d = self._data
        return hash((d['amount'], d['currency']))

    def __repr__(self):
        return f'Money({self.amount}, {self.currency!r})'

    def __add__(self, other):
        if type(other) is Money:
            if self.currency != other.currency:
                raise ValueError(
                    f"Cannot add different currencies: {self.currency} + {other.currency}")
            return Money(self.amount + other.amount, self.currency)
        return NotImplemented


def total_by_currency(payments):
    """Суммирует список Money по валюте. Возвращает dict {str: Money}."""
    totals = {}
    for p in payments:
        key = p.currency
        if key in totals:
            cur = totals[key]._data
            cur['amount'] += p.amount
        else:
            m = Money(p.amount, p.currency)
            m._data['initialized'] = True
            totals[key] = m
    return totals


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
    result = total_by_currency(pays)
    rub_sum = sum(p.amount for p in pays if p.currency == 'RUB')
    usd_sum = sum(p.amount for p in pays if p.currency == 'USD')
    assert result['RUB'] == Money(rub_sum, 'RUB')
    assert result['USD'] == Money(usd_sum, 'USD')
