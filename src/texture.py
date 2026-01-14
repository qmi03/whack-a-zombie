import pygame


class TextureManager:
    def __init__(self):
        self.background = None
        self.zombie_sprite = None

    def load(self):
        self.background = pygame.image.load(
            "assets/backdrop_with_holes.png"
        ).convert_alpha()
        self.zombie_sprite = pygame.image.load("assets/sprite.png").convert_alpha()
        self.zombie_sprite = pygame.transform.smoothscale(self.zombie_sprite, (80, 128))
