import pygame
import sys
def load():
    # path of player with different states
    PLAYER_PATH = (
            'assets/sprites/redbird-upflap.bmp',
            'assets/sprites/redbird-midflap.bmp',
            'assets/sprites/redbird-downflap.bmp'
    )

    # path of background
    BACKGROUND_PATH = 'assets/sprites/background-black.bmp'
    #BACKGROUND_PATH = 'assets/sprites/background-day.bmp'

    # path of pipe
    PIPE_PATH = 'assets/sprites/pipe-green.bmp'

    IMAGES, SOUNDS, HITMASKS = {}, {}, {}

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.bmp').convert(),
        pygame.image.load('assets/sprites/1.bmp').convert(),
        pygame.image.load('assets/sprites/2.bmp').convert(),
        pygame.image.load('assets/sprites/3.bmp').convert(),
        pygame.image.load('assets/sprites/4.bmp').convert(),
        pygame.image.load('assets/sprites/5.bmp').convert(),
        pygame.image.load('assets/sprites/6.bmp').convert(),
        pygame.image.load('assets/sprites/7.bmp').convert(),
        pygame.image.load('assets/sprites/8.bmp').convert(),
        pygame.image.load('assets/sprites/9.bmp').convert()
    )

    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.bmp').convert()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    # select random background sprites
    IMAGES['background'] = pygame.image.load(BACKGROUND_PATH).convert()

    # select random player sprites
    IMAGES['player'] = (
        pygame.image.load(PLAYER_PATH[0]).convert(),
        pygame.image.load(PLAYER_PATH[1]).convert(),
        pygame.image.load(PLAYER_PATH[2]).convert(),
    )

    # select random pipe sprites
    IMAGES['pipe'] = (
        pygame.transform.rotate(
            pygame.image.load(PIPE_PATH).convert(), 180),
        pygame.image.load(PIPE_PATH).convert(),
    )

    # hismask for pipes
    HITMASKS['pipe'] = (
        getHitmask(IMAGES['pipe'][0]),
        getHitmask(IMAGES['pipe'][1]),
    )

    # hitmask for player
    HITMASKS['player'] = (
        getHitmask(IMAGES['player'][0]),
        getHitmask(IMAGES['player'][1]),
        getHitmask(IMAGES['player'][2]),
    )

    return IMAGES, SOUNDS, HITMASKS

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask
