import pico2d

_cache = {}
_VOLUME = {
    'jump': 40,
    'land': 48,
    'throw': 40,
    'explosion_push': 80,
    'explosion_pull': 80,
    'bone_collapse': 56,
    'stage_clear': 72,
    'ui_move': 40,
    'ui_select': 56,
}


def play(name):
    wav = _cache.get(name)
    if wav is None:
        wav = pico2d.load_wav('assets/sfx/' + name + '.wav')
        wav.set_volume(_VOLUME.get(name, 56))
        _cache[name] = wav
    wav.play()


def clear():
    _cache.clear()
