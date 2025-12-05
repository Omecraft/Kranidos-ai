import pygame
import pymunk
from plateau import Plateau
from kranidos import Kranidos
from boule import Boule
from cible import Cible
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
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            self.window.fill((0,0,0))
            self.kranidos.update(events)
            self.plateau.update()
            self.boule.update()
            self.cible.draw()
            if self.cible.is_in(self.boule.x,self.boule.y):
                self.cible.generate_coordinates()
                print("Cible touchée")
            pygame.display.update()
            self.clock.tick(60)
        pygame.quit()


espace = pymunk.Space()
espace.gravity = (0,900)
game = Game(espace)
game.run()