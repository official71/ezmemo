from jellyfish import jaro_distance
from pathlib import Path
from collections import defaultdict, namedtuple
from heapq import *
from instance import MemoInstance


MIN_VALID_SCORE = 0.7
MAX_VALID_SCORE = jaro_distance('abc', 'abc')

class SearchResultItem(object):
    def __init__(self, instance):
        self.instance = instance
        self.nr_matching_tags = 0
        self.nr_perfect_matching_tags = 0
        self.score = 0.0
        self.__matching_tags = []

    def add_matching_tag(self, tag, score, perfect_match=False):
        self.nr_matching_tags += 1
        if perfect_match:
            self.nr_perfect_matching_tags += 1
            score *= 100 # dramatically overweight tags that are perfectly matched
        self.score += score
        heappush(self.__matching_tags, (-score, tag))

    def get_matching_tags(self):
        matching_tags = []
        heap = list(self.__matching_tags)
        while heap:
            matching_tags.append(heappop(heap)[1])
        return matching_tags

    def get_mismatching_tags(self):
        return list(set(self.instance.tags) - set(self.get_matching_tags()))

    def __lt__(self, other):
        if self.score != other.score:
            return self.score > other.score
        elif self.nr_perfect_matching_tags != other.nr_perfect_matching_tags:
            return self.nr_perfect_matching_tags > other.nr_perfect_matching_tags
        elif self.nr_matching_tags != other.nr_matching_tags:
            return self.nr_matching_tags > other.nr_matching_tags
        return self.instance < other.instance


class MemoIndex(object):
    def __init__(self, path):
        self.path = path
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError

        self.instances = {}
        self.tags = defaultdict(list)

        self.__construct()

    def __construct(self):
        for fpath in self.path.rglob('*.txt'):
            try:
                self.add_instance(fpath)
            except:
                continue

    def add_instance(self, fpath):
        inst = MemoInstance(fpath)
        path = inst.path.as_posix()
        self.instances[path] = inst
        for tag in inst.tags:
            self.tags[tag].append(path)

    def list_all(self):
        return sorted([SearchResultItem(instance) for instance in self.instances.values()])

    def strict_search(self, keyword_str):
        if not keyword_str: return self.list_all()
        instances = [self.instances[path] for path in self.tags[keyword_str.lower()] if path in self.instances]
        return sorted([SearchResultItem(instance) for instance in instances])

    def fuzzy_search(self, keyword_str):
        if not keyword_str: return self.list_all()
        keywords = [keyword.lower() for keyword in keyword_str.split() if keyword] + [keyword_str.lower()]

        search_results = {}
        for tag, paths in self.tags.items():
            max_score = max([jaro_distance(tag, keyword) for keyword in keywords])
            if max_score >= MIN_VALID_SCORE:
                perfect_match = max_score >= MAX_VALID_SCORE
                for path in paths:
                    instance = self.instances.get(path, None)
                    if not instance:
                        continue
                    if path in search_results:
                        search_result_item = search_results[path]
                    else:
                        search_results[path] = search_result_item = SearchResultItem(instance)
                    search_result_item.add_matching_tag(tag, max_score, perfect_match)
        return sorted(search_results.values())
