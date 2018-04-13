from collections import deque

class RecentOpenList(object):
    def __init__(self, size=10):
        self.size = size
        self.queue = deque()
        self.set = set()

    def open(self, path):
        if path in self.set:
            self.queue.remove(path)
            self.set.remove(path)
        self.__enqueue(path)

    def __enqueue(self, path):
        while len(self.queue) >= self.size:
            self.set.discard(self.queue.popleft())
        self.queue.append(path)
        self.set.add(path)

    def get_list(self):
        return list(reversed(self.queue))
