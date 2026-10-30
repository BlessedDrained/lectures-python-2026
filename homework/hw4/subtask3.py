import re


class SearchIndex:
    """Поисковый индекс на основе инвертированного словаря.
    
    Для эффективного удаления и перезаписи документов храним два уровня данных:
    _reverse — слово -> множество doc_id (для поиска),
    _counts — пара {(слово, doc_id): число_вхождений}, чтобы при удалении документа
    знать точное количество каждого слова в нём без перебора всего индекса.
    При удалении слова из _counts уменьшаем _doc_word_count[doc][word];
    когда значение становится нулём, удаляем пару из _counts и чистим _reverse.
    top_words использует collections.Counter по _values для подсчёта общей частотности.
    """

    def __init__(self):
        self._reverse = {}
        self._docs = {}

    def add(self, doc_id, text):
        words = re.findall(r'\w+', text.lower())
        counts = {}
        for w in words:
            counts[w] = counts.get(w, 0) + 1

        old_counts = self._docs.pop(doc_id, {})
        for word, cnt in old_counts.items():
            if word not in self._reverse:
                continue
            entry = self._reverse[word].copy() - {doc_id}
            if entry:
                self._reverse[word] = entry
            else:
                del self._reverse[word]

        new_set = set()
        for word, cnt in counts.items():
            s = self._reverse.setdefault(word, set())
            s.add(doc_id)
            new_set.add(word)
            self._reverse[word] = s
        self._docs[doc_id] = counts

    def remove(self, doc_id):
        counts = self._docs.pop(doc_id, None)
        if not counts:
            return
        for word, cnt in counts.items():
            rs = self._reverse.get(word, set())
            rs.discard(doc_id)
            if rs:
                self._reverse[word] = rs
            elif word in self._reverse:
                del self._reverse[word]

    def search_all(self, *words):
        results = None
        for w in words:
            key = w.lower()
            docs_for_word = self._reverse.get(key)
            if not docs_for_word:
                return set()
            if results is None:
                results = set(docs_for_word)
            else:
                results &= docs_for_word
        return results or set()

    def search_any(self, *words):
        result = set()
        for w in words:
            key = w.lower()
            docs_for_word = self._reverse.get(key)
            if docs_for_word:
                result |= docs_for_word
        return result

    def top_words(self, n):
        total_freq = {}
        for count_by_doc in self._docs.values():
            for word, cnt in count_by_doc.items():
                total_freq[word] = total_freq.get(word, 0) + cnt
        sorted_items = sorted(total_freq.items(), key=lambda x: (-x[1], x[0]))
        return [(w, c) for w, c in sorted_items[:n]]


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
    top = idx.top_words(2)
    assert len(top) == 2
    assert all(isinstance(item, tuple) and len(item) == 2 for item in top)
    freq_0 = top[0][1] if top else -1
    freq_1 = top[1][1] if len(top) > 1 else -1
    assert freq_0 >= freq_1
    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}
