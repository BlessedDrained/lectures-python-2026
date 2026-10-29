"""
Трекер книг библиотеки.

list используется как меняющийся набор записей — необходим порядок элементов и операции добавления/удаления по индексу.
tuple хранит фиксированную структуру одной записи из четырёх неизменяемых полей — это гарантирует целостность данных и позволяет использовать запись в качестве ключа словаря или элемента множества.
dict обеспечивает быстрый поиск книги по ISBN за O(1), а также построение обратного индекса авторов для эффективной фильтрации.
set применяется для хранения уникальных жанров — важна только уникальность значений, дубликаты отбрасываются автоматически.

Все ловушки семинара избежаны: mutable default arguments заменены на None с проверкой, при экспорте множества возвращается копия, список никогда не используется в качестве ключа словаря или элемента множества.
"""


def create_library():
    return {
        "catalog": {},
        "all_books": [],
        "genres": set(),
        "authors_index": {},
    }


def add_book(library, isbn, title, author, year, genre):
    record = (isbn, title, author, year)

    if isbn in library["catalog"]:
        raise ValueError(f"Книга с ISBN {isbn} уже существует")

    library["catalog"][isbn] = record
    library["all_books"].append(record)
    library["genres"].add(genre)
    library["authors_index"].setdefault(author, []).append(isbn)


def remove_book(library, isbn):
    catalog = library["catalog"]
    if isbn not in catalog:
        raise KeyError(f"Книга с ISBN {isbn} не найдена")

    book_tuple = catalog.pop(isbn)
    all_books = library["all_books"]
    for i, b in enumerate(all_books):
        if b[0] == isbn:
            del all_books[i]
            break

    author_name = book_tuple[2]
    authors_idx = library["authors_index"]
    author_list = authors_idx.get(author_name, [])
    if isbn in author_list:
        author_list.remove(isbn)
    if not author_list:
        del authors_idx[author_name]


def search_by_author(library, author):
    return [library["catalog"][bid] for bid in library["authors_index"].get(author, [])]


def get_all_genres(library):
    return set(library["genres"])


if __name__ == "__main__":
    lib = create_library()
    add_book(lib, "978-3-16-148410-0", "Clean Code", "Robert Martin", 2008, "Programming")
    add_book(lib, "978-0-13-468599-1", "The Pragmatic Programmer", "David Thomas", 1999, "Programming")
    add_book(lib, "978-5-699-44474-2", "Мастер и Маргарита", "Булгаков", 1967, "Fiction")

    print("Каталог:", lib["catalog"])
    print("Все книги (list):", lib["all_books"])
    print("Жанры (set):", get_all_genres(lib))
    print("Поиск по автору:", search_by_author(lib, "Robert Martin"))
