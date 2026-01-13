import random

import pygame

import src.const as const
import src.game as game
import src.soundtrack as soundtrack
import src.texture as texture

# ==================== INIT ====================
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
pygame.display.set_caption("Whack-a-Zombie - Custom Background")


textures = texture.TextureManager()
textures.load()

soundtracks = soundtrack.SoundManager()
soundtracks.load()

# Colors (fallback + zombie/UI)


game = game.Game(screen, textures, soundtracks)
game.run()
