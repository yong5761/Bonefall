import sprite
import camera

_MID  = 'assets/scenery_mid.png'
_FORE = 'assets/scenery_fore.png'
_MID_SHAKE  = 0.55
_FORE_SHAKE = 1.45


def draw_mid():
    out_w = int(1920 * sprite.BG_SCALE)
    out_h = int(1080 * sprite.BG_SCALE)
    cx = 960 + camera.ox * _MID_SHAKE
    cy = 540 + camera.oy * _MID_SHAKE
    sprite.load(_MID).clip_composite_draw(0, 0, 1920, 1080, 0, '', cx, cy, out_w, out_h)


def draw_fore():
    out_w = int(1920 * sprite.BG_SCALE)
    out_h = int(1080 * sprite.BG_SCALE)
    cx = 960 + camera.ox * _FORE_SHAKE
    cy = 540 + camera.oy * _FORE_SHAKE
    sprite.load(_FORE).clip_composite_draw(0, 0, 1920, 1080, 0, '', cx, cy, out_w, out_h)
