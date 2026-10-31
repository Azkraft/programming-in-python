# Книжный трекер.
# list   - меняющийся набор записей (список книг)
# tuple  - фиксированная структура одной записи (id, title, author, year, genre)
# dict   - быстрый поиск записи по ключу (id -> книга)
# set    - уникальность (множество жанров)

books: list[tuple[int, str, str, int, str]] = []      # (id, title, author, year, genre)
by_id: dict[int, tuple[int, str, str, int, str]] = {} # id -> книга
genres: set[str] = set()                         # уникальные жанры


def add_book(book_id: int, title: str, author: str, year: int, genre: str) -> None:
    book = (book_id, title, author, year, genre)
    books.append(book)
    by_id[book_id] = book
    genres.add(genre)


def find_book(book_id: int) -> tuple[int, str, str, int, str] | None:
    return by_id.get(book_id)


if __name__ == '__main__':
    add_book(1, '1984', 'Джордж Оруэлл', 1949, 'дистопия')
    add_book(2, 'Гарри Поттер и философский камень', 'Джоан Роулинг', 1997, 'фэнтези')
    add_book(3, '451 градус по Фаренгейту', 'Рэй Брэдбери', 1953, 'дистопия')

    print(find_book(2))
    print(find_book(999))
    print(sorted(genres))
