import sprite
import camera
import game_world
import sound

LOCKED = 0
READY = 1
PULLED = 2


class Lever:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.state = LOCKED

    def update(self, frame_time):
        if self.state == LOCKED and not game_world.get_enemies():
            self.state = READY
            sound.play('lever_ready')

    def receive_blast(self, vx, vy):
        if self.state == READY:
            self.state = PULLED
            sound.play('lever_pull')

    def draw(self):
        path, frame_w = sprite.SHEETS['lever']
        sprite.draw_frame(path, self.state, frame_w, 64,
                          self.x + camera.ox, self.y + camera.oy)
