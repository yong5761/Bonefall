import pico2d
import game_framework
import camera
import save_data
import game_world
import stage
import sprite
import bomb
import background
import fx
from player import Player

start_stage = 0

_player = None
_stage_idx = 0
_prev_ticks = 0
_keys = None


def _load_stage(idx):
    global _stage_idx
    _stage_idx = idx
    bomb.remove_active()
    game_world.clear()
    for tile in stage.build_stage(idx):
        game_world.add(tile)
    game_world.set_player(_player)
    for e in stage.build_enemies(idx):
        game_world.add(e)
    sx, sy = stage.get_player_start(idx)
    _player.x = float(sx)
    _player.y = float(sy)
    _player.start_x = float(sx)
    _player.start_y = float(sy)
    _player.vx = 0.0
    _player.vy = 0.0
    _player.state = 0
    _player.frame = 0.0
    _player._control_vx = 0.0
    _player.died = False


def init():
    global _player, _prev_ticks, _keys
    _keys = set()
    _prev_ticks = pico2d.SDL_GetTicks()
    sx, sy = stage.get_player_start(start_stage)
    _player = Player(sx, sy)
    _load_stage(start_stage)


def finish():
    global _player
    bomb.remove_active()
    game_world.clear()
    _player = None


def update():
    global _prev_ticks
    ticks = pico2d.SDL_GetTicks()
    frame_time = min((ticks - _prev_ticks) / 1000.0, 0.05)
    _prev_ticks = ticks

    camera.update(frame_time)
    fx.update(frame_time)
    if camera.is_hitstop():
        return
    _player.update(frame_time, _keys)
    game_world.update(frame_time)

    if _player.died:
        _load_stage(_stage_idx)
    elif not game_world.get_enemies():
        save_data.save(_stage_idx + 1)
        _load_stage((_stage_idx + 1) % 3)


def render():
    background.draw()
    game_world.draw_tiles()
    fx.draw_all_shadows()
    game_world.draw_enemies()
    game_world.draw_bombs()
    fx.draw_bomb_fuse_lights()
    _player.draw()
    game_world.draw_explosions()
    fx.draw_explosion_lights()
    fx.draw_vignette()
    fx.draw_flash()
    hud_frame = bomb.get_type() * 2
    hud_path, _ = sprite.SHEETS['bombs']
    sprite.draw_frame(hud_path, hud_frame, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME, 100, 980)
    pico2d.update_canvas()


def handle_events():
    import menu_mode
    for event in pico2d.get_events():
        if event.type == pico2d.SDL_QUIT:
            game_framework.quit()
        elif event.type == pico2d.SDL_KEYDOWN:
            _keys.add(event.key)
            if event.key == pico2d.SDLK_ESCAPE:
                game_framework.change_mode(menu_mode)
            elif event.key == pico2d.SDLK_f:
                camera.shake(14, 0.35, 1.0, 0.0)
            elif event.key in (pico2d.SDLK_1, pico2d.SDLK_2, pico2d.SDLK_3):
                _load_stage(event.key - pico2d.SDLK_1)
            elif event.key in (pico2d.SDLK_LSHIFT, pico2d.SDLK_RSHIFT):
                bomb.toggle_type()
            _player.handle_event(event)
        elif event.type == pico2d.SDL_KEYUP:
            _keys.discard(event.key)


def pause():
    pass


def resume():
    pass
