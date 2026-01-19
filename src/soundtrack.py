"""Sound and music management."""

import pygame


class SoundManager:
    """Manages game sound effects and background music."""

    def __init__(self):
        self.hit_sound = None
        self.miss_sound = None
        self.sounds_loaded = False

    def load(self):
        """Load all sound assets."""
        try:
            # Sound effects
            self.hit_sound = pygame.mixer.Sound("assets/hit.wav")
            self.miss_sound = pygame.mixer.Sound("assets/miss.wav")
            self.miss_sound.set_volume(0.4)

            # Background music
            pygame.mixer.music.load("assets/Plants vs Zombies Soundtrack/Loonboon.ogg")
            pygame.mixer.music.set_volume(0.4)

            self.sounds_loaded = True
            print("✓ Audio loaded successfully")

        except pygame.error as e:
            print(f"⚠ Audio files not found — running without audio: {e}")
            self.sounds_loaded = False

    def play_music(self):
        """Start background music loop."""
        if not self.sounds_loaded:
            return

        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)  # Loop indefinitely

    def play_hit(self):
        """Play zombie hit sound effect."""
        if self.sounds_loaded and self.hit_sound:
            self.hit_sound.play()

    def play_miss(self):
        """Play miss/timeout sound effect."""
        if self.sounds_loaded and self.miss_sound:
            self.miss_sound.play()

    def stop_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()

    def pause_music(self):
        """Pause background music."""
        pygame.mixer.music.pause()

    def resume_music(self):
        """Resume paused background music."""
        pygame.mixer.music.unpause()
