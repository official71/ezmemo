from pathlib import Path
from datetime import datetime
from template import *


class MemoInstance(object):
    def __init__(self, fpath=None):
        self.fpath = fpath
        if not fpath:
            # TODO: create instances from interactive questions
            raise NotImplementedError
        else:
            try:
                self.from_text_file(fpath)
            except Exception as e:
                print(" Failed to create memo instance: %s" % e)
                raise e

    def __lt__(self, other):
        return self.title.lower() < other.title.lower()

    def __eq__(self, other):
        return (
            self.title == other.title and
            self.tags == other.tags
        )

    def from_text_file(self, fpath):
        file_contents = import_template_file(fpath)
        self.title = file_contents.get('title', 'NULL')
        self.date = file_contents.get('date', None)
        # Tags are stored as key: value pairs, where keys are the lower cases
        # of the original tags; the keys are used for indexing and searching.
        self.tags = {tag.lower(): tag for tag in file_contents.get('tags')}
        # Do not store body, for now
        # self.body = file_contents.get('body', "")