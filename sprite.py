import pico2d

DRAW_SCALE = 2.0
FOOT_MARGIN = 8
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
