import os
import types
import subprocess
import unittest

import octopus

from octopus import (
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


class FullTest(unittest.TestCase):

    test_music_extensions = (
        "mp3", "wav", "flac", "aac", "m4a"
    )
    test_music_file_urls = (
        "http://thesixteendigital.com.s3.amazonaws.com/testfiles/Hallelujah.m4a",
        "http://thesixteendigital.com.s3.amazonaws.com/testfiles/Hallelujah.mp3",
        "http://thesixteendigital.com.s3.amazonaws.com/testfiles/E+questa+vita+un+lampo+Studio+Master.flac",
        "http://www.ee.columbia.edu/~dpwe/sounds/music/around_the_world-atc.wav",
    )

    def setUp(self):
        octopus.path = os.path.dirname(os.path.abspath(__file__))
        for url in self.test_music_file_urls:
            subprocess.call(["aria2c", url])

    def tearDown(self):

        for e in [f.split("/")[-1] for f in self.test_music_file_urls]:
            try:
                os.unlink(e)
            except FileNotFoundError:
                pass


    def test_full(self):
        self.assertIsInstance(get_tunes(), types.GeneratorType)
        self.assertIs(normalize_extension_case(), None)
        self.assertIsInstance(get_dir_size(), int)
        self.assertIsInstance(get_tune_count(), int)
        self.assertIs(main(), None)


if __name__ == '__main__':
    unittest.main()
