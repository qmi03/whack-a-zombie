import random

import pygame

import src.const as const
import src.soundtrack as soundtrack
import src.texture as texture

# ==================== INIT ====================
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Whack-a-Zombie - Custom Background")


textures = texture.TextureManager()
textures.load()

soundtracks = soundtrack.SoundManager()
soundtracks.load()

# Colors (fallback + zombie/UI)
BG_COLOR = (12, 20, 28)
ZOMBIE_COLOR = (95, 175, 85)
HIT_COLOR = (220, 50, 50)
WHITE = (240, 245, 255)
RED = (255, 50, 50)


class Game:
    def __init__(self, screen, textures, soundtracks):
        self.screen = screen
        self.textures = textures
        self.soundtracks = soundtracks
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("assets/pixel_square/Pixel Square Bold10.ttf", 64)
        self.small_font = pygame.font.Font(
            "assets/pixel_square/Pixel Square 10.ttf", 36
        )
        self.reset()

    def reset(self):
        self.score = 0
        self.lives = 5
        self.combo = 0
        self.max_combo = 0
        self.level = 1
        self.game_over = False
        self.state = "PLAY"
        self.show_debug = False
        self.holes = [False] * 20
        self.zombie_up_time = [0] * 20
        self.hit = [False] * 20
        self.last_spawn_attempt = pygame.time.get_ticks()

    def spawn_zombie(self):
        available = [i for i, up in enumerate(self.holes) if not up]
        if not available:
            return False
        idx = random.choice(available)
        self.holes[idx] = True
        self.zombie_up_time[idx] = pygame.time.get_ticks()
        self.hit[idx] = False
        if self.soundtracks.pop:
            self.soundtracks.pop.play()
        return True

    # ==================== HELPERS ====================
    def get_current_difficulty(self):
        spawn_int = max(350, const.SPAWN_INTERVAL_BASE - (self.level * 65))
        show_dur = max(500, const.SHOW_DURATION_BASE - (self.level * 55))
        spawn_chance = min(0.92, 0.60 + self.level * 0.06)
        return spawn_int, show_dur, spawn_chance

    def get_hole_rect(self, pos):
        x, y = pos
        # Tuned for ~180px horizontal / 200px vertical spacing - covers full hole area
        return pygame.Rect(x - 75, y - 65, 150, 130)

    def draw_zombie(self, x, y, hit_state):
        """Draw zombie head - positioned to emerge from hole center"""
        color = HIT_COLOR if hit_state else ZOMBIE_COLOR
        # Head (slightly above center for "popping" effect)
        pygame.draw.circle(screen, color, (x, y - 25), 60)
        # Eyes (glowing white with black pupils)
        pygame.draw.circle(screen, WHITE, (x - 22, y - 40), 16)
        pygame.draw.circle(screen, WHITE, (x + 22, y - 40), 16)
        pygame.draw.circle(screen, (0, 0, 0), (x - 22, y - 40), 9)
        pygame.draw.circle(screen, (0, 0, 0), (x + 22, y - 40), 9)
        # Grinning mouth
        pygame.draw.arc(screen, (0, 0, 0), (x - 40, y - 18, 80, 48), 3.14, 0, 8)

    def draw_debug_cross(self, x, y):
        """Red crosses + circle for alignment testing"""
        pygame.draw.line(screen, RED, (x - 40, y - 40), (x + 40, y + 40), 6)
        pygame.draw.line(screen, RED, (x - 40, y + 40), (x + 40, y - 40), 6)
        pygame.draw.circle(screen, RED, (x, y), 12, 4)

    def run(self):
        running = True
        self.state = "PLAY"
        self.soundtracks.play_music()

        while running:
            self.clock.tick(60)
            current_time = pygame.time.get_ticks()

            # ─── EVENTS ───────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and (
                        self.game_over or self.state == "MENU"
                    ):
                        self.reset()
                        self.state = "PLAY"
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.play(-1)
                    if event.key == pygame.K_d:  # Toggle debug mode
                        self.show_debug = not self.show_debug
                        print(f"Debug crosses: {'ON' if self.show_debug else 'OFF'}")

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and self.state == "PLAY"
                    and not self.game_over
                ):
                    if event.button == 1:  # Left click
                        pos = event.pos
                        hit_any = False
                        for i, center in enumerate(const.GRID):
                            if (
                                self.get_hole_rect(center).collidepoint(pos)
                                and self.holes[i]
                                and not self.hit[i]
                            ):
                                self.hit[i] = True
                                self.score += 10 + (
                                    self.combo // 3
                                )  # Better scoring for chaos
                                self.combo += 1
                                self.max_combo = max(self.max_combo, self.combo)
                                if self.soundtracks.hit:
                                    self.soundtracks.hit.play()
                                hit_any = True
                        if not hit_any and self.combo > 0:
                            self.combo = 0
                            if self.soundtracks.miss:
                                self.soundtracks.miss.play()

            # ─── UPDATE ───────────────────────────────────────
            if self.state == "PLAY" and not self.game_over:
                spawn_interval, show_duration, spawn_chance = (
                    self.get_current_difficulty()
                )

                # Level up every 40 points (adjusted for higher scores)
                if self.score >= self.level * 40:
                    self.level += 1

                # Spawn attempts
                if current_time - self.last_spawn_attempt > spawn_interval:
                    self.last_spawn_attempt = current_time
                    if random.random() < spawn_chance:
                        self.spawn_zombie()

                # Check timeouts & auto-hide
                for i in range(20):
                    if self.holes[i]:
                        elapsed = current_time - self.zombie_up_time[i]
                        if not self.hit[i] and elapsed > show_duration:
                            # Missed!
                            self.holes[i] = False
                            self.lives -= 1
                            self.combo = 0
                            if self.soundtracks.miss:
                                self.soundtracks.miss.play()
                            if self.lives <= 0:
                                self.game_over = True
                                self.state = "GAMEOVER"
                        elif self.hit[i] and elapsed > 400:  # Quick squash animation
                            self.holes[i] = False
                            self.hit[i] = False

            # ─── DRAW ─────────────────────────────────────────
            # Background first
            screen.blit(self.textures.background, (0, 0))

            # Draw zombies OVER the background holes
            for i, (x, y) in enumerate(const.GRID):
                if self.holes[i]:
                    self.draw_zombie(x, y, self.hit[i])

            # Debug crosses (if enabled - press D)
            if self.show_debug:
                for x, y in const.GRID:
                    self.draw_debug_cross(x, y)

            # UI
            score_text = self.font.render(f"{self.score}", True, WHITE)
            lives_text = self.font.render(
                f"LIVES: {self.lives}",
                True,
                (255, 70, 70) if self.lives <= 2 else (160, 220, 255),
            )
            combo_text = (
                self.small_font.render(f"COMBO x{self.combo}", True, (255, 220, 80))
                if self.combo >= 3
                else None
            )
            level_text = self.small_font.render(
                f"LEVEL {self.level}", True, (180, 255, 180)
            )

            screen.blit(score_text, (40, 20))
            screen.blit(lives_text, (WIDTH - lives_text.get_width() - 40, 20))
            if combo_text:
                screen.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 80))
            screen.blit(level_text, (40, 120))

            # Debug info
            if self.show_debug:
                debug_text = self.small_font.render(
                    "DEBUG ON (Press D to toggle)", True, RED
                )
                screen.blit(debug_text, (40, HEIGHT - 60))

            # Game Over
            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                go_text = self.font.render("GAME OVER", True, (255, 60, 60))
                final_text = self.small_font.render(
                    f"Final Score: {self.score} | Best Combo: {self.max_combo}",
                    True,
                    (220, 220, 240),
                )
                restart_text = self.small_font.render(
                    "Press R to play again", True, (160, 240, 160)
                )

                screen.blit(
                    go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 100)
                )
                screen.blit(
                    final_text, (WIDTH // 2 - final_text.get_width() // 2, HEIGHT // 2)
                )
                screen.blit(
                    restart_text,
                    (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80),
                )

            pygame.display.flip()
        pygame.quit()


game = Game(screen, textures, soundtracks)
game.run()
