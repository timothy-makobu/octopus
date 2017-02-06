import os
import types
import subprocess
import unittest
from io import StringIO

import octopus

from octopus import (
    add_id3_tag,
    reencode_mp3_and_wav,
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

class TestUtilityFunctions(TestBase):
    def test_utility_functions(self):
        self.assertIsInstance(get_tunes(), types.GeneratorType)
        self.assertIs(normalize_extension_case(), None)
        self.assertIsInstance(get_dir_size(), int)
        self.assertIsInstance(get_tune_count(), int)
        self.assertIs(main(), None)


if __name__ == '__main__':
    unittest.main()
