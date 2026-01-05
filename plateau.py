import pygame
import pymunk


class Plateau:
    def __init__(self,y,color,surface, espace):
        self.y = y
        self.color = color
        self.surface = surface
        self.has_peak = False
        self.time_peak = 0
        self.peak_coord = (0,0)
        self.espace = espace
        self.bord_g=(0,self.y)
        self.bord_d=(self.surface.get_width(),self.y)
        self.plateau=[]
        self.peak=[[],[]]
        self.draw()
        self.create_plateau()


    def create_plateau(self):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, self.bord_g, self.bord_d, 5)
        shape.elasticity = 1
        shape.friction = 1
        shape.color = (255,255,255)
        self.espace.add(body, shape)
        self.plateau=[body,shape]

    def draw_plateau(self):
        pygame.draw.line(self.surface,self.color,self.bord_g,self.bord_d,5)

    def delete_plateau(self):
        self.espace.remove(self.plateau[0],self.plateau[1])

    def create_peak(self):
        body_g = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape_g = pymunk.Segment(body_g, self.bord_g, self.peak_coord, 5)
        shape_g.elasticity = 1
        shape_g.friction = 1
        shape_g.color = (255,255,255)
        self.espace.add(body_g, shape_g)
        body_d = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape_d = pymunk.Segment(body_d, self.bord_d, self.peak_coord, 5)
        shape_d.elasticity = 1
        shape_d.friction = 1
        shape_d.color = (255,255,255)
        self.espace.add(body_d, shape_d)
        self.peak=[[body_g,body_d],[shape_g,shape_d]]


    def draw_peak(self):
        pygame.draw.line(self.surface,self.color,self.bord_g,self.peak_coord,5)
        pygame.draw.line(self.surface,self.color,self.bord_d,self.peak_coord,5)

    def delete_peak(self):
        self.espace.remove(self.peak[0][0],self.peak[0][1])
        self.espace.remove(self.peak[1][0],self.peak[1][1])

    def draw(self):
        if self.has_peak:
            self.draw_peak()
        else:
            self.draw_plateau()
            
    def tordre(self,x, boule=None):
        if not self.has_peak:
            self.has_peak = True
            self.time_peak = 120
            self.peak_coord = (x,self.y - 100)
            self.delete_plateau()
            self.create_peak()
        else:
            self.has_peak = True
            self.time_peak = 120
            self.peak_coord = (x,self.y - 100)
            self.delete_peak()
            self.create_peak()
            
        if boule:
            body = boule.boule[0]
            b_x, b_y = body.position
            
            # Calcul de la hauteur du sol à la position de la balle
            floor_y = self.y
            if 0 <= b_x <= x:
                ratio = b_x / x if x != 0 else 0
                floor_y = self.y - 100 * ratio
            elif x < b_x <= self.surface.get_width():
                ratio = (b_x - x) / (self.surface.get_width() - x)
                floor_y = (self.y - 100) + 100 * ratio
            
            # Si la balle est sous le nouveau sol (ou le touche)
            if b_y + boule.size > floor_y:
                # On téléporte la balle sur le sol + impulsion vers le haut
                body.position = (b_x, floor_y - boule.size - 5)
                body.velocity = (body.velocity.x, -400)

    def update(self):
        if self.has_peak:
            self.time_peak -= 1
            if self.time_peak <= 0:
                self.has_peak = False
                self.time_peak = 0
                self.peak_coord = (0,0)
                self.delete_peak()
                self.create_plateau()
        self.draw()
        



        
        