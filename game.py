import pygame
import pymunk
from plateau import Plateau
from kranidos import Kranidos
from boule import Boule
from cible import Cible
import numpy as np

class Game:
    def __init__(self, espace):
        self.window = pygame.display.set_mode((800,600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.plateau =  Plateau(500,(100,255,100),self.window,espace)
        self.boule = Boule(self.window,self.plateau,espace)
        self.kranidos = Kranidos(self.window,self.plateau,self.boule)
        self.create_walls(espace)
        self.cible = Cible(self.window,self.plateau)
        self.tick_to_reward = 1200
        self.fitness = 0

    def create_walls(self, espace):
        w, h = self.window.get_size()
        body_t = pymunk.Body(body_type=pymunk.Body.STATIC)
        body_b = pymunk.Body(body_type=pymunk.Body.STATIC)
        body_g = pymunk.Body(body_type=pymunk.Body.STATIC)
        body_d = pymunk.Body(body_type=pymunk.Body.STATIC)
        walls = [
            [body_t,pymunk.Segment(body_t, (0, 0), (0, h), 5)],
            [body_b,pymunk.Segment(body_b, (w, 0), (w, h), 5)],
            [body_g,pymunk.Segment(body_g, (0, 0), (w, 0), 5)],
            [body_d,pymunk.Segment(body_d, (0, h), (w, h), 5)]
        ]
        for wall in walls:
            wall[1].elasticity = 1
            wall[1].friction = 1
            espace.add(wall[0],wall[1])

    def run(self):
        while self.running:
            self.step(4)
            self.clock.tick(60)
            self.tick_to_reward -= 1
            if self.tick_to_reward == 0:
                self.running = False
        pygame.quit()
        return self.fitness

    def step(self,action):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        self.window.fill((0,0,0))
        self.output(action)
        self.kranidos.update(events)
        self.plateau.update()
        self.boule.update()
        self.cible.draw()
        if self.cible.is_in(self.boule.x,self.boule.y):
            self.cible.generate_coordinates()
            print("Cible touchée")
            self.fitness += 1
        elif self.cible.is_close(self.boule.x,self.boule.y):
            self.fitness += 0.25
            print("Cible proche")
        pygame.display.update()
        self.tick_to_reward -= 1
        if self.tick_to_reward <= 0:
            self.running = False
            
    def info_matrix(self):
        x_kranidos,y_kranidos = self.kranidos.x,self.kranidos.y
        x_boule,y_boule = self.boule.x,self.boule.y
        y_plateau = self.plateau.y
        x_cible,y_cible = self.cible.x,self.cible.y
        vitesse_boule = self.boule.boule[0].velocity
        info_matrix = np.array([x_kranidos,y_kranidos,x_boule,y_boule,y_plateau,x_cible,y_cible,vitesse_boule[0],vitesse_boule[1]])
        return info_matrix

    def output(self,action):
        if action == 0:
            if self.kranidos.x>10:
                self.kranidos.x -= 10
        elif action == 1:
            if self.kranidos.x<self.window.get_width()-10-self.kranidos.size:
                self.kranidos.x += 10
        elif action == 2:
            self.plateau.tordre(self.kranidos.x)
        elif action == 3:
            pass

