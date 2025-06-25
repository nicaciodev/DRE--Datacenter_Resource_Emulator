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

# Importa as classes do modelo de datacenter
from datacenter_model import MaquinaVirtual, ServidorFisico


# ===[ 1. Geração da População Inicial ]================================================

def generate_smarter_population(vms: List[MaquinaVirtual], servidores: List[ServidorFisico], size: int) -> List[List[int]]:
    """
    Gera uma população inicial onde cada indivíduo é uma solução válida.
    Usa uma abordagem "First Fit" com aleatoriedade para garantir diversidade.
    """
    population = []
    num_servidores = len(servidores)
    
    for _ in range(size):
        individual = [-1] * len(vms)  # Inicia o indivíduo com valores inválidos
        
        # Embaralha a ordem das VMs para cada novo indivíduo para criar diversidade
        vm_indices_embaralhados = list(range(len(vms)))
        random.shuffle(vm_indices_embaralhados)

        # Copia os servidores para simular a alocação para este indivíduo
        temp_servidores = copy.deepcopy(servidores)

        # Aplica a lógica "First Fit"
        for vm_index in vm_indices_embaralhados:
            vm_alocada = False
            for servidor_index in range(num_servidores):
                if temp_servidores[servidor_index].pode_hospedar(vms[vm_index]):
                    temp_servidores[servidor_index].alocar_vm(vms[vm_index])
                    individual[vm_index] = servidor_index
                    vm_alocada = True
                    break # VM alocada, passa para a próxima
            
            if not vm_alocada:
                # Este caso é raro, mas pode acontecer se uma única VM for maior que qualquer servidor
                print(f"AVISO: A VM {vms[vm_index].id} não pôde ser alocada em nenhum servidor.")

        population.append(individual)
        
    return population

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

def uniform_crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Realiza o Uniform Crossover, onde cada gene do filho tem 50% de chance
    de vir do Pai 1 ou do Pai 2. Este método promove mais mistura.
    """
    size = len(parent1)
    child1 = [-1] * size
    child2 = [-1] * size
    for i in range(size):
        if random.random() < 0.5:
            child1[i] = parent1[i]
            child2[i] = parent2[i]
        else:
            child1[i] = parent2[i]
            child2[i] = parent1[i]
    return child1, child2

def repair_individual(individual: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> List[int]:
    """
    Repara um indivíduo para garantir que ele seja válido (não sobrecarregue servidores).
    """
    repaired_individual = list(individual)
    
    # 1. Simula o estado atual do indivíduo para encontrar servidores sobrecarregados
    temp_servidores = {i: [] for i in range(len(servidores))}
    for vm_idx, s_id in enumerate(repaired_individual):
        temp_servidores[s_id].append(vms[vm_idx])

    # 2. Itera para encontrar e corrigir sobrecargas
    for s_id, vms_alocadas in temp_servidores.items():
        servidor = servidores[s_id]
        
        # Calcula o uso atual
        cpu_usada = sum(vm.cpu_req for vm in vms_alocadas)
        ram_usada = sum(vm.ram_req for vm in vms_alocadas)

        # Enquanto o servidor estiver sobrecarregado
        while cpu_usada > servidor.cpu_total or ram_usada > servidor.ram_total:
            # Pega uma VM aleatória deste servidor sobrecarregado para mover
            vm_para_mover = random.choice(vms_alocadas)
            vm_idx_original = [i for i, vm in enumerate(vms) if vm.id == vm_para_mover.id][0]

            # Encontra um novo lar em um servidor menos cheio
            # Ordena os outros servidores pelo uso de CPU (ou RAM), do menor para o maior
            outros_servidores_ids = sorted(
                [i for i in range(len(servidores)) if i != s_id],
                key=lambda j: sum(vm.cpu_req for vm in temp_servidores[j])
            )

            # Tenta mover a VM
            movida = False
            for new_s_id in outros_servidores_ids:
                # Verifica se o novo servidor pode hospedar a VM
                new_servidor = servidores[new_s_id]
                new_cpu_usada = sum(vm.cpu_req for vm in temp_servidores[new_s_id])
                new_ram_usada = sum(vm.ram_req for vm in temp_servidores[new_s_id])
                
                if (new_cpu_usada + vm_para_mover.cpu_req <= new_servidor.cpu_total and
                    new_ram_usada + vm_para_mover.ram_req <= new_servidor.ram_total):
                    
                    # Move a VM
                    repaired_individual[vm_idx_original] = new_s_id
                    
                    # Atualiza nossas listas temporárias para o próximo loop de verificação
                    vms_alocadas.remove(vm_para_mover)
                    temp_servidores[new_s_id].append(vm_para_mover)
                    
                    # Recalcula o uso do servidor original
                    cpu_usada = sum(vm.cpu_req for vm in vms_alocadas)
                    ram_usada = sum(vm.ram_req for vm in vms_alocadas)
                    movida = True
                    break
            
            if not movida:
                # Se não conseguiu mover, pode indicar um problema sério (ex: não há espaço em lugar nenhum)
                # Para agora, vamos apenas parar de tentar reparar este servidor.
                break
                
    return repaired_individual

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

def smart_mutate(individual: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico], probability: float) -> List[int]:
    """
    Aplica uma mutação inteligente que garante que o filho resultante seja válido.
    """
    mutated_individual = list(individual)
    
    if random.random() < probability:
        # 1. Escolhe uma VM aleatória para mover
        vm_index_to_move = random.randint(0, len(mutated_individual) - 1)
        vm_to_move = vms[vm_index_to_move]
        current_server_id = mutated_individual[vm_index_to_move]

        # 2. Encontra uma lista de servidores alternativos que podem hospedar a VM
        possible_new_homes = []
        for i, servidor in enumerate(servidores):
            # Não pode ser o mesmo servidor e precisa ter capacidade
            if i != current_server_id:
                # Simula a alocação para verificar a capacidade futura
                # Cria uma cópia para não interferir nos cálculos de outros servidores
                temp_servidor = copy.deepcopy(servidor)
                
                # Aloca temporariamente as VMs que já estão neste servidor
                vms_on_this_server = [vms[idx] for idx, s_id in enumerate(individual) if s_id == i]
                for vm in vms_on_this_server:
                    temp_servidor.alocar_vm(vm)
                
                # Agora verifica se a nova VM cabe
                if temp_servidor.pode_hospedar(vm_to_move):
                    possible_new_homes.append(i)

        # 3. Se encontrou um novo lar possível, move a VM
        if possible_new_homes:
            new_server_id = random.choice(possible_new_homes)
            mutated_individual[vm_index_to_move] = new_server_id
            
    return mutated_individual

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
