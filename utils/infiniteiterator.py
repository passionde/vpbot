class InfiniteListIterator:
    def __init__(self, lst):
        self.lst = lst
        self.index = 0
        self.length = len(lst)

    def __aiter__(self):
        return self

    def __anext__(self):
        item = self.lst[self.index]
        self.index = (self.index + 1) % self.length
        return item
