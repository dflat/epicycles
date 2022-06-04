import sys
import numpy as np
import math
import random
import time
import pygame
from pygame.locals import *
from collections import deque
from fourier import FourierTransform
from bezier_transform import example_curve, get_svg_func, Spline

BG_COLOR = pygame.Color(0,0,0)
WHITE = pygame.Color(255,255,255)
BLUE = pygame.Color(0,0,255)

class Curve:
    def __init__(self, controls):
        self.controls = controls

class Point:
    def __init__(self, point):
        self.group.append(self)
        self.pos = point
        self.parent_curves = { } # map Spline => point's index 0,1,2, or 3

    @property
    def pos(self):
        return self.xy

    @pos.setter
    def pos(self, val):
        self.xy = np.array(val)
        self.x = val[0]
        self.y = val[1]

class Endpoint(Point):
    group = []
    r = 4
    _color = pygame.Color(255,255,0)
    color = _color

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.first = False

class Barpoint(Point):
    group = []
    r = 3
    _color = pygame.Color(255,0,255)
    color = _color

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.root = None

class PathBuilder:
    min_hover_dist = 10

    def __init__(self):
        self.curves = []
        self.points = []
        self.n = 0
        self.dragged_point = None

    def get_point(self, t):
        # t is a float in [0,1]
        n = len(self.curves)
        T = 1/n
        index, ti = divmod(t, T)
        if index == n:
            index = n-1
            ti = T
        #print(index, ti, t)
        return complex(*self.curves[int(index)].get_point(ti*n)).conjugate()
        #t = t/T

    def collisions(self):
        mp = ui.mousepos 
        closest = 2e20
        selected = None
        for p in self.points:
            p.color = p._color
            ds = np.linalg.norm(mp - p.xy)
            if ds < closest:
                closest = ds
                selected = p
        return selected if closest < self.min_hover_dist else None


    def connect(self, a, b, c, d):
        spline = Spline([p.pos for p in (a,b,c,d)])
        for i, p in enumerate([a,b,c,d]):
            p.parent_curves[spline] = i
        self.curves.append(spline)

    def update(self, dt):
        if self.dragged_point is None:
            selected = self.collisions()
            if selected:
                selected.color = WHITE
                if ui.dragging and self.dragged_point is None:
                    self.dragged_point = selected

        elif self.dragged_point: 
            ds = ui.mousepos - ui.mousepos_history[0]
            self.dragged_point.pos = ui.mousepos
            #self.dragged_point.pos += ds 

            # translate any child control points attatched to the dragged_point
            children = [i for i in Barpoint.group 
                        if i.root is self.dragged_point]
            for child in children:
                child.pos += ds
                for curve, index in child.parent_curves.items():
                    curve.update_controls(index, child.pos)
                    #curve.sample(use_cache=False)

            for curve, index in self.dragged_point.parent_curves.items():
                # update curves that depend on the dragged point
                curve.update_controls(index, self.dragged_point.pos)
                curve.sample(use_cache=False)
            

        if ui.clicked:
            if self.dragged_point:
                self.dragged_point = None
            else:
                self.place_point(pygame.mouse.get_pos())

    def place_point(self, point):
        i = self.n % 3
        if i == 0:
            p = Endpoint(point)
            if self.n == 0:
                p.first = True
            else:
                self.connect(*self.points[-3:], p)
                self.points[-1].root = p # connect endpoint (4) to 3rd control 
        elif i in [1,2]:
            p = Barpoint(point)
            if i == 1:
                p.root = self.points[-1] # connect startpoint (1) to 2nd control

        self.points.append(p)
        self.n += 1

    def draw(self, surf):
        for p in self.points:
            if p in Barpoint.group:
                if p.root is not None:
                    pygame.draw.line(surf, (0,255,255),
                                     p.pos, p.root.pos, width=1) 
            pygame.draw.circle(surf, p.color, (p.x,p.y), p.r)

        for curve in self.curves:
            points = curve.sample(use_cache=True)
            pygame.draw.aalines(surf, WHITE, False, points)

        
class Epicycler:
    group = []
    scale = 1#20
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
        self.origin = self.parent.tip if self.parent else Game.windows[1].center
        self.tip = self.origin + R*np.array(
                (math.cos(-(self.angular*game.epicycle_manager.t + self.phase)),
                 math.sin(-(self.angular*game.epicycle_manager.t + self.phase))))
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
        self.trace_len = int(game.epicycle_manager.slowdown*game.fps) #trace_len
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

