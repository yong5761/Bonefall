import math
import pico2d
import sprite
import camera
import game_world
from enemy import Enemy

_BASE    = 'assets/cannon_base.png'
_BARREL  = 'assets/cannon_barrel.png'
_BASE_W, _BASE_H     = 76, 48
_BARREL_W, _BARREL_H = 80, 44
_PIVOT_SRC = 8
_AIM_ROT_SPEED = 2.0
_PIVOT_DY = -40.0
_BASE_DY  = -52.0

_DARK_TINT = (150, 140, 130)
_TELE_TINT = (255, 180, 60)


class TurretEnemy(Enemy):
    BLAST_MULT = 0.0

    def __init__(self, x, y):
        super().__init__(x, y)
        self.flip = x > 960
        self._aim_angle = math.pi if self.flip else 0.0
        self._fire_timer = 0.0
        self._telegraphing = False
        self._telegraph_timer = 0.0

    def _update_walk(self, frame_time):
        if not self._on_ground():
            self._enter_fall_grounded()
            return
        players = game_world.get_players()
        if players:
            self.flip = players[0].x < self.x
        self._update_aim(frame_time)
        self._update_fire(frame_time)

    def _update_aim(self, frame_time):
        players = game_world.get_players()
        if not players:
            return
        p = players[0]
        pivot_wy = self.y - sprite.FOOT_MARGIN * sprite.DRAW_SCALE + _PIVOT_DY
        dx = p.x - self.x
        dy = p.y - pivot_wy
        target = math.atan2(dy, dx)
        limit = math.radians(sprite.TURRET_AIM_LIMIT)
        base = math.pi if self.flip else 0.0
        offset = target - base
        while offset > math.pi:
            offset -= 2 * math.pi
        while offset < -math.pi:
            offset += 2 * math.pi
        offset = max(-limit, min(limit, offset))
        target_clamped = base + offset
        diff = target_clamped - self._aim_angle
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi
        step = _AIM_ROT_SPEED * frame_time
        if abs(diff) <= step:
            self._aim_angle = target_clamped
        else:
            self._aim_angle += step if diff > 0 else -step

    def _update_fire(self, frame_time):
        if self._telegraphing:
            self._telegraph_timer += frame_time
            if self._telegraph_timer >= sprite.TURRET_TELEGRAPH:
                self._fire()
                self._telegraphing = False
                self._fire_timer = 0.0
        else:
            self._fire_timer += frame_time
            if self._fire_timer >= sprite.TURRET_FIRE_PERIOD:
                self._telegraphing = True
                self._telegraph_timer = 0.0

    def _fire(self):
        from shot import Shot
        s = sprite.DRAW_SCALE
        muzzle_off = (_BARREL_W - _PIVOT_SRC) * s
        pivot_wy = self.y - sprite.FOOT_MARGIN * sprite.DRAW_SCALE + _PIVOT_DY
        mx = self.x + math.cos(self._aim_angle) * muzzle_off
        my = pivot_wy + math.sin(self._aim_angle) * muzzle_off
        game_world.add(Shot(mx, my, self._aim_angle))

    def draw_overlay(self, draw_y, shake_x=0.0):
        s = sprite.DRAW_SCALE
        base_img = sprite.load(_BASE)
        pico2d.SDL_SetTextureColorMod(base_img.texture, *_DARK_TINT)
        base_img.draw(
            int(self.x + camera.ox), int(draw_y + _BASE_DY),
            int(_BASE_W * s), int(_BASE_H * s))
        pico2d.SDL_SetTextureColorMod(base_img.texture, 255, 255, 255)

        barrel_img = sprite.load(_BARREL)
        tint = _TELE_TINT if self._telegraphing else _DARK_TINT
        pico2d.SDL_SetTextureColorMod(barrel_img.texture, *tint)
        pivot_y = draw_y + _PIVOT_DY
        off = (_BARREL_W / 2.0 - _PIVOT_SRC) * s
        cx = self.x + math.cos(self._aim_angle) * off
        cy = pivot_y + math.sin(self._aim_angle) * off
        barrel_img.clip_composite_draw(
            0, 0, _BARREL_W, _BARREL_H, self._aim_angle, '',
            int(cx + camera.ox), int(cy),
            int(_BARREL_W * s), int(_BARREL_H * s))
        pico2d.SDL_SetTextureColorMod(barrel_img.texture, 255, 255, 255)
