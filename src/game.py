"""Main game logic and state management."""

import random

import pygame

from . import const
from .zombie import ZombieManager


class GameState:
    """Manages game state and statistics."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset game to initial state."""
        self.score = 0
        self.lives = const.STARTING_LIVES
        self.combo = 0
        self.max_combo = 0
        self.level = 1
        self.is_game_over = False
        self.hit_count = 0
        self.miss_count = 0

    def add_score(self, points):
        """Add points to score and check for level up."""
        self.score += points
        # Level up every POINTS_PER_LEVEL points
        new_level = (self.score // const.POINTS_PER_LEVEL) + 1
        if new_level > self.level:
            self.level = new_level

    def increment_combo(self):
        """Increase combo counter."""
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)

    def break_combo(self):
        """Reset combo to zero."""
        self.combo = 0

    def lose_life(self):
        """Decrease lives and check for game over."""
        self.lives -= 1
        if self.lives <= 0:
            self.is_game_over = True

    def get_combo_bonus(self):
        """Calculate bonus points from current combo."""
        return self.combo // const.COMBO_BONUS_DIVISOR

    def register_hit(self):
        """Increment hit counter"""
        self.hit_count += 1

    def register_miss(self):
        """Increment miss counter"""
        self.miss_count += 1

    def get_hit_ratio(self):
        """Calculate hit ratio"""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total * 100.0


class DifficultyManager:
    """Calculates difficulty parameters based on current level."""

    @staticmethod
    def get_spawn_interval(level):
        """Get time between spawn attempts (decreases with level)."""
        interval = const.SPAWN_INTERVAL_BASE - (
            level * const.SPAWN_INTERVAL_DECREASE_PER_LEVEL
        )
        return max(const.MIN_SPAWN_INTERVAL, interval)

    @staticmethod
    def get_show_duration(level):
        """Get how long zombies stay visible (decreases with level)."""
        duration = const.SHOW_DURATION_BASE - (
            level * const.SHOW_DURATION_DECREASE_PER_LEVEL
        )
        return max(const.MIN_SHOW_DURATION, duration)

    @staticmethod
    def get_spawn_chance(level):
        """Get probability of spawn attempt succeeding (increases with level)."""
        chance = const.BASE_SPAWN_CHANCE + (level * const.SPAWN_CHANCE_INCREASE)
        return min(const.MAX_SPAWN_CHANCE, chance)

    @classmethod
    def get_difficulty(cls, level):
        """Get all difficulty parameters for the current level."""
        return {
            "spawn_interval": cls.get_spawn_interval(level),
            "show_duration": cls.get_show_duration(level),
            "spawn_chance": cls.get_spawn_chance(level),
        }


