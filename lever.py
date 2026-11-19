import sprite
import camera
import game_world
import sound
import fx

LOCKED = 0
READY = 1
PULLED = 2

READY_BURST_TIME = 0.6
PULL_BURST_TIME = 0.7


class Lever:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.state = LOCKED
        self.ready_elapsed = -1.0
        self.pull_elapsed = -1.0

    def update(self, frame_time):
        if self.ready_elapsed >= 0.0:
            self.ready_elapsed += frame_time
        if self.pull_elapsed >= 0.0:
            self.pull_elapsed += frame_time
        if self.state == LOCKED and not game_world.get_enemies():
            self.state = READY
            self.ready_elapsed = 0.0
            sound.play('lever_ready')

    def receive_blast(self, vx, vy):
        if self.state == READY:
            self.state = PULLED
            self.pull_elapsed = 0.0
            sound.play('lever_pull')
            fx.trigger_flash()
            fx.trigger_debris(self.x, self.y + 12.0)
            camera.shake(16.0, 0.35, 0.0, 1.0)

    def draw(self):
        path, frame_w = sprite.SHEETS['lever']
        sprite.draw_frame(path, self.state, frame_w, 64,
                          self.x + camera.ox, self.y + camera.oy)
