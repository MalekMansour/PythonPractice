import pygame
import sys
import json
import math

# ----------------------------
# GD Mini Editor + Playtest
# ----------------------------

WIDTH, HEIGHT = 1100, 560
FPS = 60

GRID = 40
GROUND_Y = 420

PLAYER_X = 220

# Scroll / speed
SCROLL_SPEED = 9.0

# Cube physics
CUBE_SIZE = 34
GRAVITY = 0.9
JUMP_VEL = -15.0

# Wave physics
WAVE_SIZE = 18
WAVE_RATE = 7.2  # pixels per frame-ish (scaled in update)

# Ship physics
SHIP_SIZE = 22
SHIP_GRAV = 0.55
SHIP_THRUST = -1.15
SHIP_MAX_VY = 10.0

# Colors
BG = (14, 16, 25)
GRID_CLR = (25, 30, 45)
GROUND_CLR = (38, 42, 60)
TEXT = (235, 240, 255)

SPIKE_CLR = (220, 70, 80)
BLOCK_CLR = (200, 90, 110)
PLATFORM_CLR = (110, 190, 130)
PORTAL_WAVE_CLR = (155, 110, 255)
PORTAL_CUBE_CLR = (110, 210, 255)
PORTAL_SHIP_CLR = (255, 170, 80)
WAVEBLOCK_CLR = (90, 120, 210)

OUTLINE = (30, 30, 30)
PLAYER_CLR = (245, 220, 90)

LEVEL_FILE = "level.json"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GD Mini - Level Editor + Playtest")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)
big = pygame.font.SysFont("consolas", 34)

def snap(v, step=GRID):
    return int(round(v / step) * step)

def draw_grid(scroll_px):
    step = GRID
    offset = int(scroll_px) % step
    for x in range(-step, WIDTH + step, step):
        pygame.draw.line(screen, GRID_CLR, (x - offset, 0), (x - offset, HEIGHT), 1)
    for y in range(0, HEIGHT, step):
        pygame.draw.line(screen, GRID_CLR, (0, y), (WIDTH, y), 1)

