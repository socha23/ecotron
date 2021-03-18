import random

class RandomSequence:
    def __init__(self, items, min_distance = None):        
        if (min_distance == None):
            min_distance = int(len(items) / 2 + 1)
        if min_distance < 1 or min_distance > len(items):
            raise "Minimum distance cannot be higher than array length"

        self._seen = []        
        self._min_distance = min_distance
        self._items = items.copy()

    def next(self):
        if len(self._seen) == self._min_distance:
            self._items.append(self._seen.pop(0))
        item = random.choice(self._items)
        self._items.remove(item)
        self._seen.append(item)
        return item
