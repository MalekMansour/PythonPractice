import pygame
import random
import sys
from copy import deepcopy

# -----------------------------
# Sudoku utilities
# -----------------------------
def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def is_valid(board, r, c, val):
    # row
    for x in range(9):
        if board[r][x] == val:
            return False
    # col
    for x in range(9):
        if board[x][c] == val:
            return False
    # box
    br = (r // 3) * 3
    bc = (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if board[rr][cc] == val:
                return False
    return True

def solve_backtracking(board):
    empty = find_empty(board)
    if not empty:
        return True
    r, c = empty
    nums = list(range(1, 10))
    random.shuffle(nums)
    for val in nums:
        if is_valid(board, r, c, val):
            board[r][c] = val
            if solve_backtracking(board):
                return True
            board[r][c] = 0
    return False

def generate_full_solution():
    board = [[0]*9 for _ in range(9)]
    solve_backtracking(board)
    return board

def count_solutions(board, limit=2):
    # count up to limit solutions (for uniqueness checking)
    empty = find_empty(board)
    if not empty:
        return 1
    r, c = empty
    total = 0
    for val in range(1, 10):
        if is_valid(board, r, c, val):
            board[r][c] = val
            total += count_solutions(board, limit)
            if total >= limit:
                board[r][c] = 0
                return total
            board[r][c] = 0
    return total

def make_puzzle(solution, clues=32):
    # Start from solution and remove numbers while keeping uniqueness (best effort).
    puzzle = deepcopy(solution)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    to_remove = 81 - clues
    removed = 0

    for (r, c) in cells:
        if removed >= to_remove:
            break
        if puzzle[r][c] == 0:
            continue
        backup = puzzle[r][c]
        puzzle[r][c] = 0

        test = deepcopy(puzzle)
        sol_count = count_solutions(test, limit=2)
        if sol_count != 1:
            puzzle[r][c] = backup
        else:
            removed += 1

    return puzzle

def board_complete_and_valid(board):
    for r in range(9):
        for c in range(9):
            val = board[r][c]
            if val == 0:
                return False
            # Temporarily clear to validate against itself
            board[r][c] = 0
            ok = is_valid(board, r, c, val)
            board[r][c] = val
            if not ok:
                return False
    return True

# -----------------------------
# Pygame UI
# -----------------------------
WIDTH, HEIGHT = 720, 820
GRID_SIZE = 630
MARGIN_X = (WIDTH - GRID_SIZE) // 2
MARGIN_Y = 140
CELL = GRID_SIZE // 9

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku (Pygame)")
clock = pygame.time.Clock()

FONT_BIG = pygame.font.SysFont("consolas", 44, bold=True)
FONT_NUM = pygame.font.SysFont("consolas", 36, bold=True)
FONT_SMALL = pygame.font.SysFont("consolas", 18)
FONT_NOTE = pygame.font.SysFont("consolas", 16)

def draw_button(rect, label, enabled=True):
    x, y, w, h = rect
    col = (40, 40, 45) if enabled else (60, 60, 65)
    pygame.draw.rect(screen, col, rect, border_radius=10)
    pygame.draw.rect(screen, (120, 120, 130), rect, 2, border_radius=10)
    text = FONT_SMALL.render(label, True, (235, 235, 240) if enabled else (180, 180, 190))
    screen.blit(text, (x + (w - text.get_width())//2, y + (h - text.get_height())//2))

def new_game(clues=32):
    sol = generate_full_solution()
    puzzle = make_puzzle(sol, clues=clues)
    given = [[puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
    notes = [[set() for _ in range(9)] for _ in range(9)]
    return puzzle, sol, given, notes

# Buttons
BTN_NEW = pygame.Rect(40, 40, 160, 48)
BTN_SOLVE = pygame.Rect(220, 40, 160, 48)
BTN_RESET = pygame.Rect(400, 40, 160, 48)
BTN_DIFFICULTY = pygame.Rect(580, 40, 100, 48)

DIFFS = [("Easy", 40), ("Med", 32), ("Hard", 26)]
diff_idx = 1  # default Medium

puzzle, solution, given, notes = new_game(clues=DIFFS[diff_idx][1])
initial_puzzle = deepcopy(puzzle)

selected = None  # (r, c)
notes_mode = False
mistakes = 0
message = ""

def reset_to_initial():
    global puzzle, notes, mistakes, message
    puzzle = deepcopy(initial_puzzle)
    notes = [[set() for _ in range(9)] for _ in range(9)]
    mistakes = 0
    message = ""

def cell_from_mouse(pos):
    mx, my = pos
    if mx < MARGIN_X or mx >= MARGIN_X + GRID_SIZE:
        return None
    if my < MARGIN_Y or my >= MARGIN_Y + GRID_SIZE:
        return None
    c = (mx - MARGIN_X) // CELL
    r = (my - MARGIN_Y) // CELL
    return int(r), int(c)

def draw():
    screen.fill((18, 18, 22))

    # Top bar text
    title = FONT_BIG.render("SUDOKU", True, (245, 245, 250))
    screen.blit(title, (MARGIN_X, 92 - title.get_height()//2))

    info = f"Notes: {'ON' if notes_mode else 'OFF'}   Mistakes: {mistakes}"
    inf_t = FONT_SMALL.render(info, True, (210, 210, 220))
    screen.blit(inf_t, (MARGIN_X + 260, 92 - inf_t.get_height()//2))

    # Buttons
    draw_button(BTN_NEW, "New (N)")
    draw_button(BTN_SOLVE, "Solve (S)")
    draw_button(BTN_RESET, "Reset")
    draw_button(BTN_DIFFICULTY, DIFFS[diff_idx][0])

    # Message
    if message:
        msg = FONT_SMALL.render(message, True, (230, 200, 120))
        screen.blit(msg, (MARGIN_X, 120))

    # Selected highlight
    if selected:
        sr, sc = selected
        # row/col highlight
        for i in range(9):
            rr = pygame.Rect(MARGIN_X + i*CELL, MARGIN_Y + sr*CELL, CELL, CELL)
            cc = pygame.Rect(MARGIN_X + sc*CELL, MARGIN_Y + i*CELL, CELL, CELL)
            pygame.draw.rect(screen, (26, 28, 38), rr)
            pygame.draw.rect(screen, (26, 28, 38), cc)

        # 3x3 box highlight
        br = (sr // 3) * 3
        bc = (sc // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                rect = pygame.Rect(MARGIN_X + c*CELL, MARGIN_Y + r*CELL, CELL, CELL)
                pygame.draw.rect(screen, (24, 26, 34), rect)

        # selected cell highlight
        rect = pygame.Rect(MARGIN_X + sc*CELL, MARGIN_Y + sr*CELL, CELL, CELL)
        pygame.draw.rect(screen, (40, 60, 95), rect)

    # Cells + numbers + notes
    for r in range(9):
        for c in range(9):
            x = MARGIN_X + c*CELL
            y = MARGIN_Y + r*CELL
            rect = pygame.Rect(x, y, CELL, CELL)

            # Cell border
            pygame.draw.rect(screen, (30, 30, 36), rect, 1)

            val = puzzle[r][c]
            if val != 0:
                # Color depending on given vs user
                col = (235, 235, 240) if given[r][c] else (130, 205, 255)
                # Wrong value hint (optional): show red tint if not matching solution
                if not given[r][c] and val != solution[r][c]:
                    col = (255, 130, 130)
                txt = FONT_NUM.render(str(val), True, col)
                screen.blit(txt, (x + (CELL - txt.get_width())//2, y + (CELL - txt.get_height())//2))
            else:
                # Notes (pencil marks)
                if notes[r][c]:
                    # layout 1..9 in a 3x3 mini-grid
                    for n in range(1, 10):
                        if n in notes[r][c]:
                            nr = (n - 1) // 3
                            nc = (n - 1) % 3
                            nt = FONT_NOTE.render(str(n), True, (170, 170, 180))
                            screen.blit(nt, (x + 8 + nc*20, y + 6 + nr*18))

    # Thick grid lines
    for i in range(10):
        thickness = 4 if i % 3 == 0 else 1
        # vertical
        pygame.draw.line(
            screen, (200, 200, 210),
            (MARGIN_X + i*CELL, MARGIN_Y),
            (MARGIN_X + i*CELL, MARGIN_Y + GRID_SIZE),
            thickness
        )
        # horizontal
        pygame.draw.line(
            screen, (200, 200, 210),
            (MARGIN_X, MARGIN_Y + i*CELL),
            (MARGIN_X + GRID_SIZE, MARGIN_Y + i*CELL),
            thickness
        )

    # Win banner
    if board_complete_and_valid(deepcopy(puzzle)):
        win = FONT_BIG.render("YOU WIN!", True, (170, 255, 180))
        pygame.draw.rect(screen, (12, 12, 16), (MARGIN_X, MARGIN_Y + GRID_SIZE + 20, GRID_SIZE, 60), border_radius=12)
        pygame.draw.rect(screen, (90, 200, 120), (MARGIN_X, MARGIN_Y + GRID_SIZE + 20, GRID_SIZE, 60), 2, border_radius=12)
        screen.blit(win, (MARGIN_X + (GRID_SIZE-win.get_width())//2, MARGIN_Y + GRID_SIZE + 28))

    pygame.display.flip()

def place_number(n):
    global mistakes, message
    if not selected:
        return
    r, c = selected
    if given[r][c]:
        return

    if notes_mode:
        if n in notes[r][c]:
            notes[r][c].remove(n)
        else:
            notes[r][c].add(n)
        return

    puzzle[r][c] = n
    notes[r][c].clear()

    if n != solution[r][c]:
        mistakes += 1
        message = "Wrong number!"
    else:
        message = ""

def clear_cell():
    global message
    if not selected:
        return
    r, c = selected
    if given[r][c]:
        return
    if notes_mode:
        notes[r][c].clear()
    else:
        puzzle[r][c] = 0
        notes[r][c].clear()
    message = ""

def solve_current():
    global puzzle, message
    puzzle = deepcopy(solution)
    message = "Solved."

# -----------------------------
# Main loop
# -----------------------------
while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if BTN_NEW.collidepoint(pos):
                puzzle, solution, given, notes = new_game(clues=DIFFS[diff_idx][1])
                initial_puzzle = deepcopy(puzzle)
                selected = None
                mistakes = 0
                message = ""
            elif BTN_SOLVE.collidepoint(pos):
                solve_current()
            elif BTN_RESET.collidepoint(pos):
                reset_to_initial()
            elif BTN_DIFFICULTY.collidepoint(pos):
                diff_idx = (diff_idx + 1) % len(DIFFS)
                puzzle, solution, given, notes = new_game(clues=DIFFS[diff_idx][1])
                initial_puzzle = deepcopy(puzzle)
                selected = None
                mistakes = 0
                message = ""
            else:
                cell = cell_from_mouse(pos)
                if cell:
                    selected = cell

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                puzzle, solution, given, notes = new_game(clues=DIFFS[diff_idx][1])
                initial_puzzle = deepcopy(puzzle)
                selected = None
                mistakes = 0
                message = ""
            elif event.key == pygame.K_s:
                solve_current()
            elif event.key == pygame.K_SPACE:
                notes_mode = not notes_mode
                message = "Notes mode ON" if notes_mode else "Notes mode OFF"
            elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                clear_cell()
            else:
                # number keys
                if pygame.K_1 <= event.key <= pygame.K_9:
                    n = event.key - pygame.K_0
                    place_number(n)
                elif pygame.K_KP1 <= event.key <= pygame.K_KP9:
                    n = event.key - pygame.K_KP0
                    place_number(n)

    draw()
