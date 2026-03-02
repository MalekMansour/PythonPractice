import pygame
import sys
import math
import random

# ----------------------------
# Geometry Dash (mini clone)
# ----------------------------

WIDTH, HEIGHT = 900, 500
FPS = 60

GROUND_Y = 380
GRAVITY = 0.9
JUMP_VEL = -15.5

PLAYER_SIZE = 36
PLAYER_X = 180

SCROLL_SPEED_START = 7.5
SPEED_INCREASE_PER_SEC = 0.12  # gentle ramp

# Colors
BG = (14, 16, 25)
GRID = (25, 30, 45)
GROUND = (38, 42, 60)
PLAYER = (245, 220, 90)
PLAYER_OUTLINE = (35, 35, 35)
OBSTACLE = (220, 70, 80)
TEXT = (235, 240, 255)
ACCENT = (90, 200, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GD Mini Clone (Python)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)
big_font = pygame.font.SysFont("consolas", 48)

def rect_from_bottom(x, bottom_y, w, h):
    return pygame.Rect(int(x), int(bottom_y - h), int(w), int(h))

def make_level():
    """
    Make a simple prebuilt "song-like" level:
    A list of obstacles with x positions (world coordinates) and type.
    """
    obstacles = []
    x = 600
    pattern = [
        ("spike", 0), ("gap", 160),
        ("spike", 0), ("spike", 60), ("gap", 220),
        ("block", 0), ("gap", 200),
        ("spike", 0), ("gap", 140), ("spike", 0), ("gap", 260),
        ("block", 0), ("block", 70), ("gap", 260),
        ("spike", 0), ("spike", 70), ("spike", 140), ("gap", 320),
        ("block", 0), ("gap", 180), ("spike", 0), ("gap", 240),
    ]
    # Repeat patterns with increasing spacing so it feels like a level
    for rep in range(8):
        for kind, dx in pattern:
            if kind == "gap":
                x += dx
                continue
            if kind == "spike":
                obstacles.append({"type": "spike", "x": x + dx})
                x += 110
            elif kind == "block":
                obstacles.append({"type": "block", "x": x + dx})
                x += 140
        x += 180 + rep * 20
    return obstacles

def spike_shape(rect):
    # Triangle points for drawing, collision uses rect (simple)
    x, y, w, h = rect
    return [(x, y + h), (x + w / 2, y), (x + w, y + h)]

def draw_grid(scroll):
    # simple parallax grid
    step = 40
    offset = int(scroll) % step
    for x in range(-step, WIDTH + step, step):
        pygame.draw.line(screen, GRID, (x - offset, 0), (x - offset, HEIGHT), 1)
    for y in range(0, HEIGHT, step):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y), 1)

class PlayerObj:
    def __init__(self):
        self.reset()

    def reset(self):
        self.y = GROUND_Y - PLAYER_SIZE
        self.vy = 0.0
        self.on_ground = True
        self.rot = 0.0
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(PLAYER_X, int(self.y), PLAYER_SIZE, PLAYER_SIZE)

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_VEL
            self.on_ground = False

    def update(self):
        if not self.alive:
            return
        self.vy += GRAVITY
        self.y += self.vy

        # ground collision
        if self.y >= GROUND_Y - PLAYER_SIZE:
            self.y = GROUND_Y - PLAYER_SIZE
            self.vy = 0.0
            self.on_ground = True

        # rotate while in air (GD vibe)
        if not self.on_ground:
            self.rot += 12.5
        else:
            # snap rotation to nearest 90 degrees on landing (looks clean)
            self.rot = round(self.rot / 90) * 90

    def draw(self):
        r = self.rect
        # draw rotated square by drawing onto a temp surface
        surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, PLAYER, (0, 0, PLAYER_SIZE, PLAYER_SIZE), border_radius=6)
        pygame.draw.rect(surf, PLAYER_OUTLINE, (0, 0, PLAYER_SIZE, PLAYER_SIZE), 3, border_radius=6)

        rotated = pygame.transform.rotate(surf, -self.rot)
        rr = rotated.get_rect(center=r.center)
        screen.blit(rotated, rr.topleft)

