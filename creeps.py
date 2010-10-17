#!/usr/bin/env python
import os, sys
from random import randint, choice
from math import sin, cos, radians, pow, sqrt
import numpy

import pygame
from pygame.sprite import Sprite

class Pos:
    def __init__(self,pos):
        self.x = pos[0]
        self.y = pos[1]

class MapModel:
    def __init__(self, width, height):
        self.visibility = 100
        self.width = width
        self.height = height
        self.objects = []
        self.obj_distance_matrix = None

    def addObject(self, obj):
        self.objects.append(obj)

    def getDistanceMatrix(self):
        N = len(self.objects)
        self.obj_distance_matrix = numpy.zeros(shape=(N,N))
        for i in range(0,N):
            for j in range(i,N):
                if i == j:
                    self.obj_distance_matrix[i,j] = 0
                else:
                    dx = self.objects[i].pos.x - self.objects[j].pos.x
                    dy = self.objects[i].pos.y - self.objects[j].pos.y
                    self.obj_distance_matrix[i,j] = sqrt(pow(dx, 2) + pow(dy, 2))
                    self.obj_distance_matrix[j,i] = self.obj_distance_matrix[i,j]

    def removeCollided(self):
        for_removal = []
        N = len(self.objects)
        for i in range(0,N):
            for j in range(i+1,N):
                if self.obj_distance_matrix[i,j] <= self.objects[i].size + self.objects[j].size:
                    for_removal.append(i)
                    for_removal.append(j)
        for_removal = list(set(for_removal))
        for_removal.sort(reverse=True)
        for obj_index in for_removal:
            del self.objects[obj_index]


    def getObjView(self, obj):
        """ return a list of visible objects """
        N = len(self.objects)
        n = self.objects.index(obj)
        view = []
        for i in range(0,N):
            if i != n:
                if self.obj_distance_matrix[i,n] <= self.visibility:
                    visible_object = {'obj_type': self.objects[i].obj_type,
                                      'size': self.objects[i].size, 
                                      'x': self.objects[i].pos.x, 
                                      'y': self.objects[i].pos.y, 
                                      'distance': self.obj_distance_matrix[i,n]}
                    view.append(visible_object)
        view.append({'obj_type': 'bounds', 'width': self.width, 'height': self.height})
        return view

    def update(self):
        self.getDistanceMatrix()
        self.removeCollided()
        for obj in self.objects:
            obj.view = self.getObjView(obj)
            obj.update()
            if obj.obj_type == 'creep':
                obj.pos.x = obj.pos.x + cos(radians(obj.direction))*obj.speed
                obj.pos.y = obj.pos.y + sin(radians(obj.direction))*obj.speed
                if obj.pos.x < obj.size:
                    obj.pos.x = obj.size
                elif obj.pos.x > self.width - obj.size:
                    obj.pos.x = self.width - obj.size
                elif obj.pos.y < obj.size:
                    obj.pos.y = obj.size
                elif obj.pos.y > self.height - obj.size:
                    obj.pos.y = self.height - obj.size

class BaseObjectModel:
    def __init__(self, size, init_position):
        self.obj_type = 'base'
        self.size = size #object radius
        self.pos = Pos(init_position) #position on map

    def update(self):
        pass

class CreepModel(BaseObjectModel):
    def __init__(self, size, init_position, init_direction, speed):
        BaseObjectModel.__init__(self,size,init_position)
        self.obj_type = 'creep'
        self.direction = init_direction #Creep direction (in degrees)
        self.speed = speed #Creep speed
        self.view = None

    def reflectFromBounds(self):
        start_acting_at = self.size #if distance is less then that, change direction
        bounds = self.view.pop()
        width = bounds['width']
        height = bounds['height']
        if self.pos.x <= start_acting_at:
            self.direction = 180 - self.direction
        elif self.pos.x >= width - start_acting_at:
            self.direction = 180 - self.direction
        elif self.pos.y <= start_acting_at:
            self.direction = -self.direction
        elif self.pos.y >= height - start_acting_at:
            self.direction = -self.direction

    def dontCollide(self):
        def getDistanceDelta(angle_delta):
            x = self.pos.x
            y = self.pos.y
            direction = self.direction + angle_delta
            speed = self.speed
            x1 = obj['x']
            y1 = obj['y']
            current_distance = obj['distance']
            x = x + cos(radians(direction))*speed
            y = y + sin(radians(direction))*speed
            dx = x - x1
            dy = y - y1
            next_step_distance = sqrt(pow(dx, 2) + pow(dy, 2))
            return next_step_distance - current_distance
            
        start_acting_at = self.size + 20
        for obj in self.view:
            if obj['obj_type'] == 'creep':
                if obj['distance'] < start_acting_at:
                    distances = {}
                    for angle in (-45, 45):
                        distances[angle] = getDistanceDelta(angle)
                    self.direction += max(distances, key=distances.get)

    def update(self):
        self.direction = self.direction % 360
        self.reflectFromBounds()
        self.dontCollide()

class MapView(Sprite):
    def __init__(self, screen, model):
        Sprite.__init__(self)
        self.screen = screen
        self.model = model
        self.images = {}
        self.images['creep'] = pygame.image.load('graycreep.png').convert_alpha()
        self.images['base'] = pygame.image.load('base.png').convert_alpha()

    def blitme(self):
        for obj in self.model.objects:
            image = self.images[obj.obj_type]
            image = pygame.transform.scale(image, (obj.size*2, obj.size*2))
            if obj.obj_type == 'creep':
                image = pygame.transform.rotate(image, -obj.direction)
            draw_pos = image.get_rect().move(obj.pos.x - obj.size, obj.pos.y - obj.size)
            self.screen.blit(image, draw_pos)
    
def run_game():
    SCREEN_WIDTH, SCREEN_HEIGHT = 200,300
    BG_COLOR = 150, 150, 80
    N_CREEPS = 10
    CREEP_RADIUS = 8 #creep radius
    CREEP_SPEED = 3

    environment = MapModel(SCREEN_WIDTH, SCREEN_HEIGHT)
    for i in range(N_CREEPS):
        creep = CreepModel(CREEP_RADIUS, (randint(0,SCREEN_WIDTH),randint(0,SCREEN_HEIGHT)), randint(0,360), CREEP_SPEED)
        environment.addObject(creep)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    clock = pygame.time.Clock()

    environment_view = MapView(screen, environment)

    while True:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        screen.fill(BG_COLOR)
        
        environment.update()
        environment_view.blitme()

        pygame.display.flip()

if __name__ == "__main__":
    run_game()

