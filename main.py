# -*- coding: utf-8 -*-
"""
Arquivo Principal do Projeto DRE (Datacenter Resource Emulator)
Este script orquestra a simulação, inicializa o Pygame, carrega o cenário,
executa o Algoritmo Genético e renderiza a visualização.
"""

# ===[ Importações ]======================================================================
import pygame
import sys
import random
import numpy as np
from datacenter_model import carregar_cenario
from genetic_algorithm import (
    generate_round_robin_population,
    swap_mutation,
    crossover_por_consenso,
    repair_individual,
    uniform_crossover,
    smart_mutate,
    generate_smarter_population,
    generate_initial_population,
    calculate_fitness,
    select_parents,
    crossover,
    mutate
)
from visualization import draw_datacenter_state, draw_fitness_plot, draw_stats_box

# ===[ Constantes ]=======================================================================
WIDTH, HEIGHT = 1490, 750
FPS = 10
PLOT_X_OFFSET = 1070

# NOTE: Cenário pequeno.
# CENARIO_FILE = 'cenario_teste.json'

# NOTE: Cenário grande.
CENARIO_FILE = 'cenario_desafiador.json'

POPULATION_SIZE = 100
N_GENERATIONS = 1000
MAX_GENS_NO_IMPROVEMENT = 200 # Para se não houver melhora por 200 gerações
MUTATION_PROBABILITY = 0.8
ELITISM_SIZE = 2
BACKGROUND_COLOR = (190, 190, 190)
BLACK = (0, 0, 0)

# ===[ Função Principal ]=================================================================
def main():
    """
    Função principal que inicializa e executa o simulador e o algoritmo genético.
    """
    # --- 1. Inicialização ---
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Consolas', 18)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DRE - Datacenter Resource Emulator")
    clock = pygame.time.Clock()

    datacenter_info = carregar_cenario(CENARIO_FILE)
    if not datacenter_info:
        print("Falha ao carregar o cenário. Encerrando o programa.")
        return
        
    vms_a_alocar = datacenter_info['vms']
    servidores = datacenter_info['servidores']
    
    # --- 2. Setup do Algoritmo Genético ---
    # NOTE: População inicial aleatória:
    # population = generate_initial_population(vms_a_alocar, servidores, POPULATION_SIZE)

    # NOTE: Gera população inicial válida:
    # population = generate_smarter_population(vms_a_alocar, servidores, POPULATION_SIZE)

    # PERF: Gera população com Round-Robin - normalmente distribuida:
    population = generate_round_robin_population(vms_a_alocar, servidores, POPULATION_SIZE)

    # TEST: Verificando o conetúdo populacional:
    # print(population)
    # print(f'''
    # Um indivíduo: {population[0]}
    # Tamanho: {len(population[0])}
    # ''')
    # exit()

    best_fitness_history = []
    
    # --- 3. Loop Principal da Simulação ---
    generation_count = 0
    running = True

    # NOTE: Para o critério de parada automático
    last_best_fitness = float('inf')
    generations_without_improvement = 0

    while running and generation_count < N_GENERATIONS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False

        # --- Lógica do Algoritmo Genético a cada Geração ---
        # TEST: Caos:
        # random.shuffle(population)

        population_fitness = [calculate_fitness(individual, vms_a_alocar, servidores) for individual in population]
        sorted_pairs = sorted(zip(population_fitness, population), key=lambda pair: pair[0])
        sorted_population = [pair[1] for pair in sorted_pairs]
        sorted_fitness = [pair[0] for pair in sorted_pairs]
        
        best_solution_this_gen = sorted_population[0]
        best_fitness_this_gen = sorted_fitness[0]
        best_fitness_history.append(best_fitness_this_gen)
        
        if generation_count % 10 == 0:
            print(f"Geração {generation_count}: Melhor Fitness = {best_fitness_this_gen}")

        # NOTE: Critério de parada automático:
        if best_fitness_this_gen < last_best_fitness:
            last_best_fitness = best_fitness_this_gen
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1

        if generations_without_improvement >= MAX_GENS_NO_IMPROVEMENT:
            print(f"\nConvergência atingida! Nenhuma melhora no fitness por {MAX_GENS_NO_IMPROVEMENT} gerações.")
            running = False # Encerra o loop

        new_population = []
        new_population.extend(sorted_population[:ELITISM_SIZE])

        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = select_parents(sorted_population, sorted_fitness)
            # TEST: Visualizando o parent1
            # print(f' parent1: {parent1}')
            # print(f' tamanho: {len(parent1)}')
            # input('>>> Pausa <<<')

            # WARN: Este crossover está gerando filhos inválidos:
            # child1, child2 = crossover(parent1, parent2)

            # WARN: Este crossover pode gerar filhos inválidos:
            child1, child2 = uniform_crossover(parent1, parent2)

            # NOTE: Reparo: Garante que os filhos se tornem válidos
            # WARN: Mas, não está entregando filhos válidos!
            # child1 = repair_individual(child1, vms_a_alocar, servidores)
            # child2 = repair_individual(child2, vms_a_alocar, servidores)

            # NOTE: Crossover por consenso
            child1, child2 = crossover_por_consenso(parent1, parent2, vms_a_alocar, servidores)

            # NOTE: Mutação aleatória:
            # child1 = mutate(child1, servidores, MUTATION_PROBABILITY)
            # child2 = mutate(child2, servidores, MUTATION_PROBABILITY)

            # NOTE: Mutação smart:
            # child1 = smart_mutate(child1, vms_a_alocar, servidores, MUTATION_PROBABILITY)
            # child2 = smart_mutate(child2, vms_a_alocar, servidores, MUTATION_PROBABILITY)

            # NOTE: Swap Mutation:
            child1 = swap_mutation(child1, vms_a_alocar, servidores, MUTATION_PROBABILITY)
            child2 = swap_mutation(child2, vms_a_alocar, servidores, MUTATION_PROBABILITY)

            new_population.append(child1)
            if len(new_population) < POPULATION_SIZE:
                new_population.append(child2)

        population = new_population
        generation_count += 1
        
        # --- Lógica de Visualização (Pygame) ---
        screen.fill(BACKGROUND_COLOR)
        
        # ALTERAÇÃO AQUI: Passando a constante PLOT_X_OFFSET como argumento
        draw_datacenter_state(screen, font, servidores, best_solution_this_gen, vms_a_alocar, PLOT_X_OFFSET)
        draw_fitness_plot(screen, best_fitness_history, PLOT_X_OFFSET)
        draw_stats_box(screen, font, generation_count, best_fitness_this_gen, PLOT_X_OFFSET)

        pygame.display.flip()
        clock.tick(FPS)

    # --- 4. Finalização ---
    print("Simulação finalizada.")
    print(f"Melhor solução final encontrada (fitness): {best_fitness_history[-1] if best_fitness_history else 'N/A'}")

    # Loop de espera para manter a janela final aberta e responsiva
    waiting_for_exit = True
    while waiting_for_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_for_exit = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    waiting_for_exit = False
        
        # O clock.tick() aqui é importante para não usar 100% da CPU enquanto espera
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
