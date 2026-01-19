"""
Whack-a-Zombie Game

A fast-paced arcade game where players must click on zombies before they escape.
Features combo scoring, increasing difficulty, and retro-style graphics.
"""

import pygame

import src.const as const
from src.game import Game
from src.soundtrack import SoundManager
from src.texture import TextureManager


def initialize_pygame():
    """Initialize pygame and mixer."""
    pygame.init()
    pygame.mixer.init()


def create_display():
    """Create and configure the game window."""
    screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
    pygame.display.set_caption("Whack-a-Zombie")
    return screen


def load_assets():
    """Load all game assets (textures and sounds)."""
    print("Loading game assets...")

    textures = TextureManager()
    textures.load()

    sounds = SoundManager()
    sounds.load()

    print("Assets loaded. Starting game...")
    return textures, sounds


def main():
    """Main entry point for the game."""
    initialize_pygame()
    screen = create_display()
    textures, sounds = load_assets()

    game = Game(screen, textures, sounds)
    game.run()


if __name__ == "__main__":
    main()
