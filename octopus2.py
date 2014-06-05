#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import optparse
import json

from mutagen.id3 import TENC
from mutagen.mp3 import MP3

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.python import log



class Transcode(protocol.ProcessProtocol):
    """ All encoding operations """
    
    def __init__(self, tune):
        self.tune = tune



if __name__ == '__main__':
    
    reactor.spawnProcess(Transcode())
    reactor.run()
