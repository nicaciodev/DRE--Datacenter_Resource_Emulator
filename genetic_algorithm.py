"""
Módulo que contém a lógica principal do Algoritmo Genético para o projeto DRE.

Este arquivo define as funções para:
- Criar a população inicial.
- Calcular o fitness de uma solução.
- Selecionar os pais para reprodução.
- Realizar o crossover entre os pais.
- Aplicar mutação em um indivíduo.
"""



# Importando
import random
import copy
from typing import List, Tuple, Dict, Any

# Importa as classes do modelo de datacenter
from datacenter_model import MaquinaVirtual, ServidorFisico



# ===[ 1. Geração da População Inicial ]================================================

def generate_round_robin_population(vms: List[MaquinaVirtual], servidores: List[ServidorFisico], size: int) -> List[List[int]]:
    """
    Gera uma população homogênea onde todas as VMs são distribuídas
    de forma sequencial (Round-Robin) entre os servidores.

    Isso resulta em uma solução inicial que usa muitos servidores, ideal
    para demonstrar a otimização do AG ao longo do tempo.
    """
    num_servidores = len(servidores)
    num_vms = len(vms)
    
    # 1. Cria UMA única solução base usando a lógica Round-Robin com verificação de capacidade
    base_individual = [-1] * num_vms
    temp_servidores = copy.deepcopy(servidores)

    for vm_index in range(num_vms):
        vm_a_alocar = vms[vm_index]
        vm_alocada = False
        
        # NOTE: Esta forma de alocar tem viés na ordem dos servidores
        # Tenta alocar a VM no servidor correspondente ao seu índice, em ciclo
        for i in range(num_servidores):
            # O operador % faz o ciclo: 0, 1, 2, 3, 4, 0, 1, 2...
            servidor_id_alvo = (vm_index + i) % num_servidores
            if temp_servidores[servidor_id_alvo].pode_hospedar(vm_a_alocar):
                temp_servidores[servidor_id_alvo].alocar_vm(vm_a_alocar)
                base_individual[vm_index] = servidor_id_alvo
                vm_alocada = True
                break # VM alocada com sucesso, passa para a próxima VM

        # # HACK: Usando a lógica "Worst Fit"
        # # Ordena os servidores pelo maior espaço de RAM livre
        # # Com tudo, isso 
        # servidores_disponiveis_ordenados = sorted(
        #     range(num_servidores),
        #     key=lambda s_id: temp_servidores[s_id].ram_disponivel,
        #     reverse=True
        # )
        # # Itera sobre os servidores na ordem do mais folgado para o mais cheio
        # for servidor_id in servidores_disponiveis_ordenados:
        #     if temp_servidores[servidor_id].pode_hospedar(vm_a_alocar):
        #         temp_servidores[servidor_id].alocar_vm(vm_a_alocar)
        #         base_individual[vm_index] = servidor_id
        #         vm_alocada = True
        #         break

        if not vm_alocada:
            print(f"AVISO EM ROUND-ROBIN: A VM {vm_a_alocar.id} não pôde ser alocada em nenhum servidor.")

    # 2. Cria a população final replicando a solução base
    population = [list(base_individual) for _ in range(size)]
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
    # TODO: Das melhores soluções, também escolher as que usam o máximo de um servidor, leberando
    # recursos dos oustros servidores que também fazem parte da solução sub-ótima.
    
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

