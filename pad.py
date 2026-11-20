import sprite
import camera
import sound
import fx
import game_world

BOUNCE = 1400.0
EXTEND_TIME = 0.18
PAD_W = 64
PAD_H = 32


class Pad:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.extend = 0.0

    def update(self, frame_time):
        if self.extend > 0.0:
            self.extend -= frame_time
        import player as _player
        import enemy as _enemy
        import bomb as _bomb
        half_w = PAD_W * sprite.DRAW_SCALE / 2.0
        for obj in (game_world.get_players() + game_world.get_enemies()
                    + game_world.get_bombs()):
            if abs(obj.x - self.x) > half_w:
                continue
            if getattr(obj, 'vy', 1.0) > 0.0:
                continue
            if isinstance(obj, _bomb.Bomb):
                feet = obj.y - _bomb.BOMB_HALF
            else:
                feet = obj.y - _enemy.HALF_H
            if not (-18.0 <= feet - self.y <= 26.0):
                continue
            self._bounce(obj, _player, _enemy, _bomb)

    def _bounce(self, obj, _player, _enemy, _bomb):
        self.extend = EXTEND_TIME
        sound.play('jump')
        fx.trigger_debris(self.x, self.y + 20.0)
        camera.shake(8.0, 0.18, 0.0, 1.0)
        if isinstance(obj, _bomb.Bomb):
            obj.y = self.y + _bomb.BOMB_HALF + 14.0
            obj.vy = BOUNCE
            obj.state = _bomb.FALLING
            obj.fuse_hold = True
            obj.fuse = 0.0
            return
        if isinstance(obj, _enemy.Enemy):
            obj.y = self.y + _enemy.HALF_H + 14.0
            obj._enter_fall_grounded()
            obj.vy = BOUNCE
            return
        obj.y = self.y + _player.HALF_H + 14.0
        obj.vy = BOUNCE
        if obj.state != _player.BLAST:
            obj.state = _player.JUMP
            obj.frame = 0.0

    def draw(self):
        s = sprite.DRAW_SCALE
        path, frame_w = sprite.SHEETS['jumppad']
        frame_idx = 1 if self.extend > 0.0 else 0
        sprite.draw_frame(path, frame_idx, frame_w, PAD_H,
                          self.x + camera.ox,
                          self.y - PAD_H * s / 2.0 + 14.0 * s + camera.oy)
