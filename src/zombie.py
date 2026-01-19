"""Zombie entity management."""

from . import const


class Zombie:
    """Represents a single zombie in a hole."""

    def __init__(self, hole_index, spawn_time):
        self.hole_index = hole_index
        self.spawn_time = spawn_time
        self.is_hit = False
        self.is_active = True

    def get_elapsed_time(self, current_time):
        """Get time since zombie spawned."""
        return current_time - self.spawn_time

    def get_visible_height(self, current_time, max_height):
        """Calculate how much of the zombie is visible (rising animation)."""
        elapsed = self.get_elapsed_time(current_time)
        progress = min(1.0, elapsed / const.ZOMBIE_RISE_DURATION)
        return int(max_height * progress)

    def get_time_remaining_ratio(self, current_time, show_duration):
        """Get ratio of time remaining before zombie escapes (for timer bar)."""
        elapsed = self.get_elapsed_time(current_time)
        return max(0.0, 1.0 - (elapsed / show_duration))

    def is_fully_risen(self, current_time, max_height):
        """Check if zombie has fully emerged (80% visible)."""
        visible_height = self.get_visible_height(current_time, max_height)
        return visible_height >= max_height * 0.8

    def mark_as_hit(self):
        """Mark this zombie as successfully hit."""
        self.is_hit = True

    def should_timeout(self, current_time, show_duration):
        """Check if zombie should disappear (not hit in time)."""
        return not self.is_hit and self.get_elapsed_time(current_time) > show_duration

    def should_cleanup(self, current_time):
        """Check if hit zombie animation is complete."""
        return (
            self.is_hit
            and self.get_elapsed_time(current_time) > const.HIT_DISPLAY_DURATION
        )


class ZombieManager:
    """Manages all active zombies in the game."""

    def __init__(self, num_holes):
        self.num_holes = num_holes
        self.zombies = [None] * num_holes

    def spawn(self, hole_index, current_time):
        """Spawn a new zombie in the specified hole."""
        if self.zombies[hole_index] is not None:
            return False

        self.zombies[hole_index] = Zombie(hole_index, current_time)
        return True

    def get_zombie(self, hole_index):
        """Get zombie at specified hole index."""
        return self.zombies[hole_index]

    def is_hole_occupied(self, hole_index):
        """Check if hole has an active zombie."""
        return self.zombies[hole_index] is not None

    def hit_zombie(self, hole_index):
        """Mark zombie as hit if it exists and hasn't been hit yet."""
        zombie = self.zombies[hole_index]
        if zombie and not zombie.is_hit:
            zombie.mark_as_hit()
            return True
        return False

    def remove_zombie(self, hole_index):
        """Remove zombie from hole."""
        self.zombies[hole_index] = None

    def get_available_holes(self):
        """Get list of hole indices that don't have zombies."""
        return [i for i in range(self.num_holes) if not self.is_hole_occupied(i)]

    def update(self, current_time, show_duration):
        """Update all zombies, removing those that should be cleaned up.

        Returns:
            int: Number of zombies that timed out (player missed)
        """
        timeouts = 0

        for i in range(self.num_holes):
            zombie = self.zombies[i]
            if zombie is None:
                continue

            # Check for timeout (zombie escaped)
            if zombie.should_timeout(current_time, show_duration):
                self.remove_zombie(i)
                timeouts += 1

            # Check for cleanup (hit animation finished)
            elif zombie.should_cleanup(current_time):
                self.remove_zombie(i)

        return timeouts

    def reset(self):
        """Clear all zombies."""
        self.zombies = [None] * self.num_holes
