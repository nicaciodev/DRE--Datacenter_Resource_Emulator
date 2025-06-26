# -*- coding: utf-8 -*-
"""
Arquivo Principal do Projeto DRE (Datacenter Resource Emulator)
Este script orquestra a simulação, inicializa o Pygame, carrega o cenário,
executa o Algoritmo Genético e renderiza a visualização.
"""

# ===[ Importações ]======================================================================
import pygame
import sys
from datacenter_model import carregar_cenario
from genetic_algorithm import (
    generate_initial_population,
    calculate_fitness,
    select_parents,
    crossover,
    mutate
)
from visualization import draw_datacenter_state, draw_fitness_plot

# ===[ Constantes ]=======================================================================
WIDTH, HEIGHT = 1600, 900
FPS = 10
PLOT_X_OFFSET = 1180
CENARIO_FILE = 'cenario_teste.json'
POPULATION_SIZE = 100
N_GENERATIONS = 1000
MUTATION_PROBABILITY = 0.1
ELITISM_SIZE = 2
WHITE = (255, 255, 255)
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
    # TEST: Visualizando: datacenter_info.
    # print('>>> Cenário >>> ', datacenter_info)
    # exit()

    if not datacenter_info:
        print("Falha ao carregar o cenário. Encerrando o programa.")
        return
    
    # Separando VMs e Servidores:
    vms_a_alocar = datacenter_info['vms'] 
    servidores = datacenter_info['servidores']
    # TEST: Visualizando: vms e servidores:
    # Exemplo: VMs>> Obj.: VM(ID: 0, CPU: 4, RAM: 16GB) 
    # print('>>> VMS >>> ', vms_a_alocar)
    # print('-' * 50)
    # Exemplo: Servidores>> Obj.: Servidor(ID: 0, CPU: 0/32, RAM: 0/128GB, VMs: 0) 
    # print('>>> Servidores >>> ', servidores)
    # exit()
    
    # --- 2. Setup do Algoritmo Genético ---
    # WARN: Cria uma população constituída somente de servidores.
    #              \
    #              \/
    population = generate_initial_population(vms_a_alocar, servidores, POPULATION_SIZE) 
    # NOTE:         /\
    #               |
    #     A forma de criar a população dessa função [generate_initial_population] é aleatória.
    #     Não há uma checagem por indivíduos válidos.

    # TEST: Visualizando: a população.
    # Exemplo: [1, 1, 1, 2, 0, 1, 2, 2, 0, 2, 1]
    # print('>>> População >>> ', population)
    # exit()

    best_fitness_history = []
    
    # --- 3. Loop Principal da Simulação ---
    generation_count = 0
    running = True
    while running and generation_count < N_GENERATIONS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False

        # --- Lógica do Algoritmo Genético a cada Geração ---
        population_fitness = [calculate_fitness(individual, vms_a_alocar, servidores) for individual in population] 
        # NOTE:                   /\
        #                         |
        #     [calculate_fitness], quando identifica um indivíduo inválido, marca com o valor infinito.
        #     A população fitness conterá valores inválidos.

        # Organizando os pares pelo fitness
        sorted_pairs = sorted(zip(population_fitness, population), key=lambda pair: pair[0])
        # TEST: Verificando valores:
        # Exemplos: >>> population_fitness: [3.0, 3.0, inf, 3.0,
        #           >>> population: [[1, 2, 1, 0, 1, 0, 1, 1, 1, 2, 2], [0, 0, 1,
        #           >>> zip: [(3.0, [2, 2, 0, 1, 2, 1, 2, 1, 1, 2, 1]), (3.0, [0, 1, 2, 2, 1,
        # print(f'''
        # >>> population_fitness: {population_fitness}
        # {'-' * 50}
        # >>> population: {population}
        # {'-' * 50}
        # >>> zip: {list(zip(population_fitness, population))}
        # ''')
        # exit()

        # Separando população e fitness já ornagizados:
        sorted_population = [pair[1] for pair in sorted_pairs]
        sorted_fitness = [pair[0] for pair in sorted_pairs]
        
        # Coletando apenas os melhores:
        best_solution_this_gen = sorted_population[0]
        best_fitness_this_gen = sorted_fitness[0]
        best_fitness_history.append(best_fitness_this_gen)
        
        if generation_count % 10 == 0:
            print(f"Geração {generation_count}: Melhor Fitness = {best_fitness_this_gen}")

        new_population = []
        new_population.extend(sorted_population[:ELITISM_SIZE])

        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = select_parents(sorted_population, sorted_fitness)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1, servidores, MUTATION_PROBABILITY)
            child2 = mutate(child2, servidores, MUTATION_PROBABILITY)
            new_population.append(child1)
            if len(new_population) < POPULATION_SIZE:
                new_population.append(child2)

        population = new_population
        generation_count += 1
        
        # --- Lógica de Visualização (Pygame) ---
        screen.fill(WHITE)
        
        # ALTERAÇÃO AQUI: Passando a constante PLOT_X_OFFSET como argumento
        draw_datacenter_state(screen, font, servidores, best_solution_this_gen, vms_a_alocar, PLOT_X_OFFSET)
        draw_fitness_plot(screen, best_fitness_history, PLOT_X_OFFSET)

        pygame.display.flip()
        clock.tick(FPS)

    # --- 4. Finalização ---
    print("Simulação finalizada.")
    print(f"Melhor solução final encontrada (fitness): {best_fitness_history[-1] if best_fitness_history else 'N/A'}")
    input("Pressione [Enter] no console para encerrar.")
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
