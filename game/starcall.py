import pygame
import random
import os
import functions_starcall as func
from game_config import *
from classes import *

def main():
    running = True
    fps = 60
    clock = pygame.time.Clock()

    debug_mode = False
    score = 0
    game_file_path = os.getenv('APPDATA') + r"\starcall"

    if not os.path.exists(game_file_path):
        os.makedirs(game_file_path)

    if not os.path.isfile(game_file_path + r"\highscores.txt"):
        with open(game_file_path + r"\highscores.txt", 'w') as file:
            file.write("0")
            hscore = 0
    else:
        with open(game_file_path + r"\highscores.txt", 'r') as file:
            hscore = int(file.readline())

    for i in range(int(surface_height / TILE_SIZE) + 1):
        wall = Wall(0, TILE_SIZE * i)
        wall2 = Wall(surface_width, TILE_SIZE * i)
        walls.append(wall)
        walls.append(wall2)

    player = Player(surface_width/2, stable_altitude)

    def draw_window():
        surface.fill(col_BACKGROUND)

        for wall in walls:
            wall.draw_self(surface)

        for enemy in enemies:
            enemy.draw_self(surface)
            if debug_mode:
                pygame.draw.rect(surface, col_WHITE, enemy.hitbox_rect)

        for particle in particles:
            particle.draw_self(surface)
            if debug_mode:
                pygame.draw.rect(surface, col_WHITE, particle.hitbox_rect)

        if not player.dead:
            player.draw_self(surface)
        if debug_mode:
            pygame.draw.rect(surface, col_WHITE, player.hitbox_rect)
            if player.hitbox_attack_rect is not None:
                pygame.draw.rect(surface, col_RED, player.hitbox_attack_rect)

        text = font_PRIMARY_BIG.render(f"{score//10}", False, col_WHITE)
        text_rect = text.get_rect(center=(surface_width/2, 10))
        surface.blit(text, text_rect)

        text = font_PRIMARY.render(f"to beat: {hscore // 10}", False, col_WHITE)
        text_rect = text.get_rect(center=(surface_width / 2, 10 + font_PRIMARY.get_height()))
        surface.blit(text, text_rect)

        if player.dead:
            text = font_PRIMARY_BIG.render("GAME OVER", False, col_WHITE)
            text_rect = text.get_rect(center=(surface_width / 2, surface_height / 2))
            surface.blit(text, text_rect)
            text = font_PRIMARY.render("Press ESC", False, col_WHITE)
            text_rect = text.get_rect(center=(surface_width / 2, surface_height / 2 + font_PRIMARY_BIG.get_height() ))
            surface.blit(text, text_rect)

        scaled_surface = pygame.transform.scale(surface, window_size)
        window.blit(scaled_surface, (0, 0))

        pygame.display.update()

    def step():
        global running
        global score
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    debug_mode = not debug_mode
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not player.dead:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                player.accelerate_horizontally(LEFT)
            if keys[pygame.K_d]:
                player.accelerate_horizontally(RIGHT)
            if keys[pygame.K_s]:
                player.accelerate_vertically(DOWN)
                player.change_sprite(spr_PLAYER_DOWN)
                player.hitbox_attack_rect = player.update_hitbox_rect(player.hitbox_attack)
            else:
                player.accelerate_vertically(UP)

                player.change_sprite(spr_PLAYER_IDLE)
                player.hitbox_attack_rect = None

            if (not keys[pygame.K_d] and not keys[pygame.K_a]) or (keys[pygame.K_d] and keys[pygame.K_a]):
                if player.hspd != 0:
                    player.hspd = func.approach(player.hspd, 0, player.horizontal_resistance)
                if player.angle != 0:
                    player.angle = func.approach(player.angle, 0, player.rotation_spd)

            player.move_and_collide()

            player.hitbox_rect = player.update_hitbox_rect(player.hitbox)

        for wall in walls[:]:
            wall.move()

        for particle in particles[:]:
            if particle.lifespan > 0:
                particle.lifespan -= 1
            elif particle.lifespan == 0 or (func.outside_surface(surface, particle) and particle.lifespan < 0):
                particles.remove(particle)
            particle.move()
            particle.hitbox_rect = particle.update_hitbox_rect(particle.hitbox)

        for enemy in enemies[:]:
            enemy.move_and_collide()
            if not enemy.dead:
                if enemy.y <= -TILE_SIZE:
                    enemies.remove(enemy)
                enemy.animate()
                enemy.hitbox_rect = enemy.update_hitbox_rect(enemy.hitbox)
                if not player.dead and player.hitbox_attack_rect is not None:
                    if enemy.hitbox_rect.colliderect(player.hitbox_attack_rect):
                        enemy.dead = True
                        enemy.vspd *= 2
                        player.vspd -= 6
                        score += 100
                if enemy.hitbox_rect.colliderect(player.hitbox_rect) and not player.dead:
                    player.dead = True
                    for i in range(2):
                        p_hspd = 0.2 * random.randint(-6, 6)
                        p_vspd = 0.5 * random.randint(-5, 0)
                        p_rot = random.randint(-10, 10)
                        part = Particle(player.x, player.y, p_hspd, p_vspd, spr_PLAYER_DEATH[i], -1, -1, 0, gravity, p_rot)
                        particles.append(part)

                        with open(game_file_path + r"\highscores.txt", 'r') as file:
                            hscore = int(file.readline())
                        if score > hscore:
                            with open(game_file_path + r"\highscores.txt", 'w') as file:
                                file.write(str(score))

            else:
                enemy.hitbox_rect = enemy.update_hitbox_rect(enemy.hitbox)
                if func.outside_surface(surface, enemy):
                    enemies.remove(enemy)

    while running:
        clock.tick(fps)
        step()
        draw_window()


main()
