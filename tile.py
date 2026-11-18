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
