import math
import pico2d
import game_world
import sprite
import camera

TILE_SHEET = 'assets/tiles.png'
TILE_SRC = 80
RAIL_NODE = 'assets/rail_node.png'
RAIL_NODE_SIZE = 38


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


def _group_on(group):
    if group == 0:
        return True
    from switch import Switch
    for obj in game_world.get_switches():
        if obj.group == group:
            return obj.on
    return True


def _carry_riders(old_left, old_right, old_surface, dx, dy):
    if dx == 0.0 and dy == 0.0:
        return
    half_h = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2
    bomb_half = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 4
    from bomb import Bomb as _Bomb
    for obj in game_world.get_players() + game_world.get_enemies() + game_world.get_bombs():
        feet_y = obj.y - (bomb_half if isinstance(obj, _Bomb) else half_h)
        if abs(feet_y - old_surface) <= 6 and old_left < obj.x < old_right:
            obj.x += dx
            obj.y += dy


class MovingTile(Tile):
    def __init__(self, x, y, ex, ey, w, group=0):
        sz = _sz()
        self.w = w
        self.group = int(group)
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
        if not _group_on(self.group):
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
        _carry_riders(old_left_x, old_right_x, old_surface_y, dx, dy)

    def rail_endpoints(self):
        sz = _sz()
        half = self.w * sz / 2.0
        return (self._sx + half,
                self._sy - sz / 4.0,
                self._sx + self._dir_x * self._dist + half,
                self._sy + self._dir_y * self._dist - sz / 4.0)

    def rail_points(self):
        x0, y0, x1, y1 = self.rail_endpoints()
        length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        if length < 1.0:
            return []
        ux = (x1 - x0) / length
        uy = (y1 - y0) / length
        pts = []
        count = int(length / 160.0)
        for k in range(count + 1):
            t = min(length, k * 160.0)
            pts.append((x0 + ux * t, y0 + uy * t))
        return pts

    def _draw_rail(self):
        x0, y0, x1, y1 = self.rail_endpoints()
        x0 += camera.ox
        y0 += camera.oy
        x1 += camera.ox
        y1 += camera.oy
        length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        if length < 1.0:
            return
        ux = (x1 - x0) / length
        uy = (y1 - y0) / length
        steps = int(length / 4.0) + 1
        for half, col in ((4, (0x16, 0x26, 0x34)), (2, (0x2E, 0x7A, 0xAA)), (1, (0x8C, 0xE6, 0xFF))):
            for k in range(steps + 1):
                t = min(length, k * 4.0)
                px = x0 + ux * t
                py = y0 + uy * t
                pico2d.draw_rectangle(int(px - half), int(py - half),
                                      int(px + half), int(py + half),
                                      col[0], col[1], col[2], 255, filled=True)
        node = sprite.load(RAIL_NODE)
        gap = 160.0
        count = int(length / gap)
        for k in range(count + 1):
            t = min(length, k * gap)
            node.draw(int(x0 + ux * t), int(y0 + uy * t), RAIL_NODE_SIZE, RAIL_NODE_SIZE)
        node.draw(int(x1), int(y1), RAIL_NODE_SIZE, RAIL_NODE_SIZE)

    def draw(self):
        self._draw_rail()
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


class CircleTile(Tile):
    def __init__(self, cx, cy, r, w, speed, start, group=0):
        self.w = w
        self.group = int(group)
        self.is_weak = False
        self.is_ice = False
        self._breaking = False
        self._break_elapsed = 0.0
        self._orbit_cx = float(cx)
        self._orbit_cy = float(cy)
        self._r = float(r)
        self._speed = float(speed)
        self._angle = float(start) % 360.0
        self._apply_angle()

    def _point(self, deg):
        a = math.radians(deg)
        return (self._orbit_cx + self._r * math.cos(a),
                self._orbit_cy + self._r * math.sin(a))

    def _apply_angle(self):
        sz = _sz()
        px, py = self._point(self._angle)
        self.left_x = px - self.w * sz / 2.0
        self.right_x = self.left_x + self.w * sz
        self.surface_y = py + sz / 4.0
        self.cx = self.left_x + self.w * sz / 2.0
        self.cy = self.surface_y - sz / 2.0

    def update(self, frame_time):
        if not _group_on(self.group):
            return
        old_left = self.left_x
        old_right = self.right_x
        old_surface = self.surface_y
        self._angle = (self._angle + self._speed * frame_time) % 360.0
        self._apply_angle()
        _carry_riders(old_left, old_right, old_surface,
                      self.left_x - old_left, self.surface_y - old_surface)

    def rail_points(self):
        circ = 2.0 * math.pi * self._r
        count = max(4, int(circ / 160.0))
        return [self._point(i * 360.0 / count) for i in range(count)]

    def _draw_rail(self):
        steps = max(32, int(2.0 * math.pi * self._r / 4.0))
        for half, col in ((4, (0x16, 0x26, 0x34)), (2, (0x2E, 0x7A, 0xAA)),
                          (1, (0x8C, 0xE6, 0xFF))):
            for k in range(steps):
                px, py = self._point(k * 360.0 / steps)
                px += camera.ox
                py += camera.oy
                pico2d.draw_rectangle(int(px - half), int(py - half),
                                      int(px + half), int(py + half),
                                      col[0], col[1], col[2], 255, filled=True)
        node = sprite.load(RAIL_NODE)
        for wx, wy in self.rail_points():
            node.draw(int(wx + camera.ox), int(wy + camera.oy),
                      RAIL_NODE_SIZE, RAIL_NODE_SIZE)

    def draw(self):
        self._draw_rail()
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
