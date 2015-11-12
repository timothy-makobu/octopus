
def test_octopus():
    try:
        from octopus import reencode_mp3
        return True
    except ImportError:
        return False
