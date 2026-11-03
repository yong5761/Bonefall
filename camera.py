import random

ox = 0.0
oy = 0.0
_power = 0.0
_duration = 0.0
_elapsed = 0.0


def shake(power, duration):
    global _power, _duration, _elapsed
    _power = power
    _duration = duration
    _elapsed = 0.0


def update(frame_time):
    global ox, oy, _elapsed
    if _elapsed < _duration:
        _elapsed += frame_time
        ratio = max(0.0, 1.0 - _elapsed / _duration)
        strength = _power * ratio * ratio
        ox = random.uniform(-strength, strength)
        oy = random.uniform(-strength, strength)
    else:
        ox = 0.0
        oy = 0.0
