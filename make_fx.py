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
    from PIL import Image as _Img
    TW, TH, SURF = 80, 80, 40
    TOTAL_W = TW * 20
    SX, SY = 200, 520   # sample region in background_mine.png (320x40)

    def _h(x, y, s=0):
        return (((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) >> 3) & 0x7FFFFFFF
    def _c(v): return max(0, min(255, int(v)))
    def _lp(a, b, t): return int(a + (b - a) * t)

    src = _Img.open('assets/background_mine.png').convert('RGB')
    sp = src.load()

    rows = [[0] * (TOTAL_W * 4) for _ in range(TH)]

    def put(fi, x, y, r, g, b, a=255):
        if 0 <= x < TW and 0 <= y < TH:
            p = (fi * TW + x) * 4
            rows[y][p] = _c(r); rows[y][p+1] = _c(g)
            rows[y][p+2] = _c(b); rows[y][p+3] = _c(a)

    def getpx(fi, x, y):
        if 0 <= x < TW and 0 <= y < TH:
            p = (fi * TW + x) * 4
            return rows[y][p], rows[y][p+1], rows[y][p+2], rows[y][p+3]
        return 0, 0, 0, 0

    def apply_caps(fi, lc, rc, edge_w=6, max_dark=0.72):
        for ex in range(edge_w):
            dark = (edge_w - ex) / edge_w * max_dark
            if lc:
                for y in range(TH):
                    r, g, b, a = getpx(fi, ex, y)
                    put(fi, ex, y, r*(1-dark), g*(1-dark), b*(1-dark), a)
            if rc:
                x2 = TW - 1 - ex
                for y in range(TH):
                    r, g, b, a = getpx(fi, x2, y)
                    put(fi, x2, y, r*(1-dark), g*(1-dark), b*(1-dark), a)

    CAP = [(True, False), (False, False), (False, True), (True, True)]

    # ---- STONE (0-3): background crop ----
    for fi in range(4):
        xo = fi * 80
        lc, rc = CAP[fi]
        for y in range(SURF):
            for x in range(TW):
                r0, g0, b0 = sp[SX + xo + x, SY + y]
                if y < 2:
                    t = 0.75
                    r = _c(r0 + (255-r0)*t); g = _c(g0 + (255-g0)*t); b = _c(b0 + (255-b0)*t)
                elif y < 7:
                    r = _c(r0*1.5); g = _c(g0*1.5); b = _c(b0*1.5)
                elif y < 10:
                    r = _c(r0*0.45); g = _c(g0*0.45); b = _c(b0*0.45)
                else:
                    r = _c(r0*1.35); g = _c(g0*1.35); b = _c(b0*1.35)
                put(fi, x, y, r, g, b, 255)
        for y in range(SURF, TH):
            td = (y - SURF) / max(TH - SURF - 1, 1)
            bright = 0.40 - 0.20 * td
            al = 255
            if y >= TH - 8:
                ft = (y - (TH - 8)) / 7.0
                al = _c(255 - 105 * ft)
            for x in range(TW):
                r0, g0, b0 = sp[SX + xo + x, SY + (y - SURF)]
                put(fi, x, y, _c(r0*bright), _c(g0*bright), _c(b0*bright), al)
        apply_caps(fi, lc, rc)
        for x in range(TW):
            mh = _h(x + fi*80, 999) % 8
            for my in range(mh):
                r, g, b, a = getpx(fi, x, my)
                t = 110/255.0
                put(fi, x, my, _c(r*(1-t)+90*t), _c(g*(1-t)+112*t), _c(b*(1-t)+58*t), 255)

    # ---- WOOD (4-7) ----
    for fi_off in range(4):
        fi = 4 + fi_off
        lc, rc = CAP[fi_off]
        for y in range(TH):
            for x in range(TW):
                if y < SURF:
                    t = y / (SURF - 1)
                    put(fi, x, y, _lp(0x7A,0x3E,t), _lp(0x5A,0x2C,t), _lp(0x38,0x1C,t), 255)
                else:
                    td = (y - SURF) / max(TH - SURF - 1, 1)
                    bright = 0.40 - 0.20 * td
                    al = 255
                    if y >= TH - 8:
                        ft = (y - (TH - 8)) / 7.0
                        al = _c(255 - 105 * ft)
                    put(fi, x, y, _c(_lp(0x3E,0x20,td)*bright), _c(_lp(0x2C,0x16,td)*bright),
                        _c(_lp(0x1C,0x0E,td)*bright), al)
        for y in range(4):
            for x in range(TW):
                put(fi, x, y, 0x96, 0x74, 0x4A, 255)
        for y in range(SURF, min(SURF+2, TH)):
            for x in range(TW):
                r, g, b, a = getpx(fi, x, y)
                put(fi, x, y, _c(r*0.5), _c(g*0.5), _c(b*0.5), a)
        num_g = 5 + fi_off % 3
        for gi in range(num_g):
            gy = int(6 + gi*(SURF-6)/num_g + (fi_off*3 + gi*7)%4)
            gx0 = _h(fi_off, gi, 1) % (TW//3)
            gx_len = TW//2 + _h(fi_off, gi, 2) % (TW//3)
            thick = 1 + (gi + fi_off) % 2
            for t2 in range(thick):
                for gx in range(gx0, min(gx0+gx_len, TW)):
                    if 0 <= gy+t2 < SURF:
                        r, g, b, a = getpx(fi, gx, gy+t2)
                        put(fi, gx, gy+t2, _c(r*0.70), _c(g*0.70), _c(b*0.70), a)
        apply_caps(fi, lc, rc)

    # ---- CRUMBLE (8-11) ----
    def _crack(fi, x0, y0, dx, dy, length):
        cx2, cy2 = float(x0), float(y0)
        for _ in range(length):
            put(fi, int(cx2), int(cy2), 0x2A, 0x1C, 0x10, 255)
            cx2 += dx; cy2 += dy

    for stage in range(4):
        fi = 8 + stage
        fi_src = 5
        for y in range(TH):
            for x in range(TW):
                r, g, b, a = getpx(fi_src, x, y)
                put(fi, x, y, r, g, b, a)
        if stage >= 0: _crack(fi, 20, 2, 0.6, 1.2, 18)
        if stage >= 1:
            _crack(fi, 50, 3, -0.4, 1.0, 20)
            _crack(fi, 35, 8, 1.0, 0.3, 15)
        if stage >= 2:
            for y in range(TH):
                for x in range(TW):
                    if x < 12 and y > TH-20: put(fi, x, y, 0, 0, 0, 0)
                    if x > TW-13 and y > TH-15: put(fi, x, y, 0, 0, 0, 0)
                    if x < 8 and y < 12: put(fi, x, y, 0, 0, 0, 0)
        if stage >= 3:
            for y in range(TH):
                for x in range(TW):
                    if x > TW//2+10 and y > SURF-5: put(fi, x, y, 0, 0, 0, 0)
                    if x < 20 and y > SURF+10: put(fi, x, y, 0, 0, 0, 0)
                    if y > SURF+25: put(fi, x, y, 0, 0, 0, 0)

    # ---- ICE (12-15) ----
    for fi_off in range(4):
        fi = 12 + fi_off
        lc, rc = CAP[fi_off]
        ICE_A = 215
        for y in range(TH):
            for x in range(TW):
                if y < SURF:
                    t = y / (SURF - 1)
                    r = _c(_lp(0xA8,0x4A,t)); g = _c(_lp(0xD4,0x7A,t)); b = _c(_lp(0xE8,0x94,t))
                    put(fi, x, y, r, g, b, ICE_A)
                else:
                    td = (y-SURF) / max(TH-SURF-1, 1)
                    bright = 0.40 - 0.20*td
                    al = ICE_A
                    if y >= TH-8:
                        ft = (y-(TH-8)) / 7.0
                        al = _c(ICE_A - (ICE_A-100)*ft)
                    put(fi, x, y, _c(0x4A*bright*1.5), _c(0x7A*bright*1.5), _c(0x94*bright*1.5), al)
        for y in range(4):
            for x in range(TW):
                put(fi, x, y, 0xE4, 0xF4, 0xFC, ICE_A)
        for band in range(2):
            bo = 8 + band*20 + fi_off*5
            for y in range(SURF):
                for x in range(TW):
                    d = abs((x+y) - bo)
                    if d < 6:
                        r, g, b, a = getpx(fi, x, y)
                        t2 = int(120*(1-d/6)) / 255.0
                        put(fi, x, y, _c(r*(1-t2)+0xD0*t2), _c(g*(1-t2)+0xEC*t2), _c(b*(1-t2)+0xF8*t2), a)
        num_cracks = 2 + fi_off%2
        for ci in range(num_cracks):
            cx2 = float((_h(fi_off, ci, 10) % (TW-20)) + 10)
            cy2 = float((_h(fi_off, ci, 11) % (SURF-10)) + 3)
            cdx = ((_h(fi_off, ci, 12) % 11) - 5) / 5.0
            for _step in range(10 + ci*4):
                r, g, b, a = getpx(fi, int(cx2), int(cy2))
                t3 = 90/255.0
                put(fi, int(cx2), int(cy2), _c(r*(1-t3)+255*t3), _c(g*(1-t3)+255*t3), _c(b*(1-t3)+255*t3), a)
                cx2 += cdx; cy2 += 1
                if int(cy2) >= SURF: break
        apply_caps(fi, lc, rc)

    # frames 16-19: fully transparent (already zeroed)
    write_png(path, TOTAL_W, TH, rows)


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
