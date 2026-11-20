import math
import sprite
import camera
import sound
import fx
import game_world

EXIT_SPEED = 760.0
MOUTH_W = 64
MOUTH_H = 64
CATCH = 44.0
MOUTH_OFFSET = 36.0


class Pipe:
    def __init__(self, ix, iy, iangle, ox, oy, oangle):
        self.ix = float(ix)
        self.iy = float(iy)
        self.iangle = float(iangle)
        self.ox = float(ox)
        self.oy = float(oy)
        self.oangle = float(oangle)

    def update(self, frame_time):
        import bomb as _bomb
        for b in game_world.get_bombs():
            if b.pipe_cool > 0.0:
                continue
            if (b.x - self.ix) ** 2 + (b.y - self.iy) ** 2 > CATCH * CATCH:
                continue
            a = math.radians(self.oangle)
            b.x = self.ox + MOUTH_OFFSET * math.cos(a)
            b.y = self.oy + MOUTH_OFFSET * math.sin(a)
            b.vx = EXIT_SPEED * math.cos(a)
            b.vy = EXIT_SPEED * math.sin(a)
            b.state = _bomb.FALLING
            b.fuse_hold = True
            b.pipe_cool = 0.4
            sound.play('throw')
            fx.trigger_debris(b.x, b.y)

    def draw(self):
        s = sprite.DRAW_SCALE
        path, frame_w = sprite.SHEETS['pipe_mouth']
        img = sprite.load(path)
        for frame_idx, x, y, ang in ((0, self.ix, self.iy, self.iangle),
                                     (1, self.ox, self.oy, self.oangle)):
            img.clip_composite_draw(frame_idx * frame_w, 0, frame_w, MOUTH_H,
                                    math.radians(ang), '',
                                    int(x + camera.ox), int(y + camera.oy),
                                    int(MOUTH_W * s), int(MOUTH_H * s))
