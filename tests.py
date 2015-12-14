import os
import types
import subprocess
import unittest
from io import StringIO

import octopus

from octopus import (
    add_id3_tag,
    reencode_mp3,
    reencode_wav_to_mp3,
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

    test_music_extensions = (
        "mp3", "wav", "flac", "aac", "m4a"
    )

    def tearDown(self):
        for e in self.test_music_extensions:
            try:
                os.unlink("fake.{}".format(e))
            except FileNotFoundError:
                pass

    def _make_fake_files(self):
        for e in self.test_music_extensions:
            subprocess.call(["touch", "fake.{}".format(e)])


class TestTranscodeFunctions(TestBase):

    def setUp(self):
        self.fake_mp3_buf = StringIO()
        self._make_fake_files()

    def test_transcode_functions(self):
        self.assertIs(add_id3_tag(self.fake_mp3_buf), None)
        self.assertIs(reencode_mp3("fake.mp3"), None)
        self.assertIs(reencode_wav_to_mp3("fake.wav"), None)
        self.assertIs(reencode_flac_to_mp3("fake.flac"), None)
        self.assertIs(reencode_itunes_to_mp3("fake.aac"), None)
        self.assertIs(dispatcher("fake.aac"), None)


class TestUtilityFunctions(TestBase):

    def setUp(self):
        octopus.path = os.path.dirname(os.path.abspath(__file__))
        self._make_fake_files()

    def test_utility_functions(self):
        self.assertIsInstance(get_tunes(), types.GeneratorType)
        self.assertIs(normalize_extension_case(), None)
        self.assertIsInstance(get_dir_size(), int)
        self.assertIsInstance(get_tune_count(), int)
        self.assertIs(main(), None)


if __name__ == '__main__':
    unittest.main()
