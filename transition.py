import pico2d

NONE = 0
HOLD = 1
OUT  = 2
IN   = 3

_HOLD_TIME = 0.7
_OUT_TIME  = 0.35
_IN_TIME   = 0.35
_LEVELS = (1, 2, 4, 8, 16, 32)
_W = 1920
_H = 1080

_state = NONE
_elapsed = 0.0
_scene_tex = None
_small_texs = {}
_initialized = False


def _init():
    global _scene_tex, _small_texs, _initialized
    r = pico2d.pico2d.renderer
    _scene_tex = pico2d.SDL_CreateTexture(
        r, pico2d.SDL_PIXELFORMAT_RGBA8888,
        pico2d.SDL_TEXTUREACCESS_TARGET, _W, _H)
    _small_texs = {}
    for b in _LEVELS:
        if b == 1:
            continue
        _small_texs[b] = pico2d.SDL_CreateTexture(
            r, pico2d.SDL_PIXELFORMAT_RGBA8888,
            pico2d.SDL_TEXTUREACCESS_TARGET, _W // b, _H // b)
    _initialized = True


def begin():
    global _state, _elapsed
    if not _initialized:
        _init()
    _state = HOLD
    _elapsed = 0.0


def active():
    return _state != NONE


def frozen():
    return _state in (OUT, IN)


def update(frame_time):
    global _state, _elapsed
    if _state == NONE:
        return False
    _elapsed += frame_time
    if _state == HOLD:
        if _elapsed >= _HOLD_TIME:
            _state = OUT
            _elapsed = 0.0
    elif _state == OUT:
        if _elapsed >= _OUT_TIME:
            _state = IN
            _elapsed = 0.0
            return True
    elif _state == IN:
        if _elapsed >= _IN_TIME:
            _state = NONE
            _elapsed = 0.0
    return False


def capture_begin():
    r = pico2d.pico2d.renderer
    pico2d.SDL_SetRenderTarget(r, _scene_tex)
    pico2d.SDL_SetRenderDrawColor(r, 0, 0, 0, 255)
    pico2d.SDL_RenderClear(r)


def capture_end():
    pico2d.SDL_SetRenderTarget(pico2d.pico2d.renderer, None)


def present():
    if _state == NONE:
        return
    r = pico2d.pico2d.renderer
    n = len(_LEVELS)
    if _state == HOLD:
        b = 1
    elif _state == OUT:
        q = _elapsed / _OUT_TIME
        idx = min(int(q * n), n - 1)
        b = _LEVELS[idx]
    else:
        q = _elapsed / _IN_TIME
        idx = max(0, n - 1 - int(q * n))
        b = _LEVELS[idx]

    src = pico2d.SDL_Rect(0, 0, _W, _H)
    dst = pico2d.SDL_Rect(0, 0, _W, _H)

    if b == 1:
        pico2d.SDL_RenderCopy(r, _scene_tex, src, dst)
        return

    sw, sh = _W // b, _H // b
    small_rect = pico2d.SDL_Rect(0, 0, sw, sh)
    small_tex = _small_texs[b]

    pico2d.SDL_SetRenderTarget(r, small_tex)
    pico2d.SDL_SetRenderDrawColor(r, 0, 0, 0, 255)
    pico2d.SDL_RenderClear(r)
    pico2d.SDL_RenderCopy(r, _scene_tex, src, small_rect)
    pico2d.SDL_SetRenderTarget(r, None)
    pico2d.SDL_RenderCopy(r, small_tex, small_rect, dst)


def reset():
    global _state
    _state = NONE
