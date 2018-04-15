from jellyfish import jaro_distance
from pathlib import Path
from collections import defaultdict
from instance import MemoInstance


MIN_VALID_SCORE = 0.7 # minimal jaro distance to count as a "match"
MAX_VALID_SCORE = jaro_distance('abc', 'abc') # jaro distance of a "perfect match"

class SearchResultItem(object):
    def __init__(self, instance):
        self.instance = instance
        self.nr_matched_tags = 0
        self.nr_perfect_matched_tags = 0
        self.score = 0.0
        self.__matched_tags = {}

    def add_matched_tag(self, tag, score, perfect_match=False):
        self.nr_matched_tags += 1
        if perfect_match:
            self.nr_perfect_matched_tags += 1
            score *= 100 # dramatically overweight tags that are perfectly matched
        self.score += score
        self.__matched_tags[tag] = score

    def get_matched_tags(self):
        keys_sorted_by_score = sorted(
            self.__matched_tags.items(), key=lambda x: x[1], reverse=True
        )
        return [
            (self.instance.tags[key], score)
            for key, score in keys_sorted_by_score
        ]

    def get_tags(self):
        matched_tags = self.get_matched_tags()
        non_match_tags = [
            (self.instance.tags[key], 0)
            for key in self.instance.tags
            if key not in self.__matched_tags
        ]
        return matched_tags + non_match_tags

    def __lt__(self, other):
        if self.score != other.score:
            return self.score > other.score
        elif self.nr_perfect_matched_tags != other.nr_perfect_matched_tags:
            return self.nr_perfect_matched_tags > other.nr_perfect_matched_tags
        elif self.nr_matched_tags != other.nr_matched_tags:
            return self.nr_matched_tags > other.nr_matched_tags
        return self.instance < other.instance


class MemoIndex(object):
    def __init__(self, memo_root):
        self.memo_root = memo_root
        if not memo_root.exists() or not memo_root.is_dir():
            raise FileNotFoundError

        self.instances = {}
        self.tags = defaultdict(set)

        self.__construct()

    def __construct(self):
        for fpath in self.memo_root.rglob('*.txt'):
            try:
                self.new_instance(fpath)
            except:
                continue

    def new_instance(self, fpath):
        inst = MemoInstance(fpath)
        self.__add_instance(inst)

    def __add_instance(self, inst):
        path = inst.fpath.as_posix()
        self.instances[path] = inst
        for tag in inst.tags.keys():
            # Tags are converted to their lower cases when constructing the instance.
            # Searching are also based on lower-case keywords.
            self.tags[tag].add(path)

    def delete_instance(self, fpath):
        path = fpath.as_posix()
        inst = self.instances.get(path)
        if inst:
            del self.instances[path]
            for tag in inst.tags.keys():
                self.tags.get(tag, set()).discard(path)

    def update_instance(self, fpath, force_update=False):
        new_inst = MemoInstance(fpath)
        path = fpath.as_posix()
        original_inst = self.instances.get(path)
        if force_update or not original_inst or original_inst != new_inst:
            self.delete_instance(fpath)
            self.__add_instance(new_inst)

    def list_by_paths(self, paths):
        instances = (self.instances.get(path) for path in paths)
        return [SearchResultItem(instance) for instance in instances if instance]

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
