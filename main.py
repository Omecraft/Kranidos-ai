import pygame
import os
# Cette ligne masque le message de bienvenue
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import neat
import pymunk
from game import Game 
import pickle
import multiprocessing
import numpy as np # Utile pour la moyenne

# --- MODIFICATION 1 : Fonction pour UN SEUL génome (plus de boucle for ici) ---
def eval_genome(genome, config):
    # IMPORTANT : Si tu as mis feed_forward = False dans la config, utilise RecurrentNetwork
    # Cela permet à l'IA d'avoir de la mémoire
    net = neat.nn.RecurrentNetwork.create(genome, config)
    
    scores = []
    
    # --- MODIFICATION 2 : La Règle de 3 (Anti-Chance) ---
    # On lance le jeu 3 fois pour le même cerveau et on fait la moyenne.
    # Si l'IA a eu de la chance une fois, elle échouera les 2 autres.
    for _ in range(3):
        current_espace = pymunk.Space()
        current_espace.gravity = (0, 900)
        
        # ATTENTION : Assure-toi que Game() n'ouvre pas de fenêtre Pygame ici !
        # Idéalement : game = Game(current_espace, mode_visuel=False)
        game = Game(current_espace)
        
        while game.running:
            inputs = game.info_matrix()
            output = net.activate(inputs)
            action = output.index(max(output))
            game.step(action)
            
            # Sécurité : Si le jeu dure trop longtemps (bug), on coupe
            # (Optionnel, à adapter selon ton jeu)
            # if game.frame_count > 2000: break

        scores.append(game.fitness)

    # On renvoie la moyenne des 3 essais
    return sum(scores) / len(scores)


def run(config_path, generation):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # --- MODIFICATION 3 : Lancement Parallèle ---
    # Utilise tous les cœurs du processeur
    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
    
    # On passe 'pe.evaluate' au lieu de ta fonction eval_genomes
    winner = p.run(pe.evaluate, generation)
    
    print('\nMeilleur génome:\n{!s}'.format(winner))
    
    with open("meilleur_genome.pkl", "wb") as f:
        pickle.dump(winner, f)

def load_best_genome():
    with open("meilleur_genome.pkl", "rb") as f:
        return pickle.load(f)

def play_best_genome(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    best_genome = load_best_genome()
    
    # Pareil ici, RecurrentNetwork si feed_forward=False
    net = neat.nn.RecurrentNetwork.create(best_genome, config)
    
    current_espace = pymunk.Space()
    current_espace.gravity = (0, 900)
    
    # Ici on veut voir le jeu, donc mode visuel activé
    game = Game(current_espace, visual_mode=True) 
    clock = pygame.time.Clock()
    
    while game.running:
        inputs = game.info_matrix()
        output = net.activate(inputs)
        action = output.index(max(output))
        
        game.step(action)
        
        # Ajout des fonctions de dessin ici si elles ne sont pas dans step()
        # game.draw() 
        # pygame.display.flip()
        
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    # Nécessaire pour le multiprocessing sur Windows
    multiprocessing.freeze_support() 
    
    choose = input("Choose a mode :\n1. Training\n2. Play best genome\n")
    if choose == "1":
        generation = int(input("Enter the number of generations : "))
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config-feedforward.txt")
        run(config_path, generation)
    elif choose == "2":
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config-feedforward.txt")
        play_best_genome(config_path)