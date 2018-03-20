from datetime import datetime
from pathlib import Path


ATTRIBUTE_LOOKUP = {
    'TITL': 'title',
    'DATE': 'date',
    'TAGS': 'tags',
}


def create_template_file(fpath):
    if not fpath:
        raise ValueError('empty file name')
    if fpath.exists():
        raise FileExistsError('file %s already exists' % fpath.as_posix())

    with fpath.open('w', encoding='utf-8') as f:
        f.writelines([
            "TITL: %s\n" % fpath.stem.replace('_', ' '),
            "DATE: %s\n" % datetime.strftime(datetime.today(), '%m-%d-%Y'),
            "TAGS: \n",
            "============================================================\n",
        ])


def _advance(f):
    line = f.readline().rstrip()
    p = line.find(':')
    if p < 0:
        return '', line
    else:
        return line[:p], line[p+1:].lstrip()


def import_template_file(fpath):
    if not fpath or not fpath.exists() or not fpath.is_file():
        raise FileNotFoundError("No text file found by name %s" % fpath.as_posix())

    contents = {}
    with fpath.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            p = line.find(':')
            if p < 0:
                # reached the end of the attribute lines
                break
            attribute, value = line[:p], line[p+1:].strip()
            if attribute == 'TITL':
                contents['title'] = value
            elif attribute == 'DATE':
                try:
                    contents['date'] = datetime.strptime(value, '%m-%d-%Y')
                except:
                    contents['date'] = datetime.today()
            elif attribute == 'TAGS':
                contents['tags'] = [tag.strip() for tag in value.split(',') if tag]
        # once reached the end of attribute lines, the rest are body contents
        contents['body'] = ''.join(line for line in f)
    return contents
