import os
import time
import pygame
import numpy as np
from classes import *
from functions_starcall import *

import tensorflow as tf
from tensorflow.keras import layers, models

class GameEnv():
    def __init__(self):
        pygame.init()

        self.enemy_spawn_timer = 100
        self.enemy_spawn_countdown = 0
        self.enemy_spawner = 0

        self.surface_width = 160
        self.surface_height = 240
        self.window_scale = 4
        self.surface = pygame.Surface((self.surface_width, self.surface_height))
        self.window_size = (self.surface_width * self.window_scale, self.surface_height * self.window_scale)

        self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED)
        pygame.display.set_caption("StarCall")

        pygame.font.init()

        # Sprites
        self.spr_PLAYER_IDLE = pygame.image.load(os.path.join("starcall/assets", "player", "protagonist_slowfall.png"))
        self.spr_PLAYER_DOWN = pygame.image.load(os.path.join("starcall/assets", "player", "protagonist_freefall.png"))

        self.spr_ROOM_WALL = pygame.image.load(os.path.join("starcall/assets", "room", "cloud_tile.png"))
        self.spr_ENEMY_EYEBAT = load_animation_sprites(os.path.join("starcall/assets", "enemies", "EyeBat"), "EyeBat", 5)

        # colors
        self.col_BACKGROUND = (50, 61, 127)
        self.col_WHITE = (255, 255, 255)
        self.col_RED = (255, 0, 0)
        self.col_GREEN = (0, 255, 0)

        # fonts
        self.font_PRIMARY = pygame.font.Font(os.path.join("starcall/assets", "fonts", "visitor1.ttf"), 12)
        self.font_PRIMARY_BIG = pygame.font.Font(os.path.join("starcall/assets", "fonts", "visitor1.ttf"), 24)

        # Constants
        self.LEFT = -1
        self.RIGHT = 1
        self.UP = -1
        self.DOWN = 1
        self.TILE_SIZE = 16

        # Game initialization variables
        self.scroll_speed = 1
        self.upwards_draft_strength = 3
        self.stable_altitude = 50
        self.gravity = 0.05

        self.enemies = []
        self.walls = []
        self.max_enemies = 4

        self.running = True
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.current_reward = 0
        
        self.reset()

    def reset(self):
        self.player = Player(surface_width/2, stable_altitude)
        self.safe_distance = self.player.hitbox[2] * 6
        self.consideration_distance = self.safe_distance * 3
        self.done = False

        self.score = 0
        # self.enemy_spawn_countdown = 0
        # self.enemy_spawner = 0

        self.walls = []
        self.enemies = []

        for i in range(int(surface_height / TILE_SIZE) + 1):
            wall = Wall(0, TILE_SIZE * i)
            wall2 = Wall(surface_width, TILE_SIZE * i)
            self.walls.append(wall)
            self.walls.append(wall2)
        return self._get_state()

    def _get_state(self):
        player_coords = np.array([self.player.x, self.player.y])
        enemies_coords = np.array([[enemy.x, enemy.y] if not enemy.dead else [0,0] for enemy in self.enemies]).flatten()
        state = np.concatenate((player_coords, enemies_coords))
        while len(state) < 2+self.max_enemies*2:
            state = np.concatenate((state, [0,0]))
        return state / self.surface_height

    # def calculate_reward(self, action):
    #     player_coords = np.array([self.player.x, self.player.y])
    #     total_reward = 0

    #     for enemy in self.enemies:
    #         if enemy.dead:
    #             continue
    #         enemy_coords = np.array([enemy.x, enemy.y])
    #         distance = np.linalg.norm(player_coords - enemy_coords)

    #         if distance < self.player.hitbox[-1]*6:
    #             if enemy_coords[1] > player_coords[1]-(self.player.hitbox[-1]*4) and enemy_coords[1]-(player_coords[1]+(self.player.hitbox[-1]*4)) < 0 :
    #                 total_reward += 2*(distance/(self.player.hitbox[-1]*6)) if action[1] != 1 else -(distance/(self.player.hitbox[-1]*6))+1
    #             elif player_coords[0] >= enemy_coords[0]-5 and player_coords[0] <= enemy_coords[0]+5 and enemy_coords[1]>player_coords[1] and action[1] == 1:
    #                 total_reward += 3
    #             else:
    #                 total_reward -= 1-(distance/(self.player.hitbox[-1]*6))


    #     if (self.middle_x - self.middle_region_width / 2 <= player_coords[0] <= self.middle_x + self.middle_region_width / 2 and
    #         self.middle_y - self.middle_region_height / 2 <= player_coords[1] <= self.middle_y + self.middle_region_height / 2):
    #         total_reward += 0.5


    #     total_reward += 1 * target_enemy_count-len(enemies)
    #     return total_reward


    # def calculate_reward(self, action):
    #     player_coords = np.array([self.player.x, self.player.y])
    #     total_reward = 0 # still alive reward

    #     if self.player.vspd != 0 or self.player.hspd != 0:
    #         total_reward+=10

    #     if player_coords[1] > self.surface_height*0.75:
    #         total_reward-= (player_coords[1]/(self.surface_height*0.75)) * 10
    #     if player_coords[0] > self.surface_width - 3 * self.TILE_SIZE:
    #         total_reward -= (1 - (self.surface_width - player_coords[0]) / (3 * self.TILE_SIZE)) * 10
    #     if player_coords[0] < 3 * self.TILE_SIZE:
    #         total_reward -= (1 - player_coords[0] / (3 * self.TILE_SIZE)) * 10


    #     # Calculate penalties for each enemy
    #     for enemy in self.enemies:
    #         if enemy.dead or enemy.y < self.stable_altitude-self.TILE_SIZE:
    #             continue

    #         enemy_coords = np.array([enemy.x, enemy.y])
    #         distance_horizontal = np.abs(player_coords[0] - enemy_coords[0])
    #         distance_vertical = np.abs(player_coords[1] - enemy_coords[1])
    #         distance = np.linalg.norm(player_coords - enemy_coords)

    #         if distance < self.safe_distance:
    #             if distance_vertical > self.safe_distance*0.75 and distance_horizontal <= 5:
    #                 total_reward += 5
    #                 if action[1]==1:
    #                     total_reward += 5

    #             else:
    #                 total_reward -= (np.exp(4 * (1 - (distance / self.safe_distance))) - 1)

    #         elif distance < self.consideration_distance and enemy_coords[1] > player_coords[1]:
    #             total_reward += (self.safe_distance - distance_horizontal) / self.safe_distance if distance_vertical > self.safe_distance else -((self.safe_distance - distance_horizontal) / self.safe_distance)
    #         elif distance < self.consideration_distance:
    #             total_reward -= (self.safe_distance - distance_horizontal) / self.safe_distance if distance_vertical > self.safe_distance else -((self.safe_distance - distance_horizontal) / self.safe_distance)
    #     return total_reward

    def calculate_reward(self, action):
        player_coords = np.array([self.player.x, self.player.y])
        total_reward = 0 

        if self.player.vspd != 0 or self.player.hspd != 0:
            total_reward += 5

        if player_coords[1] > self.surface_height * 0.75:
            total_reward -= (player_coords[1] / (self.surface_height * 0.75)) * 10

        if player_coords[0] > self.surface_width - 5 * self.TILE_SIZE:
            total_reward -= (1 - (self.surface_width - player_coords[0]) / (5 * self.TILE_SIZE)) * 10
        if player_coords[0] < 5 * self.TILE_SIZE:
            total_reward -= (1 - player_coords[0] / (5 * self.TILE_SIZE)) * 10

        for enemy in self.enemies:
            if enemy.dead or enemy.y < self.stable_altitude - self.TILE_SIZE:
                continue

            enemy_coords = np.array([enemy.x, enemy.y])
            distance_horizontal = np.abs(player_coords[0] - enemy_coords[0])
            distance_vertical = np.abs(player_coords[1] - enemy_coords[1])

            penalty = (self.surface_width - distance_horizontal) / self.surface_width * (1 / (distance_vertical + 1))
            total_reward -= penalty

        return total_reward

    def step(self, action):
        global running
        reward = 0

        if not self.player.dead:
            self.score += 1

            reward = self.calculate_reward(action)

            if action[0]==1:
                self.player.accelerate_horizontally(LEFT)
            if action[0]==2:
                self.player.accelerate_horizontally(RIGHT)
            if action[1]==1:
                self.player.accelerate_vertically(DOWN)
                self.player.change_sprite(spr_PLAYER_DOWN)
                self.player.hitbox_attack_rect = self.player.update_hitbox_rect(self.player.hitbox_attack)
            else:
                self.player.accelerate_vertically(UP)

                self.player.change_sprite(spr_PLAYER_IDLE)
                self.player.hitbox_attack_rect = None

            if action==(0,0):
                if self.player.hspd != 0:
                    self.player.hspd = approach(self.player.hspd, 0, self.player.horizontal_resistance)
                if self.player.angle != 0:
                    self.player.angle = approach(self.player.angle, 0, self.player.rotation_spd)

            self.player.move_and_collide()

            self.player.hitbox_rect = self.player.update_hitbox_rect(self.player.hitbox)

        for wall in self.walls[:]:
            wall.move()

        for enemy in self.enemies[:]:
            enemy.move_and_collide()
            if not enemy.dead:
                if enemy.y <= -TILE_SIZE:
                    self.enemies.remove(enemy)
                enemy.animate()
                enemy.hitbox_rect = enemy.update_hitbox_rect(enemy.hitbox)
                if not self.player.dead and self.player.hitbox_attack_rect is not None:
                    if enemy.hitbox_rect.colliderect(self.player.hitbox_attack_rect):
                        enemy.dead = True
                        enemy.vspd *= 2
                        self.player.vspd -= 6
                        reward += 10

                if enemy.hitbox_rect.colliderect(self.player.hitbox_rect) and not self.player.dead:
                    self.player.dead = True
                    reward -= 25
            else:
                enemy.hitbox_rect = enemy.update_hitbox_rect(enemy.hitbox)
                if outside_surface(surface, enemy):
                    self.enemies.remove(enemy)

        if self.enemy_spawn_countdown <= 0 and len(self.enemies)<self.max_enemies:
            spawn_locations = [self.TILE_SIZE, surface_width-self.TILE_SIZE, (surface_width-self.TILE_SIZE)*0.5, (surface_width-self.TILE_SIZE)*0.25, (surface_width-self.TILE_SIZE)*0.75, (surface_width-self.TILE_SIZE)*0.125, (surface_width-self.TILE_SIZE)*0.375, (surface_width-self.TILE_SIZE)*0.625, (surface_width-self.TILE_SIZE)*0.875]
            facing = [self.LEFT, self.RIGHT]
            enemy = Enemy(spawn_locations[self.enemy_spawner%len(spawn_locations)], self.surface_height-1+self.TILE_SIZE, facing[self.enemy_spawner%2])
            self.enemy_spawn_countdown = self.enemy_spawn_timer
            self.enemy_spawner += 1
            self.enemies.append(enemy)
        else:
            self.enemy_spawn_countdown -= 1 

        if self.player.dead:
            self.done = True
        self.current_reward = reward
        return self._get_state(), reward, self.done

    def render(self):

        self.clock.tick(self.fps)
        surface.fill(col_BACKGROUND)

        for wall in self.walls:
            wall.draw_self(surface)

        for enemy in self.enemies:
            enemy.draw_self(surface)

        if not self.player.dead:
            self.player.draw_self(surface)
            pygame.draw.circle(surface, (0, 255, 0), (int(self.player.x), int(self.player.y)), int(self.safe_distance), 1)
            pygame.draw.circle(surface, (200, 255, 0), (int(self.player.x), int(self.player.y)), int(self.consideration_distance), 1)


        text = font_PRIMARY_BIG.render(f"{self.score//10}", False, col_WHITE)
        text_rect = text.get_rect(center=(surface_width/2, 10))

        surface.blit(text, text_rect)

        reward_text = font_PRIMARY.render(f"{round(self.current_reward, 2)}", False, self.col_RED if self.current_reward<0 else self.col_GREEN)
        surface.blit(reward_text, (15, 5))

        scaled_surface = pygame.transform.scale(surface, window_size)
        window.blit(scaled_surface, (0, 0))

        pygame.display.update()

    def close(self):
        pygame.quit()