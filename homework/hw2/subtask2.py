"""Задание 2 — собственный баг-репорт.

Тема: неосторожный алиасинг при поверхностной копии вложенного изменяемого объекта.
Баг отличается от семинарского (там копировали список групп; здесь копируем dict с вложенным list).
"""


# === Багованный код ===
def update_user_preferences(user_db, username, new_pref_key, value):
    user_copy = dict(user_db)
    preferences = user_copy[username]
    if new_pref_key not in [p[0] for p in preferences]:
        preferences.append((new_pref_key, value))
        user_db[username] = tuple(preferences)


original_db = {
    "alice": [("theme", "dark"), ("lang", "en")],
}
update_user_preferences(original_db, "alice", "notifications", True)
print("После обновления:", original_db)


# === Объяснение ===
# Функция dict() создаёт поверхностную копию внешнего словаря, но значения внутри остаются ссылками на те же самые объекты.
# Присваивание preferences = user_copy["alice"] даёт ссылку на тот же самый список, что и original_db["alice"], поэтому append мутирует исходный словарь до перезаписи ключа кортежем.

# === Исправленная версия ===
def update_user_preferences_fixed(user_db, username, new_pref_key, value):
    if username not in user_db:
        raise KeyError(f"User '{username}' not found")

    prefs_list = list(user_db[username])
    if new_pref_key not in [p[0] for p in prefs_list]:
        prefs_list.append((new_pref_key, value))
    user_db[username] = tuple(prefs_list)


db2 = {
    "bob": [("theme", "light"), ("lang", "ru")],
}
update_user_preferences_fixed(db2, "bob", "notifications", True)
print("После исправления:", db2)
