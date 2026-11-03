import pico2d
import camera
import game_world
import stage
import sprite
import bomb
from player import Player


def main():
    pico2d.open_canvas(1920, 1080, full=True)

    for tile in stage.build_stage():
        game_world.add(tile)

    player = Player(400, 420)
    game_world.set_player(player)

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
                elif event.key == pico2d.SDLK_z:
                    bomb.place(player.x, player.y)
                elif event.key in (pico2d.SDLK_LSHIFT, pico2d.SDLK_RSHIFT):
                    bomb.toggle_type()
                player.handle_event(event)
            elif event.type == pico2d.SDL_KEYUP:
                keys.discard(event.key)

        camera.update(frame_time)
        player.update(frame_time, keys)
        game_world.update(frame_time)

        pico2d.draw_rectangle(0, 0, 1920, 1080, r=43, g=58, b=74, a=255, filled=True)
        game_world.draw()
        player.draw()

        hud_frame = bomb.get_type() * 2
        hud_path, _ = sprite.SHEETS['bombs']
        sprite.draw_frame(hud_path, hud_frame, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME, 100, 980)

        pico2d.update_canvas()

    pico2d.close_canvas()


if __name__ == '__main__':
    main()
