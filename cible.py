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
        
                
    def generate_coordinates(self, mode="random"):
        # Largeur de l'écran
        W = self.surface.get_width()
    
        if mode == "force_gauche":
            # Force la cible dans le tiers GAUCHE (ex: entre 0 et 266px)
            # Si l'IA est à gauche et tire à droite, elle rate à 100%.
            x = random.randint(0, int(W / 3))
        
        elif mode == "force_droite":
            # Force la cible dans le tiers DROIT
            # Si l'IA est à droite et tire à gauche, elle rate.
            x = random.randint(int(W * 2 / 3), W)
        
        else:
            # Comportement aléatoire classique (pour le milieu)
            x = random.randint(0, W)

        # La hauteur reste aléatoire (ou tu peux la contraindre aussi si besoin)
        y = random.randint(50, self.plateau.y - 50) # J'ai mis une petite marge de sécurité
    
        self.x = x
        self.y = y
        self.size = random.randint(20, 50)


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