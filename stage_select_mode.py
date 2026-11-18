import pico2d
import game_framework
import stage
import save_data
import background
import sprite
import ui

_CARD_W = 400
_CARD_H = 290
_MAP_W = 360
_MAP_H = 202
_MAP_SCALE = _MAP_W / 1920.0
_MAP_TOP_MARGIN = 16
_SEL_SCALE = 1.06
_PER_PAGE = 8

_BORDER_NORMAL = (0x4F, 0x5D, 0x68)
_BORDER_SEL = (0xE0, 0x89, 0x3A)
_CHECK = (0x7F, 0xC2, 0x8A)
_HINT_COLOR = (0x94, 0xA5, 0xB4)

_FONT_PATH = 'assets/fonts/Galmuri11.ttf'

_bg = None
_font_label = None
_font_hint = None
_sel = 0
_stage_data = []


def init():
    global _bg, _font_label, _font_hint, _sel, _stage_data
    _bg = pico2d.load_image('assets/menu_bg.png')
    _font_label = pico2d.load_font(_FONT_PATH, 33)
    _font_hint = pico2d.load_font(_FONT_PATH, 22)
    _sel = 0
    _stage_data = [stage.get_stage_data(i) for i in range(stage.STAGE_COUNT)]


def finish():
    global _bg, _font_label, _font_hint
    _bg = None
    _font_label = None
    _font_hint = None


def update():
    pass


def handle_events():
    global _sel
    for event in pico2d.get_events():
        if event.type == pico2d.SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == pico2d.SDL_KEYDOWN:
            if event.key == pico2d.SDLK_ESCAPE:
                game_framework.pop_mode()
                return
            elif event.key == pico2d.SDLK_LEFT:
                _sel = (_sel - 1) % stage.STAGE_COUNT
            elif event.key == pico2d.SDLK_RIGHT:
                _sel = (_sel + 1) % stage.STAGE_COUNT
            elif event.key == pico2d.SDLK_UP:
                local_row = (_sel % _PER_PAGE) // 4
                if local_row > 0:
                    _sel -= 4
            elif event.key == pico2d.SDLK_DOWN:
                local_row = (_sel % _PER_PAGE) // 4
                if local_row < 1 and _sel + 4 < stage.STAGE_COUNT:
                    _sel += 4
            elif event.key == pico2d.SDLK_RETURN:
                import play_mode
                play_mode.start_stage = _sel
                game_framework.change_mode(play_mode)
                return


def render():
    _bg.draw(960, 540)
    cleared = save_data.load()
    total_pages = (stage.STAGE_COUNT + _PER_PAGE - 1) // _PER_PAGE
    page = _sel // _PER_PAGE
    start = page * _PER_PAGE
    end = min(start + _PER_PAGE, stage.STAGE_COUNT)
    for i in range(start, end):
        _draw_card(i, i - start, cleared)
    ui.draw_text_outlined(_font_hint, 960, 150,
                   '\u2190 \u2192 \u2191 \u2193  \uc120\ud0dd      ENTER  \uc2dc\uc791      ESC  \ub4a4\ub85c',
                   _HINT_COLOR)
    if total_pages > 1:
        ui.draw_text_outlined(_font_hint, 960, 90,
                       f'{page + 1} / {total_pages}', _HINT_COLOR)
    pico2d.update_canvas()


def _draw_card(stage_idx, local_idx, cleared):
    i = stage_idx
    col = local_idx % 4
    row = local_idx // 4
    cx = float(300 + col * 440)
    cy = float(703 - row * 326)
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

    map_cx = (map_left + map_right) / 2
    map_cy = (map_bottom_y + map_top_y) / 2
    background.get_bg_image(i).clip_composite_draw(
        0, 0, 1920, 1080, 0, '',
        int(map_cx), int(map_cy), int(map_w), int(map_h))

    pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_BLEND)
    pico2d.draw_rectangle(int(map_left), int(map_bottom_y), int(map_right), int(map_top_y),
                          0, 0, 0, 90, filled=True)
    pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_NONE)

    tile_sz = int(160 * _MAP_SCALE * sc)
    tile_img = sprite.load(sprite.SHEETS['tiles'][0])
    tiles, enemies = _stage_data[i]
    for gx, gy, ti in tiles:
        tcx = map_left + (gx + 0.5) * 160 * _MAP_SCALE * sc
        tcy = map_bottom_y + (gy + 0.5) * 160 * _MAP_SCALE * sc
        half = tile_sz / 2
        if (tcx - half < map_left or tcx + half > map_right or
                tcy - half < map_bottom_y or tcy + half > map_top_y):
            continue
        tile_img.clip_composite_draw(ti * 80, 0, 80, 80, 0, '',
                                     int(tcx), int(tcy), tile_sz, tile_sz)

    spr_sz = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE * _MAP_SCALE * sc)
    enemy_img = sprite.load(sprite.SHEETS['enemy_walk'][0])
    for ex, ey in enemies:
        ecx = map_left + ex * _MAP_SCALE * sc
        ecy = map_bottom_y + ey * _MAP_SCALE * sc
        half = spr_sz / 2
        if (ecx - half < map_left or ecx + half > map_right or
                ecy - half < map_bottom_y or ecy + half > map_top_y):
            continue
        enemy_img.clip_composite_draw(0, 0, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME, 0, '',
                                      int(ecx), int(ecy), spr_sz, spr_sz)

    ps_x, ps_y = stage.get_player_start(i)
    pcx = map_left + ps_x * _MAP_SCALE * sc
    pcy = map_bottom_y + ps_y * _MAP_SCALE * sc
    half = spr_sz / 2
    if not (pcx - half < map_left or pcx + half > map_right or
            pcy - half < map_bottom_y or pcy + half > map_top_y):
        sprite.load(sprite.SHEETS['player_idle'][0]).clip_composite_draw(
            0, 0, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME, 0, '',
            int(pcx), int(pcy), spr_sz, spr_sz)

    if not is_sel:
        pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_BLEND)
        pico2d.draw_rectangle(int(map_left), int(map_bottom_y), int(map_right), int(map_top_y),
                              0, 0, 0, 102, filled=True)
        pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_NONE)

    name_cy = int((bottom + map_bottom_y) / 2)
    ui.draw_text_outlined(_font_label, int(cx), name_cy, f'STAGE {i + 1}', (255, 255, 255))

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
