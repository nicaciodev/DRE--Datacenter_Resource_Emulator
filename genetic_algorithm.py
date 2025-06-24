# -*- coding: utf-8 -*-
"""
Módulo que contém a lógica principal do Algoritmo Genético para o projeto DRE.

Este arquivo define as funções para:
- Criar a população inicial.
- Calcular o fitness de uma solução.
- Selecionar os pais para reprodução.
- Realizar o crossover entre os pais.
- Aplicar mutação em um indivíduo.
"""

import random
import copy
from typing import List, Tuple, Dict, Any

# Importa as classes do nosso modelo de datacenter
from datacenter_model import MaquinaVirtual, ServidorFisico


# ===[ 1. Geração da População Inicial ]================================================

def generate_initial_population(vms: List[MaquinaVirtual], servidores: List[ServidorFisico], size: int) -> List[List[int]]:
    """
    Gera uma população inicial de soluções (indivíduos) de forma aleatória.

    Args:
        vms (List[MaquinaVirtual]): A lista de VMs a serem alocadas.
        servidores (List[ServidorFisico]): A lista de servidores físicos disponíveis.
        size (int): O tamanho da população a ser gerada.

    Returns:
        List[List[int]]: Uma lista de indivíduos. Cada indivíduo é uma lista onde o
                         índice representa a VM e o valor o ID do servidor.
    """
    population = []
    num_servidores = len(servidores)
    num_vms = len(vms)

    for _ in range(size):
        # Para cada indivíduo, cria uma nova alocação aleatória
        individual = [random.randint(0, num_servidores - 1) for _ in range(num_vms)]
        population.append(individual)
        
    return population


# ===[ 2. Função de Fitness ]===========================================================

def calculate_fitness(individual: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> float:
    """
    Calcula o fitness de um único indivíduo.

    O fitness é baseado no número de servidores utilizados.
    Soluções que sobrecarregam servidores são invalidadas com uma penalidade altíssima.

    Args:
        individual (List[int]): A solução a ser avaliada.
        vms (List[MaquinaVirtual]): A lista de objetos VM.
        servidores (List[ServidorFisico]): A lista de objetos Servidor.

    Returns:
        float: O valor de fitness. Menor é melhor. Retorna infinito para soluções inválidas.
    """
    # Usamos deepcopy para não alterar os objetos originais do servidor a cada simulação
    temp_servidores = copy.deepcopy(servidores)
    
    # Simula a alocação do indivíduo
    for vm_index, servidor_id in enumerate(individual):
        vm_a_alocar = vms[vm_index]
        servidor_alvo = temp_servidores[servidor_id]
        
        # Verifica se o servidor tem capacidade. Se não tiver, a solução é inválida.
        if not servidor_alvo.pode_hospedar(vm_a_alocar):
            return float('inf')  # Penalidade máxima para soluções inválidas
        
        # Se puder, aloca a VM no servidor temporário
        servidor_alvo.alocar_vm(vm_a_alocar)

    # O fitness primário é o número de servidores que foram utilizados
    servidores_usados = sum(1 for s in temp_servidores if len(s.vms_hospedadas) > 0)
    
    # TODO: (Opcional Avançado): Adicionar um fator de balanceamento como objetivo secundário
    # Ex: calcular o desvio padrão do uso de CPU/RAM e adicionar ao fitness
    # fitness = servidores_usados + desvio_padrao_carga * 0.1
    
    return float(servidores_usados)


# ===[ 3. Seleção dos Pais ]=============================================================

def select_parents(population: List[List[int]], fitness_scores: List[float], num_parents: int = 2) -> List[List[int]]:
    """
    Seleciona os pais da população para o crossover.
    Uma forma simples é a seleção por torneio.
    """
    # Para simplificar, vamos usar uma seleção elitista: escolher aleatoriamente
    # entre os 10% melhores da população.
    # A população já deve vir ordenada do melhor para o pior.
    pool_size = len(population) // 10  # Usa os 10% melhores
    if pool_size < 2:
        pool_size = 2 # Garante que tenhamos pelo menos 2 no pool

    selection_pool = population[:pool_size]
    
    parents = random.sample(selection_pool, k=num_parents)
    return parents


# ===[ 4. Crossover ]===================================================================

def crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Realiza o crossover de ponto único entre dois pais para gerar dois filhos.
    """
    size = len(parent1)
    if size < 2:
        return parent1, parent2

    # Escolhe um ponto de corte aleatório
    crossover_point = random.randint(1, size - 1)

    # Gera os dois filhos combinando as partes dos pais
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]

    return child1, child2


# ===[ 5. Mutação ]======================================================================

def mutate(individual: List[int], servidores: List[ServidorFisico], probability: float) -> List[int]:
    """
    Aplica uma mutação em um indivíduo com uma dada probabilidade.
    A mutação consiste em mover uma VM para um novo servidor aleatório.
    """
    mutated_individual = list(individual)
    num_servidores = len(servidores)

    if random.random() < probability:
        # Escolhe uma VM aleatória para mover
        vm_index = random.randint(0, len(mutated_individual) - 1)
        
        # Escolhe um novo servidor aleatório para onde mover
        # Garante que o novo servidor seja diferente do atual
        current_server = mutated_individual[vm_index]
        new_server = random.choice([i for i in range(num_servidores) if i != current_server])
        
        # Aplica a mutação
        mutated_individual[vm_index] = new_server
        
    return mutated_individual
