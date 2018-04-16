from colored import *
import staticconf

"""
You might find the colored documentation very useful:
https://pypi.python.org/pypi/colored
"""

ENABLE_COLORIZER = staticconf.read_string('enable_colorizer', default='false').lower() == 'true'


def colorizer_enabled(function):
    """do not colorize if it's not enabled"""
    def wrapper(*args):
        if ENABLE_COLORIZER:
            return function(*args)
        elif args:
            return args[0]
        else:
            return args
    return wrapper


# attr and colors
ATTR_RESET = attr('reset')
COLOR_INDEX = fg(199)
COLOR_TITLE = fg(45)
COLOR_TAG_0 = fg(10) + attr('bold')
COLOR_TAG_1 = fg(10)
COLOR_TAG_2 = fg(87)
COLOR_TAG_3 = fg(208)
COLOR_TAG_4 = fg(252)


@colorizer_enabled
def color_index(index):
    return COLOR_INDEX + index + ATTR_RESET

@colorizer_enabled
def color_title(title):
    return COLOR_TITLE + title + ATTR_RESET

def _color_by_score(score):
    if score >= 1:
        return COLOR_TAG_0
    elif score >= 0.9:
        return COLOR_TAG_1
    elif score >= 0.8:
        return COLOR_TAG_2
    elif score >= 0.7:
        return COLOR_TAG_3
    return COLOR_TAG_4

@colorizer_enabled
def _color_tag(tag, score):
    return _color_by_score(score) + tag + ATTR_RESET

def color_tags(scored_tags):
    return ", ".join((_color_tag(tag, score) for tag, score in scored_tags))
