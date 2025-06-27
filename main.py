# -*- coding: utf-8 -*-
"""
Arquivo Principal do Projeto DRE (Datacenter Resource Emulator)
"""
import pygame
import sys
import random
import numpy as np

from datacenter_model import carregar_cenario
from genetic_algorithm import (
    generate_round_robin_population,
    swap_mutation,
    crossover_por_consenso,
    calculate_fitness,
    select_parents
)
from visualization import draw_datacenter_state, draw_fitness_plot, draw_stats_box

# ===[ Constantes ]=======================================================================
WIDTH, HEIGHT = 1280, 740
FPS = 30
PLOT_X_OFFSET = 860
CENARIO_FILE = 'cenario_desafiador.json'
POPULATION_SIZE = 100
N_GENERATIONS = 1000
MAX_GENS_NO_IMPROVEMENT = 200
MUTATION_PROBABILITY = 0.5
ELITISM_SIZE = 2
BACKGROUND_COLOR = (225, 225, 225)

# ===[ Função Principal ]=================================================================
def main():
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Consolas', 18)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DRE - Datacenter Resource Emulator")
    clock = pygame.time.Clock()

    datacenter_info = carregar_cenario(CENARIO_FILE)
    if not datacenter_info: return
        
    vms_a_alocar = datacenter_info['vms']
    servidores = datacenter_info['servidores']
    
    population = generate_round_robin_population(vms_a_alocar, servidores, POPULATION_SIZE)
    best_fitness_history = []
    best_solution_this_gen = population[0]
    
    generation_count = 0
    running = True
    last_best_fitness = float('inf')
    generations_without_improvement = 0
    
    scroll_x = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            if event.type == pygame.MOUSEWHEEL:
                scroll_x -= event.y * 40
        
        if not (generation_count >= N_GENERATIONS or generations_without_improvement >= MAX_GENS_NO_IMPROVEMENT):
            population_fitness = [calculate_fitness(individual, vms_a_alocar, servidores) for individual in population]
            
            sorted_pairs = sorted(zip(population_fitness, population), key=lambda pair: pair[0])
            sorted_population = [pair[1] for pair in sorted_pairs]
            sorted_fitness = [pair[0] for pair in sorted_pairs]
            
            best_solution_this_gen = sorted_population[0]
            best_fitness_this_gen = sorted_fitness[0]
            
            best_fitness_history.append(best_fitness_this_gen)
            
            if generation_count % 10 == 0:
                print(f"Geração {generation_count}: Melhor Fitness = {best_fitness_this_gen}")

            if best_fitness_this_gen < last_best_fitness:
                last_best_fitness = best_fitness_this_gen
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1

            if generations_without_improvement >= MAX_GENS_NO_IMPROVEMENT:
                print(f"\nConvergência atingida na Geração {generation_count}!")
            
            new_population = []
            new_population.extend(sorted_population[:ELITISM_SIZE])
            while len(new_population) < POPULATION_SIZE:
                # CORREÇÃO AQUI: Passando a lista 'sorted_fitness' como o segundo argumento
                parent1, parent2 = select_parents(sorted_population, sorted_fitness)
                child1, child2 = crossover_por_consenso(parent1, parent2, vms_a_alocar, servidores)
                child1 = swap_mutation(child1, vms_a_alocar, servidores, MUTATION_PROBABILITY)
                child2 = swap_mutation(child2, vms_a_alocar, servidores, MUTATION_PROBABILITY)
                new_population.append(child1)
                if len(new_population) < POPULATION_SIZE:
                    new_population.append(child2)
            population = new_population
            generation_count += 1
        
        screen.fill(BACKGROUND_COLOR)
        scroll_x = draw_datacenter_state(screen, font, servidores, best_solution_this_gen, vms_a_alocar, PLOT_X_OFFSET, scroll_x)
        plot_width = draw_fitness_plot(screen, best_fitness_history, PLOT_X_OFFSET)
        draw_stats_box(screen, font, generation_count, best_fitness_history[-1] if best_fitness_history else 0, PLOT_X_OFFSET, plot_width)
        pygame.display.flip()
        
        clock.tick(FPS)

    print("Simulação finalizada.")
    print(f"Melhor solução final encontrada (fitness): {best_fitness_history[-1] if best_fitness_history else 'N/A'}")
    
    waiting_for_exit = True
    while waiting_for_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                waiting_for_exit = False
            if event.type == pygame.MOUSEWHEEL:
                scroll_x -= event.y * 40
        
        screen.fill(BACKGROUND_COLOR)
        scroll_x = draw_datacenter_state(screen, font, servidores, best_solution_this_gen, vms_a_alocar, PLOT_X_OFFSET, scroll_x)
        plot_width = draw_fitness_plot(screen, best_fitness_history, PLOT_X_OFFSET)
        draw_stats_box(screen, font, generation_count, best_fitness_history[-1] if best_fitness_history else 0, PLOT_X_OFFSET, plot_width)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
