import pico2d

DRAW_SCALE = 2.0
FOOT_MARGIN = 8
WALK_FPS = 28
IDLE_FPS = 24
BLAST_SPEED_SRC = 600
BLAST_DECAY = 0.4
BLAST_AIR_LIMIT = 3.0
BLAST_AIR_DECAY_RATIO = 0.55
MOVING_SPEED = 120.0
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
ICE_PLAYER_ACCEL = 800.0
ICE_PLAYER_DECEL = 180.0
ICE_SLIDE_MULT = 3.0

FREEZE_TIME = 2.5
PLAYER_FREEZE_TIME = 0.8
ICE_BLAST_MULT = 0.35
ICE_DECAY_MULT = 6.0
FROZEN_TINT = (120, 190, 235)

HEAVY_SCALE = 1.3
HEAVY_WALK_RATIO = 0.55
HEAVY_BLAST_MULT = 0.45
HEAVY_STAGGER_TIME = 0.7
HEAVY_TINT = (168, 158, 146)

TURRET_FIRE_PERIOD = 2.2
TURRET_TELEGRAPH = 0.4
TURRET_AIM_LIMIT = 35.0

SHOT_SPEED = 520.0
SHOT_LIFE = 2.0
SHOT_BLAST_SRC = 420
SHOT_HALF = 8

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
    'bomb_ice_fuse':    ('assets/bomb_ice_fuse.png',    13),
    'tiles':            ('assets/tiles.png',            20),
    'lever':            ('assets/lever.png',            48),
    'switch':           ('assets/switch.png',           48),
    'jumppad':          ('assets/jumppad.png',          64),
    'pipe_mouth':       ('assets/pipe_mouth.png',       64),
    'enemy_turret_base': ('assets/enemy_turret_base.png', 1),
    'turret_barrel':     ('assets/turret_barrel.png',     1),
    'shot':              ('assets/shot.png',              1),
    'heavy_armor':       ('assets/heavy_armor.png',       1),
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
