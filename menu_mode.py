import pico2d
import game_framework
import save_data
import stage

_bg = None
_items = None
_items_sel = None
_sel = 0

_ITEM_COUNT = 4
_PANEL_CX = 960
_PANEL_CY = 540
_PANEL_H = 400
_ITEM_H = 100


def init():
    global _bg, _items, _items_sel, _sel
    _bg = pico2d.load_image('assets/menu_bg.png')
    _items = pico2d.load_image('assets/menu_items.png')
    _items_sel = pico2d.load_image('assets/menu_items_sel.png')
    _sel = 0


def finish():
    global _bg, _items, _items_sel
    del _bg
    del _items
    del _items_sel


def update():
    pass


def render():
    _bg.draw(_PANEL_CX, _PANEL_CY)
    top_y = _PANEL_CY + _PANEL_H // 2
    for i in range(_ITEM_COUNT):
        item_y = top_y - _ITEM_H // 2 - i * _ITEM_H
        src_bottom = _items.h - (i + 1) * _ITEM_H
        sheet = _items_sel if i == _sel else _items
        sheet.clip_draw(0, src_bottom, sheet.w, _ITEM_H, _PANEL_CX, item_y, 600, _ITEM_H)
    pico2d.update_canvas()


def handle_events():
    global _sel
    import title_mode
    for event in pico2d.get_events():
        if event.type == pico2d.SDL_QUIT:
            game_framework.quit()
        elif event.type == pico2d.SDL_KEYDOWN:
            if event.key == pico2d.SDLK_ESCAPE:
                game_framework.change_mode(title_mode)
            elif event.key == pico2d.SDLK_UP:
                _sel = (_sel - 1) % _ITEM_COUNT
            elif event.key == pico2d.SDLK_DOWN:
                _sel = (_sel + 1) % _ITEM_COUNT
            elif event.key == pico2d.SDLK_RETURN:
                _execute()


def pause():
    pass


def resume():
    pass


def _execute():
    import play_mode
    if _sel == 0:
        play_mode.start_stage = 0
        game_framework.change_mode(play_mode)
    elif _sel == 1:
        play_mode.start_stage = min(save_data.load(), stage.STAGE_COUNT - 1)
        game_framework.change_mode(play_mode)
    elif _sel == 2:
        import stage_select_mode
        game_framework.push_mode(stage_select_mode)
    elif _sel == 3:
        game_framework.quit()
