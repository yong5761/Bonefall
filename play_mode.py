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
import ui
import sound
import lever
from player import Player

_FONT_PATH = 'assets/fonts/Galmuri11.ttf'

start_stage = 0

_player = None
_stage_idx = 0
_prev_ticks = 0
_keys = None
_hud_font = None


def _load_stage(idx):
    global _stage_idx
    _stage_idx = idx
    background.set_stage(idx)
    bomb.remove_active()
    game_world.clear()
    for tile in stage.build_stage(idx):
        game_world.add(tile)
    game_world.set_player(_player)
    for e in stage.build_enemies(idx):
        game_world.add(e)
    lv = stage.build_lever(idx)
    if lv is not None:
        game_world.add(lv)
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
    fx.clear_particles()


def init():
    global _player, _prev_ticks, _keys, _hud_font
    _hud_font = pico2d.load_font(_FONT_PATH, 22)
    _keys = set()
    _prev_ticks = pico2d.SDL_GetTicks()
    sx, sy = stage.get_player_start(start_stage)
    _player = Player(sx, sy)
    _load_stage(start_stage)


def finish():
    global _player, _hud_font
    bomb.remove_active()
    game_world.clear()
    _player = None
    _hud_font = None


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
    else:
        levers = game_world.get_levers()
        enemies_cleared = not game_world.get_enemies()
        if levers:
            stage_done = enemies_cleared and any(lv.state == lever.PULLED for lv in levers)
        else:
            stage_done = enemies_cleared
        if stage_done:
            sound.play('stage_clear')
            save_data.save(_stage_idx + 1)
            _load_stage((_stage_idx + 1) % stage.STAGE_COUNT)


def render():
    background.draw()
    game_world.draw_tiles()
    game_world.draw_levers()
    fx.draw_all_shadows()
    game_world.draw_enemies()
    game_world.draw_bombs()
    fx.draw_bomb_fuse_lights()
    fx.draw_landing_dust()
    fx.draw_afterimages()
    _player.draw()
    game_world.draw_explosions()
    fx.draw_debris()
    fx.draw_explosion_lights()
    fx.draw_vignette()
    fx.draw_flash()
    _draw_hud()
    pico2d.update_canvas()


def _draw_hud():
    bomb_img = sprite.load('assets/ui_bomb_push.png' if bomb.get_type() == 0
                           else 'assets/ui_bomb_pull.png')
    bomb_img.draw(90, 1005)
    sprite.load('assets/ui_icon_ring.png').draw(90, 990)
    sprite.load('assets/ui_panel.png').draw(250, 990)
    sprite.load('assets/ui_panel.png').draw(1830, 990)
    color = (0xEC, 0xE8, 0xE1)
    ui.draw_text_outlined(_hud_font, 250, 990, f'적 {len(game_world.get_enemies())}', color)
    ui.draw_text_outlined(_hud_font, 1830, 990, f'STAGE {_stage_idx + 1}', color)


def handle_events():
    import menu_mode
    for event in pico2d.get_events():
        if event.type == pico2d.SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == pico2d.SDL_KEYDOWN:
            _keys.add(event.key)
            if event.key == pico2d.SDLK_ESCAPE:
                game_framework.change_mode(menu_mode)
                return
            elif event.key == pico2d.SDLK_f:
                camera.shake(14, 0.35, 1.0, 0.0)
            elif pico2d.SDLK_1 <= event.key <= pico2d.SDLK_9:
                idx = event.key - pico2d.SDLK_1
                if idx < stage.STAGE_COUNT:
                    _load_stage(idx)
            elif event.key == pico2d.SDLK_PAGEUP:
                if _stage_idx > 0:
                    _load_stage(_stage_idx - 1)
            elif event.key == pico2d.SDLK_PAGEDOWN:
                if _stage_idx + 1 < stage.STAGE_COUNT:
                    _load_stage(_stage_idx + 1)
            elif event.key in (pico2d.SDLK_LSHIFT, pico2d.SDLK_RSHIFT):
                bomb.toggle_type()
                sound.play('ui_move')
            _player.handle_event(event)
        elif event.type == pico2d.SDL_KEYUP:
            _keys.discard(event.key)


def pause():
    pass


def resume():
    pass
