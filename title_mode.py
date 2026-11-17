import ctypes
import pico2d
import game_framework

_image = None
_font = None
_start_time = 0.0

_FONT_PATH = r'C:\Users\USER\Desktop\Noto_Sans_KR\NotoSansKR-VariableFont_wght.ttf'
_FONT_SIZE = 48
_BLINK_HALF = 0.3


def _draw_centered(font, cx, y, text, color):
    w, h = ctypes.c_int(), ctypes.c_int()
    pico2d.TTF_SizeUTF8(font.font, text.encode('utf-8'), ctypes.byref(w), ctypes.byref(h))
    font.draw(cx - w.value // 2, y, text, color)


def init():
    global _image, _font, _start_time
    _image = pico2d.load_image('assets/title_screen.png')
    _font = pico2d.load_font(_FONT_PATH, _FONT_SIZE)
    _start_time = pico2d.get_time()


def finish():
    global _image, _font
    del _image
    del _font


def update():
    pass


def render():
    _image.draw(960, 540)
    if int((pico2d.get_time() - _start_time) / _BLINK_HALF) % 2 == 0:
        _draw_centered(_font, 960, 360, 'Press Enter', (255, 255, 255))
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
