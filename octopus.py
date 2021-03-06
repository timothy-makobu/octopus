#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Octopus! sounds goood :-)
''' * Re-encodes mp3 and wav * '''

import os
import re
import sys
import time
import json
import random
import multiprocessing
from subprocess import Popen, PIPE, TimeoutExpired
from clint.textui import progress
import taglib

# *** Configs *** #
CONFIG = {
    'lameopts': [
        '-m', 's', '-q', '0', '--vbr-new', '-V',
        '0', '-b', '256', '-B', '320', '--silent'
    ], 'max_proc': 10,
}

config_file = os.environ.get("MY_OCTOCONF") or\
 os.path.join(os.path.dirname(__file__), 'octoconf.json')
with open(config_file) as more_conf:
    CONFIG.update(json.loads(more_conf.read()))

for ex in [x for x in list(CONFIG.keys()) if x not in\
['lameopts', 'max_proc', 'timeout']]:
    if not os.path.isfile(CONFIG[ex]):
        print('{} is not a file; exiting ...'.format(CONFIG[ex]))
        sys.exit()

ALLOWED_EXTENSIONS = ('.mp3', '.wav')

# *** #

#list(map(exec, ("{0}={1}".format(x[0],x[1]) for x in CONFIG.items())))
#locals().update(CONFIG)

TIMEOUT = int(CONFIG["timeout"])


# Transcode factory

def add_id3_tag(tune):
    ''' Mark an mp3 as processed so octopus ignores it if fed again '''

    try:
        track = taglib.File(tune)
        track.tags['TENC'] = 'octopus'
        track.save()
    except Exception as ex:
        print(str(ex))


def normalize(tune):
    """ Set track to reference decibel level of 89db """

    Popen([CONFIG['mp3gain'], '-r', tune], \
        stdout=PIPE, stderr=PIPE).communicate(timeout=TIMEOUT)


def reencode_mp3_and_wav(tune):
    ''' Re-encodes an mp3 applying psycho-acoustics and true stereo '''

    try:

        file_ext = os.path.splitext(tune)[1]
        if file_ext == '.mp3':
            track = taglib.File(tune)
            tenc_tag = track.tags.get('TENC')
            if tenc_tag and tenc_tag[0] == 'octopus':
                return

        Popen([CONFIG['lame'], tune] + CONFIG['lameopts'],\
            stdout=PIPE, stderr=PIPE).communicate(timeout=TIMEOUT)

        if file_ext == '.mp3':
            os.rename(os.path.splitext(tune)[0]+'.mp3.mp3', tune)
        elif file_ext == '.wav':
            os.remove(tune)
            tune = os.path.splitext(tune)[0]+'.mp3'

        add_id3_tag(tune)
        normalize(tune)

    except (OSError, TimeoutExpired) as err:
        print(str(err))


# Utility functions
def get_tunes():
    ''' Yields full paths of supported music files in the directory '''

    for fileb in os.walk(PATH):
        for tune in fileb[2]:
            if os.path.splitext(os.path.join(fileb[0], tune))[1].lower()\
             in ALLOWED_EXTENSIONS:
                eff = os.path.join(fileb[0], tune)
                if os.path.getsize(eff) >= 1024:
                    yield str(eff)


def normalize_extension_case():
    ''' Sets file extensions to lowercase '''

    for fileb in os.walk(PATH):
        for tune in fileb[2]:
            extension = os.path.splitext(os.path.join(fileb[0], tune))[1]
            if any(re.match(d, extension, re.I) for d in ALLOWED_EXTENSIONS)\
            and any(x.isupper() for x in extension):
                old_song = os.path.join(fileb[0], tune)
                new_song = os.path.splitext(os.path.join(fileb[0], tune))[0]\
                 + os.path.splitext(os.path.join(fileb[0], tune))[1].lower()
                os.rename(old_song, new_song)


def get_dir_size():
    ''' Returns total sizes of all supported files in directory '''

    dir_size = 0
    for (fpath, _, files) in os.walk(PATH):
        for file in files:
            file_name = os.path.join(fpath, file)
            dir_size += os.path.getsize(file_name)
    return dir_size


def get_tune_count():
    ''' Gets total number of supported music files in directory '''

    tune_count = 0
    for fileb in os.walk(PATH):
        for tune in fileb[2]:
            if os.path.splitext(os.path.join(fileb[0], tune))[1].lower()\
             in ALLOWED_EXTENSIONS:
                tune_count += 1
    return tune_count


def main():
    ''' Commander '''

    if not os.path.isdir(PATH):
        print("{} is not a valid folder.".format(PATH))
        sys.exit()

    tune_count = get_tune_count()

    if not tune_count:
        print("Found 0 tacks to re-encode.")
        sys.exit()

    proc_count = multiprocessing.cpu_count()
    if proc_count > CONFIG['max_proc']:
        proc_count = CONFIG['max_proc']
    start_time = time.time()
    print('\nSpawning [[ {} ]] workers ...'.format(proc_count))
    print(
        'Start time: ' +
        time.strftime(
            '%a, %b %d, %Y at %I:%M:%S %p',
            time.localtime(start_time)))
    print('Setting track(s) extension(s) to lower case ...')
    normalize_extension_case()
    print(
        'Size Before Re-encode: {} MiB'.format(get_dir_size() / 1048576))
    print('Re-encoding {} track(s) ...'.format(tune_count))

    with multiprocessing.Pool(proc_count) as pool:
        for _ in zip(progress.bar(range(tune_count)),\
        pool.imap(reencode_mp3_and_wav, get_tunes())):
            time.sleep(random.randint(7, 14) / 10)

    print("Success!")
    end_time = time.time()
    print(PATH, 'End time: ' + time.strftime('%a, %b %d, %Y at %I:%M:%S %p',\
            time.localtime(end_time)))
    print('re-encoded %d track(s) in %7.2f seconds, [%5.2f minutes]' %\
        (tune_count, end_time - start_time, (end_time - start_time) / 60))
    print('Size After Re-encode: {} MiB'.format(get_dir_size() / 1048576))
    print("\nRock on! :-)")



if __name__ == '__main__':

    try:
        PATH = os.path.expanduser(input(
            'Type path to music folder (Example: /home/me/Music): ').strip())
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        sys.exit()
