import os
import random
import time
import msvcrt

# =====================
# CONFIG
# =====================
width = 20
height = 20

player_icon = "🎅"
gift_icon = "🎁"
bomb_icon = "💣"
empty = "  "

fall_speed = 0.4
bomb_chance = 0.3
frame_delay = 0.08

# =====================
# GAME STATE
# =====================
player_x = width // 2
score = 0
lives = 3
combo = 0
max_combo = 0

falling_objects = []
num_objects = 6

# =====================
# HIGH SCORE
# =====================
HIGHSCORE_FILE = "highscore.txt"
if os.path.exists(HIGHSCORE_FILE):
    with open(HIGHSCORE_FILE, "r") as f:
        highscore = int(f.read().strip())
else:
    highscore = 0

# =====================
# UTIL
# =====================
# cursor-based rendering to prevent flickering (no full screen clear)
def move_cursor_top():
    print("\033[H", end="")

def spawn_object():
    return {
        "x": random.randint(0, width - 1),
        "y": 0,
        "type": bomb_icon if random.random() < bomb_chance else gift_icon
    }

def read_input():
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key in [b'\x00', b'\xe0']:
            key = msvcrt.getch()
            if key == b'K':
                return -1
            elif key == b'M':
                return 1
        elif key in [b'a', b'A']:
            return -1
        elif key in [b'd', b'D']:
            return 1
        elif key == b'\x1b':
            return 2
    return 0

def draw_frame():
    screen = [[empty for _ in range(width)] for _ in range(height)]

    for obj in falling_objects:
        x, y = int(obj["x"]), int(obj["y"])
        if 0 <= x < width and 0 <= y < height:
            screen[y][x] = obj["type"]

    screen[height - 1][player_x] = player_icon

    hud = f" SCORE:{score}  COMBO:{combo}  LIVES:{lives}  BEST:{highscore}"
    hud = hud.ljust(width * 2)

    print(hud)
    for row in screen:
        print("".join(row))

def bomb_feedback_inline():
    pass

# =====================
# MAIN LOOP
# =====================
def main():
    global player_x, score, lives, combo, max_combo
    global falling_objects, fall_speed, bomb_chance, num_objects
    global highscore

    os.system("cls")
    print("🎄 GIFT CATCHER 🎄")
    print("← → or A/D | ESC to quit")
    time.sleep(2)

    # reserve fixed screen space so each frame fully overwrites the previous one
    move_cursor_top()
    print("\n" * (height + 2))

    falling_objects[:] = [spawn_object() for _ in range(num_objects)]
    frame_count = 0

    while lives > 0:
        move_cursor_top()

        # input
        inp = read_input()
        if inp == -1:
            player_x = max(0, player_x - 1)
        elif inp == 1:
            player_x = min(width - 1, player_x + 1)
        elif inp == 2:
            break

        # update objects
        for obj in falling_objects:
            obj["y"] += fall_speed

            if obj["y"] >= height - 1:
                hit = abs(int(obj["x"]) - player_x) <= 1

                if hit:
                    if obj["type"] == gift_icon:
                        combo += 1
                        score += 1 + combo // 3
                        max_combo = max(max_combo, combo)
                    else:
                        lives -= 1
                        combo = 0
                else:
                    combo = 0

                obj.update(spawn_object())

        # difficulty scaling
        if frame_count % 50 == 0:
            fall_speed = min(1.2, fall_speed + 0.03)
            bomb_chance = min(0.4, bomb_chance + 0.01)
            if num_objects < 10:
                falling_objects.append(spawn_object())
                num_objects += 1

        draw_frame()
        frame_count += 1
        time.sleep(frame_delay)

    move_cursor_top()
    print("🎮 GAME OVER 🎮".ljust(width * 2))
    print(f"Final Score: {score}".ljust(width * 2))
    print(f"Max Combo: {max_combo}".ljust(width * 2))

    if score > highscore:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
        print("🏆 NEW HIGH SCORE!".ljust(width * 2))

    time.sleep(3)

# =====================
# RUN
# =====================
if __name__ == "__main__":
    main()
