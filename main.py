import pico2d
import camera
import game_world
import stage
from player import Player


def main():
    pico2d.open_canvas(1920, 1080, full=True)

    for tile in stage.build_stage():
        game_world.add(tile)

    player = Player(400, 420)

    prev_ticks = pico2d.SDL_GetTicks()
    keys = set()
    running = True

    while running:
        ticks = pico2d.SDL_GetTicks()
        frame_time = min((ticks - prev_ticks) / 1000.0, 0.05)
        prev_ticks = ticks

        for event in pico2d.get_events():
            if event.type == pico2d.SDL_QUIT:
                running = False
            elif event.type == pico2d.SDL_KEYDOWN:
                keys.add(event.key)
                if event.key == pico2d.SDLK_ESCAPE:
                    running = False
                elif event.key == pico2d.SDLK_f:
                    camera.shake(14, 0.35)
                player.handle_event(event)
            elif event.type == pico2d.SDL_KEYUP:
                keys.discard(event.key)

        camera.update(frame_time)
        player.update(frame_time, keys)
        game_world.update(frame_time)

        pico2d.draw_rectangle(0, 0, 1920, 1080, r=43, g=58, b=74, a=255, filled=True)
        game_world.draw()
        player.draw()

        pico2d.update_canvas()

    pico2d.close_canvas()


if __name__ == '__main__':
    main()
