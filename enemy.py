import random
import sprite
import camera
import game_world

WALK = 0
COLLAPSE = 1
FALL = 2

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

    def receive_blast(self, vx, vy):
        if self.state == FALL:
            return
        if self.state == COLLAPSE:
            self.vx = vx * 2.0
            self.vy = vy * 2.0
            self.state = FALL
            self.frame = 0.0
            self._fall_elapsed = 0.0
            return
        self._revival_flip = vx > 0
        self.state = COLLAPSE
        self.frame = 0.0
        self._collapse_elapsed = 0.0
        self._reviving = False

    def update(self, frame_time):
        if self.state == WALK:
            self._update_walk(frame_time)
        elif self.state == COLLAPSE:
            self._update_collapse(frame_time)
        elif self.state == FALL:
            self._update_fall(frame_time)

    def _update_walk(self, frame_time):
        walk_count = sprite.SHEETS['enemy_walk'][1]
        self.frame = (self.frame + sprite.WALK_FPS * frame_time) % walk_count
        vx = -ENEMY_WALK_SPEED if self.flip else ENEMY_WALK_SPEED
        prev_x = self.x
        self.x += vx * frame_time
        if not self._on_ground():
            self.x = prev_x
            self.flip = not self.flip

    def _update_collapse(self, frame_time):
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
        self.x += self.vx * frame_time
        self.y += self.vy * frame_time
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
        elif self.state == FALL:
            path, _ = sprite.SHEETS['enemy_fall']
            t = min(self._fall_elapsed / FALL_DURATION, 1.0)
            scale = FALL_SCALE_START + (FALL_SCALE_END - FALL_SCALE_START) * t
            out_w = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE * scale)
            out_h = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE * scale)
            img = sprite.load(path)
            left = int(self.frame) * sprite.PLAYER_FRAME
            img.clip_composite_draw(left, 0, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                                    0, 'h' if self.flip else '',
                                    self.x + camera.ox, draw_y, out_w, out_h)
