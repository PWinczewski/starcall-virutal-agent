import os
import pygame
import numpy as np
from classes import *
from functions_starcall import *



class GameEnv:
    def __init__(self):
        pygame.init()
        self.surface_width = 160
        self.surface_height = 240
        self.window_scale = 4
        self.surface = pygame.Surface((self.surface_width, self.surface_height))
        self.window_size = (self.surface_width * self.window_scale, self.surface_height * self.window_scale)

        self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
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
        self.enemy_spawn_chance = 0.1
        self.upwards_draft_strength = 3
        self.stable_altitude = 50
        self.gravity = 0.05

        self.enemies = []
        self.walls = []
        self.target_enemy_count_start = 3
        self.target_enemy_count = self.target_enemy_count_start

        self.running = True
        self.fps = 60
        self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        self.player = Player(surface_width/2, stable_altitude)
        self.done = False

        self.score = 0

        self.walls = []
        self.enemies = []

        for i in range(int(surface_height / TILE_SIZE) + 1):
            wall = Wall(0, TILE_SIZE * i)
            wall2 = Wall(surface_width, TILE_SIZE * i)
            self.walls.append(wall)
            self.walls.append(wall2)


        return self._get_state()

    def _get_state(self):
        return np.array([self.player.x, self.player.y])

    def step(self, action):
        global running
        reward = 0

        if not self.player.dead:
            self.score += 1
            reward += 1 
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
                reward -= 0.1
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
                        self.score += 100
                        reward += 100
                if enemy.hitbox_rect.colliderect(self.player.hitbox_rect) and not self.player.dead:
                    self.player.dead = True
            else:
                enemy.hitbox_rect = enemy.update_hitbox_rect(enemy.hitbox)
                if outside_surface(surface, enemy):
                    self.enemies.remove(enemy)

        multiplier = (self.target_enemy_count-len(self.enemies))*self.enemy_spawn_chance
        if random.randint(0, 100) < (self.enemy_spawn_chance+multiplier) * 100:
            enemy = Enemy(random.randrange(self.TILE_SIZE, surface_width-self.TILE_SIZE), self.surface_height-1+self.TILE_SIZE)
            self.enemies.append(enemy)


        if self.player.dead:
            self.done = True
        
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

        text = font_PRIMARY_BIG.render(f"{self.score//10}", False, col_WHITE)
        text_rect = text.get_rect(center=(surface_width/2, 10))
        surface.blit(text, text_rect)

        scaled_surface = pygame.transform.scale(surface, window_size)
        window.blit(scaled_surface, (0, 0))

        pygame.display.update()

    def close(self):
        pygame.quit()



if __name__ == "__main__":
    env = GameEnv()
    for episode in range(50):
        state = env.reset()
        done = False
        score = 0
        total_reward = 0
        while not done:
            action = (np.random.choice([0, 1, 2]), np.random.choice([0, 1]))
            next_state, reward, done = env.step(action)
            # env.render()
            score = env.score
            total_reward += reward
        print('Episode:{} Score:{} Reward:{}'.format(episode+1, score//10, round(total_reward)))
    env.close()