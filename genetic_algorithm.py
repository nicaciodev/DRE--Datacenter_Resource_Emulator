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

# Em genetic_algorithm.py, substitua a função generate_round_robin_population

def generate_round_robin_population(vms: List[MaquinaVirtual], servidores: List[ServidorFisico], size: int) -> List[List[int]]:
    """
    Gera uma população inicial distribuindo as VMs em Round-Robin.
    VERSÃO ATUALIZADA: Manipula diretamente o estado dos objetos 'servidores'
    e os limpa após a criação da solução base.
    """
    num_servidores = len(servidores)
    num_vms = len(vms)
    
    # Garante que todos os servidores estão vazios antes de começar.
    for s in servidores:
        s.resetar()

    # 1. Cria UMA única solução base usando os objetos de servidor reais.
    base_individual = [-1] * num_vms

    for vm_index in range(num_vms):
        vm_a_alocar = vms[vm_index]
        vm_alocada = False
        
        for i in range(num_servidores):
            # O operador % faz o ciclo: 0, 1, 2, 0, 1, 2...
            servidor_id_alvo = (vm_index + i) % num_servidores
            servidor_alvo = servidores[servidor_id_alvo]
            
            if servidor_alvo.pode_hospedar(vm_a_alocar):
                servidor_alvo.alocar_vm(vm_a_alocar)
                base_individual[vm_index] = servidor_alvo.id
                vm_alocada = True
                break # VM alocada com sucesso, passa para a próxima VM

        if not vm_alocada:
            print(f"AVISO EM ROUND-ROBIN: A VM {vm_a_alocar.id} não pôde ser alocada em nenhum servidor.")

    # 2. ETAPA CRUCIAL: Limpa o estado de todos os servidores.
    # Após construir a solução, resetamos os servidores para que o AG
    # comece a trabalhar com um datacenter "limpo".
    for s in servidores:
        s.resetar()

    # 3. Cria a população final replicando a solução base.
    population = [list(base_individual) for _ in range(size)]
    return population


# ===[ 2. Função de Fitness ]===========================================================

