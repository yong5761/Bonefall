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


def make_tiles(path):
    TW, TH = 80, 80
    FRAMES = 20
    W = TW * FRAMES

    # --- helpers ---
    def _hash(x, y, seed=0):
        v = (x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)
        return ((v >> 3) & 0x7FFFFFFF)

    def _clamp(v): return max(0, min(255, v))

    def _lerp(a, b, t): return int(a + (b - a) * t)

    # write a pixel into a flat RGBA list indexed [y][x*4+c]
    def _put(rows, x, y, r, g, b, a):
        if 0 <= x < TW and 0 <= y < TH:
            base = x * 4
            rows[y][base] = r; rows[y][base+1] = g
            rows[y][base+2] = b; rows[y][base+3] = a

    def _get(rows, x, y):
        if 0 <= x < TW and 0 <= y < TH:
            b = x * 4
            return rows[y][b], rows[y][b+1], rows[y][b+2], rows[y][b+3]
        return 0, 0, 0, 0

    def _blend(rows, x, y, r, g, b, a):
        if 0 <= x < TW and 0 <= y < TH:
            pr, pg, pb, pa = _get(rows, x, y)
            t = a / 255.0
            _put(rows, x, y, _clamp(int(pr*(1-t)+r*t)), _clamp(int(pg*(1-t)+g*t)),
                 _clamp(int(pb*(1-t)+b*t)), max(pa, a))

    # corner-cut mask: returns False if pixel is in a cut corner (4px)
    CUT = 4
    def _corner_cut(x, y, left_cap, right_cap):
        if left_cap:
            if x < CUT and y < CUT - x: return False
            if x < CUT and y >= TH - (CUT - x): return False
        if right_cap:
            rx = TW - 1 - x
            if rx < CUT and y < CUT - rx: return False
            if rx < CUT and y >= TH - (CUT - rx): return False
        return True

    # --- stone (frames 0-3) ---
    def make_stone(fi, left_cap, right_cap):
        rows = [[0]*TW*4 for _ in range(TH)]
        SURF = 40  # surface height

        for y in range(TH):
            for x in range(TW):
                if not _corner_cut(x, y, left_cap, right_cap):
                    continue
                if y < SURF:
                    # surface gradient #7A6E5C -> #3A332B
                    t = y / (SURF - 1)
                    r = _lerp(0x7A, 0x3A, t)
                    g = _lerp(0x6E, 0x33, t)
                    b = _lerp(0x5C, 0x2B, t)
                    al = 255
                else:
                    # underside gradient -> #241F1A, bottom 6px alpha fade
                    td = (y - SURF) / (TH - SURF - 1) if TH > SURF + 1 else 0
                    r = _lerp(0x3A, 0x24, td)
                    g = _lerp(0x33, 0x1F, td)
                    b = _lerp(0x2B, 0x1A, td)
                    al = 255
                    if y >= TH - 6:
                        fade_t = (y - (TH - 6)) / 5
                        al = _clamp(int(255 - (255 - 180) * fade_t))
                _put(rows, x, y, r, g, b, al)

        # highlight top 5px
        for y in range(5):
            for x in range(TW):
                if _corner_cut(x, y, left_cap, right_cap):
                    _put(rows, x, y, 0x9A, 0x8C, 0x74, 255)

        # dark line below surface (3px)
        for y in range(SURF, SURF + 3):
            for x in range(TW):
                if _corner_cut(x, y, left_cap, right_cap):
                    _put(rows, x, y, 0x2A, 0x25, 0x1E, 255)

        # border on caps (2px dark)
        if left_cap:
            for y in range(CUT, TH - CUT):
                _put(rows, 0, y, 0x2A, 0x25, 0x1E, 255)
                _put(rows, 1, y, 0x2A, 0x25, 0x1E, 255)
        if right_cap:
            for y in range(CUT, TH - CUT):
                _put(rows, TW-1, y, 0x2A, 0x25, 0x1E, 255)
                _put(rows, TW-2, y, 0x2A, 0x25, 0x1E, 255)

        # stone split lines (vary position per frame)
        # vertical: 2 lines inside SURF zone
        offsets_v = [(23 + fi*7) % (TW-8) + 4, (51 + fi*13) % (TW-8) + 4]
        for vx in offsets_v:
            for y in range(2, SURF):
                if _corner_cut(vx, y, left_cap, right_cap):
                    _put(rows, vx, y, 0x2A, 0x25, 0x1E, 255)
                    if vx+1 < TW:
                        _put(rows, vx+1, y, 0x2A, 0x25, 0x1E, 255)
        # horizontal: 1 line
        hy = (12 + fi*5) % (SURF - 8) + 4
        for x in range(2, TW-2):
            if _corner_cut(x, hy, left_cap, right_cap):
                _put(rows, x, hy, 0x2A, 0x25, 0x1E, 255)

        # speckle (6% of surface pixels)
        for y in range(1, SURF - 1):
            for x in range(TW):
                h = _hash(x + fi*80, y)
                if h % 100 < 3:
                    _blend(rows, x, y, 0x8C, 0x7F, 0x69, 160)
                elif h % 100 < 6:
                    _blend(rows, x, y, 0x33, 0x2C, 0x25, 160)

        # moss strip on highlight (irregular horizontal band 3-5px thick)
        moss_thick = 3 + (fi * 3) % 3  # 3,4,5 per frame variant
        # break points: 3 segments with gaps
        gaps = [(10 + fi*17) % (TW//2), (40 + fi*11) % (TW//2) + TW//4]
        GAP_W = 10 + fi * 3
        for y in range(2, 2 + moss_thick):
            for x in range(TW):
                in_gap = any(abs(x - gx) < GAP_W // 2 for gx in gaps)
                if not in_gap and _corner_cut(x, y, left_cap, right_cap):
                    _blend(rows, x, y, 0x5A, 0x6B, 0x3A, 120)

        return rows

    # --- wood (frames 4-7) ---
    def make_wood(fi, left_cap, right_cap):
        rows = [[0]*TW*4 for _ in range(TH)]
        SURF = 40

        for y in range(TH):
            for x in range(TW):
                if not _corner_cut(x, y, left_cap, right_cap):
                    continue
                if y < SURF:
                    t = y / (SURF - 1)
                    r = _lerp(0x7A, 0x3E, t)
                    g = _lerp(0x5A, 0x2C, t)
                    b = _lerp(0x38, 0x1C, t)
                    al = 255
                else:
                    td = (y - SURF) / (TH - SURF - 1) if TH > SURF + 1 else 0
                    r = _lerp(0x3E, 0x20, td)
                    g = _lerp(0x2C, 0x16, td)
                    b = _lerp(0x1C, 0x0E, td)
                    al = 255
                    if y >= TH - 6:
                        fade_t = (y - (TH - 6)) / 5
                        al = _clamp(int(255 - (255 - 180) * fade_t))
                _put(rows, x, y, r, g, b, al)

        # highlight top 4px
        for y in range(4):
            for x in range(TW):
                if _corner_cut(x, y, left_cap, right_cap):
                    _put(rows, x, y, 0x96, 0x74, 0x4A, 255)

        if left_cap:
            for y in range(CUT, TH - CUT):
                _put(rows, 0, y, 0x2A, 0x1A, 0x0C, 255)
                _put(rows, 1, y, 0x2A, 0x1A, 0x0C, 255)
        if right_cap:
            for y in range(CUT, TH - CUT):
                _put(rows, TW-1, y, 0x2A, 0x1A, 0x0C, 255)
                _put(rows, TW-2, y, 0x2A, 0x1A, 0x0C, 255)

        # grain lines (5-7 horizontal lines, vary per frame)
        num_grains = 5 + fi % 3
        for gi in range(num_grains):
            gy = int(6 + gi * (SURF - 6) / num_grains + (fi * 3 + gi * 7) % 4)
            gx_start = (_hash(fi, gi, 1) % (TW // 3))
            gx_len = TW // 2 + (_hash(fi, gi, 2) % (TW // 3))
            thickness = 1 + (gi + fi) % 2
            for t in range(thickness):
                for gx in range(gx_start, min(gx_start + gx_len, TW)):
                    if _corner_cut(gx, gy + t, left_cap, right_cap):
                        _blend(rows, gx, gy + t, 0x4A, 0x35, 0x22, 180)

        # plank dividers: 2 vertical dark lines
        px1 = (22 + fi * 11) % (TW - 10) + 5
        px2 = (50 + fi * 7) % (TW - 10) + 5
        for pxv in (px1, px2):
            for y in range(2, TH - 2):
                if _corner_cut(pxv, y, left_cap, right_cap):
                    _put(rows, pxv, y, 0x2A, 0x1A, 0x0C, 255)

        # nails: 2x2 bright dots at plank ends
        plank_starts = [0, px1 + 2, px2 + 2]
        plank_ends = [px1 - 2, px2 - 2, TW - 1]
        for ps, pe in zip(plank_starts, plank_ends):
            nail_y = 15 + fi % 5
            for nx2 in (ps + 3, pe - 3):
                for dy2 in range(2):
                    for dx2 in range(2):
                        nx3, ny3 = nx2 + dx2, nail_y + dy2
                        if _corner_cut(nx3, ny3, left_cap, right_cap):
                            _put(rows, nx3, ny3, 0xA8, 0x90, 0x70, 255)

        return rows

    # --- crumbling wood (frames 8-11, based on wood center fi=1) ---
    def make_crumble(stage):
        # start from wood center
        rows = make_wood(1, False, False)
        SURF = 40

        crack_color = (0x2A, 0x1C, 0x10)

        def crack(rows, x0, y0, dx, dy, length):
            cx2, cy2 = x0, y0
            for _ in range(length):
                _put(rows, int(cx2), int(cy2), *crack_color, 255)
                if int(cx2+1) < TW:
                    _put(rows, int(cx2)+1, int(cy2), *crack_color, 200)
                cx2 += dx; cy2 += dy

        if stage >= 0:  # 1 crack
            crack(rows, 20, 2, 0.6, 1.2, 18)
        if stage >= 1:  # 3 cracks total
            crack(rows, 50, 3, -0.4, 1.0, 20)
            crack(rows, 35, 8, 1.0, 0.3, 15)
        if stage >= 2:  # corners gone (alpha=0)
            for y in range(TH):
                for x in range(TW):
                    if x < 12 and y > TH - 20:
                        _put(rows, x, y, 0, 0, 0, 0)
                    if x > TW - 13 and y > TH - 15:
                        _put(rows, x, y, 0, 0, 0, 0)
                    if x < 8 and y < 12:
                        _put(rows, x, y, 0, 0, 0, 0)
        if stage >= 3:  # more than half gone
            for y in range(TH):
                for x in range(TW):
                    if x > TW // 2 + 10 and y > SURF - 5:
                        _put(rows, x, y, 0, 0, 0, 0)
                    if x < 20 and y > SURF + 10:
                        _put(rows, x, y, 0, 0, 0, 0)
                    if y > SURF + 25:
                        _put(rows, x, y, 0, 0, 0, 0)

        return rows

    # --- ice (frames 12-15) ---
    def make_ice(fi, left_cap, right_cap):
        rows = [[0]*TW*4 for _ in range(TH)]
        SURF = 40
        ICE_ALPHA = 215

        for y in range(TH):
            for x in range(TW):
                if not _corner_cut(x, y, left_cap, right_cap):
                    continue
                if y < SURF:
                    t = y / (SURF - 1)
                    r = _lerp(0xA8, 0x4A, t)
                    g = _lerp(0xD4, 0x7A, t)
                    b = _lerp(0xE8, 0x94, t)
                    al = ICE_ALPHA
                else:
                    td = (y - SURF) / (TH - SURF - 1) if TH > SURF + 1 else 0
                    r = _lerp(0x4A, 0x28, td)
                    g = _lerp(0x7A, 0x40, td)
                    b = _lerp(0x94, 0x54, td)
                    al = ICE_ALPHA
                    if y >= TH - 6:
                        fade_t = (y - (TH - 6)) / 5
                        al = _clamp(int(ICE_ALPHA - (ICE_ALPHA - 100) * fade_t))
                _put(rows, x, y, r, g, b, al)

        # highlight top 4px
        for y in range(4):
            for x in range(TW):
                if _corner_cut(x, y, left_cap, right_cap):
                    _put(rows, x, y, 0xE4, 0xF4, 0xFC, ICE_ALPHA)

        if left_cap:
            for y in range(CUT, TH - CUT):
                _put(rows, 0, y, 0x38, 0x60, 0x78, ICE_ALPHA)
                _put(rows, 1, y, 0x38, 0x60, 0x78, ICE_ALPHA)
        if right_cap:
            for y in range(CUT, TH - CUT):
                _put(rows, TW-1, y, 0x38, 0x60, 0x78, ICE_ALPHA)
                _put(rows, TW-2, y, 0x38, 0x60, 0x78, ICE_ALPHA)

        # gloss diagonal bands (2 bands, top-left to bottom-right)
        for band in range(2):
            band_offset = 8 + band * 20 + fi * 5
            for y in range(SURF):
                for x in range(TW):
                    if not _corner_cut(x, y, left_cap, right_cap):
                        continue
                    d = abs((x + y) - band_offset)
                    if d < 6:
                        _blend(rows, x, y, 0xD0, 0xEC, 0xF8, int(120 * (1 - d / 6)))

        # cracks (2-3 thin white lines, vary per frame)
        num_cracks = 2 + fi % 2
        for ci in range(num_cracks):
            cx2 = (_hash(fi, ci, 10) % (TW - 20)) + 10
            cy2 = (_hash(fi, ci, 11) % (SURF - 10)) + 3
            cdx = ((_hash(fi, ci, 12) % 11) - 5) / 5.0
            for step in range(10 + ci * 4):
                _blend(rows, int(cx2), int(cy2), 0xFF, 0xFF, 0xFF, 90)
                cx2 += cdx; cy2 += 1
                if cy2 >= SURF: break

        return rows

    # --- assemble all 20 frames ---
    # cap layout: (left_cap, right_cap) for indices 0-3 within each set
    CAP = [(True, False), (False, False), (False, True), (True, True)]

    all_rows = [[0] * (W * 4) for _ in range(TH)]

    def blit(frame_rows, fi):
        ox = fi * TW
        for y in range(TH):
            for x in range(TW):
                src = x * 4
                dst = (ox + x) * 4
                all_rows[y][dst:dst+4] = frame_rows[y][src:src+4]

    for i in range(4):
        blit(make_stone(i, *CAP[i]), i)
    for i in range(4):
        blit(make_wood(i, *CAP[i]), 4 + i)
    for i in range(4):
        blit(make_crumble(i), 8 + i)
    for i in range(4):
        blit(make_ice(i, *CAP[i]), 12 + i)
    # frames 16-19: fully transparent (already zeroed)

    write_png(path, W, TH, all_rows)


if __name__ == '__main__':
    os.makedirs('assets', exist_ok=True)
    make_shadow('assets/shadow.png')
    make_light('assets/light.png')
    make_shot('assets/shot.png')
    make_scenery_fore('assets/scenery_fore.png')
    make_tiles('assets/tiles.png')
    print('assets/shadow.png 160x80')
    print('assets/light.png 256x256')
    print('assets/shot.png 16x16')
    print('assets/scenery_fore.png 1920x1080')
    print('assets/tiles.png 1600x80')
