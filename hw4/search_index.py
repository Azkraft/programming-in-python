import re


class SearchIndex:
    """Инвертированный индекс: слово -> множество id документов.

    _index: dict[str, set[int]] — для быстрого поиска по слову, не перебирая все
    документы (сложность зависит от числа слов запроса и размера найденных
    множеств).
    _docs: dict[int, dict[str, int]] — слова документа с их частотой; нужны,
    чтобы remove() и повторный add() работали без перебора всего индекса.
    _freq: dict[str, int] — общая частота слова по всем документам для top_words.
    """

    def __init__(self):
        self._index = {}
        self._docs = {}
        self._freq = {}

    def _words(self, text):
        return re.findall(r'\w+', text.lower())

    def add(self, doc_id, text):
        if doc_id in self._docs:
            self.remove(doc_id)
        words = self._words(text)
        doc_freq = {}
        for w in words:
            doc_freq[w] = doc_freq.get(w, 0) + 1
        self._docs[doc_id] = doc_freq
        for w, count in doc_freq.items():
            self._index.setdefault(w, set()).add(doc_id)
            self._freq[w] = self._freq.get(w, 0) + count

    def search_all(self, *words):
        result = None
        for w in words:
            docs = self._index.get(w.lower(), set())
            result = set(docs) if result is None else (result & docs)
        return result if result is not None else set()

    def search_any(self, *words):
        result = set()
        for w in words:
            result |= self._index.get(w.lower(), set())
        return result

    def remove(self, doc_id):
        doc_freq = self._docs.pop(doc_id, None)
        if doc_freq is None:
            return
        for w, count in doc_freq.items():
            bucket = self._index.get(w)
            if bucket is not None:
                bucket.discard(doc_id)
                if not bucket:
                    del self._index[w]
            self._freq[w] = self._freq.get(w, 0) - count
            if self._freq[w] <= 0:
                del self._freq[w]

    def top_words(self, n):
        return sorted(self._freq.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]
    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}


    empty = SearchIndex()
    assert empty.search_all() == set()
    assert empty.search_any() == set()
    assert empty.search_all('python') == set()
    empty.remove(999)                                    # удаление несуществующего документа
    idx.add(1, 'Python python python')                   # повторный add заменяет текст, не дублирует
    assert idx.search_all('python') == {1}
    assert idx.top_words(0) == []
    assert len(idx.top_words(100)) <= len(idx._freq)
