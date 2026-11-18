import sprite
import camera

_DARK_PATH = 'assets/darkness_overlay.png'

_stage_idx = 0


def get_bg_image(idx):
    import stage as _stage
    return sprite.load('assets/' + _stage.get_bg_name(idx))


def set_stage(idx):
    global _stage_idx
    import stage as _stage
    if idx < 0 or idx >= _stage.STAGE_COUNT:
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