class Game:
    """Main game controller."""

    # Game states
    STATE_MENU = "MENU"
    STATE_PLAY = "PLAY"
    STATE_PAUSE = "PAUSE"
    STATE_GAMEOVER = "GAMEOVER"

    def __init__(self, screen, textures, soundtracks):
        self.screen = screen
        self.textures = textures
        self.soundtracks = soundtracks

        # Timing
        self.clock = pygame.time.Clock()
        self.last_spawn_attempt = 0
        self.total_pause_time = 0
        self.pause_start_time = 0

        # Fonts
        self.font_large = pygame.font.Font(
            "assets/pixel_square/Pixel Square Bold10.ttf", 64
        )
        self.font_small = pygame.font.Font(
            "assets/pixel_square/Pixel Square 10.ttf", 36
        )

        # Game state
        self.state = self.STATE_MENU
        self.game_state = GameState()
        self.zombie_manager = ZombieManager(len(const.GRID_POSITIONS))

        # Debug
        self.show_hitboxes = False

        # Cache sprite dimensions
        self.zombie_width = self.textures.zombie_sprite.get_width()
        self.zombie_height = self.textures.zombie_sprite.get_height()
        self.zombie_half_width = self.zombie_width // 2

    def run(self):
        """Main game loop."""
        self.running = True
        self.soundtracks.play_music()

        while self.running:
            self.clock.tick(60)

            self._handle_events()
            self._update()
            self._render()

        pygame.quit()

    def reset_game(self):
        """Reset game for new playthrough."""
        self.game_state.reset()
        self.zombie_manager.reset()
        self.state = self.STATE_PLAY
        self.total_pause_time = 0
        self.last_spawn_attempt = self._get_game_time()

    # ==================== EVENT HANDLING ====================

    def _handle_events(self):
        """Process all input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keypress(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event)

    def _handle_keypress(self, key):
        """Handle keyboard input."""
        if key == pygame.K_SPACE:
            self._handle_space_key()
        elif key == pygame.K_r and self.game_state.is_game_over:
            self._restart_game()
        elif key == pygame.K_h:
            self._toggle_hitboxes()
        elif key == pygame.K_q:
            self.running = False

    def _handle_space_key(self):
        """Handle spacebar press (menu start, pause toggle)."""
        if self.state == self.STATE_MENU:
            self.reset_game()
        elif self.state == self.STATE_PLAY:
            self.state = self.STATE_PAUSE
            self.pause_start_time = pygame.time.get_ticks()
        elif self.state == self.STATE_PAUSE:
            self.state = self.STATE_PLAY
            pause_duration = pygame.time.get_ticks() - self.pause_start_time
            self.total_pause_time += pause_duration

    def _get_game_time(self):
        return pygame.time.get_ticks() - self.total_pause_time

    def _restart_game(self):
        """Restart game after game over."""
        self.reset_game()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

    def _toggle_hitboxes(self):
        """Toggle hitbox visualization."""
        self.show_hitboxes = not self.show_hitboxes
        print(f"Hitboxes: {'ON' if self.show_hitboxes else 'OFF'}")

    def _handle_click(self, event):
        """Handle mouse click events."""
        if event.button != 1:  # Only left click
            return

        if self.state != self.STATE_PLAY or self.game_state.is_game_over:
            return

        mouse_pos = event.pos
        hit_registered = False

        # Check if click hit any zombie
        for i, grid_pos in enumerate(const.GRID_POSITIONS):
            if not self.zombie_manager.is_hole_occupied(i):
                continue

            zombie = self.zombie_manager.get_zombie(i)
            if zombie.is_hit:
                continue

            hitbox = self._get_hitbox(grid_pos)
            if hitbox.collidepoint(mouse_pos):
                self._register_hit(i)
                hit_registered = True
                break

        # Miss penalty
        if not hit_registered and self.game_state.combo > 0:
            self.game_state.break_combo()
            self.game_state.register_miss()
            self.soundtracks.play_miss()

    def _register_hit(self, hole_index):
        """Register successful zombie hit."""
        self.zombie_manager.hit_zombie(hole_index)

        # Score with combo bonus
        points = const.POINTS_PER_HIT + self.game_state.get_combo_bonus()
        self.game_state.add_score(points)
        self.game_state.increment_combo()
        self.game_state.register_hit()

        self.soundtracks.play_hit()

    # ==================== UPDATE ====================

    def _update(self):
        """Update game state."""
        if self.state != self.STATE_PLAY or self.game_state.is_game_over:
            return

        difficulty = DifficultyManager.get_difficulty(self.game_state.level)

        # Attempt to spawn zombies
        current_time = self._get_game_time()
        self._attempt_spawn(current_time, difficulty)

        # Update existing zombies
        timeouts = self.zombie_manager.update(current_time, difficulty["show_duration"])

        # Handle timeouts (zombies that escaped)
        if timeouts > 0:
            for _ in range(timeouts):
                self.game_state.lose_life()
                self.game_state.register_miss()
            self.game_state.break_combo()
            self.soundtracks.play_miss()

            if self.game_state.is_game_over:
                self.state = self.STATE_GAMEOVER

    def _attempt_spawn(self, current_time, difficulty):
        """Try to spawn a new zombie."""
        time_since_last_spawn = current_time - self.last_spawn_attempt

        if time_since_last_spawn <= difficulty["spawn_interval"]:
            return

        self.last_spawn_attempt = current_time

        # Random chance to spawn
        if random.random() >= difficulty["spawn_chance"]:
            return

        # Pick random available hole
        available_holes = self.zombie_manager.get_available_holes()
        if not available_holes:
            return

        hole_index = random.choice(available_holes)
        self.zombie_manager.spawn(hole_index, current_time)

    # ==================== RENDERING ====================

    def _render(self):
        """Render current frame."""
        # Background
        self.screen.blit(self.textures.background, (0, 0))

        if self.state == self.STATE_PLAY:
            current_time = self._get_game_time()
            self._render_gameplay(current_time)

        self._render_overlay()

        pygame.display.flip()

    def _render_gameplay(self, current_time):
        """Render active gameplay elements."""
        difficulty = DifficultyManager.get_difficulty(self.game_state.level)

        # Draw zombies
        for i, grid_pos in enumerate(const.GRID_POSITIONS):
            zombie = self.zombie_manager.get_zombie(i)
            if zombie:
                self._render_zombie(
                    zombie, grid_pos, current_time, difficulty["show_duration"]
                )

        # Draw hitboxes (debug)
        if self.show_hitboxes:
            self._render_hitboxes()

        # Draw UI
        self._render_ui()

    def _render_zombie(self, zombie, grid_pos, current_time, show_duration):
        """Render a single zombie."""
        x, y = grid_pos

        # Squashed zombie (hit)
        if zombie.is_hit:
            self.screen.blit(self.textures.zombie_sprite_squashed, (x - 50, y - 20))
            return

        # Rising zombie
        visible_height = zombie.get_visible_height(current_time, self.zombie_height)
        if visible_height <= 0:
            return

        # Crop sprite from top (head appears first)
        crop_rect = pygame.Rect(0, 0, self.zombie_width, visible_height)
        cropped_sprite = self.textures.zombie_sprite.subsurface(crop_rect)
        self.screen.blit(cropped_sprite, (x - 50, y - visible_height))

        # Timer bar (only when mostly visible)
        if zombie.is_fully_risen(current_time, self.zombie_height):
            time_ratio = zombie.get_time_remaining_ratio(current_time, show_duration)
            self._render_timer_bar(x, y - visible_height, time_ratio)

    def _render_timer_bar(self, x, y, time_ratio):
        """Render countdown timer above zombie head."""
        bar_width = 60
        bar_height = 6
        bar_x = x - bar_width // 2 - 10
        bar_y = y - 15

        # Background
        pygame.draw.rect(
            self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height)
        )

        # Colored fill (changes based on time remaining)
        fill_width = int(bar_width * time_ratio)
        if time_ratio > 0.5:
            color = (100, 255, 100)  # Green
        elif time_ratio > 0.25:
            color = (255, 200, 50)  # Yellow
        else:
            color = (255, 70, 70)  # Red

        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(
            self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1
        )

    def _render_hitboxes(self):
        """Render hitbox visualization (debug)."""
        for grid_pos in const.GRID_POSITIONS:
            hitbox = self._get_hitbox(grid_pos)
            pygame.draw.rect(self.screen, const.RED, hitbox, 3)
            pygame.draw.circle(self.screen, const.WHITE, hitbox.center, 5)

    def _render_ui(self):
        """Render UI elements (score, lives, combo, level)."""

        # Score
        score_text = self.font_large.render(
            f"{self.game_state.score}", True, const.WHITE
        )
        score_x, score_y = 40, 20
        self.screen.blit(score_text, (score_x, score_y))

        # Hit/Miss Stats (to the right of score)
        hit_ratio = self.game_state.get_hit_ratio()
        stats_text = self.font_small.render(
            f"HITS: {self.game_state.hit_count} | MISS: {self.game_state.miss_count} | ACC: {hit_ratio:.1f}%",
            True,
            (200, 200, 200),
        )
        padding = 20
        stats_x = score_x + max(150, score_text.get_width()) + padding
        stats_y = score_y + (score_text.get_height() - stats_text.get_height()) // 2
        self.screen.blit(stats_text, (stats_x, stats_y))

        # Lives (red if low)
        lives_color = (255, 70, 70) if self.game_state.lives <= 2 else (160, 220, 255)
        lives_text = self.font_large.render(
            f"LIVES: {self.game_state.lives}", True, lives_color
        )
        lives_x = const.WIDTH - lives_text.get_width() - 40
        lives_y = 20
        self.screen.blit(lives_text, (lives_x, lives_y))

        # Level (under lives)
        level_text = self.font_small.render(
            f"LEVEL {self.game_state.level}", True, (180, 255, 180)
        )
        level_x = const.WIDTH - level_text.get_width() - 40
        level_y = lives_y + lives_text.get_height() + 8
        self.screen.blit(level_text, (level_x, level_y))

        # Combo (only show if >= threshold)
        if self.game_state.combo >= const.COMBO_DISPLAY_THRESHOLD:
            combo_text = self.font_small.render(
                f"COMBO x{self.game_state.combo}", True, (255, 220, 80)
            )
            self.screen.blit(
                combo_text,
                (const.WIDTH // 2 - combo_text.get_width() // 2, 80),
            )

    def _render_overlay(self):
        """Render menu/pause/gameover overlays."""
        if self.state == self.STATE_MENU:
            self._render_menu()
        elif self.state == self.STATE_PAUSE:
            self._render_pause()
        elif self.state == self.STATE_GAMEOVER:
            self._render_gameover()

    def _render_menu(self):
        """Render main menu."""
        overlay = self._create_overlay()
        self.screen.blit(overlay, (0, 0))

        title_text = self.font_large.render("WHACK-A-ZOMBIE", True, const.WHITE)
        start_text = self.font_small.render(
            "Press SPACEBAR to START", True, (160, 240, 160)
        )
        instruct_text = self.font_small.render(
            "Whack zombies before they escape! (H for hitboxes)", True, (220, 220, 240)
        )

        self._center_blit(title_text, const.HEIGHT // 2 - 80)
        self._center_blit(start_text, const.HEIGHT // 2 + 20)
        self._center_blit(instruct_text, const.HEIGHT // 2 + 80)

    def _render_pause(self):
        """Render pause screen."""
        overlay = self._create_overlay()
        self.screen.blit(overlay, (0, 0))

        paused_text = self.font_large.render("PAUSED", True, (255, 220, 80))
        resume_text = self.font_small.render(
            "SPACE to resume (Q quit)", True, (160, 240, 160)
        )

        self._center_blit(paused_text, const.HEIGHT // 2 - 40)
        self._center_blit(resume_text, const.HEIGHT // 2 + 40)

    def _render_gameover(self):
        """Render game over screen."""
        overlay = self._create_overlay()
        self.screen.blit(overlay, (0, 0))

        gameover_text = self.font_large.render("GAME OVER", True, (255, 60, 60))

        # Final stats with hit ratio
        hit_ratio = self.game_state.get_hit_ratio()
        stats_text = self.font_small.render(
            f"Final Score: {self.game_state.score} | Best Combo: {self.game_state.max_combo}",
            True,
            (220, 220, 240),
        )

        # Hit accuracy stats
        accuracy_text = self.font_small.render(
            f"Hits: {self.game_state.hit_count} | Misses: {self.game_state.miss_count} | Accuracy: {hit_ratio:.1f}%",
            True,
            (180, 220, 255),
        )

        restart_text = self.font_small.render(
            "Press R to play again", True, (160, 240, 160)
        )

        self._center_blit(gameover_text, const.HEIGHT // 2 - 120)
        self._center_blit(stats_text, const.HEIGHT // 2 - 20)
        self._center_blit(accuracy_text, const.HEIGHT // 2 + 30)
        self._center_blit(restart_text, const.HEIGHT // 2 + 100)

    # ==================== HELPERS ====================

    def _get_hitbox(self, grid_pos):
        """Get hitbox rectangle for a grid position."""
        x, y = grid_pos
        return pygame.Rect(
            x - self.zombie_half_width - 10,
            y - self.zombie_height,
            self.zombie_width + 10,
            self.zombie_height,
        )

    def _create_overlay(self):
        """Create semi-transparent overlay surface."""
        overlay = pygame.Surface((const.WIDTH, const.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        return overlay

    def _center_blit(self, surface, y_pos):
        """Blit surface centered horizontally at given y position."""
        x_pos = const.WIDTH // 2 - surface.get_width() // 2
        self.screen.blit(surface, (x_pos, y_pos))
