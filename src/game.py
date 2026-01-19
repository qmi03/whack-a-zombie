import random

import pygame

from . import const


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
        self.state = "MENU"
        self.show_hitboxes = False
        self.zombie_w = self.textures.zombie_sprite.get_width()  # 80
        self.zombie_h = self.textures.zombie_sprite.get_height()  # 128
        self.half_w = self.zombie_w // 2  # 40

    def run(self):
        self.running = True
        self.soundtracks.play_music()

        while self.running:
            self.clock.tick(60)
            current_time = pygame.time.get_ticks()

            self.event_handler()
            self.update(current_time)
            self.draw()
        pygame.quit()

    def reset(self):
        self.score = 0
        self.lives = 5
        self.combo = 0
        self.max_combo = 0
        self.level = 1
        self.game_over = False
        self.state = "PLAY"
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
        return True

    # ==================== HELPERS ====================
    def get_current_difficulty(self):
        spawn_int = max(500, const.SPAWN_INTERVAL_BASE - (self.level * 65))
        show_dur = max(1500, const.SHOW_DURATION_BASE - (self.level * 55))
        spawn_chance = min(0.92, 0.60 + self.level * 0.06)
        return spawn_int, show_dur, spawn_chance

    def get_hole_rect(self, pos):
        x, y = pos
        return pygame.Rect(
            x - self.half_w - 10, y - self.zombie_h, self.zombie_w + 10, self.zombie_h
        )

    def draw_zombie(self, x, y, is_hit):
        if not is_hit:
            self.screen.blit(self.textures.zombie_sprite, (x - 50, y - 128))
        else:
            self.screen.blit(self.textures.zombie_sprite_squashed, (x - 50, y - 20))

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == "MENU":
                        self.reset()
                    elif self.state == "PLAY":
                        self.state = "PAUSE"
                    elif self.state == "PAUSE":
                        self.state = "PLAY"
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.play(-1)
                if event.key == pygame.K_h:  # Press H to toggle hitboxes
                    self.show_hitboxes = not self.show_hitboxes
                    print(f"Hitboxes: {'ON' if self.show_hitboxes else 'OFF'}")
                if event.key == pygame.K_q:  # Press Q to quit
                    self.running = False

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and self.state == "PLAY"
                and not self.game_over
            ):
                if event.button == 1:  # Left click
                    mouse_pos = event.pos
                    hit_any = False
                    for i, center in enumerate(const.GRID):
                        if (
                            self.get_hole_rect(center).collidepoint(mouse_pos)
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

    def update(self, current_time):
        if self.state == "PLAY" and not self.game_over:
            spawn_interval, show_duration, spawn_chance = self.get_current_difficulty()

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
                    elif self.hit[i] and elapsed > 1000:  # Quick squash animation
                        self.holes[i] = False
                        self.hit[i] = False

    def draw(self):
        # Background
        self.screen.blit(self.textures.background, (0, 0))

        if self.state == "PLAY":
            # Zombies
            for i, (x, y) in enumerate(const.GRID):
                if self.holes[i]:
                    self.draw_zombie(x, y, self.hit[i])

            # Hitbox
            if self.show_hitboxes:
                for i, center in enumerate(const.GRID):
                    rect = self.get_hole_rect(center)
                    # Draw all hitboxes in red (always visible when toggled)
                    pygame.draw.rect(self.screen, const.RED, rect, 3)

                    pygame.draw.circle(self.screen, (255, 255, 255), rect.center, 5)
            # UI
            score_text = self.font.render(f"{self.score}", True, const.WHITE)
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

            self.screen.blit(score_text, (40, 20))
            self.screen.blit(
                lives_text, (const.WIDTH - lives_text.get_width() - 40, 20)
            )
            if combo_text:
                self.screen.blit(
                    combo_text, (const.WIDTH // 2 - combo_text.get_width() // 2, 80)
                )
            self.screen.blit(level_text, (40, 120))

        overlay = pygame.Surface((const.WIDTH, const.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        if self.state == "MENU":
            self.screen.blit(overlay, (0, 0))
            title_text = self.font.render("WHACK-A-ZOMBIE", True, const.WHITE)
            start_text = self.small_font.render(
                "Press SPACEBAR to START", True, (160, 240, 160)
            )
            instruct_text = self.small_font.render(
                "Whack zombies before they escape! (H for hitboxes)",
                True,
                (220, 220, 240),
            )

            # Centered positions
            title_rect = title_text.get_rect(
                center=(const.WIDTH // 2, const.HEIGHT // 2 - 80)
            )
            start_rect = start_text.get_rect(
                center=(const.WIDTH // 2, const.HEIGHT // 2 + 20)
            )
            instruct_rect = instruct_text.get_rect(
                center=(const.WIDTH // 2, const.HEIGHT // 2 + 80)
            )

            self.screen.blit(title_text, title_rect)
            self.screen.blit(start_text, start_rect)
            self.screen.blit(instruct_text, instruct_rect)
        elif self.state == "PAUSE":
            self.screen.blit(overlay, (0, 0))
            paused_text = self.font.render("PAUSED", True, (255, 220, 80))
            resume_text = self.small_font.render(
                "SPACE to resume (Q quit)", True, (160, 240, 160)
            )
            paused_rect = paused_text.get_rect(
                center=(const.WIDTH // 2, const.HEIGHT // 2 - 40)
            )
            resume_rect = resume_text.get_rect(
                center=(const.WIDTH // 2, const.HEIGHT // 2 + 40)
            )
            self.screen.blit(paused_text, paused_rect)
            self.screen.blit(resume_text, resume_rect)

        # Game Over
        if self.game_over:
            self.screen.blit(overlay, (0, 0))

            go_text = self.font.render("GAME OVER", True, (255, 60, 60))
            final_text = self.small_font.render(
                f"Final Score: {self.score} | Best Combo: {self.max_combo}",
                True,
                (220, 220, 240),
            )
            restart_text = self.small_font.render(
                "Press R to play again", True, (160, 240, 160)
            )

            self.screen.blit(
                go_text,
                (
                    const.WIDTH // 2 - go_text.get_width() // 2,
                    const.HEIGHT // 2 - 100,
                ),
            )
            self.screen.blit(
                final_text,
                (const.WIDTH // 2 - final_text.get_width() // 2, const.HEIGHT // 2),
            )
            self.screen.blit(
                restart_text,
                (
                    const.WIDTH // 2 - restart_text.get_width() // 2,
                    const.HEIGHT // 2 + 80,
                ),
            )

        pygame.display.flip()
