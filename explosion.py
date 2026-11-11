import sprite
import camera
import game_world

RADIUS = sprite.BLAST_RADIUS_SRC * sprite.DRAW_SCALE
ANIM_DURATION = 0.3
FRAME_COUNT = 11


class Explosion:
    def __init__(self, x, y, blast_type):
        self.x = float(x)
        self.y = float(y)
        self.blast_type = blast_type
        self.elapsed = 0.0
        camera.shake(14, 0.35)
        self._apply_knockback()

    def _apply_knockback(self):
        for p in game_world.get_players():
            dx = p.x - self.x
            dy = p.y - self.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > RADIUS:
                continue
            if dist < 1.0:
                nx, ny = 0.0, 1.0
            else:
                nx, ny = dx / dist, dy / dist
            if self.blast_type == 1:
                nx, ny = -nx, -ny
            p.receive_blast(nx * sprite.BLAST_SPEED_SRC * sprite.DRAW_SCALE,
                            ny * sprite.BLAST_SPEED_SRC * sprite.DRAW_SCALE)

    def update(self, frame_time):
        self.elapsed += frame_time
        if self.elapsed >= ANIM_DURATION:
            game_world.remove(self)

    def draw(self):
        frame = min(int(self.elapsed / ANIM_DURATION * FRAME_COUNT), FRAME_COUNT - 1)
        bottom_offset = sprite.PLAYER_FRAME if self.blast_type == 0 else 0
        img = sprite.load('assets/explosion.png')
        out_size = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE)
        img.clip_composite_draw(
            frame * sprite.PLAYER_FRAME, bottom_offset,
            sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
            0, '',
            self.x + camera.ox, self.y + camera.oy,
            out_size, out_size
        )
