import pygame

background = None


def load_textures():
    global background
    background = pygame.image.load("assets/backdrop_with_holes.png").convert_alpha()
