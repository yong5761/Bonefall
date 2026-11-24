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
    PILLAR_W = 110
    PILLAR_EDGE = 20
    ARCH_THICK = 40
    ARCH_NY_TOP = 0.08
    ARCH_NY_BOT = 0.30
    FADE_START_NY = 0.40
    FADE_END_NY = 0.55
    BASE_ALPHA = 130
    EDGE_ALPHA = 70
    SR, SG, SB = 14, 20, 34

    rows = []
    for y in range(h):
        ny = y / h
        row = []
        if ny >= FADE_END_NY:
            rows.append([0, 0, 0, 0] * w)
            continue
        for x in range(w):
            a = 0
            # pillars
            for pcx in PILLAR_CX:
                dx = abs(x - pcx)
                if dx < PILLAR_W / 2:
                    dist_edge = (PILLAR_W / 2) - dx
                    if dist_edge < PILLAR_EDGE:
                        col_a = int(EDGE_ALPHA + (BASE_ALPHA - EDGE_ALPHA) * dist_edge / PILLAR_EDGE)
                    else:
                        col_a = BASE_ALPHA
                    # fade out toward bottom
                    if ny >= FADE_START_NY:
                        t = (ny - FADE_START_NY) / (FADE_END_NY - FADE_START_NY)
                        col_a = int(col_a * (1.0 - t))
                    a = max(a, col_a)
            # arches between adjacent pillar pairs
            for i in range(len(PILLAR_CX) - 1):
                ax1, ax2 = PILLAR_CX[i], PILLAR_CX[i + 1]
                arc_cx = (ax1 + ax2) / 2.0
                arc_rx = (ax2 - ax1) / 2.0
                arc_cy_ny = ARCH_NY_TOP
                arc_ry_ny = ARCH_NY_BOT - ARCH_NY_TOP
                # ellipse: ((x-arc_cx)/arc_rx)^2 + ((ny-arc_cy_ny)/arc_ry_ny)^2
                nx_norm = (x - arc_cx) / arc_rx
                ny_norm = (ny - arc_cy_ny) / arc_ry_ny
                r2 = nx_norm ** 2 + ny_norm ** 2
                # ring of thickness ARCH_THICK pixels mapped to ny space
                thick_ny = ARCH_THICK / h
                outer_scale = 1.0
                inner_scale = 1.0 - thick_ny / arc_ry_ny
                if abs(nx_norm) <= 1.0 and ny_norm >= 0.0:
                    r_outer = nx_norm ** 2 + ny_norm ** 2
                    ny_inner = (ny - arc_cy_ny - thick_ny) / arc_ry_ny if arc_ry_ny > 0 else 0
                    r_inner = nx_norm ** 2 + (ny_inner if ny_inner > 0 else 0) ** 2
                    in_outer = r_outer <= 1.0
                    in_inner = r_inner <= (inner_scale ** 2) if inner_scale > 0 else False
                    if in_outer and not in_inner:
                        arch_a = BASE_ALPHA
                        if ny >= FADE_START_NY:
                            t = (ny - FADE_START_NY) / (FADE_END_NY - FADE_START_NY)
                            arch_a = int(arch_a * (1.0 - t))
                        a = max(a, arch_a)
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
    PILLAR_ALPHA = 235
    CHAIN_ALPHA = 255
    CHAIN_L_X = 275
    CHAIN_R_X = 1645
    CHAIN_NY_END = 0.45
    RING_H = 28
    RING_W = 18
    RING_GAP = 14
    FR, FG, FB = 6, 9, 16

    rows = []
    for y in range(h):
        ny = y / h
        row = []
        for x in range(w):
            a = 0
            # left pillar: x < LEFT_X, outer edge at x=0, inner edge at x=LEFT_X
            if x < LEFT_X:
                inner_dist = LEFT_X - x
                if inner_dist <= FADE_W:
                    t = inner_dist / FADE_W
                    a = max(a, int(PILLAR_ALPHA * t))
                else:
                    a = max(a, PILLAR_ALPHA)
            # right pillar: x > RIGHT_X, outer edge at x=w-1, inner edge at x=RIGHT_X
            if x > RIGHT_X:
                inner_dist = x - RIGHT_X
                if inner_dist <= FADE_W:
                    t = inner_dist / FADE_W
                    a = max(a, int(PILLAR_ALPHA * t))
                else:
                    a = max(a, PILLAR_ALPHA)
            # chains (only in ny 0..CHAIN_NY_END)
            if ny <= CHAIN_NY_END:
                for cx in (CHAIN_L_X, CHAIN_R_X):
                    if abs(x - cx) <= RING_W // 2:
                        # determine which ring segment this y falls in
                        period = RING_H + RING_GAP
                        y_in_period = int(y) % period
                        if y_in_period < RING_H:
                            # inside a ring oval vertically
                            ring_cy = y_in_period - RING_H / 2
                            ring_nx = (x - cx) / (RING_W / 2)
                            ring_ny = ring_cy / (RING_H / 2)
                            if ring_nx ** 2 + ring_ny ** 2 <= 1.0:
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
