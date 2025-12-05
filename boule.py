import pygame
import pymunk


class Boule:
    def __init__(self,surface,plateau,espace):
        self.surface = surface
        self.espace = espace
        self.x = self.surface.get_width()/2
        self.y = self.surface.get_height()/2
        self.size = 20
        self.color = (255,255,255)
        self.create_boule()

    def create_boule(self):
        mass = 10
        moment = pymunk.moment_for_circle(mass, 0, self.size)
        body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
        body.position = (self.x, self.y)
        shape = pymunk.Circle(body,self.size)
        shape.elasticity = 1
        shape.friction = 1
        shape.color = self.color
        self.espace.add(body,shape)
        self.boule=[body,shape]

    def draw(self):
        pygame.draw.circle(self.surface,self.color,(self.x,self.y),self.size)

    def update(self):
        self.draw()
        self.gravity()

    def gravity(self):
        self.espace.gravity = (0,100)
        self.espace.step(1/60)
        self.x = self.boule[0].position.x
        self.y = self.boule[0].position.y
