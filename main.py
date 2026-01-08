"""
Body Defender – Immune System Arena
Simple educational 2D game using pygame only.
"""

import math
import random
import sys
from dataclasses import dataclass

import pygame


# ----------------------------- Constants --------------------------------- #
WIDTH, HEIGHT = 900, 600
FPS = 60

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
RED = (220, 70, 70)      # Virus
GREEN = (60, 200, 120)   # Bacteria
BLUE = (80, 160, 240)    # Player (macrophage)
YELLOW = (240, 210, 80)  # Projectiles / antibodies
PURPLE = (180, 110, 220) # Alarm effect


# ----------------------------- Helper Types ------------------------------ #
@dataclass
class Upgrade:
    name: str
    description: str


# ----------------------------- Game Entities ----------------------------- #
class Player:
    """Macrophage: innate immune cell that engulfs pathogens."""

    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.radius = 18
        self.speed = 220
        self.hp = 100
        self.max_hp = 100
        self.attack_range = 35
        self.damage = 1

        # Ability: alarm signal (inflammation)
        self.alarm_cooldown = 8.0
        self.alarm_timer = 0.0
        self.alarm_duration = 2.0
        self.alarm_active = 0.0

        # Adaptive immune upgrades
        self.has_antibodies = False
        self.specificity = None  # "virus" or "bacteria"
        self.immune_memory = False

        # Auto-fire timing for antibodies
        self.shoot_timer = 0.0
        self.shoot_interval = 0.6

    def move(self, dt, keys):
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.pos += direction * self.speed * dt
        self.pos.x = max(self.radius, min(WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(HEIGHT - self.radius, self.pos.y))

    def trigger_alarm(self):
        if self.alarm_timer <= 0:
            self.alarm_active = self.alarm_duration
            self.alarm_timer = self.alarm_cooldown

    def update_timers(self, dt):
        if self.alarm_timer > 0:
            self.alarm_timer -= dt
        if self.alarm_active > 0:
            self.alarm_active -= dt
        if self.has_antibodies:
            self.shoot_timer -= dt

    def can_shoot(self):
        return self.has_antibodies and self.shoot_timer <= 0

    def reset_shoot_timer(self):
        self.shoot_timer = self.shoot_interval


class Pathogen:
    def __init__(self, kind):
        self.kind = kind  # "virus" or "bacteria"
        self.pos = pygame.Vector2(
            random.choice([random.randint(0, WIDTH), random.choice([0, WIDTH])]),
            random.choice([random.randint(0, HEIGHT), random.choice([0, HEIGHT])]),
        )
        if kind == "virus":
            self.color = RED
            self.speed = 140
            self.hp = 2
            self.radius = 10
        else:
            self.color = GREEN
            self.speed = 80
            self.hp = 4
            self.radius = 14

        self.slow_timer = 0.0

    def update(self, dt, target_pos):
        direction = target_pos - self.pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
        speed = self.speed * (0.4 if self.slow_timer > 0 else 1.0)
        self.pos += direction * speed * dt
        if self.slow_timer > 0:
            self.slow_timer -= dt

    def take_damage(self, amount):
        self.hp -= amount

    def is_alive(self):
        return self.hp > 0


class Projectile:
    """Antibody projectile: part of adaptive immunity."""

    def __init__(self, start_pos, target_pos):
        self.pos = pygame.Vector2(start_pos)
        direction = target_pos - self.pos
        self.velocity = direction.normalize() * 320 if direction.length_squared() else pygame.Vector2(0, 0)
        self.radius = 5
        self.damage = 1
        self.alive = True

    def update(self, dt):
        self.pos += self.velocity * dt
        if (
            self.pos.x < -10
            or self.pos.x > WIDTH + 10
            or self.pos.y < -10
            or self.pos.y > HEIGHT + 10
        ):
            self.alive = False


# ----------------------------- Main Game --------------------------------- #
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Body Defender – Immune System Arena")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 18)
        self.big_font = pygame.font.SysFont("arial", 28, bold=True)

        self.player = Player(WIDTH / 2, HEIGHT / 2)
        self.pathogens = []
        self.projectiles = []

        self.kills = 0
        self.adaptation_meter = 0
        self.adaptation_threshold = 10

        self.wave = 1
        self.wave_timer = 0.0
        self.wave_spawned = False
        self.max_waves = 3

        self.elapsed_time = 0.0
        self.infection = 0.0

        self.state = "instructions"  # instructions, playing, upgrade, paused, won, lost

        self.upgrades = [
            Upgrade("B Cells / Antibodies", "Auto-fire antibodies at nearby pathogens."),
            Upgrade("Specificity", "Deal +1 damage to either virus or bacteria."),
            Upgrade("Immune Memory", "Future waves spawn slower and weaker."),
        ]

    # ----------------------------- Game Flow ----------------------------- #
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()

            if self.state == "playing":
                self.update(dt)
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == "instructions" and event.key == pygame.K_SPACE:
                    self.state = "playing"
                elif event.key == pygame.K_p and self.state == "playing":
                    self.state = "paused"
                elif event.key == pygame.K_p and self.state == "paused":
                    self.state = "playing"
                elif event.key == pygame.K_r and self.state in {"won", "lost"}:
                    self.__init__()
                elif self.state == "playing":
                    if event.key == pygame.K_e:
                        self.player.trigger_alarm()
                elif self.state == "upgrade":
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self.apply_upgrade(event.key)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.move(dt, keys)
        self.player.update_timers(dt)

        # Attack (phagocytosis) on space: close-range damage.
        if keys[pygame.K_SPACE]:
            for pathogen in self.pathogens:
                if pathogen.pos.distance_to(self.player.pos) <= self.player.attack_range:
                    damage = self.player.damage
                    if self.player.specificity == pathogen.kind:
                        damage += 1
                    pathogen.take_damage(damage)

        # Alarm ability: slow nearby pathogens.
        if self.player.alarm_active > 0:
            for pathogen in self.pathogens:
                if pathogen.pos.distance_to(self.player.pos) <= 110:
                    pathogen.slow_timer = 0.2  # refreshed while in range

        # Adaptive immunity: antibodies auto-fire.
        if self.player.can_shoot() and self.pathogens:
            target = min(self.pathogens, key=lambda p: p.pos.distance_to(self.player.pos))
            self.projectiles.append(Projectile(self.player.pos, target.pos))
            self.player.reset_shoot_timer()

        # Update pathogens and check collision with player.
        for pathogen in self.pathogens:
            pathogen.update(dt, self.player.pos)
            if pathogen.pos.distance_to(self.player.pos) <= pathogen.radius + self.player.radius:
                self.player.hp -= 20 * dt

        # Update projectiles and handle hits.
        for projectile in self.projectiles:
            projectile.update(dt)
            for pathogen in self.pathogens:
                if pathogen.pos.distance_to(projectile.pos) <= pathogen.radius + projectile.radius:
                    pathogen.take_damage(projectile.damage)
                    projectile.alive = False
                    break

        # Count kills before removing defeated pathogens.
        defeated = sum(1 for p in self.pathogens if not p.is_alive())
        self.kills += defeated

        # Cleanup
        self.pathogens = [p for p in self.pathogens if p.is_alive()]
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Infection rises when pathogens persist.
        self.infection += len(self.pathogens) * 0.6 * dt

        # Update time and waves
        self.elapsed_time += dt
        self.wave_timer += dt
        self.manage_waves()

        # Adaptive immunity meter
        if self.kills >= self.adaptation_threshold:
            self.adaptation_meter = self.adaptation_threshold
            self.state = "upgrade"

        # Win/Lose conditions
        if self.player.hp <= 0 or self.infection >= 100:
            self.state = "lost"
        if self.elapsed_time >= 120 or self.wave > self.max_waves:
            self.state = "won"

    def manage_waves(self):
        if not self.wave_spawned:
            self.spawn_wave()
            self.wave_spawned = True
            self.wave_timer = 0
        # Next wave when most pathogens cleared or time passes
        if self.wave_spawned and (len(self.pathogens) <= 1 or self.wave_timer >= 22):
            self.wave += 1
            self.wave_spawned = False

    def spawn_wave(self):
        base_count = 6 + self.wave * 2
        if self.player.immune_memory:
            base_count = max(4, base_count - 3)
        for _ in range(base_count):
            kind = "virus" if random.random() < 0.6 else "bacteria"
            self.pathogens.append(Pathogen(kind))

    def apply_upgrade(self, key):
        if key == pygame.K_1:
            self.player.has_antibodies = True
        elif key == pygame.K_2:
            # Choose a type to specialize based on current majority.
            virus_count = sum(1 for p in self.pathogens if p.kind == "virus")
            self.player.specificity = "virus" if virus_count >= len(self.pathogens) / 2 else "bacteria"
        elif key == pygame.K_3:
            self.player.immune_memory = True
        # Reset meter and return to game
        self.kills = 0
        self.adaptation_meter = 0
        self.state = "playing"

    # ----------------------------- Drawing ------------------------------- #
    def draw(self):
        self.screen.fill(WHITE)
        if self.state == "instructions":
            self.draw_instructions()
        else:
            self.draw_game()
            if self.state == "paused":
                self.draw_center_text("PAUSED (Press P)", BLACK)
            if self.state == "upgrade":
                self.draw_upgrade_screen()
            if self.state == "won":
                self.draw_center_text("YOU WIN! Press R to Restart", BLUE)
            if self.state == "lost":
                self.draw_center_text("YOU LOST! Press R to Restart", RED)
        pygame.display.flip()

    def draw_game(self):
        # Player
        pygame.draw.circle(self.screen, BLUE, self.player.pos, self.player.radius)

        # Alarm effect ring
        if self.player.alarm_active > 0:
            pygame.draw.circle(self.screen, PURPLE, self.player.pos, 110, 2)

        # Pathogens
        for pathogen in self.pathogens:
            pygame.draw.circle(self.screen, pathogen.color, pathogen.pos, pathogen.radius)

        # Projectiles
        for projectile in self.projectiles:
            pygame.draw.circle(self.screen, YELLOW, projectile.pos, projectile.radius)

        # UI
        self.draw_ui()

    def draw_ui(self):
        # Health bar
        self.draw_bar(20, 20, 200, 18, self.player.hp, self.player.max_hp, BLUE, "HP")
        # Infection bar
        self.draw_bar(20, 45, 200, 18, self.infection, 100, RED, "Infection")
        # Timer and wave
        timer_text = self.font.render(f"Time: {int(self.elapsed_time)}s", True, BLACK)
        wave_text = self.font.render(f"Wave: {self.wave}/{self.max_waves}", True, BLACK)
        self.screen.blit(timer_text, (20, 70))
        self.screen.blit(wave_text, (20, 95))

        # Ability cooldown
        cooldown = max(0, self.player.alarm_timer)
        cooldown_text = self.font.render(f"Alarm (E) CD: {cooldown:.1f}s", True, BLACK)
        self.screen.blit(cooldown_text, (20, 120))

        # Educational tips
        edu = [
            "Macrophages are innate immune cells that 'eat' pathogens.",
            "Adaptive immunity learns: antibodies attack, memory responds faster.",
        ]
        for i, line in enumerate(edu):
            text = self.font.render(line, True, BLACK)
            self.screen.blit(text, (WIDTH - 450, 20 + i * 20))

    def draw_bar(self, x, y, w, h, value, max_value, color, label):
        pygame.draw.rect(self.screen, GRAY, (x, y, w, h))
        fill = max(0, min(1, value / max_value))
        pygame.draw.rect(self.screen, color, (x, y, int(w * fill), h))
        text = self.font.render(label, True, BLACK)
        self.screen.blit(text, (x + w + 8, y))

    def draw_instructions(self):
        lines = [
            "Body Defender – Immune System Arena",
            "",
            "You are a macrophage (innate immune cell).",
            "Goal: survive 120 seconds or clear 3 waves.",
            "Lose if HP hits 0 or infection reaches 100%.",
            "",
            "Controls:",
            "Move: WASD or Arrow Keys",
            "Attack (phagocytosis): SPACE",
            "Alarm Signal (slow nearby pathogens): E",
            "Pause: P",
            "",
            "Adaptive immunity:",
            "After enough kills, choose an upgrade with 1 / 2 / 3.",
            "",
            "Press SPACE to start!",
        ]
        for i, line in enumerate(lines):
            font = self.big_font if i == 0 else self.font
            text = font.render(line, True, BLACK)
            x = WIDTH / 2 - text.get_width() / 2
            y = 80 + i * 28
            self.screen.blit(text, (x, y))

    def draw_center_text(self, message, color):
        text = self.big_font.render(message, True, color)
        x = WIDTH / 2 - text.get_width() / 2
        y = HEIGHT / 2 - text.get_height() / 2
        self.screen.blit(text, (x, y))

    def draw_upgrade_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.big_font.render("Adaptive Immunity Upgrade!", True, WHITE)
        self.screen.blit(title, (WIDTH / 2 - title.get_width() / 2, 100))

        for i, upgrade in enumerate(self.upgrades, start=1):
            text = self.font.render(f"{i}) {upgrade.name} - {upgrade.description}", True, WHITE)
            self.screen.blit(text, (120, 170 + i * 30))


if __name__ == "__main__":
    Game().run()
