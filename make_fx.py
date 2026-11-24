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


def make_heavy_armor(path, w=100, h=100):
    rows = []
    cx = w * 0.5
    for y in range(h):
        row = []
        ny = y / h
        for x in range(w):
            nx_abs = abs(x - cx) / cx
            in_shoulder = ny < 0.38 and nx_abs > 0.14 and nx_abs < 0.9
            in_chest = ny >= 0.25 and ny < 0.65 and nx_abs < 0.27
            in_belt = ny >= 0.60 and ny < 0.73 and nx_abs < 0.34
            if in_shoulder or in_chest or in_belt:
                if ny < 0.08 and in_shoulder:
                    r, g, b, a = 128, 118, 105, 215
                elif nx_abs > 0.76 and in_shoulder:
                    r, g, b, a = 60, 54, 47, 200
                elif ny > 0.60 and in_chest:
                    r, g, b, a = 78, 71, 62, 220
                else:
                    r, g, b, a = 92, 84, 74, 220
                row += [r, g, b, a]
            else:
                row += [0, 0, 0, 0]
        rows.append(row)
    write_png(path, w, h, rows)


def make_turret_barrel(path, w=64, h=28):
    rows = []
    hh = h * 0.5
    for y in range(h):
        row = []
        for x in range(w):
            nx = x / w
            ny_abs = abs(y - hh) / hh
            half_norm = 0.88 - 0.28 * nx
            if ny_abs < half_norm:
                top = y < hh
                if ny_abs < 0.22 and top:
                    r, g, b = 112, 102, 90
                elif ny_abs < 0.55:
                    r, g, b = 86, 78, 68
                else:
                    r, g, b = 62, 56, 49
                if nx > 0.88:
                    r, g, b = 48, 44, 40
                row += [r, g, b, 255]
            else:
                row += [0, 0, 0, 0]
        rows.append(row)
    write_png(path, w, h, rows)


def make_turret_base(path, w=100, h=100):
    rows = []
    cx = w * 0.5
    for y in range(h):
        row = []
        ny = y / h
        for x in range(w):
            nx_abs = abs(x - cx) / cx
            in_dome = (ny >= 0.55 and ny < 0.72 and
                       (nx_abs / 0.52) ** 2 + ((ny - 0.55) / 0.17) ** 2 < 1.0)
            in_body = ny >= 0.68 and ny < 0.86 and nx_abs < 0.28
            in_base = ny >= 0.84 and ny < 0.96 and nx_abs < 0.44
            if in_dome or in_body or in_base:
                if ny < 0.65 and in_dome:
                    r, g, b, a = 118, 108, 95, 240
                elif nx_abs < 0.12 and ny < 0.72:
                    r, g, b, a = 108, 98, 86, 240
                elif nx_abs > 0.40 and in_base:
                    r, g, b, a = 62, 56, 49, 230
                else:
                    r, g, b, a = 90, 82, 71, 240
                row += [r, g, b, a]
            else:
                row += [0, 0, 0, 0]
        rows.append(row)
    write_png(path, w, h, rows)


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


if __name__ == '__main__':
    os.makedirs('assets', exist_ok=True)
    make_shadow('assets/shadow.png')
    make_light('assets/light.png')
    make_heavy_armor('assets/heavy_armor.png')
    make_turret_barrel('assets/turret_barrel.png')
    make_turret_base('assets/enemy_turret_base.png')
    make_shot('assets/shot.png')
    print('assets/shadow.png 160x80')
    print('assets/light.png 256x256')
    print('assets/heavy_armor.png 100x100')
    print('assets/turret_barrel.png 64x28')
    print('assets/enemy_turret_base.png 100x100')
    print('assets/shot.png 16x16')
