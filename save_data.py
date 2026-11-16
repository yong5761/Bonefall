import json

_SAVE_PATH = 'save.json'
_cleared = 0


def _read():
    global _cleared
    try:
        with open(_SAVE_PATH, 'r') as f:
            _cleared = json.load(f).get('cleared', 0)
    except Exception:
        _cleared = 0


_read()


def load():
    return _cleared


def save(cleared):
    global _cleared
    if cleared <= _cleared:
        return
    _cleared = cleared
    try:
        with open(_SAVE_PATH, 'w') as f:
            json.dump({'cleared': _cleared}, f)
    except Exception:
        pass
