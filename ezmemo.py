#!/usr/bin/env python3

import os
import subprocess
import staticconf
from datetime import datetime
from pathlib import Path
from shutil import copyfile
from pyfiglet import Figlet
#private
from index import MemoIndex
from instance import MemoInstance
from template import *


def get_memos_dir():
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

staticconf.YamlConfiguration(PATH_CONFIG.as_posix())
PATH_MEMOS = get_memos_dir()
EDITOR = staticconf.read_string('default_editor', default=os.getenv('EDITOR','vi'))
SEARCH_FUZZY = staticconf.read_string('default_search_fuzzy', default='True').lower() == 'true'


# clear screen and print logo
def home_screen():
    os.system('clear')
    print("=" * 60)
    print(FIGLET.renderText("      E z M e m o"))


def new_memo_via_editor():
    fpath = new_file()
    if fpath:
        input(" Press any key to start %s editing: " % EDITOR)
        try:
            subprocess.call("%s %s" % (EDITOR, fpath.as_posix()), shell=True)
            memo_index.new_instance(fpath)
        except:
            pass


def new_file():
    while True:
        fname = input(" Add a new memo, please name the memo file: ").strip()
        if not fname: break
        fpath = PATH_MEMOS / ("%s.txt" % fname)
        if fpath.exists():
            print(" Sorry, file already exists")
        else:
            # fpath.touch(mode=0o644, exist_ok=False)
            # copyfile(PATH_TEMPLATE_TXT.as_posix(), fpath)
            try:
                create_template_file(fpath)
            except Exception as e:
                print(" Failed to create new file: %s" % e)
                return None
            return fpath
    return None


def search_memo(search_type='fuzzy'):
    while True:
        keywords = input(" Search for memos, please input the keyword: ").strip()
        if search_type == 'fuzzy':
            results = memo_index.fuzzy_search(keywords)
        else:
            results = memo_index.strict_search(keywords)
        if not continue_after_search(results, keywords):
            break


def continue_after_search(results, keywords):
    os.system('clear')
    print("\n Search results for keywords \"%s\":" % keywords)
    print(" %d memo document(s) found" % len(results))
    print("-" * 30)
    if not results:
        return True
    print(" Index\t%s\tTags" % _str_fixed_length("Title", 30))
    for ind, result in enumerate(results):
        matched_tags, non_match_tags = result.get_tags()
        print(" %3d  \t%s\t%s" % (
            ind, _str_fixed_length(result.instance.title, 30),
            ", ".join(matched_tags + non_match_tags)))
    index_range = "[0]" if len(results) == 1 else "[0 - %d]" % (len(results) - 1)

    while True:
        ind = input(
            "\n Enter the index %s to open the memo, or 'b'ack to the main menu: " % index_range).strip().lower()
        if ind in ['', 'b', 'back']:
            break
        else:
            try:
                fpath = results[int(ind)].instance.path
                subprocess.call("%s %s" % (EDITOR, fpath.as_posix()), shell=True)
                memo_index.update_instance(fpath)
            except Exception as e:
                print(" Failed to open and edit memo, error: %s" % e)


# return True if process exits after this function returns
def edit_config_file():
    print(" Opening config file for editing...")
    try:
        subprocess.call("%s %s" % (EDITOR, PATH_CONFIG.as_posix()), shell=True)
    except Exception as e:
        print(" Failed to open config file for editing: %s" % e)
        return False
    opt = input(" Must restart the process for the changes to apply, quit now (Y/N)? ").strip().lower()
    return opt in ['y', 'yes', 'q']


def _str_fixed_length(string, length):
    if len(string) <= length:
        return string + " " * (length - len(string))
    elif length >= 4:
        return string[:length-3] + "..."
    else:
        return string[:length]


# directory of memos
if not PATH_MEMOS.exists():
    PATH_MEMOS.mkdir(mode=0o744, exist_ok=True)
    if not PATH_MEMOS.exists():
        raise FileNotFoundError
elif not PATH_MEMOS.is_dir():
    raise FileExistsError

# construct index
memo_index = MemoIndex(PATH_MEMOS)

# main loop
stop = False
while not stop:
    home_screen()
    print(" Actions:")
    print(
        " 1. New memo\n"
        " 2. Search memo\n"
        " 3. Settings\n"
        " 4. Quit\n"
    )
    opt = input(" Please select action: ").strip().lower()

    if opt == "4":
        stop = True
    elif opt == "1":
        new_memo_via_editor()
    elif opt == "2":
        search_type = 'fuzzy' if SEARCH_FUZZY else 'strict'
        search_memo(search_type=search_type)
    elif opt == "3":
        stop = edit_config_file()

    # break
