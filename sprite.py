import pico2d

DRAW_SCALE = 2.0
FOOT_MARGIN = 8
WALK_FPS = 28
IDLE_FPS = 6
PLAYER_FRAME = 100

SHEETS = {
    'player_idle':      ('assets/player_idle.png',      4),
    'player_walk':      ('assets/player_walk.png',      16),
    'player_jump':      ('assets/player_jump.png',      11),
    'player_plant':     ('assets/player_plant.png',     4),
    'player_blast':     ('assets/player_blast.png',     6),
    'enemy_walk':       ('assets/enemy_walk.png',       8),
    'enemy_collapse':   ('assets/enemy_collapse.png',   6),
    'enemy_fall':       ('assets/enemy_fall.png',       3),
    'bombs':            ('assets/bombs.png',            4),
    'bomb_push_fuse':   ('assets/bomb_push_fuse.png',   4),
    'bomb_pull_fuse':   ('assets/bomb_pull_fuse.png',   4),
    'tiles':            ('assets/tiles.png',            12),
}

_cache = {}


def load(path):
    if path not in _cache:
        _cache[path] = pico2d.load_image(path)
    return _cache[path]


def draw_frame(path, frame, frame_w, frame_h, x, y, flip=False):
    img = load(path)
    left = int(frame * frame_w)
    out_w = int(frame_w * DRAW_SCALE)
    out_h = int(frame_h * DRAW_SCALE)
    img.clip_composite_draw(left, 0, frame_w, frame_h, 0, 'h' if flip else '', x, y, out_w, out_h)
