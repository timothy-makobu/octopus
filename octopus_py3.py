#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Octopus! sounds goood :-)

# * Re-encodes mp3, wav, m4a, aac and flac

import os
import sys
import time
import json
import random
import datetime
import multiprocessing
from subprocess import Popen, PIPE
from clint.textui import progress
from mutagen.id3 import TENC
from mutagen.mp3 import MP3

__author__ = "Timothy Makobu"

# *** configs *** #
config = {
    'lameopts':['-m', 's', '-q', '0', '--vbr-new', '-V', '0', '-b', '128', '-B', '192', '--silent'],
    'max_proc':10,
}

with open(os.path.join(os.path.dirname(__file__), 'octoconf.json')) as more_conf:
    config.update(json.loads(more_conf.read()))

for ex in [x for x in list(config.keys()) if x not in ['lameopts','max_proc']]:
    if not os.path.isfile(config[ex]):
        print('%s is not a file; exiting ...' % config[ex])
        sys.exit()
# *** #

# Transcode factory
def _add_id3_tag(tune):
    track = MP3(tune)
    track['TENC'] = TENC(encoding=3, text='octopus')
    track.save()

def reencode_mp3(tune):
    try:
        track = MP3(tune)
        if 'TENC' in track:
            if track['TENC'] == 'octopus':
                return
        _add_id3_tag(tune)
        trash_can.write(b''.join(Popen([lame, tune]+lameopts, stdout=PIPE, stderr=PIPE).communicate()))
        os.rename(os.path.splitext(tune)[0]+'.mp3.mp3', tune)
        trash_can.write(b''.join(Popen([mp3gain, '-r', '-q', tune], stdout=PIPE, stderr=PIPE).communicate()))
    except OSError as e:
        octo_error_log(path, str(e))
        pass

def reencode_wav_to_mp3(tune):
    try:
        trash_can.write(b''.join(Popen([lame, tune]+lameopts, stdout=PIPE, stderr=PIPE).communicate()))
        os.remove(tune)
        os.rename(tune+'.mp3', os.path.splitext(tune)[0] + '.mp3')
        _add_id3_tag(os.path.splitext(tune)[0] + '.mp3')
        trash_can.write(b''.join(
            Popen([mp3gain, '-r', '-q', os.path.splitext(tune)[0] + '.mp3'], stdout=PIPE, stderr=PIPE).communicate()))
    except OSError as e:
        octo_error_log(path, str(e))
        pass

def reencode_itunes_to_mp3(tune):
    try:
        trash_can.write(b''.join(
            Popen([faad, '-q', '-o', os.path.splitext(tune)[0] + '.wav', tune], stdout=PIPE, stderr=PIPE).communicate()))
        os.remove(tune)
        trash_can.write(b''.join(Popen([lame, os.path.splitext(tune)[0] + '.wav']+lameopts, stdout=PIPE, stderr=PIPE).communicate()))
        os.remove(os.path.splitext(tune)[0] + '.wav')
        os.rename(os.path.splitext(tune)[0] + '.wav.mp3', os.path.splitext(tune)[0] + '.mp3')
        _add_id3_tag(os.path.splitext(tune)[0] + '.mp3')
        trash_can.write(b''.join(
            Popen([mp3gain, '-r', '-q', os.path.splitext(tune)[0] + '.mp3'], stdout=PIPE, stderr=PIPE).communicate()))
    except OSError as e:
        octo_error_log(path, str(e))
        pass

def reencode_flac_to_mp3(tune):
    try:
        trash_can.write(b''.join(Popen([flac, '-ds', tune], stdout=PIPE, stderr=PIPE).communicate()))
        os.remove(tune)
        trash_can.write(b''.join(Popen([lame, os.path.splitext(tune)[0] + '.wav']+lameopts, stdout=PIPE, stderr=PIPE).communicate()))
        os.remove(os.path.splitext(tune)[0] + '.wav')
        os.rename(os.path.splitext(tune)[0] + '.wav.mp3', os.path.splitext(tune)[0] + '.mp3')
        _add_id3_tag(os.path.splitext(tune)[0] + '.mp3')
        trash_can.write(b''.join(
            Popen([mp3gain, '-r', '-q', os.path.splitext(tune)[0] + '.mp3'], stdout=PIPE, stderr=PIPE).communicate()))
    except OSError as e:
        octo_error_log(path, str(e))
        pass


# Utility functions
def get_tunes(path):
    for fileb in os.walk(path):
        for tune in fileb[2]:
            if os.path.splitext(os.path.join(fileb[0], tune))[1].lower() in ('.mp3','.wav','.acc','.m4a','.flac'):
                eff = os.path.join(fileb[0], tune)
                if os.path.getsize(eff) >= 1024:
                    yield str(eff)

