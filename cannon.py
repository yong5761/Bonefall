import math
import sprite
import camera
import sound
import fx

LOAD_TIME = 0.8
MUZZLE_SPEED = 1150.0
REACH = 150.0

BASE = 'assets/cannon_base.png'
BARREL = 'assets/cannon_barrel.png'
BASE_W = 76
BASE_H = 48
BARREL_W = 80
BARREL_H = 44
PIVOT_SRC = 16.0


class Cannon:
    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.has_bomb = False
        self.bomb_type = 0
        self.loaded = 0.0

    def in_reach(self, px, py):
        return (not self.has_bomb and abs(px - self.x) <= REACH
                and abs(py - self.y) <= REACH)

    def load(self, bomb_type):
        self.has_bomb = True
        self.bomb_type = bomb_type
        self.loaded = 0.0
        sound.play('lever_pull')

    def _pivot(self):
        return self.x, self.y + 10.0 * sprite.DRAW_SCALE

    def _muzzle(self):
        a = math.radians(self.angle)
        px, py = self._pivot()
        length = (BARREL_W - PIVOT_SRC) * sprite.DRAW_SCALE
        return px + length * math.cos(a), py + length * math.sin(a)

    def update(self, frame_time):
        if not self.has_bomb:
            return
        self.loaded += frame_time
        if self.loaded >= LOAD_TIME:
            self._fire()

    def _fire(self):
        import bomb
        a = math.radians(self.angle)
        mx, my = self._muzzle()
        bomb.launch(mx, my, MUZZLE_SPEED * math.cos(a),
                    MUZZLE_SPEED * math.sin(a), self.bomb_type)
        self.has_bomb = False
        self.loaded = 0.0
        sound.play('throw')
        camera.shake(13.0, 0.28, math.cos(a), math.sin(a))
        fx.trigger_debris(mx, my)

    def draw(self):
        s = sprite.DRAW_SCALE
        a = math.radians(self.angle)
        px, py = self._pivot()
        off = (BARREL_W / 2.0 - PIVOT_SRC) * s
        cx = px + off * math.cos(a)
        cy = py + off * math.sin(a)
        img = sprite.load(BARREL)
        img.clip_composite_draw(0, 0, BARREL_W, BARREL_H, a, '',
                                int(cx + camera.ox), int(cy + camera.oy),
                                int(BARREL_W * s), int(BARREL_H * s))
        sprite.load(BASE).draw(int(self.x + camera.ox), int(self.y + camera.oy),
                               int(BASE_W * s), int(BASE_H * s))
