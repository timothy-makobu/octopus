import os
import types
import subprocess
import unittest
from io import StringIO

import octopus

from octopus import main

class TestEverything(unittest.TestCase):

    def test_everything(self):
        octopus.PATH = os.path.dirname(os.path.abspath(__file__))
        self.assertIs(main(), None)


if __name__ == '__main__':
    unittest.main()
