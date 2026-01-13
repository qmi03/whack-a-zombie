import random

import pygame

import src.const as const
import src.texture as texture

# ==================== INIT ====================
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720  # Updated to your background size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Whack-a-Zombie - Custom Background")
clock = pygame.time.Clock()
texture.load_textures()

try:
    hit_sound = pygame.mixer.Sound("assets/hit.wav")
    pop_sound = pygame.mixer.Sound("pop.wav")
    miss_sound = pygame.mixer.Sound("miss.wav")
    pygame.mixer.music.load("bg_music_loop.mp3")
    pygame.mixer.music.set_volume(0.4)
except:
    pop_sound = miss_sound = None
    print("Sounds not found - running without audio")

# Colors (fallback + zombie/UI)
BG_COLOR = (12, 20, 28)
ZOMBIE_COLOR = (95, 175, 85)
HIT_COLOR = (220, 50, 50)
WHITE = (240, 245, 255)
RED = (255, 50, 50)  # For debug crosses


# ==================== GAME STATE ====================
def reset_game():
    global score, lives, game_over, state, combo, max_combo, level, show_debug
    global holes, zombie_up_time, hit, last_spawn_attempt
    score = 0
    lives = 5
    combo = 0
    max_combo = 0
    level = 1
    game_over = False
    state = "PLAY"
    show_debug = False
    holes = [False] * 20
    zombie_up_time = [0] * 20
    hit = [False] * 20
    last_spawn_attempt = pygame.time.get_ticks()


reset_game()

# Difficulty progression (tuned for 20 holes)
SPAWN_INTERVAL_BASE = 1000  # Slightly faster base
SHOW_DURATION_BASE = 950

FONT = pygame.font.Font("./assets/pixel_square/Pixel Square Bold10.ttf", 64)
SMALL_FONT = pygame.font.Font("assets/pixel_square/Pixel Square 10.ttf", 36)


# ==================== HELPERS ====================
def get_hole_rect(pos):
    x, y = pos
    # Tuned for ~180px horizontal / 200px vertical spacing - covers full hole area
    return pygame.Rect(x - 75, y - 65, 150, 130)


def spawn_zombie():
    available = [i for i, up in enumerate(holes) if not up]
    if not available:
        return False
    idx = random.choice(available)
    holes[idx] = True
    zombie_up_time[idx] = pygame.time.get_ticks()
    hit[idx] = False
    if pop_sound:
        pop_sound.play()
    return True


def get_current_difficulty():
    spawn_int = max(350, SPAWN_INTERVAL_BASE - (level * 65))
    show_dur = max(500, SHOW_DURATION_BASE - (level * 55))
    spawn_chance = min(0.92, 0.60 + level * 0.06)
    return spawn_int, show_dur, spawn_chance


def draw_zombie(x, y, hit_state):
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


def draw_debug_cross(x, y):
    """Red crosses + circle for alignment testing"""
    pygame.draw.line(screen, RED, (x - 40, y - 40), (x + 40, y + 40), 6)
    pygame.draw.line(screen, RED, (x - 40, y + 40), (x + 40, y - 40), 6)
    pygame.draw.circle(screen, RED, (x, y), 12, 4)


# ==================== MAIN LOOP ====================
running = True
state = "PLAY"

while running:
    current_time = pygame.time.get_ticks()
    dt = clock.tick(60)

    # ─── EVENTS ───────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (game_over or state == "MENU"):
                reset_game()
                state = "PLAY"
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            if event.key == pygame.K_d:  # Toggle debug mode
                show_debug = not show_debug
                print(f"Debug crosses: {'ON' if show_debug else 'OFF'}")

        if event.type == pygame.MOUSEBUTTONDOWN and state == "PLAY" and not game_over:
            if event.button == 1:  # Left click
                pos = event.pos
                hit_any = False
                for i, center in enumerate(const.GRID):
                    if (
                        get_hole_rect(center).collidepoint(pos)
                        and holes[i]
                        and not hit[i]
                    ):
                        hit[i] = True
                        score += 10 + (combo // 3)  # Better scoring for chaos
                        combo += 1
                        max_combo = max(max_combo, combo)
                        if hit_sound:
                            hit_sound.play()
                        hit_any = True
                if not hit_any and combo > 0:
                    combo = 0
                    if miss_sound:
                        miss_sound.play()

    # ─── UPDATE ───────────────────────────────────────
    if state == "PLAY" and not game_over:
        spawn_interval, show_duration, spawn_chance = get_current_difficulty()

        # Level up every 40 points (adjusted for higher scores)
        if score >= level * 40:
            level += 1

        # Spawn attempts
        if current_time - last_spawn_attempt > spawn_interval:
            last_spawn_attempt = current_time
            if random.random() < spawn_chance:
                spawn_zombie()

        # Check timeouts & auto-hide
        for i in range(20):
            if holes[i]:
                elapsed = current_time - zombie_up_time[i]
                if not hit[i] and elapsed > show_duration:
                    # Missed!
                    holes[i] = False
                    lives -= 1
                    combo = 0
                    if miss_sound:
                        miss_sound.play()
                    if lives <= 0:
                        game_over = True
                        state = "GAMEOVER"
                elif hit[i] and elapsed > 400:  # Quick squash animation
                    holes[i] = False
                    hit[i] = False

    # ─── DRAW ─────────────────────────────────────────
    # Background first
    screen.blit(texture.background, (0, 0))

    # Draw zombies OVER the background holes
    for i, (x, y) in enumerate(const.GRID):
        if holes[i]:
            draw_zombie(x, y, hit[i])

    # Debug crosses (if enabled - press D)
    if show_debug:
        for x, y in const.GRID:
            draw_debug_cross(x, y)

    # UI
    score_text = FONT.render(f"{score}", True, WHITE)
    lives_text = FONT.render(
        f"LIVES: {lives}", True, (255, 70, 70) if lives <= 2 else (160, 220, 255)
    )
    combo_text = (
        SMALL_FONT.render(f"COMBO x{combo}", True, (255, 220, 80))
        if combo >= 3
        else None
    )
    level_text = SMALL_FONT.render(f"LEVEL {level}", True, (180, 255, 180))

    screen.blit(score_text, (40, 20))
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 40, 20))
    if combo_text:
        screen.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 80))
    screen.blit(level_text, (40, 120))

    # Debug info
    if show_debug:
        debug_text = SMALL_FONT.render("DEBUG ON (Press D to toggle)", True, RED)
        screen.blit(debug_text, (40, HEIGHT - 60))

    # Game Over
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        go_text = FONT.render("GAME OVER", True, (255, 60, 60))
        final_text = SMALL_FONT.render(
            f"Final Score: {score} | Best Combo: {max_combo}", True, (220, 220, 240)
        )
        restart_text = SMALL_FONT.render("Press R to play again", True, (160, 240, 160))

        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(final_text, (WIDTH // 2 - final_text.get_width() // 2, HEIGHT // 2))
        screen.blit(
            restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80)
        )

    pygame.display.flip()

pygame.quit()