def draw_ground(scroll):
    pygame.draw.rect(screen, GROUND, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    # little moving highlights
    for i in range(0, WIDTH + 120, 120):
        x = i - (scroll * 0.7) % 120
        pygame.draw.rect(screen, (55, 62, 90), (x, GROUND_Y + 10, 70, 10), border_radius=6)

def obstacle_rect(obs):
    if obs["type"] == "spike":
        # spikes sit on ground
        return rect_from_bottom(obs["x"], GROUND_Y, 34, 34)
    else:
        # blocks
        return rect_from_bottom(obs["x"], GROUND_Y, 44, 44)

def draw_obstacles(obstacles, scroll):
    for obs in obstacles:
        x_screen = obs["x"] - scroll
        if x_screen < -100 or x_screen > WIDTH + 100:
            continue
        r = obstacle_rect(obs).copy()
        r.x = int(x_screen)

        if obs["type"] == "spike":
            pygame.draw.polygon(screen, OBSTACLE, spike_shape(r))
            pygame.draw.polygon(screen, (30, 30, 30), spike_shape(r), 2)
        else:
            pygame.draw.rect(screen, (200, 90, 110), r, border_radius=6)
            pygame.draw.rect(screen, (30, 30, 30), r, 2, border_radius=6)
            # inner detail
            inner = r.inflate(-14, -14)
            pygame.draw.rect(screen, (235, 150, 165), inner, border_radius=6)

def collide(player_rect, obstacles, scroll):
    # simple AABB collision (good enough for a mini clone)
    for obs in obstacles:
        r = obstacle_rect(obs)
        r.x = int(obs["x"] - scroll)
        if r.right < -50:
            continue
        if r.left > WIDTH + 50:
            # obstacles are in order; can break early if you want
            pass
        if player_rect.colliderect(r):
            return True
    return False

def draw_hud(distance, best, speed):
    s1 = font.render(f"Distance: {int(distance)}", True, TEXT)
    s2 = font.render(f"Best: {int(best)}", True, TEXT)
    s3 = font.render(f"Speed: {speed:.1f}", True, ACCENT)
    screen.blit(s1, (18, 14))
    screen.blit(s2, (18, 40))
    screen.blit(s3, (18, 66))

def title_screen():
    t = big_font.render("GD MINI CLONE", True, TEXT)
    p = font.render("Press SPACE to start • Hold SPACE to jump timing • R to restart", True, (190, 200, 220))
    screen.blit(t, (WIDTH//2 - t.get_width()//2, 160))
    screen.blit(p, (WIDTH//2 - p.get_width()//2, 225))

def game_over_screen(distance, best):
    t = big_font.render("CRASH!", True, OBSTACLE)
    p1 = font.render(f"Distance: {int(distance)}   Best: {int(best)}", True, TEXT)
    p2 = font.render("Press R to retry • ESC to quit", True, (190, 200, 220))
    screen.blit(t, (WIDTH//2 - t.get_width()//2, 160))
    screen.blit(p1, (WIDTH//2 - p1.get_width()//2, 225))
    screen.blit(p2, (WIDTH//2 - p2.get_width()//2, 255))

def main():
    player = PlayerObj()
    obstacles = make_level()

    state = "menu"  # menu, playing, dead
    scroll = 0.0
    distance = 0.0
    best = 0.0
    speed = SCROLL_SPEED_START
    time_playing = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0

        # ---- events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:
                    if state == "menu":
                        state = "playing"
                        player.reset()
                        scroll = 0.0
                        distance = 0.0
                        speed = SCROLL_SPEED_START
                        time_playing = 0.0
                    elif state == "playing":
                        player.jump()
                    elif state == "dead":
                        # allow space to retry too
                        state = "playing"
                        player.reset()
                        scroll = 0.0
                        distance = 0.0
                        speed = SCROLL_SPEED_START
                        time_playing = 0.0

                if event.key == pygame.K_r:
                    state = "playing"
                    player.reset()
                    scroll = 0.0
                    distance = 0.0
                    speed = SCROLL_SPEED_START
                    time_playing = 0.0

        keys = pygame.key.get_pressed()
        if state == "playing":
            # optional: let holding space trigger jump only when grounded
            if keys[pygame.K_SPACE]:
                player.jump()

            time_playing += dt
            speed = SCROLL_SPEED_START + time_playing * SPEED_INCREASE_PER_SEC

            scroll += speed
            distance += speed * (1.0 / 3.0)  # just a scaled value

            player.update()

            if collide(player.rect, obstacles, scroll):
                state = "dead"
                best = max(best, distance)

        # ---- draw ----
        screen.fill(BG)
        draw_grid(scroll * 0.5)
        draw_ground(scroll)
        draw_obstacles(obstacles, scroll)

        if state in ("playing", "dead"):
            player.draw()
            draw_hud(distance, best, speed)
        else:
            # menu
            title_screen()
            draw_hud(distance, best, speed)

        if state == "dead":
            game_over_screen(distance, best)

        pygame.display.flip()

if __name__ == "__main__":
    main()
