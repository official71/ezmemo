#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime
from shutil import copyfile
#private
from config import *
from index import MemoIndex
from instance import MemoInstance
from recent_open import RecentOpenList
from template import *


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
            path = fpath.as_posix()
            subprocess.call("%s %s" % (EDITOR, path), shell=True)
            memo_index.new_instance(fpath)
        except:
            return
        recent_open_list.open(path)


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
    for index, result in enumerate(results):
        tags = result.get_tags()
        print(" %3d  \t%s\t%s" % (
            index, _str_fixed_length(result.instance.title, 30),
            ", ".join((tag for tag, _ in tags))))
    index_range = "[0]" if len(results) == 1 else "[0 - %d]" % (len(results) - 1)

    while True:
        index = input(
            "\n Enter the index %s to open the memo, or 'b'ack to the main menu: " % index_range).strip().lower()
        if index in ['', 'b', 'back']:
            break
        else:
            try:
                fpath = results[int(index)].instance.fpath
                path = fpath.as_posix()
                subprocess.call("%s %s" % (EDITOR, path), shell=True)
                memo_index.update_instance(fpath)
            except Exception as e:
                print(" Failed to open and edit memo, error: %s" % e)
                continue
            recent_open_list.open(path)


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


def recently_opened():
    os.system('clear')
    results = memo_index.list_by_paths(recent_open_list.get_list())
    if not results:
        input(" No records. Press any key to continue: ")
        return

    print("\n Recently opened memos:")
    print("-" * 30)
    print(" Index\t%s\tTags" % _str_fixed_length("Title", 30))
    for ind, result in enumerate(results):
        print(" %3d  \t%s\t%s" % (
            ind, _str_fixed_length(result.instance.title, 30),
            ", ".join(list(result.instance.tags.values()))))
    index_range = "[0]" if len(results) == 1 else "[0 - %d]" % (len(results) - 1)

    while True:
        ind = input(
            "\n Enter the index %s to open the memo, or 'b'ack to the main menu: " % index_range).strip().lower()
        if ind in ['', 'b', 'back']:
            break
        else:
            try:
                fpath = results[int(ind)].instance.fpath
                path = fpath.as_posix()
                subprocess.call("%s %s" % (EDITOR, path), shell=True)
                memo_index.update_instance(fpath)
            except Exception as e:
                print(" Failed to open and edit memo, error: %s" % e)
                continue
            recent_open_list.open(path)


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

# recent-open list
recent_open_list = RecentOpenList(
    size=RECENT_OPEN_LIST_SIZE,
    yaml_fpath=PATH_RECENT_OPEN,
)

# main loop
stop = False
while not stop:
    home_screen()
    print(" Actions:")
    print(
        " 1. New memo\n"
        " 2. Search memos\n"
        " 3. Recently opened memos\n"
        " 4. Configurations\n"
        " 5. Quit\n"
    )
    opt = input(" Please select action: ").strip().lower()

    if opt == "5":
        stop = True
    elif opt == "1":
        new_memo_via_editor()
    elif opt == "2":
        search_type = 'fuzzy' if SEARCH_FUZZY else 'strict'
        search_memo(search_type=search_type)
    elif opt == "3":
        recently_opened()
    elif opt == "4":
        stop = edit_config_file()
# save recently opened list
recent_open_list.save()