class Window:
    def __init__(self, w, h, x_off=0, y_off=0):
        self.w = w
        self.h = h
        self.center = np.array((x_off, y_off)) + np.array((w/2,h/2))
        self.top_right = np.array((x_off + w, y_off))
        self.bot_right = np.array((x_off + w, y_off + h))

    def draw(self, surf):
        pygame.draw.line(surf, WHITE, self.top_right, self.bot_right, width=2)

class EpicycleManager:
    def __init__(self, path_builder): 
        self.slowdown = 10
        self.t = 0
        self.path_builder = path_builder 
        self.reset_fourier()
            
    def add_fourier_cycle(self):
        parent = self.epis[-1] if self.epis else None
        if parent:
            parent.trace = False

        ck = self.ft.next() 

        ## create epicycle
        epi = Pencil(parent=parent, radius=ck.r, freq=ck.freq, phase=ck.phase,
                     slowdown=self.slowdown, trace=True, color=WHITE) 
        self.epis.append(epi)

        # recolor epicycles
        n = len(self.epis)
        for i, e in enumerate(self.epis):
            L = (i+1)/n 
            e.color = BG_COLOR.lerp(WHITE, 0.2*(1-L) + 0.8*L)

    def reset_fourier(self):
        self.ft = FourierTransform(self.path_builder.get_point,
                                    center_on_screen=True)
        self.epis = []

    def update(self, dt):
        self.t += dt/1000/self.slowdown
        for epi in self.epis:
            epi.update(dt)

    def draw(self, surf):
        for epi in self.epis:
            epi.draw(surf)

class Game:
    W = 1600#1920#640
    H = 800#1080#480
    center = np.array((W/2, H/2))
    windows = [Window(W/2,H,0,0), Window(W/2,H,x_off=W/2,y_off=0)]

    def __init__(self):
        self.fps = 60.0
        self.width = Game.W
        self.height = Game.H
        self.clock = pygame.time.Clock()
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.dt = 1/self.fps 
        #self.t = 0
        #self.slowdown=10


        #self.ft = FourierTransform(example_curve())
        #self.ft = FourierTransform(get_svg_func('svgs/xi.svg'),
        #                           center_on_screen=True)
        #self.reset_fourier()
        #self.ft = FourierTransform(self.path_builder.get_point,
        #                            center_on_screen=True)
        self.path_builder = PathBuilder()
        self.epicycle_manager = EpicycleManager(self.path_builder)

    def update(self, dt):
        #self.t += dt/1000/self.slowdown

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit() 
                sys.exit() 

            if event.type == pygame.KEYDOWN:
                if event.key == K_x:
                    pygame.quit()
                    sys.exit()
                if event.key == K_e:
                    game.epicycle_manager.add_fourier_cycle()
                if event.key == K_w:
                    for i in range(50):
                        game.epicycle_manager.add_fourier_cycle()
                if event.key == K_j:
                    Epicycler.scale /= 1.25
                if event.key == K_k:
                    Epicycler.scale *= 1.25
                if event.key == K_r:
                    game.epicycle_manager.reset_fourier()

            if event.type == pygame.MOUSEBUTTONUP:
                print(event.button, 'button')
                if event.button == 1:
                    ui.mousestate = 'up'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    ui.mousestate = 'down'

        ui.update(dt)

        self.path_builder.update(dt)
        self.epicycle_manager.update(dt)

        #for epi in Epicycler.group:
        #    epi.update(dt)

     
    def draw(self):
        self.screen.fill(BG_COLOR) 

        for window in Game.windows:
            window.draw(self.screen)

        #for epi in Epicycler.group:
        #    epi.draw(self.screen)
        self.path_builder.draw(self.screen)
        self.epicycle_manager.draw(self.screen)


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

class UI:
    def __init__(self):
        self.mousestate = None
        self.mousepos = None 
        self.prev_mousepos = None
        self.dragging = False
        self.clicked = False
        self.mousepos_history = deque(maxlen=2)

    def update(self,dt):
        self.clicked = False
        self.mousepos = pygame.mouse.get_pos()
        self.mousepos_history.append(np.array(self.mousepos))
        self.dragging = self.mousestate == 'down'
        self.clicked = self.mousestate == 'up'
        if self.clicked:
            self.mousestate = None
            self.dragging = False

ui = UI()

game = Game()
game.run()