def crossover_por_consenso(parent1: List[int], parent2: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> Tuple[List[int], List[int]]:
    """
    Realiza um Crossover de Particionamento por Consenso.
    Este método garante que os filhos gerados sejam sempre válidos.
    """
    
    # --- Filho 1 ---
    child1, _ = criar_filho_cpc(parent1, parent2, vms, servidores)
    
    # --- Filho 2 ---
    # Para o segundo filho, podemos inverter a ordem dos pais para gerar diversidade
    child2, _ = criar_filho_cpc(parent2, parent1, vms, servidores)

    return child1, child2

def criar_filho_cpc(pai_base: List[int], pai_guia: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]):
    """
    Função auxiliar que cria um único filho usando a lógica CPC.
    Crossover de Particionamento por Consenso
    """
    num_vms = len(vms)
    filho = [-1] * num_vms # Preenche o filho inicialmente com valores inválidos.
    
    # 1. Particionamento: Encontra o consenso e o conflito
    vms_consenso_indices = {i for i in range(num_vms) if pai_base[i] == pai_guia[i]}
    vms_conflito_indices = [i for i in range(num_vms) if i not in vms_consenso_indices]
    
    # Embaralha a ordem de alocação do conflito para adicionar aleatoriedade
    random.shuffle(vms_conflito_indices)

    # 2. Construção da Base do Filho com o Consenso
    temp_servidores = copy.deepcopy(servidores)
    for vm_idx in vms_consenso_indices:
        servidor_id = pai_base[vm_idx]
        filho[vm_idx] = servidor_id
        temp_servidores[servidor_id].alocar_vm(vms[vm_idx])

    # NOTE: Esta forma tem viés com a ordem dos servidores.
    # # 3. Alocação Inteligente do Conflito usando First Fit
    # for vm_idx in vms_conflito_indices:
    #     vm_alocada = False
    #     for servidor_id in range(len(servidores)):
    #         if temp_servidores[servidor_id].pode_hospedar(vms[vm_idx]):
    #             filho[vm_idx] = servidor_id
    #             temp_servidores[servidor_id].alocar_vm(vms[vm_idx])
    #             vm_alocada = True
    #             break

    # HACK: Lógica "Worst Fit": Ordena os servidores.
    for vm_idx in vms_conflito_indices:
        vm_a_alocar = vms[vm_idx]
        vm_alocada = False
        
        # LÓGICA "WORST FIT" REFINADA: Ordena por RAM livre e depois por CPU livre
        servidores_disponiveis_ordenados = sorted(
            range(len(servidores)),
            key=lambda s_id: (temp_servidores[s_id].ram_disponivel, temp_servidores[s_id].cpu_disponivel),
            reverse=True
        )

        for servidor_id in servidores_disponiveis_ordenados:
            if temp_servidores[servidor_id].pode_hospedar(vm_a_alocar):
                filho[vm_idx] = servidor_id
                temp_servidores[servidor_id].alocar_vm(vm_a_alocar)
                vm_alocada = True
                break
        
        if not vm_alocada:
            print(f"AVISO EM CROSSOVER: Não foi possível alocar a VM de conflito {vm_idx}.")
            # Se não couber em lugar nenhum, alocamos em um lugar aleatório (gerando um indivíduo inválido que será punido)
            filho[vm_idx] = random.randint(0, len(servidores) - 1)


    return filho, temp_servidores



# ===[ 5. Mutação ]======================================================================

def swap_mutation(individual: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico], probability: float) -> List[int]:
    """
    Realiza a mutação de troca entre duas VMs, garantindo a validade da solução.
    """
    mutated_individual = list(individual)
    if random.random() < probability and len(vms) >= 2:
        # 1. Sorteia dois índices de VM diferentes
        vm_index_1, vm_index_2 = random.sample(range(len(vms)), 2)

        # 2. Pega as informações sobre as VMs e seus servidores atuais
        server_id_1 = mutated_individual[vm_index_1]
        server_id_2 = mutated_individual[vm_index_2]

        # Não faz sentido trocar VMs que já estão no mesmo servidor
        if server_id_1 == server_id_2:
            return mutated_individual

        vm1 = vms[vm_index_1]
        vm2 = vms[vm_index_2]
        servidor1 = servidores[server_id_1]
        servidor2 = servidores[server_id_2]

        # 3. Simula o estado dos servidores APÓS a troca
        # Carga atual do Servidor 1 SEM a VM1, mas COM a VM2
        nova_cpu_s1 = sum(vms[i].cpu_req for i, s_id in enumerate(mutated_individual) if s_id == server_id_1 and i != vm_index_1) + vm2.cpu_req
        nova_ram_s1 = sum(vms[i].ram_req for i, s_id in enumerate(mutated_individual) if s_id == server_id_1 and i != vm_index_1) + vm2.ram_req

        # Carga atual do Servidor 2 SEM a VM2, mas COM a VM1
        nova_cpu_s2 = sum(vms[i].cpu_req for i, s_id in enumerate(mutated_individual) if s_id == server_id_2 and i != vm_index_2) + vm1.cpu_req
        nova_ram_s2 = sum(vms[i].ram_req for i, s_id in enumerate(mutated_individual) if s_id == server_id_2 and i != vm_index_2) + vm1.ram_req

        # 4. Verifica se a troca é válida
        if (nova_cpu_s1 <= servidor1.cpu_total and nova_ram_s1 <= servidor1.ram_total and
            nova_cpu_s2 <= servidor2.cpu_total and nova_ram_s2 <= servidor2.ram_total):
            
            # 5. Se for válida, aplica a troca
            mutated_individual[vm_index_1] = server_id_2
            mutated_individual[vm_index_2] = server_id_1

    return mutated_individual

