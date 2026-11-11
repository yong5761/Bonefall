from tile import Tile
from enemy import Enemy


def build_stage():
    tiles = []

    tiles.append(Tile(0, 1, 0))
    for col in range(1, 5):
        tiles.append(Tile(col, 1, 1))
    tiles.append(Tile(5, 1, 2))

    tiles.append(Tile(7, 1, 0))
    tiles.append(Tile(8, 1, 1))
    tiles.append(Tile(9, 1, 2))

    tiles.append(Tile(0, 2, 0))
    tiles.append(Tile(1, 2, 1))
    tiles.append(Tile(2, 2, 2))

    tiles.append(Tile(9, 2, 4))
    tiles.append(Tile(10, 2, 5))
    tiles.append(Tile(11, 2, 6))

    tiles.append(Tile(4, 4, 0))
    tiles.append(Tile(5, 4, 1))
    tiles.append(Tile(6, 4, 1))
    tiles.append(Tile(7, 4, 2))

    return tiles


def build_enemies():
    return [
        Enemy(720, 420),
        Enemy(1300, 420),
        Enemy(960, 900),
    ]
