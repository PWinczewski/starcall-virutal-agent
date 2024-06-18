import pygame
import functions_starcall as func
import os

surface_width = 160
surface_height = 240
window_scale = 4
surface = pygame.Surface((surface_width, surface_height))
window_size = (surface_width * window_scale, surface_height * window_scale)

window = pygame.display.set_mode(window_size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
pygame.display.set_caption("StarCall")

pygame.font.init()

# Sprites
spr_PLAYER_IDLE = pygame.image.load(os.path.join("starcall/assets", "player", "protagonist_slowfall.png"))
spr_PLAYER_DOWN = pygame.image.load(os.path.join("starcall/assets", "player", "protagonist_freefall.png"))

spr_ROOM_WALL = pygame.image.load(os.path.join("starcall/assets", "room", "cloud_tile.png"))
spr_ENEMY_EYEBAT = func.load_animation_sprites(os.path.join("starcall/assets", "enemies", "EyeBat"), "EyeBat", 5)


# colors
col_BACKGROUND = (50, 61, 127)
col_WHITE = (255, 255, 255)
col_RED = (255, 0, 0)

# fonts
font_PRIMARY = pygame.font.Font(os.path.join("starcall/assets", "fonts", "visitor1.ttf"), 12)
font_PRIMARY_BIG = pygame.font.Font(os.path.join("starcall/assets", "fonts", "visitor1.ttf"), 24)

# Constants
LEFT = -1
RIGHT = 1
UP = -1
DOWN = 1
TILE_SIZE = 16

# Menu


# Game initialization variables
scroll_speed = 1
enemy_spawn_chance = 0.1
upwards_draft_strength = 3
stable_altitude = 50
gravity = 0.05

enemies = []
walls = []
particles = []
target_enemy_count_start = 3
target_enemy_count = target_enemy_count_start