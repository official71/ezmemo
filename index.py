from jellyfish import jaro_distance
from pathlib import Path
from collections import defaultdict, namedtuple
from heapq import *
from instance import MemoInstance


MIN_VALID_SCORE = 0.7 # minimal jaro distance to count as a "match"
MAX_VALID_SCORE = jaro_distance('abc', 'abc') # jaro distance of a "perfect match"

class SearchResultItem(object):
    def __init__(self, instance):
        self.instance = instance
        self.nr_matched_tags = 0
        self.nr_perfect_matched_tags = 0
        self.score = 0.0
        self.__matched_tags = []

    def add_matched_tag(self, tag, score, perfect_match=False):
        self.nr_matched_tags += 1
        if perfect_match:
            self.nr_perfect_matched_tags += 1
            score *= 100 # dramatically overweight tags that are perfectly matched
        self.score += score
        heappush(self.__matched_tags, (-score, tag))

    def get_tags(self):
        matched_tags = []
        index_lookup, index = {}, 0
        heap = list(self.__matched_tags)
        while heap:
            tag = heappop(heap)[1]
            matched_tags.append(tag)
            index_lookup[tag] = index
            index += 1
        # List matched_tags contains all tags that are matching the search query,
        # sorted by relevance. However these tags are all lower-case, and we need
        # to return the original tags saved in the instance.
        non_match_tags = []
        for tag in self.instance.tags:
            tag_lower = tag.lower()
            if tag_lower in index_lookup:
                matched_tags[index_lookup[tag_lower]] = tag
            else:
                non_match_tags.append(tag)
        return matched_tags, non_match_tags

    def __lt__(self, other):
        if self.score != other.score:
            return self.score > other.score
        elif self.nr_perfect_matched_tags != other.nr_perfect_matched_tags:
            return self.nr_perfect_matched_tags > other.nr_perfect_matched_tags
        elif self.nr_matched_tags != other.nr_matched_tags:
            return self.nr_matched_tags > other.nr_matched_tags
        return self.instance < other.instance


class MemoIndex(object):
    def __init__(self, path):
        self.path = path
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError

        self.instances = {}
        self.tags = defaultdict(set)

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
            # As keys, tags are converted to their lower cases.
            # Searching are also based on lower-case keywords.
            self.tags[tag.lower()].add(path)

    def list_all(self):
        return sorted([SearchResultItem(instance) for instance in self.instances.values()])

    def strict_search(self, keyword_str):
        if not keyword_str: return self.list_all()
        instances = [self.instances[path] for path in self.tags[keyword_str.lower()] if path in self.instances]
        return sorted([SearchResultItem(instance) for instance in instances])

    def fuzzy_search(self, keyword_str):
        if not keyword_str: return self.list_all()
        keywords = [keyword.lower() for keyword in keyword_str.split() if keyword]
        if ' ' in keyword_str:
            # also include the whole string if it consists of multiple words
            keywords.append(keyword_str.lower())

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
                    search_result_item.add_matched_tag(tag, max_score, perfect_match)
        return sorted(search_results.values())
