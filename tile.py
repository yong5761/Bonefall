import game_world
import sprite
import camera

TILE_SHEET = 'assets/tiles.png'
TILE_SRC = 80


def _sz():
    return int(TILE_SRC * sprite.DRAW_SCALE)


class Tile:
    def __init__(self, gx, gy, tile_index):
        sz = _sz()
        self.tile_index = tile_index
        self.cx = gx * sz + sz // 2
        self.surface_y = (gy + 1) * sz
        self.cy = self.surface_y - sz // 2
        self.left_x = gx * sz
        self.right_x = (gx + 1) * sz
        self.is_weak = tile_index in (4, 5, 6, 7)
        self.is_ice = tile_index in (12, 13, 14, 15)
        self._breaking = False
        self._break_elapsed = 0.0

    def update(self, frame_time):
        if not self.is_weak:
            return
        if self._breaking:
            self._break_elapsed += frame_time
            if self._break_elapsed >= sprite.WEAK_BREAK_TIME:
                game_world.remove(self)
            return
        if self._has_occupant():
            self._breaking = True

    def _has_occupant(self):
        from enemy import COLLAPSE
        half_h = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2
        foot_half_w = int(sprite.FOOT_HALF_W_SRC * sprite.DRAW_SCALE)
        for obj in game_world.get_players():
            feet_y = obj.y - half_h
            if abs(feet_y - self.surface_y) <= 4:
                if obj.x + foot_half_w > self.left_x and obj.x - foot_half_w < self.right_x:
                    return True
        for obj in game_world.get_enemies():
            if obj.state != COLLAPSE:
                continue
            feet_y = obj.y - half_h
            if abs(feet_y - self.surface_y) <= 4:
                if obj.x + foot_half_w > self.left_x and obj.x - foot_half_w < self.right_x:
                    return True
        return False

    def draw(self):
        if self._breaking:
            step = int(self._break_elapsed / sprite.WEAK_BREAK_TIME * 4)
            frame_idx = 8 + min(step, 3)
            sprite.draw_frame(TILE_SHEET, frame_idx, TILE_SRC, TILE_SRC,
                              self.cx + camera.ox, self.cy + camera.oy)
        else:
            sprite.draw_frame(TILE_SHEET, self.tile_index, TILE_SRC, TILE_SRC,
                              self.cx + camera.ox, self.cy + camera.oy)


def ice_at(x, feet_y):
    for tile in game_world.get_tiles():
        if not tile.is_ice:
            continue
        if x <= tile.left_x or x >= tile.right_x:
            continue
        if abs(feet_y - tile.surface_y) <= 4:
            return True
    return False


class MovingTile(Tile):
    def __init__(self, x, y, ex, ey, w):
        sz = _sz()
        self.w = w
        self.is_weak = False
        self.is_ice = False
        self._breaking = False
        self._break_elapsed = 0.0
        self._sx = float(x)
        self._sy = float(y)
        dx = float(ex) - float(x)
        dy = float(ey) - float(y)
        self._dist = (dx * dx + dy * dy) ** 0.5
        if self._dist >= 1.0:
            self._dir_x = dx / self._dist
            self._dir_y = dy / self._dist
        else:
            self._dir_x = 0.0
            self._dir_y = 0.0
        self._traveled = 0.0
        self._forward = True
        self.left_x = float(x)
        self.surface_y = float(y)
        self.right_x = float(x) + w * sz
        self.cx = float(x) + w * sz / 2.0
        self.cy = float(y) - sz / 2.0

    def update(self, frame_time):
        if self._dist < 1.0:
            return
        sz = _sz()
        old_left_x = self.left_x
        old_right_x = self.right_x
        old_surface_y = self.surface_y
        step = sprite.MOVING_SPEED * frame_time
        if self._forward:
            self._traveled += step
            if self._traveled >= self._dist:
                self._traveled = self._dist
                self._forward = False
        else:
            self._traveled -= step
            if self._traveled <= 0.0:
                self._traveled = 0.0
                self._forward = True
        new_left_x = self._sx + self._dir_x * self._traveled
        new_surface_y = self._sy + self._dir_y * self._traveled
        dx = new_left_x - old_left_x
        dy = new_surface_y - old_surface_y
        self.left_x = new_left_x
        self.surface_y = new_surface_y
        self.right_x = new_left_x + self.w * sz
        self.cx = new_left_x + self.w * sz / 2.0
        self.cy = new_surface_y - sz / 2.0
        half_h = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2
        bomb_half = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 4
        from bomb import Bomb as _Bomb
        for obj in game_world.get_players() + game_world.get_enemies() + game_world.get_bombs():
            feet_y = obj.y - (bomb_half if isinstance(obj, _Bomb) else half_h)
            if abs(feet_y - old_surface_y) <= 6 and old_left_x < obj.x < old_right_x:
                obj.x += dx
                obj.y += dy

    def draw(self):
        sz = _sz()
        for i in range(self.w):
            if self.w == 1:
                frame_idx = 19
            elif i == 0:
                frame_idx = 16
            elif i == self.w - 1:
                frame_idx = 18
            else:
                frame_idx = 17
            tile_cx = self.left_x + (i + 0.5) * sz
            sprite.draw_frame(TILE_SHEET, frame_idx, TILE_SRC, TILE_SRC,
                               tile_cx + camera.ox, self.cy + camera.oy)
