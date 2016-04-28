import os
import types
import subprocess
import unittest
from io import StringIO

import octopus

from octopus import (
    add_id3_tag,
    reencode_mp3_and_wav,
    reencode_flac_to_mp3,
    reencode_itunes_to_mp3,
    dispatcher,
    get_tunes,
    normalize_extension_case,
    get_dir_size,
    get_tune_count,
    main
)


class TestBase(unittest.TestCase):
    octopus.PATH = os.path.dirname(os.path.abspath(__file__))


class TestReencodeFunctions(TestBase):
    def test_reencode_functions(self):
        self.assertIs(add_id3_tag("wave.mp3"), None)
        self.assertIs(reencode_mp3_and_wav("wave.mp3"), None)
        self.assertIs(reencode_mp3_and_wav("8_Channel_ID.wav"), None)
        self.assertIs(reencode_flac_to_mp3("BIS1536-001-flac_24.flac"), None)
        self.assertIs(reencode_itunes_to_mp3("MediaConvert_Test_7%20-%20AAC_AAC-LC_Stereo_96kbps_44100Hz%20-%20Eric_Clapton-Wonderful_Tonight.AAC"), None)
        self.assertIs(dispatcher("iTunes_test2_AAC-LC_v4_Stereo_VBR_128kbps_44100Hz.m4a"), None)


class TestUtilityFunctions(TestBase):
    def test_utility_functions(self):
        self.assertIsInstance(get_tunes(), types.GeneratorType)
        self.assertIs(normalize_extension_case(), None)
        self.assertIsInstance(get_dir_size(), int)
        self.assertIsInstance(get_tune_count(), int)
        self.assertIs(main(), None)


if __name__ == '__main__':
    unittest.main()
