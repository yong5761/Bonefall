import sprite
import camera
import sound
import fx


class Switch:
    def __init__(self, x, y, group):
        self.x = float(x)
        self.y = float(y)
        self.group = int(group)
        self.on = False

    def update(self, frame_time):
        pass

    def receive_blast(self, vx, vy):
        self.on = not self.on
        sound.play('lever_pull')
        fx.trigger_debris(self.x, self.y + 12.0)
        camera.shake(10.0, 0.25, 0.0, 1.0)

    def draw(self):
        path, frame_w = sprite.SHEETS['switch']
        sprite.draw_frame(path, 1 if self.on else 0, frame_w, 64,
                          self.x + camera.ox, self.y + camera.oy)
