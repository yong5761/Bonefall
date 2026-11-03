import sprite
import camera
import game_world

BOMB_HALF = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 4
PLAYER_HALF_H = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2
GRAVITY = -2000.0
FUSE_TIME = 1.5
BODY_FPS = 4

FALLING = 0
LANDED = 1

_current_type = 0
_active = None


def get_type():
    return _current_type


def toggle_type():
    global _current_type
    _current_type = 1 - _current_type


def place(x, y):
    global _active
    if _active is None:
        b = Bomb(x, y - PLAYER_HALF_H + BOMB_HALF, _current_type)
        _active = b
        game_world.add(b)


def _clear_active():
    global _active
    _active = None


class Bomb:
    def __init__(self, x, y, bomb_type):
        self.x = float(x)
        self.y = float(y)
        self.vy = 0.0
        self.bomb_type = bomb_type
        self.state = FALLING
        self.fuse = 0.0
        self.body_frame = 0.0

    def update(self, frame_time):
        self.body_frame = (self.body_frame + BODY_FPS * frame_time) % 2.0

        if self.state == FALLING:
            if self._on_ground():
                self._snap_to_ground()
                self.state = LANDED
                self.vy = 0.0
                return
            self.vy += GRAVITY * frame_time
            prev_y = self.y
            self.y += self.vy * frame_time
            if self.vy <= 0 and self._try_land(prev_y):
                self.state = LANDED

        elif self.state == LANDED:
            self.fuse += frame_time
            if self.fuse >= FUSE_TIME:
                import explosion
                game_world.add(explosion.Explosion(self.x, self.y, self.bomb_type))
                _clear_active()
                game_world.remove(self)

    def _on_ground(self):
        feet_y = self.y - BOMB_HALF
        for tile in game_world.get_tiles():
            if self.x + BOMB_HALF <= tile.left_x or self.x - BOMB_HALF >= tile.right_x:
                continue
            if abs(feet_y - tile.surface_y) <= 4:
                return True
        return False

    def _snap_to_ground(self):
        feet_y = self.y - BOMB_HALF
        for tile in game_world.get_tiles():
            if self.x + BOMB_HALF <= tile.left_x or self.x - BOMB_HALF >= tile.right_x:
                continue
            if abs(feet_y - tile.surface_y) <= 8:
                self.y = tile.surface_y + BOMB_HALF
                return

    def _try_land(self, prev_y):
        prev_feet = prev_y - BOMB_HALF
        curr_feet = self.y - BOMB_HALF
        for tile in game_world.get_tiles():
            if self.x + BOMB_HALF <= tile.left_x or self.x - BOMB_HALF >= tile.right_x:
                continue
            if prev_feet > tile.surface_y and curr_feet <= tile.surface_y:
                self.y = tile.surface_y + BOMB_HALF
                self.vy = 0.0
                return True
        return False

    def draw(self):
        frame_offset = self.bomb_type * 2
        body_frame = frame_offset + int(self.body_frame)
        path, _ = sprite.SHEETS['bombs']
        sprite.draw_frame(path, body_frame, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                          self.x + camera.ox, self.y + camera.oy)
        if self.state == LANDED:
            fuse_key = 'bomb_pull_fuse' if self.bomb_type == 1 else 'bomb_push_fuse'
            fuse_path, fuse_count = sprite.SHEETS[fuse_key]
            fuse_frame = int(min(self.fuse / FUSE_TIME * fuse_count, fuse_count - 1))
            sprite.draw_frame(fuse_path, fuse_frame, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                               self.x + camera.ox, self.y + camera.oy)
