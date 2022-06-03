import sys
import numpy as np
import math
import random
import time
import pygame
from pygame.locals import *
from collections import deque
from fourier import FourierTransform, ck
from bezier_transform import example_curve

BG_COLOR = pygame.Color(0,0,0)
WHITE = pygame.Color(255,255,255)
BLUE = pygame.Color(0,0,255)

class Curve:
    def __init__(self, controls):
        self.controls = controls

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
class Endpoint(Point):
    pass
class Barpoint(Point):
    pass

class Path:
    def __init__(self):
        self.curves = []
        self.points = []
        self.n = 0

    def place_point(self, x, y):
        i = self.n % 4
        if i in [0,3]:
            p = Endpoint(x,y)
        elif i in [1,2]:
            p = Barpoint(x,y)
        self.points.append(p)
        self.n += 1

    def add_curve(self, curve:Curve):
        self.curves.append(curve)
        
class Epicycler:
    group = []
    scale = 20
    def __init__(self, parent=None, 
                       radius=1, phase=0, freq=1,
                       slowdown=1, color=WHITE):
        self.parent = parent
        self.group.append(self)
        self.r = radius
        self.phase = phase
        self.freq = freq
        self.angular = freq*2*np.pi

        # display settings
        self.slowdown = slowdown 
        self.color = color
        self.w = 3

        self.get_tip() # initialize tip

    def update(self, dt):
        self.get_tip()

    def get_tip(self):
        R = self.scale*self.r
        self.origin = self.parent.tip if self.parent else Game.center
        self.tip = self.origin + R*np.array(
                (math.cos(-(self.angular*game.t + self.phase)),
                 math.sin(-(self.angular*game.t + self.phase))))
        # the negative angle is due to pygame reversing positive=CCW convention 

    def draw(self, surf):
        pygame.draw.line(surf, self.color, self.origin,
                         self.tip, width=self.w)
        pygame.draw.circle(surf, self.color, self.origin, # ring
                           self.scale*self.r, width=1)
        pygame.draw.circle(surf, self.color, self.tip, # tip
                           max(1, self.scale*self.r/12))

class Pencil(Epicycler):
    def __init__(self, *args, pencil_color=BLUE, trace=True,
                trace_len=1000, **kwargs):
        self.trace = trace
        self.trace_len = int(game.slowdown*game.fps) #trace_len
        self.pos_history = deque(maxlen=self.trace_len)
        self.pencil_color = pencil_color
        super().__init__(*args, **kwargs)

    def get_tip(self):
        super().get_tip()
        self.pos_history.append(self.tip)

    def draw(self, surf):
        super().draw(surf)
        if self.trace and len(self.pos_history) > 1:
            for i in range(len(self.pos_history)-1):
                n = len(self.pos_history)
                pygame.draw.line(surf, BG_COLOR.lerp(self.pencil_color, i/n), 
                            self.pos_history[i], self.pos_history[i+1], width=2)

class Game:
    W = 640
    H = 480
    center = np.array((W/2, H/2))

    def __init__(self):
        self.fps = 60.0
        self.width = 640
        self.height = 480
        self.clock = pygame.time.Clock()
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.dt = 1/self.fps 
        self.t = 0
        self.slowdown=10

        self.epis = []
        self.f = example_curve()
        self.ft = FourierTransform(self.f)
        self.k = 0

        t="""
        e0 = Epicycler(parent=None, radius=3,
                  phase=0, freq=1, slowdown=10, color=BG_COLOR.lerp(WHITE, .1))
        e1 = Epicycler(parent=e0, radius=2,
                  phase=0, freq=2, slowdown=10, color=BG_COLOR.lerp(WHITE, .2))
        e2 = Epicycler(parent=e1, radius=1, phase=math.pi/4,
                       freq=3, slowdown=10, color=BG_COLOR.lerp(WHITE, .3))
        e3 = Pencil(parent=e2, radius=2, phase=math.pi/4,
                       freq=-1, slowdown=10, color=BG_COLOR.lerp(WHITE, .4))
                       """
                       
    def add_fourier_cycle(self):
        parent = self.epis[-1] if self.epis else None
        if parent:
            parent.trace = False

        Ck = ck(self.k, self.f) #self.ft.C(self.k)
        r = np.linalg.norm(Ck)
        phase = np.arctan2(Ck.imag, Ck.real)
        freq = self.k
        epi = Pencil(parent=parent, radius=r, freq=freq, phase=phase,
                     slowdown=self.slowdown, trace=True, color=WHITE) 
        self.epis.append(epi)
        t="""
        if self.k > 0:
            ck = self.ft.C(-self.k)
            freq = -self.k
            r = np.linalg.norm(ck)
            phase = np.arctan2(ck.imag, ck.real)
            epi = Pencil(parent=parent, radius=r, freq=freq, phase=phase,
                         slowdown=self.slowdown, trace=True, color=WHITE) 
            self.epis.append(epi)
            """

        n = len(self.epis)
        for i, e in enumerate(self.epis):
            L = (i+1)/n 
            e.color = BG_COLOR.lerp(WHITE, L)

        if self.k <= 0:
            self.k = abs(self.k) + 1 
        else:
            self.k = -self.k
        #self.k *= (-1)**(n-1) # alternate negative and positive frequencies
        print('next freq (k):', self.k)

    def add_cycle(self): 
        parent = self.epis[-1] if self.epis else None
        if parent:
            parent.trace = False
        r = random.randint(1,4)
        freq = random.randint(-6,6)
        epi = Pencil(parent=parent, radius=r, freq=freq, phase=0,
                     slowdown=self.slowdown, trace=True, color=WHITE) 
        self.epis.append(epi)
        # remap colors
        n = len(self.epis)
        for i, e in enumerate(self.epis):
            L = (i+1)/n 
            e.color = BG_COLOR.lerp(WHITE, L)


    def update(self, dt):
        self.t += dt/1000/self.slowdown

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit() 
                sys.exit() 
            if event.type == pygame.KEYDOWN:
                if event.key == K_x:
                    pygame.quit()
                    sys.exit()
                if event.key == K_e:
                    game.add_fourier_cycle()
                if event.key == K_j:
                    Epicycler.scale /= 1.25
                if event.key == K_k:
                    Epicycler.scale *= 1.25

        for epi in Epicycler.group:
            epi.update(dt)
     
    def draw(self):
        self.screen.fill(BG_COLOR) 
        for epi in Epicycler.group:
            epi.draw(self.screen)

        pygame.display.flip()
     
    def run(self):
        started = False
        #self.dt*=1000
        dt = 17
        while True: 
            self.update(dt) 
            self.draw()
            #if not started:
            #    time.sleep(2)
            #    started = True
            dt = self.clock.tick(self.fps) # fix timing bug

game = Game()
game.run()
