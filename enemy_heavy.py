import random
import pico2d
import sprite
import camera
import sound
from enemy import Enemy, ENEMY_WALK_SPEED, COLLAPSE, FALL, FROZEN, WALK

STAGGER = 4


class HeavyEnemy(Enemy):
    WALK_SPEED = ENEMY_WALK_SPEED * sprite.HEAVY_WALK_RATIO
    BLAST_MULT = sprite.HEAVY_BLAST_MULT
    DRAW_SCALE_MULT = sprite.HEAVY_SCALE
    BODY_TINT = sprite.HEAVY_TINT

    def __init__(self, x, y):
        super().__init__(x, y)
        self._stagger_elapsed = 0.0
        self._stagger_vx = 0.0
        self._stagger_slide_progress = 0.0
        self._stagger_flash_elapsed = 0.0

    def receive_blast(self, vx, vy):
        if self.state == WALK:
            self._stagger_elapsed = 0.0
            self._stagger_vx = vx * self.BLAST_MULT
            self._stagger_slide_progress = 0.0
            self._stagger_flash_elapsed = 0.0
            self.state = STAGGER
            sound.play('bone_collapse')
            return
        if self.state == STAGGER:
            vx_s = vx * self.BLAST_MULT
            self._revival_flip = vx_s > 0
            self._slide_vx = vx_s
            self._slide_progress = 0.0
            self.state = COLLAPSE
            sound.play('bone_collapse')
            self.frame = 0.0
            self._collapse_elapsed = 0.0
            self._reviving = False
            return
        super().receive_blast(vx, vy)

    def update(self, frame_time):
        if self.state == STAGGER:
            self._update_stagger(frame_time)
        else:
            super().update(frame_time)

    def _update_stagger(self, frame_time):
        self._stagger_elapsed += frame_time
        self._stagger_flash_elapsed += frame_time
        if self._stagger_vx != 0.0:
            from tile import ice_at
            mult = sprite.ICE_SLIDE_MULT if ice_at(self.x, self.y - self.half_h) else 1.0
            self._stagger_slide_progress += frame_time / (sprite.BLAST_DECAY * mult)
            ratio = max(0.0, 1.0 - self._stagger_slide_progress)
            self.x += self._stagger_vx * ratio * frame_time
        if not self._on_ground():
            self._enter_fall_grounded()
            return
        if self._stagger_elapsed >= sprite.HEAVY_STAGGER_TIME:
            self.state = WALK
            self._stagger_vx = 0.0

    def draw(self):
        if self.state == STAGGER:
            draw_y = self.y + camera.oy - sprite.FOOT_MARGIN * sprite.DRAW_SCALE
            out = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE * self.DRAW_SCALE_MULT)
            shake_x = random.uniform(-2, 2) * sprite.DRAW_SCALE
            path, _ = sprite.SHEETS[self.SHEET_WALK]
            img = sprite.load(path)
            t = sprite.HEAVY_TINT
            pico2d.SDL_SetTextureColorMod(img.texture, t[0], t[1], t[2])
            img.clip_composite_draw(
                0, 0, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                0, 'h' if self.flip else '',
                int(self.x + camera.ox + shake_x), int(draw_y), out, out)
            pico2d.SDL_SetTextureColorMod(img.texture, 255, 255, 255)
            self.draw_overlay(draw_y, shake_x)
        else:
            super().draw()

    def draw_overlay(self, draw_y, shake_x=0.0):
        path, _ = sprite.SHEETS['heavy_armor']
        img = sprite.load(path)
        out = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE * self.DRAW_SCALE_MULT)
        flashing = (self.state == STAGGER
                    and self._stagger_flash_elapsed < sprite.FLASH_TIME)
        if flashing:
            pico2d.SDL_SetTextureColorMod(img.texture, 255, 220, 160)
        img.clip_composite_draw(
            0, 0, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
            0, 'h' if self.flip else '',
            int(self.x + camera.ox + shake_x), int(draw_y), out, out)
        if flashing:
            pico2d.SDL_SetTextureColorMod(img.texture, 255, 255, 255)
