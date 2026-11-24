import math
import sprite
import camera
import game_world
from tile import TILE_SRC as _TILE_SRC

_TILE_SZ = int(_TILE_SRC * sprite.DRAW_SCALE)


class Shot:
    def __init__(self, x, y, angle_rad):
        self.x = float(x)
        self.y = float(y)
        self._vx = math.cos(angle_rad) * sprite.SHOT_SPEED
        self._vy = math.sin(angle_rad) * sprite.SHOT_SPEED
        self._angle = angle_rad
        self._life = 0.0

    def update(self, frame_time):
        self._life += frame_time
        if self._life >= sprite.SHOT_LIFE:
            game_world.remove(self)
            return
        self.x += self._vx * frame_time
        self.y += self._vy * frame_time
        half = sprite.SHOT_HALF
        for tile in game_world.get_tiles():
            if (self.x + half > tile.left_x and self.x - half < tile.right_x
                    and self.y + half > tile.surface_y - _TILE_SZ
                    and self.y - half < tile.surface_y):
                game_world.remove(self)
                return
        from player import HALF_H, FOOT_HALF_W
        for p in game_world.get_players():
            if (abs(self.x - p.x) < half + FOOT_HALF_W
                    and abs(self.y - p.y) < half + HALF_H):
                blast = sprite.SHOT_BLAST_SRC * sprite.DRAW_SCALE
                p.receive_blast(math.cos(self._angle) * blast,
                                math.sin(self._angle) * blast * 0.3)
                game_world.remove(self)
                return
        from bomb import Bomb, BOMB_HALF, FALLING
        for b in game_world.get_bombs():
            if (abs(self.x - b.x) < half + BOMB_HALF
                    and abs(self.y - b.y) < half + BOMB_HALF):
                push = sprite.SHOT_BLAST_SRC * sprite.DRAW_SCALE * 0.5
                b.vx = math.cos(self._angle) * push
                b.vy = math.sin(self._angle) * push * 0.3
                b.state = FALLING
                b.fuse_hold = True
                b.hold_elapsed = 0.0
                game_world.remove(self)
                return

    def draw(self):
        path, _ = sprite.SHEETS['shot']
        img = sprite.load(path)
        out = int(16 * sprite.DRAW_SCALE)
        img.clip_composite_draw(0, 0, 16, 16, 0, '',
                                int(self.x + camera.ox), int(self.y + camera.oy),
                                out, out)