def normalize_extension_case(path):
    for fileb in os.walk(path):
        for tune in fileb[2]:
            if os.path.splitext(os.path.join(fileb[0], tune))[1] in ('.MP3','.WAV','.ACC','.M4A','.FLAC'):
                oldSong = os.path.join(fileb[0], tune)
                newSong = os.path.splitext(os.path.join(fileb[0], tune))[0]+os.path.splitext(os.path.join(fileb[0], tune))[1].lower()
                os.rename(oldSong, newSong)

def get_dir_size(path):
    dirSize = 0
    for (fpath, dirs, files) in os.walk(path):
        for file in files:
            filename = os.path.join(fpath, file)
            dirSize += os.path.getsize(filename)
    return dirSize

def octo_log(path, message, p=True):
    if p:
        print(message.replace('<br>', '\n'))
    fh = open(os.path.join(path, 'OCTOPUS-LOG.html'), 'a')
    fh.write(message+'<br>')
    fh.close()

def octo_error_log(path, message):
    fh = open(os.path.join(path, 'error_log.html'), 'a')
    fh.write(message+'<br>')
    fh.close()

def get_tune_count(path):
    tune_count = 0
    for fileb in os.walk(path):
        for tune in fileb[2]:
            if os.path.splitext(os.path.join(fileb[0], tune))[1].lower() in ('.mp3','.wav','.acc','.m4a','.flac'):
                tune_count += 1
    return tune_count



# Managers
def dispatcher(tune):
    ext = os.path.splitext(tune)[1]
    if ext == '.mp3':
        reencode_mp3(tune)
    elif ext == '.wav':
        reencode_wav_to_mp3(tune)
    elif ext in ('.acc','.m4a'):
        reencode_itunes_to_mp3(tune)
    elif ext == '.flac':
        reencode_flac_to_mp3(tune)

def main():
    if not os.path.isdir(path):
        input("%s is not a valid folder. Press ENTER to exit ..." % path)
        sys.exit()

    curr_tune = 1
    tune_count = get_tune_count(path)

    if not tune_count:
        input("Found %d tacks to re-encode. Press ENTER to exit ..." % tune_count)
        sys.exit()
    if input('\nOk; ready to reencode %d tracks.\nHave you backed up the\n[%s]\nfolder??? \n[y/N]: ' % (tune_count, os.getcwd())).lower() != 'y':
        sys.exit()

    for log_file in ('OCTOPUS-LOG.html', 'error_log.html'):
        if os.path.isfile(os.path.join(path, log_file)):
            os.remove(os.path.join(path, log_file))

    octo_log(path, '<head><title>OCTOPUS-LOG</title></head>', p=False)
    octo_log(path, '<b>Octopus!</b> Sounds goood :)<br>', p=False)
    proc_count = multiprocessing.cpu_count() * 2
    if proc_count > config['max_proc']: proc_count = config['max_proc']
    start_time = time.time()
    octo_log(path, 'Spawning [[ %d ]] workers ...' % proc_count)
    octo_log(path, 'Start time: '+ time.strftime('%a, %b %d, %Y at %I:%M:%S %p', time.localtime(start_time)))
    octo_log(path, 'Setting track(s) extension(s) to lower case ...')
    normalize_extension_case(path)
    octo_log(path, 'Size Before Re-encode: %d MiB' % (get_dir_size(path)/1048576))
    octo_log(path, 'Re-encoding %d track(s) ...<br>' % tune_count)

    pool = multiprocessing.Pool(proc_count)
    for i,exhaust in zip(progress.bar(range(tune_count)), pool.imap(dispatcher, get_tunes(path))):
        time.sleep(random.randint(7,14) / 10)
        del(exhaust)


    octo_log(path, "<br>Success!<br>")
    end_time = time.time()
    octo_log(path, 'End time: '+time.strftime('%a, %b %d, %Y at %I:%M:%S %p', time.localtime(end_time)))
    octo_log(path, 're-encoded %d track(s) in %7.2f seconds, [%5.2f minutes]' % (tune_count, end_time - start_time, (end_time - start_time)/60))
    octo_log(path, 'Size After Re-encode: %d MiB' % (get_dir_size(path)/1048576))
    print("\nRock on! :-)")
    octo_log(path, '<p><a href="https://github.com/timkofu/octopus">GitHub</a>', p=False)


if __name__ == '__main__':

    try:
        locals().update(config)
        trash_can = open(os.devnull, 'wb')
        path = input('Type path to music folder (Example: /home/me/Music): ').strip()
        sys.exit(main())
    except KeyboardInterrupt:
        print();sys.exit()
