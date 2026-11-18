import ctypes
import pico2d

_OUTLINE_COLOR = (0x16, 0x11, 0x0D)
_OUTLINE_OFFSET = 2


def draw_text_outlined(font, cx, cy, text, color):
    w, h = ctypes.c_int(), ctypes.c_int()
    pico2d.TTF_SizeUTF8(font.font, text.encode('utf-8'), ctypes.byref(w), ctypes.byref(h))
    x = int(cx - w.value // 2)
    y = int(cy - h.value // 2)
    oc = _OUTLINE_COLOR
    o = _OUTLINE_OFFSET
    for dx, dy in ((-o, 0), (o, 0), (0, -o), (0, o)):
        font.draw(x + dx, y + dy, text, oc)
    font.draw(x, y, text, color)
