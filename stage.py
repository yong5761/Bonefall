import os
import sys
from tile import Tile
from enemy import Enemy

_GRID_ROWS = 7
_GRID_COLS = 12

_TILE_CHARS = {
    '#': 0,
    '=': 4,
    '~': 12,
}

_ENTITY_PREFIXES = {
    'P': 'player',
    'E': 'enemy',
    'L': 'lever',
    'M': 'moving',
    'C': 'circle',
    'S': 'switch',
    'K': 'cannon',
    'J': 'jumppad',
    'T': 'pipe',
}

_COORD_COUNTS = {
    'player': (2,),
    'enemy': (2,),
    'lever': (2,),
    'moving': (5, 6),
    'circle': (6, 7),
    'switch': (3,),
    'cannon': (3,),
    'jumppad': (2,),
    'pipe': (6,),
}

_STAGES = []
_PLAYER_STARTS = []
_ENEMY_STARTS = []
_LEVER_STARTS = []
_MOVING_STARTS = []
_CIRCLE_STARTS = []
_SWITCH_STARTS = []
_CANNON_STARTS = []
_PAD_STARTS = []
_PIPE_STARTS = []
_BG_NAMES = []


def _auto_tile(row, gx, ch):
    base = _TILE_CHARS[ch]
    has_left = gx > 0 and row[gx - 1] == ch
    has_right = gx < _GRID_COLS - 1 and row[gx + 1] == ch
    if not has_left and has_right:
        return base
    if has_left and has_right:
        return base + 1
    if has_left and not has_right:
        return base + 2
    return base + 3


def _load_file(path):
    fname = os.path.basename(path)
    with open(path, encoding='utf-8') as f:
        lines = [ln.rstrip('\r\n') for ln in f.readlines()]
    while lines and lines[-1].strip() == '':
        lines.pop()

    if not lines or not lines[0].startswith('bg:'):
        sys.exit(f'{fname}:1: bg: 줄이 없다')
    bg_name = lines[0][3:].strip()

    if len(lines) < 1 + _GRID_ROWS:
        sys.exit(f'{fname}: 격자 줄이 {_GRID_ROWS}개 미만이다')

    grid = lines[1:1 + _GRID_ROWS]
    for ri, row in enumerate(grid):
        if len(row) != _GRID_COLS:
            sys.exit(f'{fname}:{ri + 2}: 격자 줄 길이가 {len(row)}이다 (12이어야 한다)')

    tiles = []
    for ri, row in enumerate(grid):
        gy = (_GRID_ROWS - 1) - ri
        for gx, ch in enumerate(row):
            if ch == '.':
                continue
            if ch not in _TILE_CHARS:
                sys.exit(f'{fname}:{ri + 2}: 알 수 없는 격자 글자 \'{ch}\'')
            tiles.append((gx, gy, _auto_tile(row, gx, ch)))

    player_start = None
    lever_start = None
    enemies = []
    moving_starts = []
    circle_starts = []
    switch_starts = []
    cannon_starts = []
    pad_starts = []
    pipe_starts = []
    for li, line in enumerate(lines[1 + _GRID_ROWS:], start=2 + _GRID_ROWS):
        if line.strip() == '':
            continue
        if ':' not in line:
            sys.exit(f'{fname}:{li}: 접두사가 없는 줄')
        prefix = line[:line.index(':')].strip()
        if prefix not in _ENTITY_PREFIXES:
            sys.exit(f'{fname}:{li}: 알 수 없는 접두사 \'{prefix}\'')
        kind = _ENTITY_PREFIXES[prefix]
        rest = line[line.index(':') + 1:].split(',')
        if len(rest) not in _COORD_COUNTS[kind]:
            sys.exit(f'{fname}:{li}: 좌표 형식 오류')
        try:
            nums = [int(v.strip()) for v in rest]
        except ValueError:
            sys.exit(f'{fname}:{li}: 좌표가 정수가 아니다')
        if kind == 'player':
            if player_start is not None:
                sys.exit(f'{fname}:{li}: P: 줄이 둘 이상이다')
            player_start = (nums[0], nums[1])
        elif kind == 'enemy':
            enemies.append((nums[0], nums[1]))
        elif kind == 'lever':
            if lever_start is not None:
                sys.exit(f'{fname}:{li}: L: 줄이 둘 이상이다')
            lever_start = (nums[0], nums[1])
        elif kind == 'moving':
            moving_starts.append(tuple(nums) + ((0,) if len(nums) == 5 else ()))
        elif kind == 'circle':
            circle_starts.append(tuple(nums) + ((0,) if len(nums) == 6 else ()))
        elif kind == 'switch':
            switch_starts.append((nums[0], nums[1], nums[2]))
        elif kind == 'cannon':
            cannon_starts.append((nums[0], nums[1], nums[2]))
        elif kind == 'jumppad':
            pad_starts.append((nums[0], nums[1]))
        elif kind == 'pipe':
            pipe_starts.append(tuple(nums))

    if player_start is None:
        sys.exit(f'{fname}: P: 줄이 없다')

    return (bg_name, tiles, player_start, enemies, lever_start,
            moving_starts, circle_starts, switch_starts, cannon_starts,
            pad_starts, pipe_starts)


