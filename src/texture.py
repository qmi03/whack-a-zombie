"""Texture and sprite management."""

import pygame


class TextureManager:
    """Manages game textures and sprites."""

    # Sprite dimensions
    ZOMBIE_WIDTH = 80
    ZOMBIE_HEIGHT = 128
    ZOMBIE_SQUASHED_HEIGHT = 20

    def __init__(self):
        self.background = None
        self.zombie_sprite = None
        self.zombie_sprite_squashed = None

    def load(self):
        """Load all texture assets."""
        try:
            # Background
            self.background = pygame.image.load(
                "assets/backdrop_with_holes.png"
            ).convert_alpha()

            # Zombie sprite
            raw_sprite = pygame.image.load("assets/sprite.png").convert_alpha()

            # Normal zombie (standing)
            self.zombie_sprite = pygame.transform.smoothscale(
                raw_sprite, (self.ZOMBIE_WIDTH, self.ZOMBIE_HEIGHT)
            )

            # Squashed zombie (hit)
            self.zombie_sprite_squashed = pygame.transform.smoothscale(
                raw_sprite, (self.ZOMBIE_WIDTH, self.ZOMBIE_SQUASHED_HEIGHT)
            )

            print("✓ Textures loaded successfully")

        except pygame.error as e:
            print(f"✗ Error loading textures: {e}")
            raise

    def get_zombie_dimensions(self):
        """Get zombie sprite dimensions as (width, height) tuple."""
        return (self.ZOMBIE_WIDTH, self.ZOMBIE_HEIGHT)
