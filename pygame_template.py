import sys
import numpy as np
import pygame
from pygame.locals import *

class Game:
    def __init__(self):
        self.fps = 60.0
        self.width = 640
        self.height = 480
        self.clock = pygame.time.Clock()
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.dt = 1/self.fps 

    def update(self):
        dt = self.dt
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit() 
                sys.exit() 
     
    def draw(self):
        self.screen.fill((0, 0, 0)) 
        pygame.display.flip()
     
    def run(self):
        while True: 
            self.update() 
            self.draw()
            self.dt = self.clock.tick(self.fps)
