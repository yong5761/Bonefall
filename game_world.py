_objects = []
_player = None


def add(obj):
    _objects.append(obj)


def remove(obj):
    if obj in _objects:
        _objects.remove(obj)


def set_player(p):
    global _player
    _player = p


def get_players():
    return [_player] if _player is not None else []


def update(frame_time):
    for obj in list(_objects):
        obj.update(frame_time)


def draw():
    for obj in _objects:
        obj.draw()


def clear():
    _objects.clear()


def get_tiles():
    from tile import Tile
    return [obj for obj in _objects if isinstance(obj, Tile)]
