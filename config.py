import os
import staticconf
from pathlib import Path
from pyfiglet import Figlet


def _get_memos_dir():
    dir_memos = staticconf.read_string('dir_memos', default='')
    # try absolute dir
    path_memos = Path(dir_memos)
    if path_memos and path_memos.exists() and path_memos.is_dir():
        return path_memos
    # try relative dir
    path_memos = PATH_CWD / dir_memos
    if path_memos and path_memos.exists() and path_memos.is_dir():
        return path_memos
    return None


# global utilities
FIGLET = Figlet(font='big')
PATH_CWD = Path.cwd()
PATH_CONFIG = PATH_CWD / 'config.yaml'
PATH_RECENT_OPEN = PATH_CWD / 'recent_open.yaml'

staticconf.YamlConfiguration(PATH_CONFIG.as_posix())
PATH_MEMOS = _get_memos_dir()
EDITOR = staticconf.read_string('default_editor', default=os.getenv('EDITOR','vi'))
SEARCH_FUZZY = staticconf.read_string('default_search_fuzzy', default='True').lower() == 'true'
RECENT_OPEN_LIST_SIZE = staticconf.read_int('recent_open_list_size', default=10)
