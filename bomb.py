import sprite
import camera
import game_world
import sound

BOMB_HALF = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 4
GRAVITY = -2000.0
FUSE_TIME = 1.0
HOLD_LIMIT = 2.0
BODY_FPS = 4

FALLING = 0
LANDED = 1

_current_type = 0
_active = None
_reserved = False


def get_type():
    return _current_type


def toggle_type():
    global _current_type
    _current_type = (_current_type + 1) % 3


def is_busy():
    return _active is not None or _reserved


def reserve():
    global _reserved
    _reserved = True


def launch(x, y, vx, vy, bomb_type):
    global _active, _reserved
    _reserved = False
    if _active is not None:
        return
    b = Bomb(x, y, bomb_type, vx, vy)
    b.fuse_hold = True
    _active = b
    game_world.add(b)


def throw(x, y, flip):
    global _active
    if _active is None and not _reserved:
        vx = -(sprite.THROW_SPEED_SRC * sprite.DRAW_SCALE) if flip else (sprite.THROW_SPEED_SRC * sprite.DRAW_SCALE)
        vy = sprite.THROW_VY_SRC * sprite.DRAW_SCALE
        b = Bomb(x, y, _current_type, vx, vy)
        _active = b
        game_world.add(b)
        sound.play('throw')


def _clear_active():
    global _active
    _active = None


def remove_active():
    global _active, _reserved
    _reserved = False
    if _active is not None:
        game_world.remove(_active)
    _clear_active()


class Bomb:
    def __init__(self, x, y, bomb_type, vx=0.0, vy=0.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.bomb_type = bomb_type
        self.state = FALLING
        self.fuse = 0.0
        self.fuse_hold = False
        self.hold_elapsed = 0.0
        self.body_frame = 0.0

    def update(self, frame_time):
        self.body_frame = (self.body_frame + BODY_FPS * frame_time) % 2.0
        if self.fuse_hold and self.state == FALLING and self.hold_elapsed < HOLD_LIMIT:
            self.hold_elapsed += frame_time
        else:
            self.fuse += frame_time

        if self.fuse >= FUSE_TIME:
            import explosion
            game_world.add(explosion.Explosion(self.x, self.y, self.bomb_type))
            if self.bomb_type == 2:
                sound.play('ice_freeze')
            else:
                sound.play('explosion_push' if self.bomb_type == 0 else 'explosion_pull')
            _clear_active()
            game_world.remove(self)
            return

        if self.state == FALLING:
            if self.y < -300:
                _clear_active()
                game_world.remove(self)
                return
            if self.vy <= 0.0 and self._on_ground():
                self._snap_to_ground()
                self.fuse_hold = False
                self.state = LANDED
                if not self._on_ice():
                    self.vx = 0.0
                self.vy = 0.0
                return
            self.vy += GRAVITY * frame_time
            self.x += self.vx * frame_time
            prev_y = self.y
            self.y += self.vy * frame_time
            if self.vy <= 0 and self._try_land(prev_y):
                self.fuse_hold = False
                self.state = LANDED
                if not self._on_ice():
                    self.vx = 0.0

        elif self.state == LANDED:
            if self.vx != 0.0:
                self.x += self.vx * frame_time
                if self._on_ice():
                    self.vx -= self.vx * sprite.ICE_TILE_FRICTION * frame_time
                    if abs(self.vx) < 20:
                        self.vx = 0.0
                else:
                    self.vx = 0.0
            if not self._on_ground():
                self.state = FALLING

    def _on_ice(self):
        from tile import ice_at
        return ice_at(self.x, self.y - BOMB_HALF)

    def _on_ground(self):
        feet_y = self.y - BOMB_HALF
        from pad import pad_at
        if pad_at(self.x, feet_y):
            return False
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
        from pad import pad_at
        if pad_at(self.x, curr_feet):
            return False
        for tile in game_world.get_tiles():
            if self.x + BOMB_HALF <= tile.left_x or self.x - BOMB_HALF >= tile.right_x:
                continue
            if prev_feet > tile.surface_y and curr_feet <= tile.surface_y:
                self.y = tile.surface_y + BOMB_HALF
                self.vy = 0.0
                return True
        return False

    def draw(self):
        fuse_key = ('bomb_push_fuse', 'bomb_pull_fuse',
                    'bomb_ice_fuse')[self.bomb_type]
        fuse_path, fuse_count = sprite.SHEETS[fuse_key]
        fuse_frame = int(min(self.fuse / FUSE_TIME * fuse_count, fuse_count - 1))
        sprite.draw_frame(fuse_path, fuse_frame, sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
                          self.x + camera.ox, self.y + camera.oy)
