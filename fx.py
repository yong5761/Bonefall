import math
import random
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

_AIRBORNE_SHEETS = {2: 'player_jump', 3: 'player_blast'}
_AFTERIMAGE_INTERVAL = 0.035
_AFTERIMAGE_LIFETIME = 0.16
_AFTERIMAGE_MAX = 3
_DUST_LIFETIME = 0.35
_DEBRIS_LIFETIME = 0.5

_flash_elapsed = 0.0
_flash_duration = 0.0

_afterimage_timer = 0.0
_afterimages = []

_dust = []
_player_airborne = False
_player_prev_vy = 0.0

_debris = []


def clear_particles():
    global _afterimage_timer, _player_airborne, _player_prev_vy
    _afterimages.clear()
    _dust.clear()
    _debris.clear()
    _afterimage_timer = 0.0
    _player_airborne = False
    _player_prev_vy = 0.0


def trigger_flash():
    global _flash_elapsed, _flash_duration
    _flash_elapsed = 0.0
    _flash_duration = sprite.FLASH_TIME


def trigger_debris(x, y):
    for _ in range(10):
        angle = random.uniform(0.0, math.pi * 2.0)
        speed = random.uniform(420.0, 900.0)
        _debris.append([float(x), float(y),
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        0.0])


def update(frame_time):
    global _flash_elapsed, _afterimage_timer, _player_airborne, _player_prev_vy

    if _flash_elapsed < _flash_duration:
        _flash_elapsed += frame_time

    for a in _afterimages:
        a[5] += frame_time
    _afterimages[:] = [a for a in _afterimages if a[5] < _AFTERIMAGE_LIFETIME]

    for player in game_world.get_players():
        curr_airborne = player.state in _AIRBORNE_SHEETS
        if _player_airborne and not curr_airborne:
            count = 11 if abs(_player_prev_vy) > 700 else 7
            feet_y = player.y - _ENTITY_HALF_H
            for _ in range(count):
                _dust.append([
                    player.x + random.uniform(-20.0, 20.0),
                    feet_y,
                    random.uniform(-220.0, 220.0),
                    random.uniform(40.0, 140.0),
                    0.0
                ])
        if curr_airborne:
            _player_prev_vy = player.vy
        _player_airborne = curr_airborne

    _afterimage_timer += frame_time
    if _afterimage_timer >= _AFTERIMAGE_INTERVAL:
        _afterimage_timer = 0.0
        for player in game_world.get_players():
            if player.state in _AIRBORNE_SHEETS and abs(player.vy) >= 300:
                sheet = _AIRBORNE_SHEETS[player.state]
                _afterimages.append([
                    player.x, player.y,
                    sprite.SHEETS[sheet][0],
                    int(player.frame),
                    player.flip,
                    0.0
                ])
                if len(_afterimages) > _AFTERIMAGE_MAX:
                    _afterimages.pop(0)

    for d in _dust:
        d[3] += -900.0 * frame_time
        d[0] += d[2] * frame_time
        d[1] += d[3] * frame_time
        d[4] += frame_time
    _dust[:] = [d for d in _dust if d[4] < _DUST_LIFETIME]

    for d in _debris:
        d[3] += -1100.0 * frame_time
        d[0] += d[2] * frame_time
        d[1] += d[3] * frame_time
        d[4] += frame_time
    _debris[:] = [d for d in _debris if d[4] < _DEBRIS_LIFETIME]


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


