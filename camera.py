import math
import random

ox = 0.0
oy = 0.0
_power = 0.0
_duration = 0.0
_elapsed = 0.0
_dx = 0.0
_dy = 0.0
_hitstop_elapsed = 0.0
_hitstop_duration = 0.0


def shake(power, duration, dx, dy):
    global _power, _duration, _elapsed, _dx, _dy
    dist = (dx * dx + dy * dy) ** 0.5
    if dist < 1e-6:
        _dx, _dy = 0.0, 1.0
    else:
        _dx, _dy = dx / dist, dy / dist
    _power = power
    _duration = duration
    _elapsed = 0.0


def hitstop(duration):
    global _hitstop_elapsed, _hitstop_duration
    if _hitstop_elapsed < _hitstop_duration:
        return
    _hitstop_duration = duration
    _hitstop_elapsed = 0.0


def is_hitstop():
    return _hitstop_elapsed < _hitstop_duration


def update(frame_time):
    global ox, oy, _elapsed, _hitstop_elapsed
    if _hitstop_elapsed < _hitstop_duration:
        _hitstop_elapsed += frame_time
    if _elapsed < _duration:
        _elapsed += frame_time
        t = _elapsed
        decay = (1.0 - t / _duration) ** 2
        osc = math.cos(2.0 * math.pi * 18.0 * t)
        noise_x = random.uniform(-_power * 0.2, _power * 0.2) * decay
        noise_y = random.uniform(-_power * 0.2, _power * 0.2) * decay
        ox = _dx * _power * decay * osc + noise_x
        oy = _dy * _power * decay * osc + noise_y
    else:
        ox = 0.0
        oy = 0.0
