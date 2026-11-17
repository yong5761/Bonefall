import sprite
import camera

_BG_PATH = 'assets/background_loop.png'
_DARK_PATH = 'assets/darkness_overlay.png'

_BG_PATHS = [
    'assets/background_loop.png',
    'assets/background_loop.png',
    'assets/background_loop.png',
]


def get_bg_image(idx):
    return sprite.load(_BG_PATHS[idx])


def draw():
    out_w = int(1920 * sprite.BG_SCALE)
    out_h = int(1080 * sprite.BG_SCALE)
    cx = 960 + camera.ox
    cy = 540 + camera.oy
    sprite.load(_BG_PATH).clip_composite_draw(0, 0, 1920, 1080, 0, '', cx, cy, out_w, out_h)
    sprite.load(_DARK_PATH).clip_composite_draw(0, 0, 1920, 1080, 0, '', cx, cy, out_w, out_h)
