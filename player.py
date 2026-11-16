import pico2d
import sprite
import camera
import game_world

IDLE = 0
WALK = 1
JUMP = 2
BLAST = 3
PLANT = 4

GRAVITY = -2000.0
JUMP_VY = 900.0
MOVE_SPEED = 400.0
FOOT_HALF_W = int(sprite.FOOT_HALF_W_SRC * sprite.DRAW_SCALE)
HALF_H = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2

_STATE_SHEET = {
    IDLE: 'player_idle',
    WALK: 'player_walk',
    JUMP: 'player_jump',
    BLAST: 'player_blast',
    PLANT: 'player_plant',
}


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.state = IDLE
        self.flip = False
        self.frame = 0.0
        self._blast_vx = 0.0
        self._blast_elapsed = 0.0
        self._control_vx = 0.0
        self.died = False

    def handle_event(self, event):
        if event.type == pico2d.SDL_KEYDOWN:
            if event.key == pico2d.SDLK_SPACE and self.state not in (JUMP, BLAST, PLANT):
                self.vy = JUMP_VY
                self.state = JUMP
                self.frame = 0.0
            elif event.key == pico2d.SDLK_z and self.state not in (PLANT, BLAST):
                import bomb
                bomb.throw(self.x, self.y, self.flip)
                self.state = PLANT
                self.frame = 0.0

    def receive_blast(self, vx, vy):
        self.vx = vx
        self.vy = vy
        self._blast_vx = vx
        self._blast_elapsed = 0.0
        self.state = BLAST
        self.frame = 0.0
        spd = (vx * vx + vy * vy) ** 0.5
        if spd < 1.0:
            sdx, sdy = 0.0, 1.0
        else:
            sdx, sdy = vx / spd, vy / spd
        camera.shake(20, sprite.BLAST_DECAY, sdx, sdy)

    def update(self, frame_time, keys):
        if self.state == PLANT:
            left = pico2d.SDLK_LEFT in keys
            right = pico2d.SDLK_RIGHT in keys
            if left and not right:
                self.vx = -MOVE_SPEED
                self.flip = True
            elif right and not left:
                self.vx = MOVE_SPEED
                self.flip = False
            else:
                self.vx = 0.0
            on_ground = self._on_ground()
            if not on_ground:
                self.vy += GRAVITY * frame_time
            else:
                self.vy = 0.0
            prev_y = self.y
            self.x += self.vx * frame_time
            self.y += self.vy * frame_time
            half_sprite_w = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2
            self.x = max(float(half_sprite_w), min(1920.0 - half_sprite_w, self.x))
            if not on_ground and self.vy <= 0:
                saved_frame = self.frame
                self._try_land(prev_y)
                self.frame = saved_frame
            plant_count = sprite.SHEETS[_STATE_SHEET[PLANT]][1]
            self.frame += sprite.PLANT_FPS * frame_time
            if self.frame >= plant_count:
                self.frame = 0.0
                if self._on_ground():
                    self.state = WALK if (left or right) else IDLE
                else:
                    self.state = JUMP
            if self.y < -300:
                self._reset()
            return

        if self.state == BLAST:
            self._blast_elapsed += frame_time
            ratio = max(0.0, 1.0 - self._blast_elapsed / sprite.BLAST_DECAY)
            self.vx = self._blast_vx * ratio
            left = pico2d.SDLK_LEFT in keys
            right = pico2d.SDLK_RIGHT in keys
            if left and not right:
                self._control_vx = -MOVE_SPEED * sprite.AIR_CONTROL_RATIO
                self.flip = True
            elif right and not left:
                self._control_vx = MOVE_SPEED * sprite.AIR_CONTROL_RATIO
                self.flip = False
            else:
                self._control_vx = 0.0
            prev_y = self.y
            self.vy += GRAVITY * frame_time
            self.x += (self.vx + self._control_vx) * frame_time
            self.y += self.vy * frame_time
            half_sprite_w = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2
            self.x = max(float(half_sprite_w), min(1920.0 - half_sprite_w, self.x))
            prev_feet = prev_y - HALF_H
            curr_feet = self.y - HALF_H
            landed = False
            for tile in game_world.get_tiles():
                if self.x + FOOT_HALF_W <= tile.left_x or self.x - FOOT_HALF_W >= tile.right_x:
                    continue
                if prev_feet >= tile.surface_y and curr_feet <= tile.surface_y:
                    self.y = tile.surface_y + HALF_H
                    self.vy = 0.0
                    landed = True
                    break
            if landed and self._blast_elapsed >= sprite.BLAST_DECAY:
                self.state = WALK if (left or right) else IDLE
            if self.y < -300:
                self._reset()
            blast_count = sprite.SHEETS['player_blast'][1]
            self.frame = min(self._blast_elapsed / sprite.BLAST_DECAY * blast_count, float(blast_count - 1))
            return

        left = pico2d.SDLK_LEFT in keys
        right = pico2d.SDLK_RIGHT in keys

        if left and not right:
            self.vx = -MOVE_SPEED
            self.flip = True
        elif right and not left:
            self.vx = MOVE_SPEED
            self.flip = False
        else:
            self.vx = 0.0

        if self.state == JUMP:
            self.vy += GRAVITY * frame_time

        prev_y = self.y
        self.x += self.vx * frame_time
        self.y += self.vy * frame_time

        half_sprite_w = int(sprite.PLAYER_FRAME * sprite.DRAW_SCALE) // 2
        self.x = max(float(half_sprite_w), min(1920.0 - half_sprite_w, self.x))

        if self.state == JUMP:
            if self.vy <= 0 and self._try_land(prev_y):
                self.state = WALK if (left or right) else IDLE
        else:
            if not self._on_ground():
                self.state = JUMP
                self.vy = 0.0
            else:
                self.state = WALK if (left or right) else IDLE

        if self.y < -300:
            self._reset()

        if self.state == IDLE:
            self.frame = (self.frame + sprite.IDLE_FPS * frame_time) % sprite.SHEETS[_STATE_SHEET[IDLE]][1]
        elif self.state == WALK:
            self.frame = (self.frame + sprite.WALK_FPS * frame_time) % sprite.SHEETS[_STATE_SHEET[WALK]][1]
        else:
            if self.vy > 820:
                self.frame = 0.0
            elif self.vy > 730:
                self.frame = 1.0
            elif self.vy > 640:
                self.frame = 2.0
            elif self.vy > 550:
                self.frame = 3.0
            elif self.vy > 460:
                self.frame = 4.0
            elif self.vy > 375:
                self.frame = 5.0
            elif self.vy > 290:
                self.frame = 6.0
            elif self.vy > 205:
                self.frame = 7.0
            elif self.vy > 125:
                self.frame = 8.0
            elif self.vy > 45:
                self.frame = 9.0
            elif self.vy > -45:
                self.frame = 10.0
            elif self.vy > -125:
                self.frame = 11.0
            elif self.vy > -205:
                self.frame = 12.0
            elif self.vy > -290:
                self.frame = 13.0
            elif self.vy > -375:
                self.frame = 14.0
            elif self.vy > -460:
                self.frame = 15.0
            elif self.vy > -550:
                self.frame = 16.0
            elif self.vy > -640:
                self.frame = 17.0
            elif self.vy > -730:
                self.frame = 18.0
            elif self.vy > -820:
                self.frame = 19.0
            else:
                self.frame = 20.0

    def _try_land(self, prev_y):
        prev_feet = prev_y - HALF_H
        curr_feet = self.y - HALF_H
        for tile in game_world.get_tiles():
            if self.x + FOOT_HALF_W <= tile.left_x or self.x - FOOT_HALF_W >= tile.right_x:
                continue
            if prev_feet > tile.surface_y and curr_feet <= tile.surface_y:
                self.y = tile.surface_y + HALF_H
                self.vy = 0.0
                self.frame = 0.0
                return True
        return False

    def _on_ground(self):
        feet_y = self.y - HALF_H
        for tile in game_world.get_tiles():
            if self.x + FOOT_HALF_W <= tile.left_x or self.x - FOOT_HALF_W >= tile.right_x:
                continue
            if abs(feet_y - tile.surface_y) <= 4:
                return True
        return False

    def _reset(self):
        import bomb
        bomb.remove_active()
        self.x = self.start_x
        self.y = self.start_y
        self.vx = 0.0
        self.vy = 0.0
        self.state = IDLE
        self.frame = 0.0
        self.died = True

    def draw(self):
        path, _ = sprite.SHEETS[_STATE_SHEET[self.state]]
        draw_y = self.y + camera.oy - sprite.FOOT_MARGIN * sprite.DRAW_SCALE
        sprite.draw_frame(
            path, int(self.frame), sprite.PLAYER_FRAME, sprite.PLAYER_FRAME,
            self.x + camera.ox, draw_y, self.flip
        )
