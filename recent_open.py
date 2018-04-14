from collections import deque
from pathlib import Path
import yaml

class RecentOpenList(object):
    def __init__(self, size=10, yaml_fpath=None):
        self.size = size
        self.queue = deque()
        self.set = set()
        self.yaml_fpath = yaml_fpath
        self.__load_yaml()

    def __load_yaml(self):
        if not self.yaml_fpath:
            return
        if self.yaml_fpath.exists():
            if not self.yaml_fpath.is_file():
                raise FileExistsError(
                    "Invalid yaml file for recently opened list: %s" % self.yaml_fpath.as_posix()
                )
            # construct the queue by loading yaml file
            with self.yaml_fpath.open('r', encoding='utf-8') as f:
                paths = yaml.load(f)
                if paths is not None:
                    for path in paths:
                        fpath = Path(path)
                        if fpath and fpath.is_file():
                            self.open(path)

    def __dump_yaml(self):
        if self.yaml_fpath:
            with self.yaml_fpath.open('w', encoding='utf-8') as f:
                paths = list(self.queue)
                if paths:
                    yaml.dump(paths, f, default_flow_style=False)

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

    def save(self):
        self.__dump_yaml()