def draw_lever_lights():
    import lever
    img = sprite.load(_LIGHT_PATH)
    for lv in game_world.get_levers():
        if lv.state == lever.LOCKED:
            continue
        gx = lv.x + camera.ox
        gy = lv.y + 12.0 + camera.oy
        pulsed = lv.state == lever.PULLED
        phase = lv.ready_elapsed if lv.ready_elapsed >= 0.0 else 0.0
        base_size = 250 if pulsed else 190
        base_alpha = (170 if pulsed else 105) + (30 if pulsed else 45) * math.sin(phase * 6.0)
        _draw_light(img, gx, gy, int(base_size), int(base_alpha))
        for elapsed, span, peak in (
                (lv.ready_elapsed, lever.READY_BURST_TIME, 190),
                (lv.pull_elapsed, lever.PULL_BURST_TIME, 240)):
            if elapsed < 0.0 or elapsed >= span:
                continue
            q = elapsed / span
            _draw_light(img, gx, gy, int(140 + 560 * q), int(peak * (1.0 - q)))


def _draw_light(img, x, y, size, alpha, color=(255, 186, 92)):
    alpha = max(0, min(255, alpha))
    if alpha <= 0:
        return
    pico2d.SDL_SetTextureBlendMode(img.texture, pico2d.SDL_BLENDMODE_ADD)
    pico2d.SDL_SetTextureColorMod(img.texture, color[0], color[1], color[2])
    pico2d.SDL_SetTextureAlphaMod(img.texture, alpha)
    img.clip_composite_draw(0, 0, 256, 256, 0, '', x, y, size, size)
    pico2d.SDL_SetTextureColorMod(img.texture, 255, 255, 255)
    pico2d.SDL_SetTextureBlendMode(img.texture, pico2d.SDL_BLENDMODE_BLEND)
    pico2d.SDL_SetTextureAlphaMod(img.texture, 255)


RAIL_COLOR = (96, 196, 255)


def draw_rail_lights():
    img = sprite.load(_LIGHT_PATH)
    for tl in game_world.get_tiles():
        points = getattr(tl, 'rail_points', None)
        if points is None:
            continue
        for wx, wy in points():
            if tl.left_x <= wx <= tl.right_x and abs(wy - (tl.surface_y - 40.0)) <= 48.0:
                continue
            _draw_light(img, wx + camera.ox, wy + camera.oy, 56, 78, RAIL_COLOR)


def draw_afterimages():
    out_w = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE)
    out_h = out_w
    for a in _afterimages:
        x, y, path, frame_idx, flip, elapsed = a
        alpha = int(75.0 * (1.0 - elapsed / _AFTERIMAGE_LIFETIME))
        if alpha <= 0:
            continue
        img = sprite.load(path)
        draw_x = int(x + camera.ox)
        draw_y = int(y + camera.oy - sprite.FOOT_MARGIN * sprite.DRAW_SCALE)
        img.opacify(alpha / 255.0)
        img.clip_composite_draw(frame_idx * sprite.PLAYER_FRAME, 0,
                                sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                                0, 'h' if flip else '',
                                draw_x, draw_y, out_w, out_h)
        img.opacify(1.0)


def draw_landing_dust():
    img = sprite.load(_SHADOW_PATH)
    for d in _dust:
        x, y, vx, vy, elapsed = d
        t = elapsed / _DUST_LIFETIME
        alpha = int(150.0 * (1.0 - t))
        if alpha <= 0:
            continue
        size = int(18.0 + 16.0 * t)
        img.opacify(alpha / 255.0)
        img.clip_composite_draw(0, 0, 160, 80, 0, '',
                                int(x + camera.ox), int(y + camera.oy),
                                size, max(1, size // 2))
        img.opacify(1.0)


def draw_debris():
    img = sprite.load(_LIGHT_PATH)
    for d in _debris:
        x, y, vx, vy, elapsed = d
        t = elapsed / _DEBRIS_LIFETIME
        alpha = int(220.0 * (1.0 - t))
        if alpha <= 0:
            continue
        size = max(1, int(16.0 - 10.0 * t))
        pico2d.SDL_SetTextureBlendMode(img.texture, pico2d.SDL_BLENDMODE_ADD)
        pico2d.SDL_SetTextureAlphaMod(img.texture, alpha)
        img.clip_composite_draw(0, 0, 256, 256, 0, '',
                                int(x + camera.ox), int(y + camera.oy),
                                size, size)
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
