import pygame
import pymunk
from plateau import Plateau
from kranidos import Kranidos
from boule import Boule
from cible import Cible
import numpy as np
import random  # <--- AJOUTÉ : Indispensable pour la gestion des zones

class Game:
    # On ajoute 'scenario' pour pouvoir forcer des tests spécifiques plus tard si besoin
    def __init__(self, espace, visual_mode=False, scenario="random"):
        self.visual_mode = visual_mode
        self.scenario = scenario
        self.w = 800
        self.h = 600
        
        # --- ANTI-SPAM ---
        self.cooldown = 0  # Compteur de rechargement pour l'action "Tordre"

        # --- GESTION DE L'AFFICHAGE ---
        if self.visual_mode:
            pygame.init()
            self.window = pygame.display.set_mode((self.w, self.h))
            self.clock = pygame.time.Clock()
        else:
            self.window = pygame.Surface((self.w, self.h))
            self.clock = None 

        self.running = True
        self.plateau = Plateau(500, (100, 255, 100), self.window, espace)
        self.boule = Boule(self.window, self.plateau, espace)
        self.kranidos = Kranidos(self.window, self.plateau, self.boule)
        self.create_walls(espace)
        self.cible = Cible(self.window, self.plateau)
        
        # --- PHYSIQUE : DAMPING (Friction de l'air) ---
        # Permet à la balle de s'arrêter au lieu de rouler à l'infini.
        espace.damping = 0.5
        
        # --- INITIALISATION INTELLIGENTE DE LA CIBLE ---
        # On ne laisse pas le hasard faire n'importe quoi au début
        self.spawn_cible_strategic()

        self.tick_to_reward = 1200 
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

    # --- NOUVELLE MÉTHODE : GESTION DES ZONES ---
    def spawn_cible_strategic(self):
        """
        Place la cible soit tout à gauche, soit tout à droite.
        JAMAIS au milieu pour éviter les tirs chanceux.
        """
        w = self.w
        
        # Si on a défini un scénario strict (via le main.py)
        if self.scenario == "force_gauche":
            self.cible.x = random.randint(20, int(w * 0.30))
        elif self.scenario == "force_droite":
            self.cible.x = random.randint(int(w * 0.70), w - 20)
        else:
            # Mode Random "Hardcore" : 50% Gauche / 50% Droite
            if random.random() < 0.5:
                # Zone Gauche (0 à 30%)
                self.cible.x = random.randint(20, int(w * 0.30))
            else:
                # Zone Droite (70% à 100%)
                self.cible.x = random.randint(int(w * 0.70), w - 20)
        
        # Hauteur et taille aléatoires
        self.cible.y = random.randint(50, self.plateau.y - 50)
        self.cible.size = random.randint(20, 50)

    def step(self, action):
        if self.visual_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
        
        self.window.fill((0, 0, 0))
        
        self.output(action)
        
        self.plateau.update()
        self.boule.update()
        self.cible.draw() 
        
        self.has_fitness()
        
        if self.visual_mode:
            self.kranidos.update(pygame.event.get()) 
            pygame.display.update()

        self.tick_to_reward -= 1
        if self.tick_to_reward <= 0:
            self.running = False

    def output(self, action):
        # --- GESTION DU COOLDOWN ---
        if self.cooldown > 0:
            self.cooldown -= 1 # On décrémente le timer à chaque frame

        if action == 0:
            if self.kranidos.x > 10:
                self.kranidos.x -= 10
        elif action == 1:
            if self.kranidos.x < self.w - 10 - self.kranidos.size:
                self.kranidos.x += 10
        elif action == 2:
            # On ne peut tirer que si le cooldown est à 0
            # On ne peut tirer que si le cooldown est à 0
            if self.cooldown == 0:
                self.plateau.tordre(self.kranidos.x)
                self.cooldown = 30 # BLOQUE L'ACTION PENDANT 30 FRAMES (0.5s)
                
                # --- MODIFICATION : PENALITÉ D'INSTABILITÉ ---
                # Plus la balle bouge vite, plus ça coûte cher de taper.
                # Cela encourage l'IA à attendre que la balle se stabilise.
                v = self.boule.boule[0].velocity
                speed = v.length
                
                # Formule : Coût de base (1.0) + Penalité de vitesse
                # Si vitesse = 0 -> Coût = 1.0
                # Si vitesse = 200 (roule) -> Coût = 1.0 + 1.0 = 2.0
                # Si vitesse = 800 (vole) -> Coût = 1.0 + 4.0 = 5.0
                instability_cost = 1.0 + (speed * 0.005)
                
                self.fitness -= instability_cost
        elif action == 3:
            pass 

    def has_fitness(self):
        if self.cible.is_in(self.boule.x, self.boule.y):
            # --- MODIFICATION : On utilise notre générateur stratégique ---
            self.spawn_cible_strategic() 
            
            self.fitness += 5.0 
            
            if self.plateau.has_peak:
                self.fitness += 2.0
            
            self.tick_to_reward += 200 
            
        elif self.cible.is_close(self.boule.x, self.boule.y):
            self.fitness += 0.1 
            
        elif self.boule.y < 175:
            self.fitness += 0.1
        
    def info_matrix(self):
        x_kranidos = self.kranidos.x
        x_boule, y_boule = self.boule.x, self.boule.y
        x_cible, y_cible = self.cible.x, self.cible.y
        vitesse_boule = self.boule.boule[0].velocity
        
        W, H = float(self.w), float(self.h)

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