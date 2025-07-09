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
        
        for i in range(num_servidores):
            # O operador % faz o ciclo: 0, 1, 2, 3, 4, 0, 1, 2...
            servidor_id_alvo = (vm_index + i) % num_servidores
            if temp_servidores[servidor_id_alvo].pode_hospedar(vm_a_alocar):
                temp_servidores[servidor_id_alvo].alocar_vm(vm_a_alocar)
                base_individual[vm_index] = servidor_id_alvo
                vm_alocada = True
                break # VM alocada com sucesso, passa para a próxima VM

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

def doac_crossover_v4(parent1: List[int], parent2: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> Tuple[List[int], List[int]]:
    """
    Dominant Optimal Anti-Cancer
    Função principal do Crossover DOAC v4.
    Orquestra a criação de dois filhos, cada um baseado em um dos pais,
    """
    # Cria o primeiro filho usando o Pai 1 como referência principal
    child1 = _criar_filho_doac_v4(parent1, parent2, vms, servidores)
    
    # Cria o segundo filho invertendo os papéis para gerar diversidade
    child2 = _criar_filho_doac_v4(parent2, parent1, vms, servidores)

    return child1, child2

def _criar_filho_doac_v4(pai: List[int], mae: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> List[int]:
    """
    Dominant Optimal Anti-Cancer
    1- Identifica o gene bom e o torna dominante.
    2- Crusa os demais genes dos pais.
    3- Ataca o Câncer no filho.
    """
    # PASSO 1: Inicia o filho e os estados temporários
    num_vms = len(vms)
    filho = [-1] * num_vms
    vms_ja_alocadas = [False] * num_vms
    temp_servidores_build = [ServidorFisico(s.id, s.cpu_total, s.ram_total) for s in servidores]
    
    # PASSO 2 & 3: Calcula fitness e identifica o melhor dos pais
    fitness_pai = calculate_fitness(pai, vms, servidores)
    fitness_mae = calculate_fitness(mae, vms, servidores)
    melhor_pai = pai if fitness_pai <= fitness_mae else mae
    
    # PASSO 4 & 5: Identificar e Aplicar o Gene Dominante do MELHOR pai
    servidores_ativos_melhor_pai = {s_id for s_id in melhor_pai if s_id != -1}
    if servidores_ativos_melhor_pai:
        id_servidor_dominante = max(servidores_ativos_melhor_pai, key=lambda s_id: servidores[s_id].cpu_total + servidores[s_id].ram_total)
        vms_a_herdar_indices = [i for i, s_id in enumerate(melhor_pai) if s_id == id_servidor_dominante]
        for vm_idx in vms_a_herdar_indices:
            if not vms_ja_alocadas[vm_idx] and temp_servidores_build[id_servidor_dominante].pode_hospedar(vms[vm_idx]):
                filho[vm_idx] = id_servidor_dominante
                # PASSO 6: Marca a VM como usada
                vms_ja_alocadas[vm_idx] = True
                temp_servidores_build[id_servidor_dominante].alocar_vm(vms[vm_idx])

    # PASSO 6 (continuação): Construção Alternada do Restante do Filho
    for i in range(num_vms):
        if filho[i] == -1: # Se a posição do filho está vazia
            genitor = pai if i % 2 == 0 else mae
            vm_idx_candidato = next((j for j in range(num_vms) if not vms_ja_alocadas[j]), -1)
            
            if vm_idx_candidato != -1:
                servidor_proposto = genitor[vm_idx_candidato]
                vm_a_alocar = vms[vm_idx_candidato]
                
                if temp_servidores_build[servidor_proposto].pode_hospedar(vm_a_alocar):
                    filho[i] = servidor_proposto
                else: # Fallback "First Fit"
                    for s_id_alt in range(len(servidores)):
                        if temp_servidores_build[s_id_alt].pode_hospedar(vm_a_alocar):
                            filho[i] = s_id_alt
                            break
                
                if filho[i] != -1:
                    temp_servidores_build[filho[i]].alocar_vm(vm_a_alocar)
                    vms_ja_alocadas[vm_idx_candidato] = True

    # PASSO 7: Tratamento Anti-Câncer no filho já montado
    servidores_ativos_filho = {s_id for s_id in filho if s_id != -1}
    if len(servidores_ativos_filho) > 1:
        id_cancer = min(servidores_ativos_filho, key=lambda s_id: servidores[s_id].cpu_total + servidores[s_id].ram_total)
        
        vms_no_cancer_idx = [i for i, s_id in enumerate(filho) if s_id == id_cancer]
        servidores_alvo_ids = [s_id for s_id in servidores_ativos_filho if s_id != id_cancer]
        
        filho_reparado = list(filho)
        sucesso_reparo = True
        
        # Simula o estado para o reparo
        temp_servidores_reparo = [ServidorFisico(s.id, s.cpu_total, s.ram_total) for s in servidores]
        for vm_idx, s_id in enumerate(filho_reparado):
             if s_id != -1: temp_servidores_reparo[s_id].alocar_vm(vms[vm_idx])

        for vm_idx in vms_no_cancer_idx:
            vm_a_mover = vms[vm_idx]
            temp_servidores_reparo[id_cancer].vms_hospedadas.remove(vm_a_mover)
            
            alocado = False
            for novo_lar_id in servidores_alvo_ids:
                if temp_servidores_reparo[novo_lar_id].pode_hospedar(vm_a_mover):
                    filho_reparado[vm_idx] = novo_lar_id
                    temp_servidores_reparo[novo_lar_id].alocar_vm(vm_a_mover)
                    alocado = True
                    break
            
            if not alocado:
                sucesso_reparo = False
                break
        
        if sucesso_reparo:
            filho = filho_reparado # Aplica o reparo bem-sucedido

    # PASSO 8: Validação Final e Retorno Seguro
    if calculate_fitness(filho, vms, servidores) == float('inf'):
        print(f"AVISO: Filho gerado pelo crossover com reparo era inválido. Retornando o melhor dos pais.")
        return melhor_pai
    else:
        return filho


def doac_crossover(parent1: List[int], parent2: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> Tuple[List[int], List[int]]:
    """
    Dominant Optimal Anti-Cancer
    Função principal do Crossover DOAC.
    Orquestra a criação de dois filhos a partir de dois pais, usando a lógica
    de construção heurística projetada por você.
    """
    # Cria o primeiro filho usando o Pai 1 como referência para o "consenso"
    child1 = _criar_filho_doac(parent1, parent2, vms, servidores)
    
    # Cria o segundo filho invertendo os papéis para gerar diversidade
    child2 = _criar_filho_doac(parent2, parent1, vms, servidores)

    return child1, child2

def _criar_filho_doac(pai_base: List[int], pai_guia: List[int], vms: List[MaquinaVirtual], servidores: List[ServidorFisico]) -> List[int]:
    """
    Cria um único filho seguindo a hierarquia de prioridades:
    1. Anti-Câncer (Alocar a maior VM no maior servidor).
    2. Consenso (Preservar o que os pais concordam).
    3. Alocação Heurística do Resto (Maiores primeiro no mais folgado).
    """
    num_vms = len(vms)
    filho = [-1] * num_vms
    vms_ja_alocadas = [False] * num_vms
    temp_servidores = [ServidorFisico(s.id, s.cpu_total, s.ram_total) for s in servidores]

    # --- PASSO 1: AÇÃO ANTI-CÂNCER (PRIORIDADE MÁXIMA) ---
    # Identifica a maior VM e o maior servidor
    maior_vm_idx = max(range(num_vms), key=lambda i: vms[i].ram_req + vms[i].cpu_req)
    maior_servidor_id = max(range(len(servidores)), key=lambda i: servidores[i].ram_total + servidores[i].cpu_total)

    # Aloca a maior VM no maior servidor, se possível
    if temp_servidores[maior_servidor_id].pode_hospedar(vms[maior_vm_idx]):
        filho[maior_vm_idx] = maior_servidor_id
        temp_servidores[maior_servidor_id].alocar_vm(vms[maior_vm_idx])
        vms_ja_alocadas[maior_vm_idx] = True
        # print("Ação Anti-Câncer aplicada.")

    # --- PASSO 2: PRESERVAÇÃO DO CONSENSO (SEGUNDA PRIORIDADE) ---
    for i in range(num_vms):
        # Se a VM ainda não foi alocada E os pais concordam sobre ela
        if not vms_ja_alocadas[i] and pai_base[i] == pai_guia[i]:
            servidor_id = pai_base[i]
            if temp_servidores[servidor_id].pode_hospedar(vms[i]):
                filho[i] = servidor_id
                temp_servidores[servidor_id].alocar_vm(vms[i])
                vms_ja_alocadas[i] = True

    # --- PASSO 3: ALOCAÇÃO HEURÍSTICA DO RESTANTE (TERCEIRA PRIORIDADE) ---
    # Pega todas as VMs que ainda não foram alocadas
    vms_restantes_indices = [i for i, alocada in enumerate(vms_ja_alocadas) if not alocada]

    # Ordena as VMs restantes da maior para a menor (Decreasing Size)
    vms_restantes_ordenadas = sorted(
        vms_restantes_indices,
        key=lambda i: vms[i].ram_req + vms[i].cpu_req,
        reverse=True
    )

    # Aloca as VMs restantes usando a lógica "Worst Fit"
    for vm_idx in vms_restantes_ordenadas:
        vm_a_alocar = vms[vm_idx]
        
        # Ordena os servidores pelo maior espaço livre
        servidores_disponiveis_ordenados = sorted(
            range(len(servidores)),
            key=lambda s_id: temp_servidores[s_id].ram_disponivel + temp_servidores[s_id].cpu_disponivel,
            reverse=True
        )

        for servidor_id in servidores_disponiveis_ordenados:
            if temp_servidores[servidor_id].pode_hospedar(vm_a_alocar):
                filho[vm_idx] = servidor_id
                temp_servidores[servidor_id].alocar_vm(vm_a_alocar)
                break # Passa para a próxima VM

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

