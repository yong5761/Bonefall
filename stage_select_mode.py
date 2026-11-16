import ctypes
import pico2d
import game_framework
import stage
import save_data

_CARD_W = 480
_CARD_H = 320
_CARD_CY = 540
_CARD_CX = [420, 960, 1500]
_MAP_W = 440
_MAP_H = 248
_MAP_SCALE = _MAP_W / 1920.0
_MAP_TOP_MARGIN = 20
_SEL_SCALE = 1.06

_NORMAL_TILE = (0x7A, 0x8C, 0x99)
_WEAK_TILE = (0x9A, 0x84, 0x70)
_ENEMY_DOT = (0xEC, 0xE8, 0xE1)
_MAP_BG = (0x1C, 0x27, 0x33)
_BORDER_NORMAL = (0x4F, 0x5D, 0x68)
_BORDER_SEL = (0xE0, 0x89, 0x3A)
_CHECK = (0x7F, 0xC2, 0x8A)
_HINT_COLOR = (0x94, 0xA5, 0xB4)

_FONT_PATH = r'C:\Users\USER\Desktop\Noto_Sans_KR\NotoSansKR-VariableFont_wght.ttf'

_bg = None
_font_label = None
_font_hint = None
_sel = 0
_stage_data = []


def _centered_text(font, cx, cy, text, color):
    w, h = ctypes.c_int(), ctypes.c_int()
    pico2d.TTF_SizeUTF8(font.font, text.encode('utf-8'), ctypes.byref(w), ctypes.byref(h))
    font.draw(int(cx - w.value // 2), int(cy - h.value // 2), text, color)


def init():
    global _bg, _font_label, _font_hint, _sel, _stage_data
    _bg = pico2d.load_image('assets/menu_bg.png')
    _font_label = pico2d.load_font(_FONT_PATH, 32)
    _font_hint = pico2d.load_font(_FONT_PATH, 24)
    _sel = 0
    _stage_data = [stage.get_stage_data(i) for i in range(stage.STAGE_COUNT)]


def finish():
    global _bg, _font_label, _font_hint
    del _bg
    del _font_label
    del _font_hint


def update():
    pass


def handle_events():
    global _sel
    for event in pico2d.get_events():
        if event.type == pico2d.SDL_QUIT:
            game_framework.quit()
        elif event.type == pico2d.SDL_KEYDOWN:
            if event.key == pico2d.SDLK_ESCAPE:
                game_framework.pop_mode()
            elif event.key == pico2d.SDLK_LEFT:
                _sel = (_sel - 1) % stage.STAGE_COUNT
            elif event.key == pico2d.SDLK_RIGHT:
                _sel = (_sel + 1) % stage.STAGE_COUNT
            elif event.key == pico2d.SDLK_RETURN:
                import play_mode
                play_mode.start_stage = _sel
                game_framework.pop_mode()
                game_framework.change_mode(play_mode)


def render():
    _bg.draw(960, 540)
    cleared = save_data.load()
    for i in range(stage.STAGE_COUNT):
        _draw_card(i, cleared)
    _centered_text(_font_hint, 960, 120,
                   '\u2190  \u2192   \uc120\ud0dd       ENTER  \uc2dc\uc791       ESC  \ub4a4\ub85c',
                   _HINT_COLOR)
    pico2d.update_canvas()


def _draw_card(i, cleared):
    cx = float(_CARD_CX[i])
    cy = float(_CARD_CY)
    is_sel = (i == _sel)
    sc = _SEL_SCALE if is_sel else 1.0

    cw = _CARD_W * sc
    ch = _CARD_H * sc
    left = cx - cw / 2
    right = cx + cw / 2
    bottom = cy - ch / 2
    top = cy + ch / 2

    bw = 8 if is_sel else 4
    border = _BORDER_SEL if is_sel else _BORDER_NORMAL
    pico2d.draw_rectangle(int(left - bw), int(bottom - bw), int(right + bw), int(top + bw),
                          border[0], border[1], border[2], 255, filled=True)
    pico2d.draw_rectangle(int(left), int(bottom), int(right), int(top),
                          0x28, 0x33, 0x3E, 255, filled=True)

    map_w = _MAP_W * sc
    map_h = _MAP_H * sc
    map_left = cx - map_w / 2
    map_right = cx + map_w / 2
    map_top_y = top - _MAP_TOP_MARGIN * sc
    map_bottom_y = map_top_y - map_h

    pico2d.draw_rectangle(int(map_left), int(map_bottom_y), int(map_right), int(map_top_y),
                          _MAP_BG[0], _MAP_BG[1], _MAP_BG[2], 255, filled=True)

    tile_sz = 160 * _MAP_SCALE * sc
    tiles, enemies = _stage_data[i]
    for gx, gy, ti in tiles:
        tx = map_left + gx * 160 * _MAP_SCALE * sc
        ty = map_bottom_y + gy * 160 * _MAP_SCALE * sc
        col = _WEAK_TILE if ti >= 4 else _NORMAL_TILE
        pico2d.draw_rectangle(int(tx), int(ty), int(tx + tile_sz), int(ty + tile_sz),
                              col[0], col[1], col[2], 255, filled=True)

    dot_r = 5.0 * sc
    for ex, ey in enemies:
        mx = map_left + ex * _MAP_SCALE * sc
        my = map_bottom_y + ey * _MAP_SCALE * sc
        pico2d.draw_circle(int(mx), int(my), int(dot_r),
                           _ENEMY_DOT[0], _ENEMY_DOT[1], _ENEMY_DOT[2], 255, filled=True)

    if not is_sel:
        pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_BLEND)
        pico2d.draw_rectangle(int(map_left), int(map_bottom_y), int(map_right), int(map_top_y),
                              0, 0, 0, 102, filled=True)
        pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_NONE)

    name_cy = int((bottom + map_bottom_y) / 2)
    _centered_text(_font_label, int(cx), name_cy, f'STAGE {i + 1}', (255, 255, 255))

    if i < cleared:
        cr = 18.0 * sc
        ccx = right - 24.0 * sc
        ccy = top - 24.0 * sc
        pico2d.draw_circle(int(ccx), int(ccy), int(cr),
                           _CHECK[0], _CHECK[1], _CHECK[2], 255, filled=True)
        px1 = ccx - cr * 0.5
        py1 = ccy + cr * 0.1
        px2 = ccx - cr * 0.05
        py2 = ccy - cr * 0.45
        px3 = ccx + cr * 0.5
        py3 = ccy + cr * 0.5
        pico2d.draw_line(int(px1), int(py1), int(px2), int(py2), 20, 20, 20, 255)
        pico2d.draw_line(int(px2), int(py2), int(px3), int(py3), 20, 20, 20, 255)


def pause():
    pass


def resume():
    pass
