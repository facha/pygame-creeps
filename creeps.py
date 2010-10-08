#!/usr/bin/env python
import os, sys
from random import randint, choice
from math import sin, cos, radians

import pygame
from pygame.sprite import Sprite

class Pos:
    def __init__(self,pos):
        self.x = pos[0]
        self.y = pos[1]

class Creep(Sprite):
    def __init__(self, screen, filename, init_position, init_direction, speed):
        Sprite.__init__(self)
        self.screen = screen
        self.base_image = pygame.image.load(filename).convert_alpha()
        self.image = self.base_image

        self.pos = Pos(init_position)
        self.direction = init_direction
        self.speed = speed

    def update(self):
        self.direction = self.direction % 360
        self.image = pygame.transform.rotate(self.base_image, -self.direction)
        
        self.pos.x = self.pos.x + cos(radians(self.direction))*self.speed
        self.pos.y = self.pos.y + sin(radians(self.direction))*self.speed
        
        self.image_w, self.image_h = self.image.get_size()
        bounds_rect = self.screen.get_rect().inflate(-self.image_w, -self.image_h)
        
        if self.pos.x < bounds_rect.left:
            self.pos.x = bounds_rect.left
            self.direction = 180 - self.direction
        elif self.pos.x > bounds_rect.right:
            self.pos.x = bounds_rect.right
            self.direction = 180 - self.direction
        elif self.pos.y < bounds_rect.top:
            self.pos.y = bounds_rect.top
            self.direction = -self.direction
        elif self.pos.y > bounds_rect.bottom:
            self.pos.y = bounds_rect.bottom
            self.direction = -self.direction
    
    def blitme(self):
        draw_pos = self.image.get_rect().move(
            self.pos.x - self.image_w / 2, 
            self.pos.y - self.image_h / 2)
        self.screen.blit(self.image, draw_pos)
           
def run_game():
    SCREEN_WIDTH, SCREEN_HEIGHT = 300, 400
    BG_COLOR = 150, 150, 80
    N_CREEPS = 10
    CREEP_SPEED = 2

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    clock = pygame.time.Clock()

    # Create N_CREEPS random creeps.
    creeps = []    
    for i in range(N_CREEPS):
        creeps.append(Creep(screen, 'graycreep.png', 
                            (randint(0,SCREEN_WIDTH),randint(0,SCREEN_HEIGHT)), 
                            randint(0,360), CREEP_SPEED))

    while True:
        clock.tick(40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        screen.fill(BG_COLOR)
        
        for creep in creeps:
            creep.update()
            creep.blitme()

        pygame.display.flip()

if __name__ == "__main__":
    run_game()

