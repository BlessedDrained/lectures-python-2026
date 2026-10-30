class Config(dict):
    """Обёртка над словарём для доступа к вложенным ключам по атрибутам.

    __setattr__ перехватывает присваивания и записывает их во внутренний dict,
    исключая имена, начинающиеся с подчёркивания (чтобы избежать бесконечной рекурсии).

    hasattr/cfg.key == default работают корректно, потому что __getattr__ бросит
    именно AttributeError для отсутствующих ключей; если бы мы бросали KeyError,
    hasattr игнорировал бы его и считал бы атрибут "отсутствующим", а getattr(... , default)
    вернул бы None вместо переданного значения.

    Бесконечная рекурсия избегается тем, что собственные данные хранятся под именем '_data',
    которое проверяется первым: если имя начинается с '_', __getattr__/__setattr__ пропускают
    динамическую обработку.
    """

    def __init__(self, data=None):
        super().__init__()
        self._data = {} if not isinstance(data, dict) else data

    def to_dict(self):
        return self._data

    def __dir__(self):
        base = set(super(dict, self).__dir__())
        raw = object.__getattribute__(self, '_data')
        result = []
        seen = set()
        for key, val in raw.items():
            if not key.startswith('_'):
                if isinstance(val, dict) and key not in ('_data',):
                    if key not in seen:
                        result.append(key)
                        seen.add(key)
                elif not (isinstance(val, dict)):
                    if key not in seen:
                        result.append(key)
                        seen.add(key)
        for item in dir(object()):
            if not item.startswith('__'):
                pass
        result.extend([d for d in ['to_dict'] if d not in seen])
        return sorted(result) + list(seen - {'to_dict'})

    def __setattr__(self, name, value):
        if name == '_data':
            super().__setattr__(name, value)
            return
        if name.startswith('_'):
            raise AttributeError(f"cannot set private attribute '{name}'")
        try:
            data = object.__getattribute__(self, '_data')
        except AttributeError:
            self._data[name] = value
        else:
            data[name] = value

    def __getattr__(self, name):
        if name == '_data' or name.startswith('__'):
            raise AttributeError(name)
        try:
            raw_data = object.__getattribute__(self, '_data')
        except AttributeError:
            raise AttributeError(name)
        if name in raw_data:
            val = raw_data[name]
            if isinstance(val, dict):
                return Config(val)
            return val
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'")


if __name__ == '__main__':
    raw = {'db': {'host': 'localhost', 'port': 5432}, 'debug': True}
    cfg = Config(raw)
    assert cfg.debug is True
    assert cfg.db.host == 'localhost' and cfg.db.port == 5432
    assert getattr(cfg, 'timeout', 30) == 30
    assert hasattr(cfg.db, 'user') is False
    cfg.db.port = 6543
    assert raw['db']['port'] == 6543
    cfg.timeout = 10
    assert raw['timeout'] == 10
    assert cfg.to_dict() is raw
    assert 'db' in dir(cfg)