def _load_all():
    stages_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stages')
    if not os.path.isdir(stages_dir):
        sys.exit('stages/ 폴더가 없다')
    paths = sorted(
        os.path.join(stages_dir, fn)
        for fn in os.listdir(stages_dir)
        if fn.endswith('.txt')
    )
    if not paths:
        sys.exit('stages/ 폴더에 .txt 파일이 없다')
    for path in paths:
        (bg_name, tiles, player_start, enemies, lever_start,
         moving_starts, circle_starts, switch_starts,
         cannon_starts, pad_starts, pipe_starts) = _load_file(path)
        _BG_NAMES.append(bg_name)
        _STAGES.append(tiles)
        _PLAYER_STARTS.append(player_start)
        _ENEMY_STARTS.append(enemies)
        _LEVER_STARTS.append(lever_start)
        _MOVING_STARTS.append(moving_starts)
        _CIRCLE_STARTS.append(circle_starts)
        _SWITCH_STARTS.append(switch_starts)
        _CANNON_STARTS.append(cannon_starts)
        _PAD_STARTS.append(pad_starts)
        _PIPE_STARTS.append(pipe_starts)


_load_all()

STAGE_COUNT = len(_STAGES)


def get_player_start(idx):
    return _PLAYER_STARTS[idx]


def get_bg_name(idx):
    return _BG_NAMES[idx]


def build_stage(idx=0):
    return [Tile(gx, gy, ti) for gx, gy, ti in _STAGES[idx]]


def get_stage_data(idx):
    return _STAGES[idx], _ENEMY_STARTS[idx]


def build_enemies(idx=0):
    return [Enemy(x, y) for x, y in _ENEMY_STARTS[idx]]


def get_lever_start(idx):
    return _LEVER_STARTS[idx]


def build_lever(idx=0):
    from lever import Lever
    pos = _LEVER_STARTS[idx]
    if pos is None:
        return None
    return Lever(pos[0], pos[1])


def build_moving(idx=0):
    from tile import MovingTile
    return [MovingTile(x, y, ex, ey, w, g) for x, y, ex, ey, w, g in _MOVING_STARTS[idx]]


def build_circles(idx=0):
    from tile import CircleTile
    return [CircleTile(cx, cy, r, w, speed, start, g)
            for cx, cy, r, w, speed, start, g in _CIRCLE_STARTS[idx]]


def build_switches(idx=0):
    from switch import Switch
    return [Switch(x, y, g) for x, y, g in _SWITCH_STARTS[idx]]


def build_cannons(idx=0):
    from cannon import Cannon
    return [Cannon(x, y, angle) for x, y, angle in _CANNON_STARTS[idx]]


def build_pads(idx=0):
    from pad import Pad
    return [Pad(x, y) for x, y in _PAD_STARTS[idx]]


def build_pipes(idx=0):
    from pipe import Pipe
    return [Pipe(*vals) for vals in _PIPE_STARTS[idx]]
