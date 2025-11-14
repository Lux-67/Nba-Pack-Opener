import pygame
import json
import random
import os

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NBA Pack Opener")

font = pygame.font.SysFont("Arial", 24)

# -----------------------------
# LOAD PLAYER DATABASE
# -----------------------------
with open("data/players.json", "r") as f:
    PLAYERS = json.load(f)

RARITY_COLORS = {
    "Common": (160, 160, 160),
    "Uncommon": (80, 200, 120),
    "Rare": (50, 150, 255),
    "Epic": (170, 50, 255),
    "Legendary": (255, 215, 0)
}

RARITY_ANIM_STRENGTH = {
    "Common": 20,
    "Uncommon": 35,
    "Rare": 50,
    "Epic": 70,
    "Legendary": 90
}

PACKS = [
    {"name": "Bronze Pack", "cost": 100, "weights": {"Common": 80, "Uncommon": 15, "Rare": 5}},
    {"name": "Silver Pack", "cost": 250, "weights": {"Common": 60, "Uncommon": 30, "Rare": 10}},
    {"name": "Gold Pack", "cost": 500, "weights": {"Uncommon": 50, "Rare": 35, "Epic": 15}},
    {"name": "Diamond Pack", "cost": 1200, "weights": {"Rare": 40, "Epic": 40, "Legendary": 20}},
    {"name": "Galaxy Pack", "cost": 3000, "weights": {"Epic": 60, "Legendary": 40}}
]

# -----------------------------
# LOAD SAVE FILE
# -----------------------------
save_path = "data/save.json"

if os.path.exists(save_path):
    with open(save_path, "r") as f:
        SAVE = json.load(f)
else:
    SAVE = {"coins": 1000, "inventory": []}

# -----------------------------
# PARTICLE EFFECTS
# -----------------------------
particles = []

def spawn_particles(color, amount):
    for _ in range(amount):
        particles.append([
            WIDTH // 2, HEIGHT // 2,
            random.randint(-5, 5),
            random.randint(-5, 5),
            random.randint(5, 12),
            color
        ])

# -----------------------------
# DRAW PLAYER CARD
# -----------------------------
def draw_player_card(player):
    screen.fill((20, 20, 20))

    rarity = player["rarity"]
    color = RARITY_COLORS[rarity]

    # rectangle
    pygame.draw.rect(screen, color, (300, 120, 300, 360), border_radius=15)

    text = font.render(player["name"], True, (255, 255, 255))
    screen.blit(text, (330, 150))

    overall = font.render(f"OVR: {player['overall']}", True, (255, 255, 255))
    screen.blit(overall, (330, 200))

    rarity_text = font.render(f"Rarity: {player['rarity']}", True, color)
    screen.blit(rarity_text, (330, 250))

    pygame.display.update()

# -----------------------------
# PACK OPENING LOGIC
# -----------------------------
def choose_rarity(weights):
    rarity_pool = []
    for rarity, chance in weights.items():
        rarity_pool += [rarity] * chance
    return random.choice(rarity_pool)

def open_pack(pack):
    rarity = choose_rarity(pack["weights"])
    player = random.choice(PLAYERS[rarity])
    SAVE["inventory"].append(player)

    # particle animation
    spawn_particles(RARITY_COLORS[rarity], RARITY_ANIM_STRENGTH[rarity])

    return player

# -----------------------------
# SAVE PROGRESS
# -----------------------------
def save_game():
    with open(save_path, "w") as f:
        json.dump(SAVE, f, indent=4)

# -----------------------------
# MAIN LOOP
# -----------------------------
running = True
selected_player = None

clock = pygame.time.Clock()

while running:
    screen.fill((30, 30, 30))

    # draw coins
    coin_text = font.render(f"Coins: {SAVE['coins']}", True, (255, 255, 255))
    screen.blit(coin_text, (20, 20))

    # draw packs
    y = 100
    for pack in PACKS:
        text = font.render(f"{pack['name']} - {pack['cost']} coins", True, (255, 255, 255))
        screen.blit(text, (50, y))
        y += 50

    # update particles
    for p in particles:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 0.3
        if p[4] > 0:
            pygame.draw.circle(screen, p[5], (int(p[0]), int(p[1])), int(p[4]))
        else:
            particles.remove(p)

    # show pulled card
    if selected_player:
        draw_player_card(selected_player)

    pygame.display.update()

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y_click = event.pos

            # pack clicked?
            if 100 <= y_click <= 350:
                index = (y_click - 100) // 50
                if 0 <= index < len(PACKS):
                    pack = PACKS[index]

                    if SAVE["coins"] >= pack["cost"]:
                        SAVE["coins"] -= pack["cost"]
                        selected_player = open_pack(pack)
                        save_game()
                    else:
                        print("Not enough coins!")

    clock.tick(60)

pygame.quit()
