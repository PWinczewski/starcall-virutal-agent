
import functions_starcall as func
from game_config import *


class Creature:
    def __init__(self, x, y):
        self.dead = False
        self.x = x
        self.y = y
        self.angle = 0
        self.facing = RIGHT
        self.hspd = 0
        self.vspd = 0
        self.hitbox = None
        self.hitbox_rect = None

        self.active_image = None
        self.rect = None

    def draw_self(self, draw_surface):
        if self.active_image is not None:
            img = self.active_image
            if self.facing == LEFT:
                img = pygame.transform.flip(self.active_image, True, False)
            img, self.rect = func.rot_center(img, self.angle, self.x, self.y)
            draw_surface.blit(img, self.rect)

    def get_width(self):
        return self.active_image.get_width()

    def get_height(self):
        return self.active_image.get_height()

    def get_hitbox_width(self):
        return self.hitbox[2]

    def get_hitbox_height(self):
        return self.hitbox[3]

    def change_sprite(self, sprite):
        if self.active_image != sprite:
            self.active_image = sprite

    def update_hitbox_rect(self, hitbox):
        return pygame.Rect(self.x + hitbox[0], self.y + hitbox[1], hitbox[2], hitbox[3])


class Player(Creature):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image_idle = spr_PLAYER_IDLE
        self.image_down = spr_PLAYER_DOWN
        self.active_image = self.image_idle
        self.mask = pygame.mask.from_surface(self.active_image)
        self.max_vspd = 1
        self.max_hspd = 2
        self.spd_buildup_h = 0.2
        self.spd_buildup_v = 0.5
        self.horizontal_resistance = 0.075
        self.facing = RIGHT
        self.max_angle = 35
        self.rotation_spd = 1.5
        self.hitbox = (-4, -2, 9, 9)
        self.hitbox_rect = self.update_hitbox_rect(self.hitbox)
        self.hitbox_attack = (-1, 0, 3, 24)
        self.hitbox_attack_rect = self.update_hitbox_rect(self.hitbox_attack)

    def accelerate_horizontally(self, direction):
        if self.vspd > 0:
            self.hspd = func.approach(self.hspd, self.max_hspd / 2  * direction, self.spd_buildup_h)
        else:
            self.hspd = func.approach(self.hspd, self.max_hspd * direction, self.spd_buildup_h)
            self.angle = func.approach(self.angle, self.max_angle*direction*-1, self.rotation_spd)
        self.facing = direction

    def accelerate_vertically(self, direction):
        if direction == DOWN:
            self.angle = 0
            self.vspd = func.approach(self.vspd, self.max_vspd, self.spd_buildup_v)
        else:
            self.vspd = func.approach(self.vspd, -(self.max_vspd+upwards_draft_strength), self.spd_buildup_v*upwards_draft_strength)

    def move_and_collide(self):
        if self.hspd != 0:
            predicted_pos = self.x + self.hspd + self.get_hitbox_width()/2 * self.facing
            if predicted_pos > surface_width - TILE_SIZE or predicted_pos < TILE_SIZE:
                self.hspd = 0
            self.x += self.hspd
        if self.vspd != 0:
            predicted_pos = self.y + self.vspd + self.get_hitbox_height()/2
            if predicted_pos > surface_height - self.hitbox[3] or predicted_pos < stable_altitude:
                self.vspd = 0
            self.y += self.vspd


class Enemy(Creature):
    def __init__(self, x, y, facing):
        super().__init__(x, y)
        self.vspd = scroll_speed
        self.sprite = spr_ENEMY_EYEBAT
        self.frame = 0
        self.active_image = spr_ENEMY_EYEBAT[self.frame]
        self.facing = facing
        self.hspd = 1 * self.facing
        self.anim_clock = 0
        self.anim_speed = 6
        self.hitbox = (-6, -8, 13, 17)
        self.hitbox_rect = self.update_hitbox_rect(self.hitbox)

    def move_and_collide(self):
        if not self.dead:
            predicted_pos = self.x + self.hspd + self.get_hitbox_width()/2 * self.facing
            if predicted_pos > surface_width - TILE_SIZE or predicted_pos < TILE_SIZE:
                self.hspd *= -1
                self.facing *= -1
        else:
            self.vspd -= gravity
        self.x += self.hspd
        self.y -= self.vspd

    def animate(self):
        if self.anim_clock <= 0:
            self.anim_clock = self.anim_speed
            if self.frame+1 > len(self.sprite)-1:
                self.frame = 0
            else:
                self.frame += 1
            self.change_sprite(self.sprite[self.frame])
        self.anim_clock -= 1


class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active_image = spr_ROOM_WALL
        self.vspd = scroll_speed
        if x > surface_width/2:
            self.active_image = pygame.transform.flip(self.active_image, True, False)
            self.rect = self.active_image.get_rect(topright=(x, y))
        else:
            self.rect = self.active_image.get_rect(topleft=(x, y))

    def draw_self(self, draw_surface):
        if self.active_image is not None:
            if self.x > surface_width / 2:
                self.rect = self.active_image.get_rect(topright=(self.x, self.y))
            else:
                self.rect = self.active_image.get_rect(topleft=(self.x, self.y))
            draw_surface.blit(self.active_image, self.rect)

    def move(self):
        self.y -= self.vspd
        if self.y <= -TILE_SIZE:
            self.y = surface_height-1

class Particle:
    def __init__(self, x, y, hspd, vspd, sprite, frame=-1, lifespan=-1, horizontal_resistance=0, gravity=0, rotation=0):
        self.x = x
        self.y = y
        self.angle = 0
        self.facing = RIGHT
        self.hspd = hspd
        self.vspd = vspd
        self.rotation = rotation
        self.hitbox = None
        self.hitbox_rect = None
        self.lifespan = lifespan
        self.gravity = gravity
        self.horizontal_resistance = horizontal_resistance

        self.sprite = sprite
        self.frame = frame
        if frame != -1:
            self.active_image = sprite[frame]
        else:
            self.active_image = sprite
        self.rect = None
        self.hitbox = (-self.get_width()/2, -self.get_height()/2, self.get_width(), self.get_height())
        self.hitbox_rect = self.update_hitbox_rect(self.hitbox)

    def draw_self(self, draw_surface):
        if self.active_image is not None:
            img = self.active_image
            if self.facing == LEFT:
                img = pygame.transform.flip(self.active_image, True, False)
            img, self.rect = func.rot_center(img, self.angle, self.x, self.y)
            draw_surface.blit(img, self.rect)

    def move(self):
        self.x += self.hspd
        self.y += self.vspd
        self.hspd = func.approach(self.hspd, 0, self.horizontal_resistance)
        self.vspd += self.gravity
        self.angle += self.rotation

    def update_hitbox_rect(self, hitbox):
        return pygame.Rect(self.x + hitbox[0], self.y + hitbox[1], hitbox[2], hitbox[3])

    def get_width(self):
        return self.active_image.get_width()

    def get_height(self):
        return self.active_image.get_height()