import sprite
import camera

_FORE = 'assets/scenery_fore.png'
_FORE_SHAKE = 1.45


def draw_fore():
    out_w = int(1920 * sprite.BG_SCALE)
    out_h = int(1080 * sprite.BG_SCALE)
    cx = 960 + camera.ox * _FORE_SHAKE
    cy = 540 + camera.oy * _FORE_SHAKE
    sprite.load(_FORE).clip_composite_draw(0, 0, 1920, 1080, 0, '', cx, cy, out_w, out_h)
