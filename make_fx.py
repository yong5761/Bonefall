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


if __name__ == '__main__':
    os.makedirs('assets', exist_ok=True)
    make_shadow('assets/shadow.png')
    make_light('assets/light.png')
    make_shot('assets/shot.png')
    print('assets/shadow.png 160x80')
    print('assets/light.png 256x256')
    print('assets/shot.png 16x16')