def calculate_fitness(individual: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> float:
    """
    Calcula o fitness de um indivíduo seguindo o modelo "Lousa Limpa".
    1. Reseta o estado dos servidores.
    2. Simula a alocação do indivíduo.
    3. Retorna o número de servidores usados ou infinito se a solução for inválida.
    """
    # PASSO 1: Prepara a "Lousa Limpa"
    # Garante que todos os servidores estão vazios antes de começar a avaliação.
    for s in servidores:
        s.resetar()

    # PASSO 2: Simula a alocação do indivíduo nos objetos reais
    for vm_index, servidor_id in enumerate(individual):
        vm_a_alocar = vms[vm_index]
        
        # Checagem de segurança para IDs inválidos no cromossomo
        if not (0 <= servidor_id < len(servidores)):
            return float('inf') 

        servidor_alvo = servidores[servidor_id]
        
        # Validação: O servidor alvo tem capacidade?
        if not servidor_alvo.pode_hospedar(vm_a_alocar):
            return float('inf') # Penalidade máxima para soluções inválidas
        
        # Se for válido, aloca a VM
        servidor_alvo.alocar_vm(vm_a_alocar)

    # PASSO 3: Calcula o resultado
    # O fitness é o número de servidores que foram utilizados nesta simulação.
    servidores_usados = sum(1 for s in servidores if s.vms_hospedadas)
    
    return float(servidores_usados)

# ===[ 3. Seleção dos Pais ]=============================================================

def select_parents(population: List[List[int]],  num_parents: int = 2) -> List[List[int]]:
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

def doac_cross(parent1: List[int], parent2: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> Tuple[List[int], List[int]]:
    """
    Dominant Optimal Anti-Cancer
    Função principal do Crossover DOAC v4.
    Orquestra a criação de dois filhos, cada um baseado em um dos pais,
    """
    # Cria o primeiro filho usando o Pai 1 como referência principal
    child1 = _criar_filho_doac(parent1, parent2, vms, servidores)
    
    # Cria o segundo filho invertendo os papéis para gerar diversidade
    child2 = _criar_filho_doac(parent2, parent1, vms, servidores)

    return child1, child2


def _criar_filho_doac(pai: List[int], mae: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> List[int]:
    """
    Cria um filho usando a lógica DOAC (Dominant Optimal Anti-Cancer)
    seguindo o modelo "Lousa Limpa" - VERSÃO FINAL E ROBUSTA.
    """
    num_vms = len(vms)
    
    # PASSO 1: Identifica o melhor dos pais
    fitness_pai = calculate_fitness(pai, vms, servidores)
    fitness_mae = calculate_fitness(mae, vms, servidores)
    melhor_pai = pai if fitness_pai <= fitness_mae else mae

    # --- Início da Construção do Filho ---
    filho = [-1] * num_vms
    
    # Limpa os servidores para iniciar a construção do zero ("Lousa Limpa").
    for s in servidores:
        s.resetar()
            
    # PASSO 2: Aplica o Gene Dominante
    servidores_ativos_melhor_pai = {s_id for s_id in melhor_pai if s_id != -1}
    if servidores_ativos_melhor_pai:
        id_servidor_dominante = max(servidores_ativos_melhor_pai, key=lambda s_id: servidores[s_id].cpu_total + servidores[s_id].ram_total)
        for vm_idx, s_id in enumerate(melhor_pai):
            if s_id == id_servidor_dominante:
                servidores[id_servidor_dominante].alocar_vm(vms[vm_idx])
                filho[vm_idx] = id_servidor_dominante

    # PASSO 3: Construção Alternada do Restante do Filho
    for i in range(num_vms):
        if filho[i] == -1:
            genitor = pai if i % 2 == 0 else mae
            servidor_proposto_id = genitor[i]
            vm_a_alocar = vms[i]
            if 0 <= servidor_proposto_id < len(servidores) and servidores[servidor_proposto_id].pode_hospedar(vm_a_alocar):
                servidores[servidor_proposto_id].alocar_vm(vm_a_alocar)
                filho[i] = servidor_proposto_id
            else:
                for s in sorted(servidores, key=lambda srv: srv.ram_disponivel, reverse=True):
                    if s.pode_hospedar(vm_a_alocar):
                        s.alocar_vm(vm_a_alocar)
                        filho[i] = s.id
                        break
    
    # PASSO 4: Tratamento Anti-Câncer (Lógica Robusta)
    servidores_ativos_filho = {s_id for s_id in filho if s_id != -1}
    if len(servidores_ativos_filho) > 1:
        id_cancer = min(servidores_ativos_filho, key=lambda s_id: servidores[s_id].cpu_total + servidores[s_id].ram_total)
        servidor_cancer = servidores[id_cancer]
        vms_no_cancer_idx = [i for i, s_id in enumerate(filho) if s_id == id_cancer]
        servidores_alvo = sorted([s for s in servidores if s.id in servidores_ativos_filho and s.id != id_cancer], key=lambda srv: srv.ram_disponivel, reverse=True)
        
        filho_reparado = list(filho)
        sucesso_reparo_total = True
        
        for vm_idx in vms_no_cancer_idx:
            vm_a_mover_obj = vms[vm_idx]
            alocado = False
            for novo_lar in servidores_alvo:
                if novo_lar.pode_hospedar(vm_a_mover_obj):
                    servidor_cancer.desalocar_vm(vm_a_mover_obj)
                    novo_lar.alocar_vm(vm_a_mover_obj)
                    filho_reparado[vm_idx] = novo_lar.id
                    alocado = True
                    break
            if not alocado:
                sucesso_reparo_total = False
                break
        
        # <<< MELHORIA DE ROBUSTEZ: Verifica o sucesso do reparo >>>
        if sucesso_reparo_total:
            # Se o reparo foi um sucesso, o 'filho' se torna a versão reparada.
            # O estado dos objetos 'servidores' já está correto.
            filho = filho_reparado
        else:
            # Se o reparo falhou, o 'filho' continua sendo o original (antes do reparo).
            # Para garantir a consistência, limpamos os servidores e reconstruímos
            # o estado para corresponder ao 'filho' original.
            for s in servidores:
                s.resetar()
            for vm_idx, s_id in enumerate(filho):
                if s_id != -1:
                    servidores[s_id].alocar_vm(vms[vm_idx])

    # PASSO 5: Validação Final
    for s in servidores:
        s.resetar()
        
    if -1 in filho:
        return melhor_pai
    else:
        return filho

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
    # 3. Alocação Inteligente do Conflito usando First Fit
    for vm_idx in vms_conflito_indices:
        vm_alocada = False
        for servidor_id in range(len(servidores)):
            if temp_servidores[servidor_id].pode_hospedar(vms[vm_idx]):
                filho[vm_idx] = servidor_id
                temp_servidores[servidor_id].alocar_vm(vms[vm_idx])
                vm_alocada = True
                break

    # HACK: Lógica "Worst Fit": Ordena os servidores.
    # for vm_idx in vms_conflito_indices:
    #     vm_a_alocar = vms[vm_idx]
    #     vm_alocada = False
    #     # LÓGICA "WORST FIT" REFINADA: Ordena por RAM livre e depois por CPU livre
    #     servidores_disponiveis_ordenados = sorted(
    #         range(len(servidores)),
    #         key=lambda s_id: (temp_servidores[s_id].ram_disponivel, temp_servidores[s_id].cpu_disponivel),
    #         reverse=True
    #     )
    #     for servidor_id in servidores_disponiveis_ordenados:
    #         if temp_servidores[servidor_id].pode_hospedar(vm_a_alocar):
    #             filho[vm_idx] = servidor_id
    #             temp_servidores[servidor_id].alocar_vm(vm_a_alocar)
    #             vm_alocada = True
    #             break
        
        if not vm_alocada:
            print(f"AVISO EM CROSSOVER: Não foi possível alocar a VM de conflito {vm_idx}.")
            # Se não couber em lugar nenhum, alocamos em um lugar aleatório (gerando um indivíduo inválido que será punido)
            filho[vm_idx] = random.randint(0, len(servidores) - 1)


    return filho, temp_servidores



# ===[ 5. Mutação ]======================================================================

def robin_hood_mutation(individual: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico], probability: float) -> List[int]:
    """
    Esta é uma mutação agressiva.
    Tenta consolidar o servidor menos utilizado ("pobre") movendo suas VMs
    para os servidores mais utilizados ("ricos").
    """
    if random.random() > probability:
        return individual

    # 1. Simula o estado e identifica servidores ativos e suas cargas
    temp_servidores = [ServidorFisico(s.id, s.cpu_total, s.ram_total) for s in servidores]
    servidores_em_uso = {} # {id_servidor: [lista de vms]}
    for vm_idx, s_id in enumerate(individual):
        if s_id not in servidores_em_uso: servidores_em_uso[s_id] = []
        servidores_em_uso[s_id].append(vms[vm_idx])
        temp_servidores[s_id].alocar_vm(vms[vm_idx])

    active_server_ids = [s_id for s_id, vms_list in servidores_em_uso.items() if vms_list]
    if len(active_server_ids) < 2: return individual

    # PASSO 1: Identifica o servidor de menor capacidade/carga ("pobre") para esvaziar
    # O servidor "pobre" é o que tem menos VMs. Em caso de empate, o com menos carga.
    servidor_pobre_id = min(active_server_ids, key=lambda s_id: (len(servidores_em_uso[s_id]), temp_servidores[s_id].cpu_usada + temp_servidores[s_id].ram_usada))
    
    # Lista de VMs a serem movidas
    vms_para_mover = sorted(servidores_em_uso[servidor_pobre_id], key=lambda vm: vm.cpu_req + vm.ram_req, reverse=True)
    
    # Lista de servidores que podem receber as VMs ("ricos" em espaço)
    servidores_alvo_ids = [s_id for s_id in active_server_ids if s_id != servidor_pobre_id]

    # Cria uma cópia do indivíduo para aplicar a mutação
    mutated_individual = list(individual)
    
    # PASSO 2 & 3: Tenta alocar as VMs do servidor pobre nos outros servidores
    sucesso_total = True
    for vm_a_mover in vms_para_mover:
        vm_idx = vms.index(vm_a_mover)
        vm_alocada = False

        # Heurística "Worst Fit": ordena os alvos pelo maior espaço livre
        alvos_ordenados = sorted(servidores_alvo_ids, key=lambda s_id: temp_servidores[s_id].ram_disponivel + temp_servidores[s_id].cpu_disponivel, reverse=True)
        
        for alvo_id in alvos_ordenados:
            if temp_servidores[alvo_id].pode_hospedar(vm_a_mover):
                # Sucesso! Atualiza o estado temporário para a próxima iteração
                temp_servidores[alvo_id].alocar_vm(vm_a_mover)
                mutated_individual[vm_idx] = alvo_id
                vm_alocada = True
                break
        
        if not vm_alocada:
            sucesso_total = False
            break # Se uma VM não couber, a consolidação falha

    # PASSO 4: Se todas as VMs foram movidas, a mutação é bem-sucedida
    if sucesso_total:
        print(f"--- Mutação de Consolidação (Robin Hood) bem-sucedida! Servidor {servidor_pobre_id} esvaziado. ---")
        return mutated_individual
    else:
        # Se falhou, retorna o indivíduo original sem alterações
        return individual


def swap_mutation(individual: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico], probability: float) -> List[int]:
    """
    Realiza a mutação de troca (swap) entre duas VMs, garantindo a validade da solução
    e seguindo o modelo "Lousa Limpa".
    """
    if random.random() < probability and len(vms) >= 2:
        # PASSO 1: Sorteia dois índices de VM diferentes para a troca
        vm_index_1, vm_index_2 = random.sample(range(len(vms)), 2)

        server_id_1 = individual[vm_index_1]
        server_id_2 = individual[vm_index_2]

        # Não faz sentido trocar VMs que já estão no mesmo servidor
        if server_id_1 == server_id_2:
            return individual

        # PASSO 2: Prepara a "Lousa Limpa" e constrói o estado atual
        # Limpamos todos os servidores e depois alocamos as VMs conforme o 'individual'
        for s in servidores:
            s.resetar()
        for i, s_id in enumerate(individual):
            if s_id != -1:
                servidores[s_id].alocar_vm(vms[i])
        
        # Pega os objetos relevantes
        vm1 = vms[vm_index_1]
        vm2 = vms[vm_index_2]
        servidor1 = servidores[server_id_1]
        servidor2 = servidores[server_id_2]

        # PASSO 3: Simula a troca DESALOCANDO as VMs de suas posições atuais
        servidor1.desalocar_vm(vm1)
        servidor2.desalocar_vm(vm2)

        # PASSO 4: Verifica se a troca é válida nos servidores agora "vazios"
        if servidor1.pode_hospedar(vm2) and servidor2.pode_hospedar(vm1):
            # A troca é válida. Aplica a mutação no cromossomo.
            individual[vm_index_1] = server_id_2
            individual[vm_index_2] = server_id_1
        
        # PASSO 5: Limpa a "bancada" para a próxima função
        # Independentemente de a mutação ter ocorrido ou não, resetamos os servidores.
        for s in servidores:
            s.resetar()

    return individual
