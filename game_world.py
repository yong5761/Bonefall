_objects = []


def add(obj):
    _objects.append(obj)


def update(frame_time):
    for obj in _objects:
        obj.update(frame_time)


def draw():
    for obj in _objects:
        obj.draw()


def clear():
    _objects.clear()


def get_tiles():
    from tile import Tile
    return [obj for obj in _objects if isinstance(obj, Tile)]
