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

class MapModel:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.objects = []

    def addObject(self, obj):
        self.objects.append(obj)

    def update(self):
        for obj in self.objects:
            obj.update()
            if obj.pos.x < obj.size:
                obj.pos.x = obj.size
                obj.direction = 180 - obj.direction
            elif obj.pos.x > self.width - obj.size:
                obj.pos.x = self.width - obj.size
                obj.direction = 180 - obj.direction
            elif obj.pos.y < obj.size:
                obj.pos.y = obj.size
                obj.direction = -obj.direction
            elif obj.pos.y > self.height - obj.size:
                obj.pos.y = self.height - obj.size
                obj.direction = -obj.direction

class CreepModel:
    def __init__(self, size, init_position, init_direction, speed):
        self.name = 'creep'
        self.size = size #Creep Radius
        self.pos = Pos(init_position) #Creep position on map
        self.direction = init_direction #Creep direction (in degrees)
        self.speed = speed #Creep speed

    def update(self):
        self.direction = self.direction % 360
        self.pos.x = self.pos.x + cos(radians(self.direction))*self.speed
        self.pos.y = self.pos.y + sin(radians(self.direction))*self.speed

class MapView(Sprite):
    def __init__(self, screen, model):
        Sprite.__init__(self)
        self.screen = screen
        self.model = model
        self.base_image = pygame.image.load('graycreep.png').convert_alpha()

    def blitme(self):
        for obj in self.model.objects:
            image = pygame.transform.scale(self.base_image, (obj.size*2, obj.size*2))
            image = pygame.transform.rotate(image, -obj.direction)
            draw_pos = image.get_rect().move(obj.pos.x - obj.size, obj.pos.y - obj.size)
            self.screen.blit(image, draw_pos)
    
def run_game():
    SCREEN_WIDTH, SCREEN_HEIGHT = 300, 400
    BG_COLOR = 150, 150, 80
    N_CREEPS = 10
    CREEP_SIZE = 8
    CREEP_SPEED = 2

    environment = MapModel(SCREEN_WIDTH, SCREEN_HEIGHT)
    for i in range(N_CREEPS):
        creep = CreepModel(CREEP_SIZE , (randint(0,SCREEN_WIDTH),randint(0,SCREEN_HEIGHT)), randint(0,360), CREEP_SPEED)
        environment.addObject(creep)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    clock = pygame.time.Clock()

    environment_view = MapView(screen, environment)

    while True:
        clock.tick(40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        screen.fill(BG_COLOR)
        
        environment.update()
        environment_view.blitme()

        pygame.display.flip()

if __name__ == "__main__":
    run_game()

