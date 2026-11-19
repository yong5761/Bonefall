import pico2d

DRAW_SCALE = 2.0
FOOT_MARGIN = 8
WALK_FPS = 28
IDLE_FPS = 24
BLAST_SPEED_SRC = 600
BLAST_DECAY = 0.4
BLAST_AIR_LIMIT = 3.0
HITSTOP_TIME = 0.05
BLAST_RADIUS_SRC = 160
FOOT_HALF_W_SRC = 8
THROW_SPEED_SRC = 240
THROW_VY_SRC = 250
PLANT_FPS = 33
PLAYER_FRAME = 100
AIR_CONTROL_RATIO = 0.5
COLLAPSED_DECAY_MULT = 2.0
WEAK_BREAK_TIME = 1.2
BG_SCALE = 1.03
FLASH_TIME = 0.08
FLASH_ALPHA = 200

ICE_TILE_FRICTION = 0.25
ICE_PLAYER_ACCEL_MULT = 0.25
ICE_SLIDE_MULT = 3.0

FREEZE_TIME = 2.5
PLAYER_FREEZE_TIME = 0.8
ICE_BLAST_MULT = 0.35
ICE_DECAY_MULT = 6.0
FROZEN_TINT = (120, 190, 235)

SHEETS = {
    'player_idle':      ('assets/player_idle.png',      16),
    'player_walk':      ('assets/player_walk.png',      16),
    'player_jump':      ('assets/player_jump.png',      21),
    'player_plant':     ('assets/player_plant.png',     13),
    'player_blast':     ('assets/player_blast.png',     21),
    'enemy_walk':       ('assets/enemy_walk.png',       16),
    'enemy_collapse':   ('assets/enemy_collapse.png',   21),
    'enemy_fall':       ('assets/enemy_fall.png',       9),
    'bombs':            ('assets/bombs.png',            6),
    'bomb_push_fuse':   ('assets/bomb_push_fuse.png',   13),
    'bomb_pull_fuse':   ('assets/bomb_pull_fuse.png',   13),
    'tiles':            ('assets/tiles.png',            16),
    'lever':            ('assets/lever.png',            48),
}

_cache = {}


def load(path):
    if path not in _cache:
        _cache[path] = pico2d.load_image(path)
    return _cache[path]


def draw_frame(path, frame, frame_w, frame_h, x, y, flip=False, tint=None):
    img = load(path)
    left = int(frame * frame_w)
    out_w = int(frame_w * DRAW_SCALE)
    out_h = int(frame_h * DRAW_SCALE)
    if tint is not None:
        pico2d.SDL_SetTextureColorMod(img.texture, tint[0], tint[1], tint[2])
    img.clip_composite_draw(left, 0, frame_w, frame_h, 0, 'h' if flip else '', x, y, out_w, out_h)
    if tint is not None:
        pico2d.SDL_SetTextureColorMod(img.texture, 255, 255, 255)
