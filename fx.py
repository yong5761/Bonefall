import math
import pico2d
import sprite
import camera
import game_world

_SHADOW_PATH = 'assets/shadow.png'
_LIGHT_PATH = 'assets/light.png'

_PLAYER_FOOT_HW = int(sprite.FOOT_HALF_W_SRC * sprite.DRAW_SCALE)
_BASE_SHADOW_W = _PLAYER_FOOT_HW * 2 * 2.2
_ENTITY_HALF_H = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2
_BOMB_HALF_H = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 4

_flash_elapsed = 0.0
_flash_duration = 0.0


def trigger_flash():
    global _flash_elapsed, _flash_duration
    _flash_elapsed = 0.0
    _flash_duration = sprite.FLASH_TIME


def update(frame_time):
    global _flash_elapsed
    if _flash_elapsed < _flash_duration:
        _flash_elapsed += frame_time


def _find_surface(entity_x, entity_y, search_hw):
    best = None
    for tile in game_world.get_tiles():
        if entity_x + search_hw <= tile.left_x or entity_x - search_hw >= tile.right_x:
            continue
        if tile.surface_y <= entity_y:
            if best is None or tile.surface_y > best:
                best = tile.surface_y
    return best


def _draw_shadow(entity_x, entity_y, search_hw, half_h, size_mult=1.0):
    surf_y = _find_surface(entity_x, entity_y, search_hw)
    if surf_y is None:
        return
    h = max(0, (entity_y - half_h) - surf_y)
    if h > 400:
        return
    t = min(h / 400.0, 1.0)
    scale = 1.0 - 0.5 * t
    alpha = int(255 * (1.0 - 0.75 * t))
    w = max(1, int(_BASE_SHADOW_W * scale * size_mult))
    ht = max(1, w // 2)
    img = sprite.load(_SHADOW_PATH)
    img.opacify(alpha / 255.0)
    img.clip_composite_draw(0, 0, 160, 80, 0, '',
                            entity_x + camera.ox, surf_y + camera.oy, w, ht)
    img.opacify(1.0)


def draw_all_shadows():
    from bomb import BOMB_HALF
    for player in game_world.get_players():
        _draw_shadow(player.x, player.y, _PLAYER_FOOT_HW, _ENTITY_HALF_H)
    for enemy in game_world.get_enemies():
        _draw_shadow(enemy.x, enemy.y, _PLAYER_FOOT_HW, _ENTITY_HALF_H)
    for b in game_world.get_bombs():
        _draw_shadow(b.x, b.y, BOMB_HALF, _BOMB_HALF_H, 0.6)


def draw_bomb_fuse_lights():
    from bomb import FUSE_TIME
    img = sprite.load(_LIGHT_PATH)
    for b in game_world.get_bombs():
        p = b.fuse / FUSE_TIME
        size = int(180 + 160 * p)
        raw = (90 + 120 * p) * (0.85 + 0.15 * math.sin(b.fuse * 26.0))
        alpha = max(0, min(255, int(raw)))
        pico2d.SDL_SetTextureBlendMode(img.texture, pico2d.SDL_BLENDMODE_ADD)
        pico2d.SDL_SetTextureAlphaMod(img.texture, alpha)
        img.clip_composite_draw(0, 0, 256, 256, 0, '',
                                b.x + camera.ox, b.y + camera.oy, size, size)
        pico2d.SDL_SetTextureBlendMode(img.texture, pico2d.SDL_BLENDMODE_BLEND)
        pico2d.SDL_SetTextureAlphaMod(img.texture, 255)


def draw_explosion_lights():
    from explosion import ANIM_DURATION, RADIUS
    img = sprite.load(_LIGHT_PATH)
    for obj in game_world.get_explosions():
        q = min(obj.elapsed / ANIM_DURATION, 1.0)
        size = int(RADIUS * 2 * (1.0 + 0.8 * q))
        alpha = int(220 * (1.0 - q))
        pico2d.SDL_SetTextureBlendMode(img.texture, pico2d.SDL_BLENDMODE_ADD)
        pico2d.SDL_SetTextureAlphaMod(img.texture, alpha)
        img.clip_composite_draw(0, 0, 256, 256, 0, '',
                                obj.x + camera.ox, obj.y + camera.oy, size, size)
        pico2d.SDL_SetTextureBlendMode(img.texture, pico2d.SDL_BLENDMODE_BLEND)
        pico2d.SDL_SetTextureAlphaMod(img.texture, 255)


def draw_vignette():
    if _flash_elapsed < _flash_duration:
        return
    pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_BLEND)
    pico2d.draw_rectangle(0, 0, 1920, 1080, 0, 0, 0, 40, filled=True)
    pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_NONE)


def draw_flash():
    if _flash_elapsed >= _flash_duration:
        return
    alpha = int(sprite.FLASH_ALPHA * (1.0 - _flash_elapsed / _flash_duration))
    pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_BLEND)
    pico2d.draw_rectangle(0, 0, 1920, 1080, 255, 255, 255, alpha, filled=True)
    pico2d.SDL_SetRenderDrawBlendMode(pico2d.pico2d.renderer, pico2d.SDL_BLENDMODE_NONE)
