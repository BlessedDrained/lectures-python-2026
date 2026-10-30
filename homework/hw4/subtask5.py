class LRUCache:
    """LRU-кэш на основе обычного dict и односвязного списка.
    
    Удаление самого старого элемента работает за O(1), потому что мы храним
    ссылки на узлы в словаре _nodes. При каждом обращении get или put ключ
    перемещается в конец списка методом _move_to_end(), а при переполнении
    удаляется голова списка через _pop_head() — оба действия меняют только
    указатели prev/next у двух соседних узлов без перебора всего списка.
    """

    class _Node:
        __slots__ = ('key', 'value', '_prev', '_next')

        def __init__(self, key=None, value=None):
            self.key = key
            self.value = value
            self._prev = None
            self._next = None

    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError('capacity must be >= 1')
        self.capacity = capacity
        self.size = 0

        self._nodes = {}

        self._head = object.__new__(LRUCache._Node)
        self._tail = object.__new__(LRUCache._Node)
        self._head._next = self._tail
        self._tail._prev = self._head


    def _unlink(self, node):
        node._prev._next = node._next
        node._next._prev = node._prev

    def _move_to_end(self, node):
        """Переместить существующий узел в конец (самый свежий)."""
        self._unlink(node)
        prev_tail_prev = self._tail._prev
        prev_tail_prev._next = node
        node._prev = prev_tail_prev
        node._next = self._tail
        self._tail._prev = node

    def _add_at_end(self, key, value):
        """Добавить новый узел после tail."""
        node = LRUCache._Node(key, value)
        self._nodes[key] = node
        prev_tail_prev = self._tail._prev
        prev_tail_prev._next = node
        node._prev = prev_tail_prev
        node._next = self._tail
        self._tail._prev = node
        return node

    def _pop_head(self):
        """Удалить самый старый элемент (сразу после головы). O(1)."""
        victim = self._head._next
        if victim is self._tail:
            return None
        del self._nodes[victim.key]
        self._head._next = victim._next
        victim._next._prev = self._head
        victim._prev = None
        victim._next = None
        self.size -= 1
        return victim


    def get(self, key, default=None):
        if key not in self._nodes:
            return default
        node = self._nodes[key]
        self._move_to_end(node)
        return node.value

    def put(self, key, value):
        if key in self._nodes:
            node = self._nodes[key]
            node.value = value
            self._move_to_end(node)
        else:
            if self.size >= self.capacity:
                self._pop_head()
            self._add_at_end(key, value)
            self.size += 1

    def __len__(self):
        return self.size

    def __contains__(self, key):
        return key in self._nodes


if __name__ == '__main__':
    c = LRUCache(2)
    c.put('a', 1)
    c.put('b', 2)
    assert c.get('a') == 1
    c.put('c', 3)
    assert 'b' not in c and c.get('a') == 1 and c.get('c') == 3
    c.put('a', 10)
    c.put('d', 4)
    assert c.get('c') is None and c.get('a') == 10 and len(c) == 2
