import pico2d
import game_framework
import ui

_image = None
_logo = None
_font_press = None
_start_time = 0.0

_FONT_PATH = 'assets/fonts/Galmuri11.ttf'
_BLINK_HALF = 0.3
_COLOR_LIGHT = (0xEC, 0xE8, 0xE1)


def init():
    global _image, _logo, _font_press, _start_time
    _image = pico2d.load_image('assets/title_screen.png')
    _logo = pico2d.load_image('assets/bonefall_logo.png')
    _font_press = pico2d.load_font(_FONT_PATH, 33)
    _start_time = pico2d.get_time()


def finish():
    global _image, _logo, _font_press
    _image = None
    _logo = None
    _font_press = None


def update():
    pass


def render():
    _image.draw(960, 540)
    _logo.clip_composite_draw(0, 0, 1266, 247, 0, '', 960, 937, 900, 176)
    if int((pico2d.get_time() - _start_time) / _BLINK_HALF) % 2 == 0:
        ui.draw_text_outlined(_font_press, 960, 150, 'Press Enter', _COLOR_LIGHT)
    pico2d.update_canvas()


def handle_events():
    import menu_mode
    for event in pico2d.get_events():
        if event.type == pico2d.SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == pico2d.SDL_KEYDOWN:
            if event.key == pico2d.SDLK_ESCAPE:
                game_framework.quit()
                return
            elif event.key == pico2d.SDLK_RETURN:
                game_framework.change_mode(menu_mode)
                return
