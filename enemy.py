import random
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
        self._frozen_sheet = 'enemy_walk'
        self._freeze_remaining = 0.0
        self._freeze_elapsed = 0.0
        tiles = game_world.get_tiles()
        self._fade_threshold_y = min((t.surface_y for t in tiles), default=0.0)

    def receive_blast(self, vx, vy):
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
            self._frozen_sheet = 'enemy_walk' if self.state == WALK else 'enemy_collapse'
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
            mult = sprite.ICE_SLIDE_MULT if ice_at(self.x, self.y - HALF_H) else 1.0
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
        walk_count = sprite.SHEETS['enemy_walk'][1]
        self.frame = (self.frame + sprite.WALK_FPS * frame_time) % walk_count
        if not self._on_ground():
            self._enter_fall_grounded()
            return
        vx = -ENEMY_WALK_SPEED if self.flip else ENEMY_WALK_SPEED
        prev_x = self.x
        self.x += vx * frame_time
        if not self._on_ground():
            self.x = prev_x
            self.flip = not self.flip

    def _update_collapse(self, frame_time):
        if self._slide_vx != 0.0:
            from tile import ice_at
            mult = sprite.ICE_SLIDE_MULT if ice_at(self.x, self.y - HALF_H) else 1.0
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
        prev_feet = prev_y - HALF_H
        curr_feet = self.y - HALF_H
        for tile in game_world.get_tiles():
            if self.x + ENEMY_HALF_W <= tile.left_x or self.x - ENEMY_HALF_W >= tile.right_x:
                continue
            if prev_feet >= tile.surface_y and curr_feet <= tile.surface_y:
                self.y = tile.surface_y + HALF_H
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
        if self.y < -HALF_H or self._fall_elapsed > 5.0:
            game_world.remove(self)

    def _on_ground(self):
        feet_y = self.y - HALF_H
        for tile in game_world.get_tiles():
            if self.x + ENEMY_HALF_W <= tile.left_x or self.x - ENEMY_HALF_W >= tile.right_x:
                continue
            if abs(feet_y - tile.surface_y) <= 4:
                return True
        return False

    def draw(self):
        draw_y = self.y + camera.oy - sprite.FOOT_MARGIN * sprite.DRAW_SCALE
        if self.state == WALK:
            path, _ = sprite.SHEETS['enemy_walk']
            sprite.draw_frame(path, int(self.frame), sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                              self.x + camera.ox, draw_y, self.flip)
        elif self.state == COLLAPSE:
            path, _ = sprite.SHEETS['enemy_collapse']
            shake_x = 0.0
            shake_y = 0.0
            if not self._reviving and self._collapse_elapsed >= COLLAPSE_TIME - WARNING_TIME:
                shake_x = random.uniform(-2, 2) * sprite.DRAW_SCALE
                shake_y = random.uniform(-2, 2) * sprite.DRAW_SCALE
            sprite.draw_frame(path, int(self.frame), sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                              self.x + camera.ox + shake_x, draw_y + shake_y, self.flip)
        elif self.state == FROZEN:
            path, _ = sprite.SHEETS[self._frozen_sheet]
            sprite.draw_frame(path, int(self.frame), sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                              self.x + camera.ox, draw_y, self.flip,
                              tint=sprite.FROZEN_TINT)
        elif self.state == FALL:
            path, _ = sprite.SHEETS['enemy_fall']
            if self._below_threshold:
                t = min(self._fade_elapsed / FALL_DURATION, 1.0)
                scale = FALL_SCALE_START + (FALL_SCALE_END - FALL_SCALE_START) * t
                out_w = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE * scale)
                out_h = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE * scale)
                img = sprite.load(path)
                left = int(self.frame) * sprite.PLAYER_FRAME
                img.clip_composite_draw(left, 0, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                                        0, 'h' if self.flip else '',
                                        self.x + camera.ox, draw_y, out_w, out_h)
            else:
                sprite.draw_frame(path, int(self.frame), sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                                  self.x + camera.ox, draw_y, self.flip)
