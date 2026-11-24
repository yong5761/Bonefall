import math, os, struct, zlib


def write_png(path, w, h, pixels):
    raw = b''.join(b'\x00' + bytes(pixels[y]) for y in range(h))
    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c))
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def make_shadow(path, w=160, h=80):
    cx, cy = w / 2, h / 2
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            d = math.hypot((x - cx) / (w / 2), (y - cy) / (h / 2))
            a = int(170 * (1.0 - d) ** 1.6) if d < 1.0 else 0
            row += [10, 14, 20, max(a, 0)]
        rows.append(row)
    write_png(path, w, h, rows)


def make_light(path, s=256):
    c = s / 2
    rows = []
    for y in range(s):
        row = []
        for x in range(s):
            d = math.hypot(x - c, y - c) / c
            a = int(255 * (1.0 - d) ** 2.2) if d < 1.0 else 0
            row += [255, 236, 190, max(a, 0)]
        rows.append(row)
    write_png(path, s, s, rows)


def make_shot(path, w=16, h=16):
    rows = []
    cx, cy = w * 0.5, h * 0.5
    for y in range(h):
        row = []
        for x in range(w):
            d = math.hypot(x - cx + 0.5, y - cy + 0.5) / (w * 0.42)
            if d < 1.0:
                a = int(255 * (1.0 - d ** 0.65))
                t = 1.0 - d
                r = 255
                g = int(220 * t + 90 * (1 - t))
                b = int(40 * t)
                row += [r, min(255, g), max(0, b), max(0, a)]
            else:
                row += [0, 0, 0, 0]
        rows.append(row)
    write_png(path, w, h, rows)


def make_scenery_mid(path, w=1920, h=1080):
    PILLAR_CX = [300, 960, 1620]
    PILLAR_W = 150
    PILLAR_EDGE = 20
    FADE_START_NY = 0.40
    FADE_END_NY = 0.55
    BASE_ALPHA = 175
    EDGE_ALPHA = 70
    SR, SG, SB = 10, 14, 24

    rows = []
    for y in range(h):
        ny = y / h
        row = []
        if ny >= FADE_END_NY:
            rows.append([0, 0, 0, 0] * w)
            continue
        for x in range(w):
            a = 0
            for pcx in PILLAR_CX:
                dx = abs(x - pcx)
                if dx < PILLAR_W / 2:
                    dist_edge = (PILLAR_W / 2) - dx
                    if dist_edge < PILLAR_EDGE:
                        col_a = int(EDGE_ALPHA + (BASE_ALPHA - EDGE_ALPHA) * dist_edge / PILLAR_EDGE)
                    else:
                        col_a = BASE_ALPHA
                    if ny >= FADE_START_NY:
                        t = (ny - FADE_START_NY) / (FADE_END_NY - FADE_START_NY)
                        col_a = int(col_a * (1.0 - t))
                    a = max(a, col_a)
            if a > 0:
                row += [SR, SG, SB, a]
            else:
                row += [0, 0, 0, 0]
        rows.append(row)
    write_png(path, w, h, rows)


def make_scenery_fore(path, w=1920, h=1080):
    LEFT_X = 300
    RIGHT_X = 1620
    PILLAR_W = 150
    FADE_W = 60
    PILLAR_ALPHA = 200
    PILLAR_NY_END = 0.34
    PILLAR_FADE_START = 0.26
    CHAIN_ALPHA = 255
    CHAIN_L_X = 275
    CHAIN_R_X = 1645
    CHAIN_NY_END = 0.30
    RING_H = 36
    RING_W = 22
    RING_GAP = -6
    RING_THICK = 6
    FR, FG, FB = 6, 9, 16

    period = RING_H + RING_GAP  # 30

    rows = []
    for y in range(h):
        ny = y / h
        row = []
        for x in range(w):
            a = 0
            # left pillar
            if x < LEFT_X and ny < PILLAR_NY_END:
                inner_dist = LEFT_X - x
                base_a = int(PILLAR_ALPHA * min(inner_dist, FADE_W) / FADE_W)
                if ny >= PILLAR_FADE_START:
                    tv = (ny - PILLAR_FADE_START) / (PILLAR_NY_END - PILLAR_FADE_START)
                    base_a = int(base_a * (1.0 - tv))
                a = max(a, base_a)
            # right pillar
            if x > RIGHT_X and ny < PILLAR_NY_END:
                inner_dist = x - RIGHT_X
                base_a = int(PILLAR_ALPHA * min(inner_dist, FADE_W) / FADE_W)
                if ny >= PILLAR_FADE_START:
                    tv = (ny - PILLAR_FADE_START) / (PILLAR_NY_END - PILLAR_FADE_START)
                    base_a = int(base_a * (1.0 - tv))
                a = max(a, base_a)
            # chains (hollow overlapping rings)
            if ny <= CHAIN_NY_END:
                rx = RING_W / 2.0
                ry = RING_H / 2.0
                rx_in = rx - RING_THICK
                ry_in = ry - RING_THICK
                for cx in (CHAIN_L_X, CHAIN_R_X):
                    dx = x - cx
                    if abs(dx) > rx:
                        continue
                    # find all ring indices whose span includes y
                    i_lo = max(0, (y - RING_H + 1) // period)
                    i_hi = y // period + 1
                    for i in range(i_lo, i_hi + 1):
                        ring_top = i * period
                        dy = y - (ring_top + ry)
                        nx_e = dx / rx
                        ny_e = dy / ry
                        if nx_e ** 2 + ny_e ** 2 <= 1.0:
                            nx_i = dx / rx_in if rx_in > 0 else 1e9
                            ny_i = dy / ry_in if ry_in > 0 else 1e9
                            if nx_i ** 2 + ny_i ** 2 > 1.0:
                                a = max(a, CHAIN_ALPHA)
            if a > 0:
                row += [FR, FG, FB, a]
            else:
                row += [0, 0, 0, 0]
        rows.append(row)
    write_png(path, w, h, rows)


if __name__ == '__main__':
    os.makedirs('assets', exist_ok=True)
    make_shadow('assets/shadow.png')
    make_light('assets/light.png')
    make_shot('assets/shot.png')
    make_scenery_mid('assets/scenery_mid.png')
    make_scenery_fore('assets/scenery_fore.png')
    print('assets/shadow.png 160x80')
    print('assets/light.png 256x256')
    print('assets/shot.png 16x16')
    print('assets/scenery_mid.png 1920x1080')
    print('assets/scenery_fore.png 1920x1080')
