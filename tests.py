import sys
import unittest
from io import StringIO

from octopus import (
    config,
    add_id3_tag,
)


class BlanketTests(unittest.TestCase):

    def setUp(self):
        self.fake_mp3 = StringIO()

    def test_add_id3_tag(self):
        self.assertIs(add_id3_tag(self.fake_mp3), None)

if __name__ == '__main__':
    unittest.main()
