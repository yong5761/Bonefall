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


def get_enemies():
    from enemy import Enemy
    return [obj for obj in _objects if isinstance(obj, Enemy)]


def get_bombs():
    from bomb import Bomb
    return [obj for obj in _objects if isinstance(obj, Bomb)]


def get_explosions():
    from explosion import Explosion
    return [obj for obj in _objects if isinstance(obj, Explosion)]


def draw_tiles():
    from tile import Tile
    for obj in _objects:
        if isinstance(obj, Tile):
            obj.draw()


def draw_enemies():
    from enemy import Enemy
    for obj in _objects:
        if isinstance(obj, Enemy):
            obj.draw()


def draw_bombs():
    from bomb import Bomb
    for obj in _objects:
        if isinstance(obj, Bomb):
            obj.draw()


def get_levers():
    from lever import Lever
    return [obj for obj in _objects if isinstance(obj, Lever)]


def draw_levers():
    from lever import Lever
    for obj in _objects:
        if isinstance(obj, Lever):
            obj.draw()


def draw_explosions():
    from explosion import Explosion
    for obj in _objects:
        if isinstance(obj, Explosion):
            obj.draw()


def get_switches():
    from switch import Switch
    return [obj for obj in _objects if isinstance(obj, Switch)]


def draw_switches():
    from switch import Switch
    for obj in _objects:
        if isinstance(obj, Switch):
            obj.draw()


def get_cannons():
    from cannon import Cannon
    return [obj for obj in _objects if isinstance(obj, Cannon)]


def draw_cannons():
    from cannon import Cannon
    for obj in _objects:
        if isinstance(obj, Cannon):
            obj.draw()


def get_pads():
    from pad import Pad
    return [obj for obj in _objects if isinstance(obj, Pad)]


def draw_pads():
    from pad import Pad
    for obj in _objects:
        if isinstance(obj, Pad):
            obj.draw()
