import pygame


class TextureManager:
    def __init__(self):
        self.background = None

    def load(self):
        self.background = pygame.image.load(
            "assets/backdrop_with_holes.png"
        ).convert_alpha()
