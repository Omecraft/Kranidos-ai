import pygame
import pymunk
import random

class Cible:
    def __init__(self,surface,plateau):
        self.surface = surface
        self.plateau = plateau
        self.x,self.y = 0,0
        self.size = 50
        self.generate_coordinates()
        self.size = 50
        self.color = (255,0,0)
        
                
    def generate_coordinates(self):
        #Coordonnées aléatoires entre les limites de la fenêtre et le plateau
        x = random.randint(0,self.surface.get_width())
        y = random.randint(0,self.plateau.y)
        self.x = x
        self.y = y
        self.size = random.randint(20,50)


    def draw(self):
        pygame.draw.circle(self.surface,self.color,(self.x,self.y),self.size)

    def is_in(self,x,y):
        if x-self.size<=self.x<=x+self.size and y-self.size<=self.y<=y+self.size:
            return True
        else:
            return False

    def is_close(self,x,y):
        #If the ball is close to the target (less than 50 pixels)
        distance_squared = (x - self.x)**2 + (y - self.y)**2
        if distance_squared <= 50**2:
            return True
        else:
            return False