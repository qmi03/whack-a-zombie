import pygame


class SoundManager:
    def __init__(self):
        self.hit = None
        self.pop = None
        self.miss = None

    def load(self):
        try:
            self.hit = pygame.mixer.Sound("assets/hit.wav")

            pygame.mixer.music.load("assets/Plants vs Zombies Soundtrack/Loonboon.ogg")
            pygame.mixer.music.set_volume(0.4)
        except pygame.error:
            print("Sounds not found — running without audio")

    def play_music(self):
        if pygame.mixer.music.get_busy() is False:
            pygame.mixer.music.play(-1)
