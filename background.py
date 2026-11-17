import sprite
import camera

_BG_PATH = 'assets/background_loop.png'
_DARK_PATH = 'assets/darkness_overlay.png'

_BG_PATHS = [
    'assets/background_loop.png',
    'assets/background_mine.png',
    'assets/background_loop.png',
]

_stage_idx = 0


def get_bg_image(idx):
    return sprite.load(_BG_PATHS[idx])


def set_stage(idx):
    global _stage_idx
    if idx < 0 or idx >= len(_BG_PATHS):
        _stage_idx = 0
    else:
        _stage_idx = idx


def draw():
    out_w = int(1920 * sprite.BG_SCALE)
    out_h = int(1080 * sprite.BG_SCALE)
    cx = 960 + camera.ox
    cy = 540 + camera.oy
    get_bg_image(_stage_idx).clip_composite_draw(0, 0, 1920, 1080, 0, '', cx, cy, out_w, out_h)
    sprite.load(_DARK_PATH).clip_composite_draw(0, 0, 1920, 1080, 0, '', cx, cy, out_w, out_h)
