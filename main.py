import game_framework
import pico2d
import title_mode

pico2d.open_canvas(1920, 1080, full=True)
pico2d.SDL_SetWindowFullscreen(pico2d.pico2d.window, pico2d.SDL_WINDOW_FULLSCREEN_DESKTOP)
game_framework.run(title_mode)
pico2d.close_canvas()
