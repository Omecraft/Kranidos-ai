import pygame
import os
import neat
import pymunk
from game import Game 
import pickle

# 1. La fonction d'évaluation (Ton entraîneur)1
def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        
        # On crée un espace physique vierge pour ce joueur
        current_espace = pymunk.Space()
        current_espace.gravity = (0, 900)
        
        game = Game(current_espace)
        
        # Boucle de jeu
        while game.running:
            # IA joue
            inputs = game.info_matrix()
            output = net.activate(inputs)
            action = output.index(max(output))
            
            game.step(action)
            genome.fitness = game.fitness

# 2. La fonction principale de lancement
def run(config_path,generation):
    # Chargement de la configuration NEAT
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Création de la population (basée sur ton fichier texte)
    p = neat.Population(config)

    # Ajout des statistiques dans la console (pour voir l'évolution en direct)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Lancement de la simulation !
    # C'est ici que la magie opère :
    winner = p.run(eval_genomes, generation)
    
    print('\nMeilleur génome:\n{!s}'.format(winner))
    
    # Sauvegarde du meilleur génome
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
    net = neat.nn.FeedForwardNetwork.create(best_genome, config)
    
    # On crée un espace physique vierge pour ce joueur
    current_espace = pymunk.Space()
    current_espace.gravity = (0, 900)
    
    game = Game(current_espace)
    clock = pygame.time.Clock()
    
    # Boucle de jeu
    while game.running:
        # IA joue
        inputs = game.info_matrix()
        output = net.activate(inputs)
        action = output.index(max(output))
        
        game.step(action)
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    choose = input("Choose a mode :\n1. Training\n2. Play best genome\n")
    if choose == "1":
        generation = int(input("Enter the number of generations : "))
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config-feedforward.txt")
        run(config_path,generation)
    elif choose == "2":
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config-feedforward.txt")
        play_best_genome(config_path)