from pathlib import Path
from datetime import datetime
from template import *


class MemoInstance(object):
    def __init__(self, path=None):
        self.path = path
        if not path:
            # TODO: create instances from interactive questions
            raise NotImplementedError
        else:
            try:
                self.from_text_file(path)
            except Exception as e:
                print(" Failed to create memo instance: %s" % e)
                raise e

    def __lt__(self, other):
        return self.title.lower() < other.title.lower()

    def from_text_file(self, path):
        file_contents = import_template_file(path)
        self.title = file_contents.get('title', 'NULL')
        self.date = file_contents.get('date', None)
        self.tags = file_contents.get('tags', [])
        self.body = file_contents.get('body', "")
