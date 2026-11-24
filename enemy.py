import random
import pico2d
import sprite
import camera
import game_world
import sound

WALK = 0
COLLAPSE = 1
FALL = 2
FROZEN = 3

ENEMY_HALF_W = int(sprite.FOOT_HALF_W_SRC * sprite.DRAW_SCALE)
HALF_H = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2

ENEMY_WALK_SPEED = 200.0
COLLAPSE_FPS = 12.0
REVIVE_FPS = 12.0
COLLAPSE_TIME = 2.5
WARNING_TIME = 0.5
FALL_DURATION = 0.5
FALL_SCALE_START = 2.0
FALL_SCALE_END = 0.6
GRAVITY = -2000.0


class Enemy:
    WALK_SPEED = ENEMY_WALK_SPEED
    BLAST_MULT = 1.0
    DRAW_SCALE_MULT = 1.0
    SHEET_WALK = 'enemy_walk'
    BODY_TINT = None

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.state = WALK
        self.flip = False
        self.frame = 0.0
        self._collapse_elapsed = 0.0
        self._reviving = False
        self._revival_flip = False
        self._fall_elapsed = 0.0
        self._fall_blast_vx = 0.0
        self._fall_decay = sprite.BLAST_DECAY
        self._below_threshold = False
        self._fade_elapsed = 0.0
        self._slide_vx = 0.0
        self._slide_progress = 0.0
        self._frozen_sheet = self.SHEET_WALK
        self._freeze_remaining = 0.0
        self._freeze_elapsed = 0.0
        self.half_w = int(ENEMY_HALF_W * self.DRAW_SCALE_MULT)
        self.half_h = int(HALF_H * self.DRAW_SCALE_MULT)
        tiles = game_world.get_tiles()
        self._fade_threshold_y = min((t.surface_y for t in tiles), default=0.0)

    def receive_blast(self, vx, vy):
        vx *= self.BLAST_MULT
        vy *= self.BLAST_MULT
        if self.state == FALL:
            return
        if self.state == FROZEN:
            self._slide_vx = vx
            self._freeze_elapsed = 0.0
            return
        if self.state == COLLAPSE:
            if vy < 0:
                vy = 300.0
            self.vx = vx
            self.vy = vy
            self._fall_blast_vx = vx
            self._fall_decay = sprite.BLAST_DECAY * sprite.COLLAPSED_DECAY_MULT
            self._slide_vx = 0.0
            self._below_threshold = False
            self._fade_elapsed = 0.0
            self.state = FALL
            self.frame = 0.0
            self._fall_elapsed = 0.0
            return
        self._revival_flip = vx > 0
        self._slide_vx = vx
        self._slide_progress = 0.0
        self.state = COLLAPSE
        sound.play('bone_collapse')
        self.frame = 0.0
        self._collapse_elapsed = 0.0
        self._reviving = False

    def freeze(self, vx):
        if self.state == FALL:
            return
        if self.state != FROZEN:
            self._frozen_sheet = self.SHEET_WALK if self.state == WALK else 'enemy_collapse'
        self.state = FROZEN
        self._freeze_remaining = sprite.FREEZE_TIME
        self._freeze_elapsed = 0.0
        self._slide_vx = vx

    def update(self, frame_time):
        if self.state == WALK:
            self._update_walk(frame_time)
        elif self.state == COLLAPSE:
            self._update_collapse(frame_time)
        elif self.state == FALL:
            self._update_fall(frame_time)
        elif self.state == FROZEN:
            self._update_frozen(frame_time)

    def _update_frozen(self, frame_time):
        self._freeze_remaining -= frame_time
        if self._freeze_remaining <= 0.0:
            self.state = WALK
            self._slide_vx = 0.0
            sound.play('ice_break')
            return
        if not self._on_ground():
            self._enter_fall_grounded()
            return
        if self._slide_vx != 0.0:
            from tile import ice_at
            mult = sprite.ICE_SLIDE_MULT if ice_at(self.x, self.y - self.half_h) else 1.0
            self._freeze_elapsed += frame_time / (sprite.BLAST_DECAY * sprite.ICE_DECAY_MULT * mult)
            ratio = max(0.0, 1.0 - self._freeze_elapsed)
            self.x += self._slide_vx * ratio * frame_time

    def _enter_fall_grounded(self):
        self.vx = 0.0
        self.vy = 0.0
        self._slide_vx = 0.0
        self._fall_blast_vx = 0.0
        self._fall_decay = sprite.BLAST_DECAY
        self._below_threshold = False
        self._fade_elapsed = 0.0
        self.state = FALL
        self.frame = 0.0
        self._fall_elapsed = 0.0

    def _update_walk(self, frame_time):
        walk_count = sprite.SHEETS[self.SHEET_WALK][1]
        self.frame = (self.frame + sprite.WALK_FPS * frame_time) % walk_count
        if not self._on_ground():
            self._enter_fall_grounded()
            return
        vx = -self.WALK_SPEED if self.flip else self.WALK_SPEED
        prev_x = self.x
        self.x += vx * frame_time
        if not self._on_ground():
            self.x = prev_x
            self.flip = not self.flip

    def _update_collapse(self, frame_time):
        if self._slide_vx != 0.0:
            from tile import ice_at
            mult = sprite.ICE_SLIDE_MULT if ice_at(self.x, self.y - self.half_h) else 1.0
            self._slide_progress += frame_time / (sprite.BLAST_DECAY * mult)
            ratio = max(0.0, 1.0 - self._slide_progress)
            self.x += self._slide_vx * ratio * frame_time
        if not self._on_ground():
            self._enter_fall_grounded()
            return
        collapse_frames = sprite.SHEETS['enemy_collapse'][1]
        if not self._reviving:
            self._collapse_elapsed += frame_time
            self.frame = min(self._collapse_elapsed * COLLAPSE_FPS, float(collapse_frames - 1))
            if self._collapse_elapsed >= COLLAPSE_TIME:
                self._reviving = True
                self.frame = float(collapse_frames - 1)
        else:
            self.frame -= REVIVE_FPS * frame_time
            if self.frame <= 0.0:
                self.frame = 0.0
                self.flip = self._revival_flip
                self.state = WALK
                self._reviving = False
                self._collapse_elapsed = 0.0

    def _update_fall(self, frame_time):
        self._fall_elapsed += frame_time
        self.vy += GRAVITY * frame_time
        prev_y = self.y
        self.x += self.vx * frame_time
        self.y += self.vy * frame_time
        prev_feet = prev_y - self.half_h
        curr_feet = self.y - self.half_h
        for tile in game_world.get_tiles():
            if self.x + self.half_w <= tile.left_x or self.x - self.half_w >= tile.right_x:
                continue
            if prev_feet >= tile.surface_y and curr_feet <= tile.surface_y:
                self.y = tile.surface_y + self.half_h
                self.vy = 0.0
                self._slide_vx = self.vx
                self._slide_progress = 0.0
                self.vx = 0.0
                self._fall_blast_vx = 0.0
                self._below_threshold = False
                self._fade_elapsed = 0.0
                sound.play('bone_collapse')
                self.state = COLLAPSE
                self.frame = 0.0
                self._collapse_elapsed = 0.0
                self._reviving = False
                return
        if not self._below_threshold and self.y < self._fade_threshold_y:
            self._below_threshold = True
            self._fade_elapsed = 0.0
        if self._below_threshold:
            self._fade_elapsed += frame_time
        fall_frames = sprite.SHEETS['enemy_fall'][1]
        t = min(self._fall_elapsed / FALL_DURATION, 1.0)
        self.frame = t * (fall_frames - 1)
        if self.y < -self.half_h or self._fall_elapsed > 5.0:
            game_world.remove(self)

    def _on_ground(self):
        feet_y = self.y - self.half_h
        for tile in game_world.get_tiles():
            if self.x + self.half_w <= tile.left_x or self.x - self.half_w >= tile.right_x:
                continue
            if abs(feet_y - tile.surface_y) <= 4:
                return True
        return False

    def _tint_on(self, img, tint):
        if tint is not None:
            pico2d.SDL_SetTextureColorMod(img.texture, tint[0], tint[1], tint[2])

    def _tint_off(self, img):
        pico2d.SDL_SetTextureColorMod(img.texture, 255, 255, 255)

    def draw(self):
        draw_y = self.y + camera.oy - sprite.FOOT_MARGIN * sprite.DRAW_SCALE
        out = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE * self.DRAW_SCALE_MULT)
        if self.state == WALK:
            path, _ = sprite.SHEETS[self.SHEET_WALK]
            img = sprite.load(path)
            self._tint_on(img, self.BODY_TINT)
            img.clip_composite_draw(
                int(self.frame) * sprite.PLAYER_FRAME, 0,
                sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                0, 'h' if self.flip else '',
                self.x + camera.ox, draw_y, out, out)
            self._tint_off(img)
        elif self.state == COLLAPSE:
            path, _ = sprite.SHEETS['enemy_collapse']
            shake_x = 0.0
            shake_y = 0.0
            if not self._reviving and self._collapse_elapsed >= COLLAPSE_TIME - WARNING_TIME:
                shake_x = random.uniform(-2, 2) * sprite.DRAW_SCALE
                shake_y = random.uniform(-2, 2) * sprite.DRAW_SCALE
            img = sprite.load(path)
            self._tint_on(img, self.BODY_TINT)
            img.clip_composite_draw(
                int(self.frame) * sprite.PLAYER_FRAME, 0,
                sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                0, 'h' if self.flip else '',
                self.x + camera.ox + shake_x, draw_y + shake_y, out, out)
            self._tint_off(img)
        elif self.state == FROZEN:
            path, _ = sprite.SHEETS[self._frozen_sheet]
            img = sprite.load(path)
            t = sprite.FROZEN_TINT
            pico2d.SDL_SetTextureColorMod(img.texture, t[0], t[1], t[2])
            img.clip_composite_draw(
                int(self.frame) * sprite.PLAYER_FRAME, 0,
                sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                0, 'h' if self.flip else '',
                self.x + camera.ox, draw_y, out, out)
            self._tint_off(img)
        elif self.state == FALL:
            path, _ = sprite.SHEETS['enemy_fall']
            img = sprite.load(path)
            if self._below_threshold:
                tt = min(self._fade_elapsed / FALL_DURATION, 1.0)
                scale = FALL_SCALE_START + (FALL_SCALE_END - FALL_SCALE_START) * tt
                fw = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE * scale * self.DRAW_SCALE_MULT)
                self._tint_on(img, self.BODY_TINT)
                img.clip_composite_draw(
                    int(self.frame) * sprite.PLAYER_FRAME, 0,
                    sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                    0, 'h' if self.flip else '',
                    self.x + camera.ox, draw_y, fw, fw)
                self._tint_off(img)
            else:
                self._tint_on(img, self.BODY_TINT)
                img.clip_composite_draw(
                    int(self.frame) * sprite.PLAYER_FRAME, 0,
                    sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                    0, 'h' if self.flip else '',
                    self.x + camera.ox, draw_y, out, out)
                self._tint_off(img)
        self.draw_overlay(draw_y)

    def draw_overlay(self, draw_y, shake_x=0.0):
        pass