def draw_ground():
    pygame.draw.rect(screen, GROUND_CLR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

def rect_from_bottom_world(xw, bottom_y, w, h):
    return pygame.Rect(int(xw), int(bottom_y - h), int(w), int(h))

def spike_points(rect):
    return [(rect.left, rect.bottom), (rect.centerx, rect.top), (rect.right, rect.bottom)]

def world_to_screen_x(xw, scroll):
    return xw - scroll

def make_portal_rect(xw, kind):
    # portals sit on ground
    if kind == "portal_wave":
        return rect_from_bottom_world(xw, GROUND_Y, 26, 88)
    if kind == "portal_cube":
        return rect_from_bottom_world(xw, GROUND_Y, 26, 88)
    if kind == "portal_ship":
        return rect_from_bottom_world(xw, GROUND_Y, 26, 88)
    return rect_from_bottom_world(xw, GROUND_Y, 26, 88)

def draw_item(item, scroll, editor=False):
    t = item["type"]
    xw = item["x"]
    xs = int(world_to_screen_x(xw, scroll))

    if t == "spike":
        r = rect_from_bottom_world(xs, GROUND_Y, 34, 34)
        pts = spike_points(r)
        pygame.draw.polygon(screen, SPIKE_CLR, pts)
        pygame.draw.polygon(screen, OUTLINE, pts, 2)

    elif t == "block":
        r = rect_from_bottom_world(xs, GROUND_Y, 44, 44)
        pygame.draw.rect(screen, BLOCK_CLR, r, border_radius=6)
        pygame.draw.rect(screen, OUTLINE, r, 2, border_radius=6)

    elif t == "platform":
        # stored as top_y (absolute)
        w = item.get("w", 120)
        h = item.get("h", 20)
        top_y = item.get("top_y", GROUND_Y - 80)
        r = pygame.Rect(xs, int(top_y), int(w), int(h))
        pygame.draw.rect(screen, PLATFORM_CLR, r, border_radius=8)
        pygame.draw.rect(screen, OUTLINE, r, 2, border_radius=8)

    elif t.startswith("portal_"):
        r = make_portal_rect(xs, t)
        clr = PORTAL_WAVE_CLR if t == "portal_wave" else PORTAL_CUBE_CLR if t == "portal_cube" else PORTAL_SHIP_CLR
        pygame.draw.rect(screen, clr, r, border_radius=10)
        pygame.draw.rect(screen, OUTLINE, r, 2, border_radius=10)
        cx, cy = r.center
        for rad in (7, 12, 17, 22, 27, 32):
            pygame.draw.circle(screen, (210, 190, 255), (cx, cy), rad, 2)

    elif t == "wave_block":
        # hazard rectangle for wave/ship, stored as y,w,h
        y = item.get("y", 160)
        w = item.get("w", 80)
        h = item.get("h", 80)
        r = pygame.Rect(xs, int(y), int(w), int(h))
        pygame.draw.rect(screen, WAVEBLOCK_CLR, r, border_radius=10)
        pygame.draw.rect(screen, OUTLINE, r, 2, border_radius=10)

    # In editor: show id-like hint (optional)
    if editor:
        pass

def item_hitbox(item, scroll):
    t = item["type"]
    xs = int(world_to_screen_x(item["x"], scroll))

    if t == "spike":
        return rect_from_bottom_world(xs, GROUND_Y, 34, 34)
    if t == "block":
        return rect_from_bottom_world(xs, GROUND_Y, 44, 44)
    if t == "platform":
        w = item.get("w", 120)
        h = item.get("h", 20)
        top_y = item.get("top_y", GROUND_Y - 80)
        return pygame.Rect(xs, int(top_y), int(w), int(h))
    if t.startswith("portal_"):
        return make_portal_rect(xs, t)
    if t == "wave_block":
        y = item.get("y", 160)
        w = item.get("w", 80)
        h = item.get("h", 80)
        return pygame.Rect(xs, int(y), int(w), int(h))
    return pygame.Rect(xs, 0, 0, 0)

def item_hitbox_world(item):
    # used for saving deletion by world mouse: compare world X with scroll=0 then offset later
    # We'll do deletion using screen hitboxes (scroll-aware), so we don't need this.
    return None

def save_level(items, path=LEVEL_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

def load_level(path=LEVEL_FILE):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # basic validation
        if isinstance(data, list):
            return data
    except FileNotFoundError:
        return []
    except Exception:
        return []
    return []

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.mode = "cube"  # cube, wave, ship
        # cube
        self.y = GROUND_Y - CUBE_SIZE
        self.vy = 0.0
        self.on_ground = True
        self.rot = 0.0
        # wave
        self.wave_y = 200.0
        # ship
        self.ship_y = 200.0
        self.ship_vy = 0.0
        self.dead = False

    def rect_cube(self):
        return pygame.Rect(PLAYER_X, int(self.y), CUBE_SIZE, CUBE_SIZE)

    def rect_wave(self):
        return pygame.Rect(PLAYER_X, int(self.wave_y - WAVE_SIZE/2), WAVE_SIZE, WAVE_SIZE)

    def rect_ship(self):
        return pygame.Rect(PLAYER_X, int(self.ship_y - SHIP_SIZE/2), SHIP_SIZE, SHIP_SIZE)

    def jump(self):
        if self.mode == "cube" and self.on_ground:
            self.vy = JUMP_VEL
            self.on_ground = False

    def switch_mode(self, new_mode):
        if new_mode == self.mode:
            return
        # keep vertical position roughly consistent
        if self.mode == "cube":
            center = self.y + CUBE_SIZE / 2
        elif self.mode == "wave":
            center = self.wave_y
        else:
            center = self.ship_y

        self.mode = new_mode
        if new_mode == "cube":
            self.y = center - CUBE_SIZE / 2
            self.vy = 0.0
            self.on_ground = False
        elif new_mode == "wave":
            self.wave_y = center
        else:
            self.ship_y = center
            self.ship_vy = 0.0

    def update_cube(self):
        self.vy += GRAVITY
        self.y += self.vy
        self.on_ground = False

        if self.y >= GROUND_Y - CUBE_SIZE:
            self.y = GROUND_Y - CUBE_SIZE
            self.vy = 0.0
            self.on_ground = True
            self.rot = round(self.rot / 90) * 90
        else:
            self.rot += 12.0

    def resolve_platforms(self, platforms, scroll):
        # landing only (simple)
        pr = self.rect_cube()
        for p in platforms:
            r = item_hitbox(p, scroll)
            if r.width == 0:
                continue
            if pr.colliderect(r) and self.vy >= 0:
                # came from above
                if (pr.bottom - self.vy) <= r.top + 10:
                    self.y = r.top - CUBE_SIZE
                    self.vy = 0.0
                    self.on_ground = True
                    pr = self.rect_cube()

    def update_wave(self, keys):
        # hold = up, release = down (wave vibe)
        going_up = keys[pygame.K_SPACE]
        self.wave_y += (-WAVE_RATE if going_up else WAVE_RATE)

        # keep in bounds
        self.wave_y = clamp(self.wave_y, 20, HEIGHT - 20)

    def update_ship(self, keys):
        # flappy-ish ship
        thrust = keys[pygame.K_SPACE]
        self.ship_vy += SHIP_GRAV
        if thrust:
            self.ship_vy += SHIP_THRUST
        self.ship_vy = clamp(self.ship_vy, -SHIP_MAX_VY, SHIP_MAX_VY)
        self.ship_y += self.ship_vy
        self.ship_y = clamp(self.ship_y, 20, HEIGHT - 20)

    def update(self, keys, platforms, scroll):
        if self.dead:
            return
        if self.mode == "cube":
            self.update_cube()
            self.resolve_platforms(platforms, scroll)
        elif self.mode == "wave":
            self.update_wave(keys)
        else:
            self.update_ship(keys)

    def draw(self):
        if self.mode == "cube":
            r = self.rect_cube()
            surf = pygame.Surface((CUBE_SIZE, CUBE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(surf, PLAYER_CLR, (0, 0, CUBE_SIZE, CUBE_SIZE), border_radius=6)
            pygame.draw.rect(surf, OUTLINE, (0, 0, CUBE_SIZE, CUBE_SIZE), 3, border_radius=6)
            rotated = pygame.transform.rotate(surf, -self.rot)
            rr = rotated.get_rect(center=r.center)
            screen.blit(rotated, rr.topleft)
        elif self.mode == "wave":
            hb = self.rect_wave()
            pts = [(hb.left, hb.bottom), (hb.right, hb.centery), (hb.left, hb.top)]
            pygame.draw.polygon(screen, PLAYER_CLR, pts)
            pygame.draw.polygon(screen, OUTLINE, pts, 2)
        else:
            hb = self.rect_ship()
            # tiny ship triangle
            pts = [(hb.left, hb.centery), (hb.right, hb.top), (hb.right, hb.bottom)]
            pygame.draw.polygon(screen, PLAYER_CLR, pts)
            pygame.draw.polygon(screen, OUTLINE, pts, 2)

def find_item_at_mouse(items, mx, my, scroll):
    # return index of topmost item under cursor
    for i in range(len(items) - 1, -1, -1):
        r = item_hitbox(items[i], scroll)
        if r.collidepoint(mx, my):
            return i
    return None

def hud_editor(selected_tool, size_w, size_h, scroll):
    tools = [
        "1 Spike",
        "2 Block(Hazard)",
        "3 Platform(Solid)",
        "4 Portal->Wave",
        "5 Portal->Cube",
        "6 Portal->Ship",
        "7 WaveBlock(Hazard)",
    ]
    y = 10
    title = big.render("EDITOR", True, TEXT)
    screen.blit(title, (10, y))
    y += 40

    info = font.render(f"Tool: {selected_tool}   Size: {size_w}x{size_h}   Scroll: {int(scroll)}", True, TEXT)
    screen.blit(info, (10, y))
    y += 26

    hint = font.render("LMB place  |  RMB delete  |  Wheel / [ ] size  |  S save  L load  |  P play", True, (200, 210, 240))
    screen.blit(hint, (10, y))
    y += 30

    for line in tools:
        c = (210, 230, 255) if line.startswith(selected_tool[0]) else (180, 190, 205)
        screen.blit(font.render(line, True, c), (10, y))
        y += 22

def hud_play(mode, dist, dead=False):
    mode_s = font.render(f"Mode: {mode.upper()}", True, (210, 230, 255))
    d_s = font.render(f"Distance: {int(dist)}", True, TEXT)
    screen.blit(mode_s, (10, 10))
    screen.blit(d_s, (10, 34))
    hint = font.render("SPACE jump/thrust (cube jump only)  |  R restart  |  E back to editor", True, (200, 210, 240))
    screen.blit(hint, (10, 58))
    if dead:
        t = big.render("CRASH!  (R to restart)", True, SPIKE_CLR)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, 120))

def main():
    items = []  # list of dicts with world x coordinates

    mode = "editor"  # editor or play
    scroll = 0.0

    player = Player()
    distance = 0.0

    # editor tool state
    tool = "1 Spike"
    size_w, size_h = 120, 20  # platform/waveblock default
    waveblock_w, waveblock_h = 80, 80

    # camera scroll in editor
    editor_scroll = 0.0
    editor_scroll_speed = 18.0

    def reset_play():
        nonlocal scroll, distance
        scroll = 0.0
        distance = 0.0
        player.reset()

    while True:
        dt = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # shared
                if event.key == pygame.K_s and mode == "editor":
                    save_level(items)
                if event.key == pygame.K_l and mode == "editor":
                    items = load_level()

                if event.key == pygame.K_p and mode == "editor":
                    mode = "play"
                    reset_play()

                if event.key == pygame.K_e and mode == "play":
                    mode = "editor"
                    # keep editor scroll near where you were
                    editor_scroll = scroll

                if event.key == pygame.K_r and mode == "play":
                    reset_play()

                # tool selection
                if mode == "editor":
                    if event.key == pygame.K_1: tool = "1 Spike"
                    if event.key == pygame.K_2: tool = "2 Block(Hazard)"
                    if event.key == pygame.K_3: tool = "3 Platform(Solid)"
                    if event.key == pygame.K_4: tool = "4 Portal->Wave"
                    if event.key == pygame.K_5: tool = "5 Portal->Cube"
                    if event.key == pygame.K_6: tool = "6 Portal->Ship"
                    if event.key == pygame.K_7: tool = "7 WaveBlock(Hazard)"

                    if event.key == pygame.K_LEFTBRACKET:
                        size_w = max(40, size_w - 40)
                        size_h = max(20, size_h - 10)
                        waveblock_w = max(40, waveblock_w - 20)
                        waveblock_h = max(40, waveblock_h - 20)
                    if event.key == pygame.K_RIGHTBRACKET:
                        size_w = min(360, size_w + 40)
                        size_h = min(80, size_h + 10)
                        waveblock_w = min(240, waveblock_w + 20)
                        waveblock_h = min(240, waveblock_h + 20)

            if event.type == pygame.MOUSEWHEEL and mode == "editor":
                if event.y > 0:
                    size_w = min(360, size_w + 40)
                    size_h = min(80, size_h + 10)
                    waveblock_w = min(240, waveblock_w + 20)
                    waveblock_h = min(240, waveblock_h + 20)
                else:
                    size_w = max(40, size_w - 40)
                    size_h = max(20, size_h - 10)
                    waveblock_w = max(40, waveblock_w - 20)
                    waveblock_h = max(40, waveblock_h - 20)

            if event.type == pygame.MOUSEBUTTONDOWN and mode == "editor":
                mx, my = pygame.mouse.get_pos()
                # right click delete
                if event.button == 3:
                    idx = find_item_at_mouse(items, mx, my, editor_scroll)
                    if idx is not None:
                        items.pop(idx)
                # left click place
                if event.button == 1:
                    # world position (snap X to grid)
                    xw = snap(mx + editor_scroll, GRID)
                    # place type based on tool
                    if tool.startswith("1"):
                        items.append({"type": "spike", "x": xw})
                    elif tool.startswith("2"):
                        items.append({"type": "block", "x": xw})
                    elif tool.startswith("3"):
                        # platform at mouse Y (snap to grid)
                        top_y = snap(my, GRID)
                        items.append({"type": "platform", "x": xw, "top_y": top_y, "w": size_w, "h": size_h})
                    elif tool.startswith("4"):
                        items.append({"type": "portal_wave", "x": xw})
                    elif tool.startswith("5"):
                        items.append({"type": "portal_cube", "x": xw})
                    elif tool.startswith("6"):
                        items.append({"type": "portal_ship", "x": xw})
                    elif tool.startswith("7"):
                        y = snap(my, GRID)
                        items.append({"type": "wave_block", "x": xw, "y": y, "w": waveblock_w, "h": waveblock_h})

                    # keep deterministic order by x (nice for play)
                    items.sort(key=lambda it: (it["x"], it["type"]))

        # --- update ---
        if mode == "editor":
            # editor camera movement
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                editor_scroll = max(0.0, editor_scroll - editor_scroll_speed)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                editor_scroll += editor_scroll_speed

        else:
            if not player.dead:
                scroll += SCROLL_SPEED
                distance += SCROLL_SPEED * 0.35

                platforms = [it for it in items if it["type"] == "platform"]
                player.update(keys, platforms, scroll)

                # collisions + portals
                # screen hitboxes are built with scroll
                if player.mode == "cube":
                    pr = player.rect_cube()
                    for it in items:
                        t = it["type"]
                        if t == "platform":
                            continue
                        if t == "wave_block":
                            continue
                        r = item_hitbox(it, scroll)
                        if r.right < -120 or r.left > WIDTH + 120:
                            continue
                        if pr.colliderect(r):
                            if t == "portal_wave":
                                player.switch_mode("wave")
                            elif t == "portal_cube":
                                player.switch_mode("cube")
                            elif t == "portal_ship":
                                player.switch_mode("ship")
                            elif t in ("spike", "block"):
                                player.dead = True
                                break

                elif player.mode == "wave":
                    hb = player.rect_wave()
                    # bounds
                    if hb.top <= 0 or hb.bottom >= HEIGHT:
                        player.dead = True
                    # hazards
                    if not player.dead:
                        for it in items:
                            if it["type"] == "wave_block":
                                r = item_hitbox(it, scroll)
                                if r.right < -120 or r.left > WIDTH + 120:
                                    continue
                                if hb.colliderect(r):
                                    player.dead = True
                                    break
                            elif it["type"].startswith("portal_"):
                                r = item_hitbox(it, scroll)
                                if hb.colliderect(r):
                                    if it["type"] == "portal_wave":
                                        player.switch_mode("wave")
                                    elif it["type"] == "portal_cube":
                                        player.switch_mode("cube")
                                    elif it["type"] == "portal_ship":
                                        player.switch_mode("ship")

                else:  # ship
                    hb = player.rect_ship()
                    # bounds
                    if hb.top <= 0 or hb.bottom >= HEIGHT:
                        player.dead = True
                    # hazards
                    if not player.dead:
                        for it in items:
                            if it["type"] == "wave_block":
                                r = item_hitbox(it, scroll)
                                if r.right < -120 or r.left > WIDTH + 120:
                                    continue
                                if hb.colliderect(r):
                                    player.dead = True
                                    break
                            elif it["type"].startswith("portal_"):
                                r = item_hitbox(it, scroll)
                                if hb.colliderect(r):
                                    if it["type"] == "portal_wave":
                                        player.switch_mode("wave")
                                    elif it["type"] == "portal_cube":
                                        player.switch_mode("cube")
                                    elif it["type"] == "portal_ship":
                                        player.switch_mode("ship")

            # cube jump input (on key down is nicer, but this works)
            if player.mode == "cube" and keys[pygame.K_SPACE] and not player.dead:
                # only jump if grounded; we won't spam due to grounded check
                player.jump()

        # --- draw ---
        screen.fill(BG)

        if mode == "editor":
            draw_grid(editor_scroll)
            draw_ground()

            # draw all items
            for it in items:
                draw_item(it, editor_scroll, editor=True)

            # ghost preview placement
            mx, my = pygame.mouse.get_pos()
            preview_xw = snap(mx + editor_scroll, GRID)
            preview_xs = int(world_to_screen_x(preview_xw, editor_scroll))

            # show preview differently per tool
            if tool.startswith("1"):
                r = rect_from_bottom_world(preview_xs, GROUND_Y, 34, 34)
                pygame.draw.polygon(screen, SPIKE_CLR, spike_points(r))
                pygame.draw.polygon(screen, (255, 255, 255), spike_points(r), 2)
            elif tool.startswith("2"):
                r = rect_from_bottom_world(preview_xs, GROUND_Y, 44, 44)
                pygame.draw.rect(screen, BLOCK_CLR, r, border_radius=6)
                pygame.draw.rect(screen, (255, 255, 255), r, 2, border_radius=6)
            elif tool.startswith("3"):
                top_y = snap(my, GRID)
                r = pygame.Rect(preview_xs, int(top_y), int(size_w), int(size_h))
                pygame.draw.rect(screen, PLATFORM_CLR, r, border_radius=8)
                pygame.draw.rect(screen, (255, 255, 255), r, 2, border_radius=8)
            elif tool.startswith("4"):
                r = make_portal_rect(preview_xs, "portal_wave")
                pygame.draw.rect(screen, PORTAL_WAVE_CLR, r, border_radius=10)
                pygame.draw.rect(screen, (255, 255, 255), r, 2, border_radius=10)
            elif tool.startswith("5"):
                r = make_portal_rect(preview_xs, "portal_cube")
                pygame.draw.rect(screen, PORTAL_CUBE_CLR, r, border_radius=10)
                pygame.draw.rect(screen, (255, 255, 255), r, 2, border_radius=10)
            elif tool.startswith("6"):
                r = make_portal_rect(preview_xs, "portal_ship")
                pygame.draw.rect(screen, PORTAL_SHIP_CLR, r, border_radius=10)
                pygame.draw.rect(screen, (255, 255, 255), r, 2, border_radius=10)
            elif tool.startswith("7"):
                y = snap(my, GRID)
                r = pygame.Rect(preview_xs, int(y), int(waveblock_w), int(waveblock_h))
                pygame.draw.rect(screen, WAVEBLOCK_CLR, r, border_radius=10)
                pygame.draw.rect(screen, (255, 255, 255), r, 2, border_radius=10)

            hud_editor(tool, size_w if not tool.startswith("7") else waveblock_w,
                       size_h if not tool.startswith("7") else waveblock_h,
                       editor_scroll)

        else:
            draw_grid(scroll)
            draw_ground()

            # draw items
            for it in items:
                draw_item(it, scroll, editor=False)

            # draw player
            player.draw()
            hud_play(player.mode, distance, dead=player.dead)

        pygame.display.flip()

if __name__ == "__main__":
    main()
