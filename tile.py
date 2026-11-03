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

    def update(self, frame_time):
        pass

    def draw(self):
        sprite.draw_frame(
            TILE_SHEET, self.tile_index, TILE_SRC, TILE_SRC,
            self.cx + camera.ox, self.cy + camera.oy
        )
