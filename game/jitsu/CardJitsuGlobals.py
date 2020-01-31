from panda3d.core import Vec4

CARD_MODEL = 'phase_13/models/props/jitsucard'
TRACK_FIRE = 3
TRACK_WATER = 4
TRACK_ICE = 5


if process == 'client':
    FONT = loader.loadFont('fonts/ImpressBT.ttf', lineHeight=1.0)

TRACK_COLORS = {
    # 0: Vec4(0.559, 0.59, 0.875, 1.0),
    # 1: Vec4(0.996, 0.898, 0.32, 1.0),
    2: Vec4(0.305, 0.969, 0.402, 1.0),
    3: Vec4(0.559, 0.59, 0.875, 1.0),
    4: Vec4(0.992, 0.48, 0.168, 1.0),
    5: Vec4(1.0, 0.6, 1.0, 1.0),
    6: Vec4(0.996, 0.898, 0.32, 1.0),
}

ICON_SCALE = {
    TRACK_FIRE: 2,
    TRACK_WATER: 12,
    TRACK_ICE: 0.5,
}

WON_CARD_POSITIONS = {
    TRACK_FIRE: {
        1: (-0.95, 0, 0.25),
        2: (-0.85, 0, 0.25),
        3: (-0.75, 0, 0.25),
        4: (-0.65, 0, 0.25),
        5: (-0.55, 0, 0.25),

        6: (0.55, 0, 0.25),
        7: (0.65, 0, 0.25),
        8: (0.75, 0, 0.25),
        9: (0.85, 0, 0.25),
        10: (0.95, 0, 0.25)
    },
    TRACK_WATER: {
        1: (-0.95, 0, 0),
        2: (-0.85, 0, 0),
        3: (-0.75, 0, 0),
        4: (-0.65, 0, 0),
        5: (-0.55, 0, 0),

        6: (0.55, 0, 0),
        7: (0.65, 0, 0),
        8: (0.75, 0, 0),
        9: (0.85, 0, 0),
        10: (0.95, 0, 0)
    },
    TRACK_ICE: {
        1: (-0.95, 0, -0.25),
        2: (-0.85, 0, -0.25),
        3: (-0.75, 0, -0.25),
        4: (-0.65, 0, -0.25),
        5: (-0.55, 0, -0.25),

        6: (0.55, 0, -0.25),
        7: (0.65, 0, -0.25),
        8: (0.75, 0, -0.25),
        9: (0.85, 0, -0.25),
        10: (0.95, 0, -0.25)
    }
}

CARD_POSITIONS = {
    0: (-0.7, 0, -.77),
    1: (-0.4, 0, -.77),
    2: (-0.1, 0, -.77),
    3: (0.2, 0, -.77),
    4: (0.5, 0, -.77),
    # these are all the positions for the non-local player
    5: (-0.7, 0, .77),
    6: (-0.47, 0, .77),
    7: (-0.24, 0, .77),
    8: (-0.01, 0, .77),
    9: (0.22, 0, .77),
}

NONE = 0
WHITE = 1
YELLOW = 2
ORANGE = 3
GREEN = 4
BLUE = 5
RED = 6
PURPLE = 7
BROWN = 8
BLACK = 9

RANK_COLORS = {
    WHITE: Vec4(1, 1, 1, 1),
    YELLOW: Vec4(1, 1, 0, 1),
    ORANGE: Vec4(1, 0.6, 0, 1),
    RED: Vec4(1, 0, 0, 1),
    GREEN: Vec4(0.5, 0.8, 0, 1),
    BLUE: Vec4(0, 0, 1, 1),
    PURPLE: Vec4(0.5, 0, 1, 1),
    BROWN: Vec4(0.5, 0.3, 0.2, 1),
    BLACK: Vec4(0, 0, 0, 1)
}


# win requirements:
# white belt = 5
# yellow = 13
# orange = 21
# green = 30
# blue = 40
# red = 52
# purple = 64
# brown = 76
# black = 88


def getBeltLevel(winCount):
    level = NONE
    if 5 <= winCount < 13:
        level = WHITE
    elif 13 <= winCount < 21:
        level = YELLOW
    elif 21 <= winCount < 30:
        level = ORANGE
    elif 30 <= winCount < 40:
        level = GREEN
    elif 40 <= winCount < 52:
        level = BLUE
    elif 52 <= winCount < 64:
        level = RED
    elif 64 <= winCount < 76:
        level = PURPLE
    elif 76 <= winCount < 88:
        level = BROWN
    elif winCount >= 88:
        level = BLACK
    return level


IMAGE_NODES = {
    TRACK_WATER: '**/*inventory_geyser*',
    TRACK_FIRE: '**/*fire*',
    TRACK_ICE: '**/g1*'
}


ALL_DECK = [
    (TRACK_FIRE, 2), (TRACK_FIRE, 3), (TRACK_FIRE, 4), (TRACK_FIRE, 5), (TRACK_FIRE, 6),
    (TRACK_WATER, 2), (TRACK_WATER, 3), (TRACK_WATER, 4), (TRACK_WATER, 5), (TRACK_WATER, 6),
    (TRACK_ICE, 2), (TRACK_ICE, 3), (TRACK_ICE, 4), (TRACK_ICE, 5), (TRACK_ICE, 6)
]

NUM_PLAYERS = 2
NUM_CARDS = 5
SELECTION_TIMEOUT = 15
UNREVEALED_HPR = (0, 0, 90)
REVEALED_HPR = (0, 0, 90)
LOCAL_CARD_DEST = (-0.25, 0, 0)
OTHER_CARD_DEST = (0.25, 0, 0)
PLAYER_QUIT = 0
PLAYER_LOST = 1
PLAYER_WON = 2
