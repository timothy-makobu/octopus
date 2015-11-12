
def test_octopus():
    try:
        import octopus
        return True
    except ImportError:
        return False
