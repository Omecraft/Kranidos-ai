import pygame
import pymunk
from plateau import Plateau
from kranidos import Kranidos
from boule import Boule
from cible import Cible
import numpy as np

class Game:
    def __init__(self, espace, visual_mode=False):
        self.visual_mode = visual_mode
        self.w = 800
        self.h = 600
        
        # --- MODIFICATION 1 : GESTION DE L'AFFICHAGE ---
        if self.visual_mode:
            pygame.init()
            self.window = pygame.display.set_mode((self.w, self.h))
            self.clock = pygame.time.Clock()
        else:
            # Mode "Fantôme" : On crée une surface en mémoire pour ne pas
            # faire planter les classes Boule/Plateau qui ont besoin d'une "window"
            # mais on n'ouvre pas de vraie fenêtre Windows.
            self.window = pygame.Surface((self.w, self.h))
            self.clock = None 

        self.running = True
        self.plateau = Plateau(500, (100, 255, 100), self.window, espace)
        self.boule = Boule(self.window, self.plateau, espace)
        self.kranidos = Kranidos(self.window, self.plateau, self.boule)
        self.create_walls(espace)
        self.cible = Cible(self.window, self.plateau)
        self.tick_to_reward = 1200 # Durée de vie max (20 secondes à 60fps)
        self.fitness = 0

    def create_walls(self, espace):
        body_t = pymunk.Body(body_type=pymunk.Body.STATIC)
        body_b = pymunk.Body(body_type=pymunk.Body.STATIC)
        body_g = pymunk.Body(body_type=pymunk.Body.STATIC)
        body_d = pymunk.Body(body_type=pymunk.Body.STATIC)
        walls = [
            [body_t, pymunk.Segment(body_t, (0, 0), (0, self.h), 5)],
            [body_b, pymunk.Segment(body_b, (self.w, 0), (self.w, self.h), 5)],
            [body_g, pymunk.Segment(body_g, (0, 0), (self.w, 0), 5)],
            [body_d, pymunk.Segment(body_d, (0, self.h), (self.w, self.h), 5)]
        ]
        for wall in walls:
            wall[1].elasticity = 1
            wall[1].friction = 1
            espace.add(wall[0], wall[1])

    # --- MODIFICATION 2 : LE CŒUR DU JEU ---
    def step(self, action):
        # 1. Gestion des événements (Seulement si on regarde)
        if self.visual_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # Important : passer les events à Kranidos seulement si visuel
                # sinon l'IA contrôle tout
                # self.kranidos.update(events) <--- A désactiver pour l'IA pure ?
                # Si kranidos.update sert juste à l'animation, c'est ok.
        
        # 2. Nettoyage écran (virtuel ou réel)
        self.window.fill((0, 0, 0))
        
        # 3. Action de l'IA
        self.output(action)
        
        # 4. Mises à jour physiques
        self.plateau.update()
        self.boule.update()
        self.cible.draw() # Dessine sur la surface (virtuelle ou réelle)
        
        # 5. Calcul des points
        self.has_fitness()
        
        # 6. Affichage RÉEL (Seulement si mode visuel activé)
        if self.visual_mode:
            self.kranidos.update(pygame.event.get()) # Juste pour l'affichage
            pygame.display.update()
            # self.clock.tick(60) # Optionnel : limiter les FPS ou laisser à fond

        # 7. Gestion du temps (Timer)
        self.tick_to_reward -= 1
        if self.tick_to_reward <= 0:
            self.running = False

    def output(self, action):
        # Utilisation de self.w au lieu de window.get_width() pour la sécurité
        if action == 0:
            if self.kranidos.x > 10:
                self.kranidos.x -= 10
        elif action == 1:
            if self.kranidos.x < self.w - 10 - self.kranidos.size:
                self.kranidos.x += 10
        elif action == 2:
            self.plateau.tordre(self.kranidos.x)
        elif action == 3:
            pass # L'IA décide de ne rien faire

    def has_fitness(self):
        # --- MODIFICATION 3 : PAS DE PRINTS ! ---
        # Les prints ralentissent l'entraînement x100
        
        if self.cible.is_in(self.boule.x, self.boule.y):
            self.cible.generate_coordinates()
            self.fitness += 5.0 # RECOMPENSE MAJEURE
            
            # Bonus si fait avec style (bosse)
            if self.plateau.has_peak:
                self.fitness += 2.0
            
            # On prolonge un peu sa vie pour qu'il puisse marquer encore
            self.tick_to_reward += 200 
            
        elif self.cible.is_close(self.boule.x, self.boule.y):
            self.fitness += 0.1 # Petite récompense pour l'encourager
            
            # Pénalité légère s'il spamme la bosse pour rien
            # (Optionnel, à voir si l'IA triche)

    def info_matrix(self):
        x_kranidos = self.kranidos.x
        x_boule, y_boule = self.boule.x, self.boule.y
        x_cible, y_cible = self.cible.x, self.cible.y
        vitesse_boule = self.boule.boule[0].velocity
        
        # Dimensions stockées
        W, H = float(self.w), float(self.h)

        # Inputs relatifs (Meilleure apprentissage)
        delta_action_x = (x_kranidos - x_boule) / W
        delta_target_x = (x_cible - x_boule) / W
        delta_target_y = (y_cible - y_boule) / H
        dist_sol = (y_boule - self.plateau.y) / H
        vx = vitesse_boule[0] / 1000.0
        vy = vitesse_boule[1] / 1000.0

        return np.array([
            delta_action_x,
            delta_target_x,
            delta_target_y,
            dist_sol,
            vx,
            vy
        ])