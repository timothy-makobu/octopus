#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Octopus! sounds goood :-)

# * Re-encodes mp3, wav, m4a, aac and flac * #

import os
import re
import sys
import time
import json
import random
import datetime
import multiprocessing
from subprocess import Popen, PIPE, TimeoutExpired
from clint.textui import progress
from mutagen.id3 import TENC
from mutagen.mp3 import MP3

__author__ = "Timothy Makobu"

# *** configs *** #
config = {
    'lameopts': [
        '-m',
        's',
        '-q',
        '0',
        '--vbr-new',
        '-V',
        '0',
        '-b',
        '128',
        '-B',
        '192',
        '--silent'],
    'max_proc': 10,
}

with open(os.path.join(os.path.dirname(__file__), 'octoconf.json')) as more_conf:
    config.update(json.loads(more_conf.read()))

for ex in [
    x for x in list(
        config.keys()) if x not in [
            'lameopts',
        'max_proc']]:
    if not os.path.isfile(config[ex]):
        print('{} is not a file; exiting ...'.format(config[ex]))
        sys.exit()

allowed_extensions = ('.mp3', '.wav', '.acc', '.m4a', '.flac')
subprocess_timeout = 60  # longer for longer mp3s (more than 5 mins)

# *** #

locals().update(config)

# Transcode factory


def add_id3_tag(tune):
    try:
        track = MP3(tune)
        track['TENC'] = TENC(encoding=3, text='octopus')
        track.save()
    except Exception:
        pass


def reencode_mp3(tune):
    try:
        track = MP3(tune)
        if 'TENC' in track:
            if track['TENC'] == 'octopus':
                return
        Popen(
            [
                lame,
                tune] +
            lameopts,
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        os.rename(os.path.splitext(tune)[0] + '.mp3.mp3', tune)
        Popen(
            [
                mp3gain,
                '-r',
                '-q',
                tune],
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        add_id3_tag(tune)
    except (OSError, TimeoutExpired) as e:
        print(str(e))
        pass


def reencode_wav_to_mp3(tune):
    try:

        Popen(
            [
                lame,
                tune] +
            lameopts,
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        os.remove(tune)
        os.rename(tune + '.mp3', os.path.splitext(tune)[0] + '.mp3')
        Popen(
            [
                mp3gain,
                '-r',
                '-q',
                os.path.splitext(tune)[0] +
                '.mp3'],
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        add_id3_tag(os.path.splitext(tune)[0] + '.mp3')
    except (OSError, TimeoutExpired) as e:
        print(str(e))
        pass


def reencode_itunes_to_mp3(tune):
    try:
        Popen(
            [
                faad,
                '-q',
                '-o',
                os.path.splitext(tune)[0] +
                '.wav',
                tune],
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        os.remove(tune)
        Popen(
            [
                lame,
                os.path.splitext(tune)[0] +
                '.wav'] +
            lameopts,
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        os.remove(os.path.splitext(tune)[0] + '.wav')
        os.rename(
            os.path.splitext(tune)[0] +
            '.wav.mp3',
            os.path.splitext(tune)[0] +
            '.mp3')
        Popen(
            [
                mp3gain,
                '-r',
                '-q',
                os.path.splitext(tune)[0] +
                '.mp3'],
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        add_id3_tag(os.path.splitext(tune)[0] + '.mp3')
    except (OSError, TimeoutExpired) as e:
        print(str(e))
        pass


def reencode_flac_to_mp3(tune):
    try:
        Popen(
            [
                flac,
                '-ds',
                tune],
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        os.remove(tune)
        Popen(
            [
                lame,
                os.path.splitext(tune)[0] +
                '.wav'] +
            lameopts,
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        os.remove(os.path.splitext(tune)[0] + '.wav')
        os.rename(
            os.path.splitext(tune)[0] +
            '.wav.mp3',
            os.path.splitext(tune)[0] +
            '.mp3')
        Popen(
            [
                mp3gain,
                '-r',
                '-q',
                os.path.splitext(tune)[0] +
                '.mp3'],
            stdout=PIPE,
            stderr=PIPE).communicate(
            timeout=subprocess_timeout)
        add_id3_tag(os.path.splitext(tune)[0] + '.mp3')
    except (OSError, TimeoutExpired) as e:
        print(str(e))
        pass


# Utility functions
def get_tunes():
    for fileb in os.walk(path):
        for tune in fileb[2]:
            if os.path.splitext(os.path.join(fileb[0], tune))[
                    1].lower() in allowed_extensions:
                eff = os.path.join(fileb[0], tune)
                if os.path.getsize(eff) >= 1024:
                    yield str(eff)


def normalize_extension_case():
    for fileb in os.walk(path):
        for tune in fileb[2]:
            extension = os.path.splitext(os.path.join(fileb[0], tune))[1]
            if any(
                    re.match(
                        d,
                        extension,
                        re.I) for d in allowed_extensions) and any(
                    x.isupper() for x in extension):
                oldSong = os.path.join(fileb[0], tune)
                newSong = os.path.splitext(os.path.join(fileb[0], tune))[
                    0] + os.path.splitext(os.path.join(fileb[0], tune))[1].lower()
                os.rename(oldSong, newSong)


def get_dir_size():
    dirSize = 0
    for (fpath, dirs, files) in os.walk(path):
        for file in files:
            filename = os.path.join(fpath, file)
            dirSize += os.path.getsize(filename)
    return dirSize


def get_tune_count():
    tune_count = 0
    for fileb in os.walk(path):
        for tune in fileb[2]:
            if os.path.splitext(os.path.join(fileb[0], tune))[
                    1].lower() in allowed_extensions:
                tune_count += 1
    return tune_count


def dispatcher(tune):
    ext = os.path.splitext(tune)[1]
    if ext == '.mp3':
        reencode_mp3(tune)
    elif ext == '.wav':
        reencode_wav_to_mp3(tune)
    elif ext in ('.acc', '.m4a'):
        reencode_itunes_to_mp3(tune)
    elif ext == '.flac':
        reencode_flac_to_mp3(tune)


def main():
    if not os.path.isdir(path):
        input("{} is not a valid folder. Press ENTER to exit ...".format(path))
        sys.exit()

    tune_count = get_tune_count()

    if not tune_count:
        input("Found 0 tacks to re-encode. Press ENTER to exit ...")
        sys.exit()

    proc_count = multiprocessing.cpu_count() * 2
    if proc_count > config['max_proc']:
        proc_count = config['max_proc']
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
        for _ in zip(
            progress.bar(
                range(tune_count)), pool.imap(
                dispatcher, get_tunes())):
            time.sleep(random.randint(7, 14) / 10)

    print("Success!")
    end_time = time.time()
    print(
        path,
        'End time: ' +
        time.strftime(
            '%a, %b %d, %Y at %I:%M:%S %p',
            time.localtime(end_time)))
    print(
        're-encoded %d track(s) in %7.2f seconds, [%5.2f minutes]' %
        (tune_count, end_time - start_time, (end_time - start_time) / 60))
    print('Size After Re-encode: {} MiB'.format(get_dir_size() / 1048576))
    print("\nRock on! :-)")


if __name__ == '__main__':

    try:
        path = os.path.expanduser(input(
            'Type path to music folder (Example: /home/me/Music): ').strip())
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        sys.exit()
