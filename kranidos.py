import pygame


#Personnage du jeux, permettant de tordre le plateau
class Kranidos:
    def __init__(self,surface,plateau,boule=None):
        self.surface = surface
        self.boule = boule
        self.plateau = plateau
        self.x=self.surface.get_width()/2
        self.y=self.plateau.y
        self.size=50
        self.image = pygame.image.load("kranidos.png")
        self.image = pygame.transform.scale(self.image,(self.size,self.size))
        

    def draw(self):
        self.surface.blit(self.image,(self.x,self.y))

    def handle_event(self,events):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= 10
        if keys[pygame.K_RIGHT]:
            self.x += 10

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.plateau.tordre(self.x+self.size/2, self.boule)

    def update(self,events):
        self.handle_event(events)
        self.draw()
        