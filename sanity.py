# Arquivo [sanity.py]

# Importações:
import json
from typing import List

from datacenter_model import (
    ServidorFisico,
    MaquinaVirtual
)



def server_internal_sanity_check(servidor: 'ServidorFisico'):
    """
    Verifica se a lista 'vms_hospedadas' de um único servidor contém
    objetos de VM duplicados.
    """
    vm_ids_vistos = set()
    for vm in servidor.vms_hospedadas:
        if vm.id in vm_ids_vistos:
            # ERRO ENCONTRADO!
            print("\n" + "="*80)
            print(f"!!! ERRO DE DUPLICAÇÃO INTERNA DETECTADO !!!")
            print(f"O Servidor {servidor.id} está tentando desenhar a VM {vm.id} mais de uma vez.")
            
            todos_os_ids = [v.id for v in servidor.vms_hospedadas]
            print(f"Conteúdo completo da lista 'vms_hospedadas' do servidor: {todos_os_ids}")
            print("Isso indica um erro na forma como o estado é construído ou modificado.")
            print("A execução será interrompida.")
            print("="*80 + "\n")
            exit()
        else:
            vm_ids_vistos.add(vm.id)



def servidor_sanity_check(servidor: 'ServidorFisico', best_solution: List[int]):
    """
    Verifica se as VMs contidas em um objeto de servidor correspondem
    ao que é ditado pelo cromossomo 'best_solution'.
    """
    servidor_id_atual = servidor.id

    # Itera sobre as VMs que o objeto 'servidor' ACHA que ele contém
    for vm_hospedada in servidor.vms_hospedadas:
        vm_id = vm_hospedada.id

        # Verifica no cromossomo (nossa "fonte da verdade") onde essa VM deveria estar
        servidor_id_correto = best_solution[vm_id]

        # Compara a realidade (onde a VM está) com a verdade (onde deveria estar)
        if servidor_id_atual != servidor_id_correto:
            print("\n" + "="*80)
            print(f"!!! ERRO DE INCONSISTÊNCIA DE ESTADO DETECTADO !!!")
            print(f"A função de desenho está prestes a desenhar a VM {vm_id} no Servidor {servidor_id_atual},")
            print(f"mas de acordo com a solução final, ela deveria estar no Servidor {servidor_id_correto}.")
            print("Isso prova que o estado dos objetos 'servidores' está sendo corrompido.")
            print("A execução será interrompida.")
            print("="*80 + "\n")
            exit()



def allocated_vms_sanity_check(vm_a_checar: 'MaquinaVirtual', servidores: List['ServidorFisico']):
    """
    Verifica se uma VM específica já existe em mais de um local na lista de servidores.
    Esta é uma verificação de diagnóstico para ser usada durante a construção do estado.
    """
    count = 0
    locations = []
    
    # Itera por todos os servidores e todas as VMs alocadas
    for servidor in servidores:
        for vm_hospedada in servidor.vms_hospedadas:
            # Compara pelo ID, que é o identificador único
            if vm_hospedada.id == vm_a_checar.id:
                count += 1
                locations.append(servidor.id)

    # Se a contagem for maior que 1, significa que a VM foi encontrada em múltiplos lugares
    if count > 1:
        print("\n" + "="*80)
        print(f"!!! ERRO DE SANIDADE EM TEMPO REAL DETECTADO !!!")
        print(f"A VM de ID {vm_a_checar.id} ('{vm_a_checar.nome_real}') foi encontrada em {count} servidores ao mesmo tempo.")
        print(f"Servidores onde a VM foi encontrada: {locations}")
        print("A execução será interrompida.")
        print("="*80 + "\n")
        exit() # Interrompe o programa imediatamente



def reports_sanity_check(report_log_path: str, report_detalhado_path: str):
    """
    Verifica a consistência interna e externa dos arquivos de relatório JSON.
    VERSÃO CORRIGIDA: Lida corretamente com os tipos de dados (string vs int).
    """
    print("\n--- Iniciando Verificação de Sanidade dos Relatórios ---")
    erros_encontrados = False

    try:
        # --- Verificação do Relatório Lógico ---
        with open(report_log_path, 'r') as f:
            logico = json.load(f)
        
        vm_mapa_logico = {}
        for servidor_id_str, vms_lista in logico.items():
            for vm_id in vms_lista:
                # <<< CORREÇÃO: Converte o servidor_id de string para int
                servidor_id_int = int(servidor_id_str)
                if vm_id in vm_mapa_logico:
                    print(f"[ERRO-LÓGICO] VM ID {vm_id} encontrada no Servidor {servidor_id_int} e também no Servidor {vm_mapa_logico[vm_id]}.")
                    erros_encontrados = True
                else:
                    vm_mapa_logico[vm_id] = servidor_id_int
        
        # --- Verificação do Relatório Detalhado ---
        with open(report_detalhado_path, 'r') as f:
            detalhado = json.load(f)

        vm_mapa_detalhado = {}
        for servidor_info in detalhado['servidores_em_uso']:
            servidor_id = servidor_info['servidor_id']
            for vm_info in servidor_info['vms_alocadas']:
                vm_id = vm_info['vm_id']
                if vm_id in vm_mapa_detalhado:
                    print(f"[ERRO-DETALHADO] VM ID {vm_id} encontrada no Servidor {servidor_id} e também no Servidor {vm_mapa_detalhado[vm_id]}.")
                    erros_encontrados = True
                else:
                    vm_mapa_detalhado[vm_id] = servidor_id

        # --- Verificação de Consistência entre os Relatórios ---
        if vm_mapa_logico != vm_mapa_detalhado:
            print("[ERRO-CONSISTÊNCIA] Os mapas de alocação entre o relatório lógico e o detalhado são diferentes.")
            erros_encontrados = True

    except FileNotFoundError as e:
        print(f"[ERRO-ARQUIVO] Não foi possível encontrar o arquivo: {e.filename}")
        erros_encontrados = True
    except Exception as e:
        print(f"[ERRO-INESPERADO] Ocorreu um erro durante a verificação: {e}")
        erros_encontrados = True

    if not erros_encontrados:
        print("[OK] Verificação de sanidade concluída. Nenhum erro encontrado nos relatórios.")
    else:
        print("\nVerificação de sanidade concluída. Foram encontrados erros.")


def datacenter_info_sanity_check(datacenter_info):
    """
    Checa a sanidade da variável datacenter_info, verificando tipos
    e procurando por IDs duplicados de forma eficiente.
    """

    # --- Checagem dos Servidores ---
    ids_servidores_vistos = set()
    for item in datacenter_info['servidores']:
        # 1. Checa se o objeto é do tipo correto
        if not isinstance(item, ServidorFisico):
            print(f'Erro de Tipo! O item "{item}" não é um objeto ServidorFisico.')
            exit()

        # 2. Checa se o ID já foi visto
        if item.id in ids_servidores_vistos:
            print(f'Erro de Duplicidade! Servidor com ID {item.id} encontrado mais de uma vez.')
            exit()
        
        # Se passou nas checagens, adiciona o ID ao conjunto de IDs vistos
        ids_servidores_vistos.add(item.id)

    # --- Checagem das VMs ---
    ids_vms_vistas = set()
    for item in datacenter_info['vms']:
        # 1. Checa se o objeto é do tipo correto
        if not isinstance(item, MaquinaVirtual):
            print(f'Erro de Tipo! O item "{item}" não é um objeto MaquinaVirtual.')
            exit()

        # 2. Checa se o ID já foi visto
        if item.id in ids_vms_vistas:
            print(f'Erro de Duplicidade! VM com ID {item.id} encontrada mais de uma vez.')
            exit()
            
        # Se passou nas checagens, adiciona o ID ao conjunto de IDs vistos
        ids_vms_vistas.add(item.id)

    # Se a função chegou até aqui, está tudo OK.
    # print("Sanity check concluído: A estrutura de dados 'datacenter_info' é válida.")



def population_sanity_check(population, population_size, datacenter_info):
    """
    Verifica a integridade estrutural da população de soluções.

    Args:
        population (List[List[int]]): A população gerada pelo algoritmo.
        population_size (int): O tamanho esperado da população.
        datacenter_info (Dict): Dicionário com as listas de VMs e servidores.
    """
    # --- Checagem 1: O tamanho geral da população está correto? ---
    if len(population) != population_size:
        print(f"Erro de Sanidade: A população deveria ter {population_size} indivíduos, mas tem {len(population)}.")
        exit()

    # Extrai informações necessárias para as próximas checagens
    num_vms = len(datacenter_info['vms'])
    num_servidores = len(datacenter_info['servidores'])

    # --- Itera sobre cada indivíduo para checagens mais profundas ---
    for i, individual in enumerate(population):

        # --- Checagem 2: O indivíduo tem o número correto de genes (um para cada VM)? ---
        if len(individual) != num_vms:
            print(f"Erro de Sanidade: O indivíduo de índice {i} deveria ter {num_vms} genes, mas tem {len(individual)}.")
            exit()

        # --- Itera sobre cada gene (ID do servidor) dentro do indivíduo ---
        for gene in individual:

            # --- Checagem 3: O gene é um inteiro válido? ---
            # 3a: Checa se não é um inteiro
            if not isinstance(gene, int):
                print(f"Erro de Sanidade: Gene '{gene}' no indivíduo {i} não é um número inteiro.")
                exit()
            
            # 3b: Checa se é um valor negativo
            if gene < 0:
                print(f"Erro de Sanidade: Gene '{gene}' no indivíduo {i} é um ID de servidor negativo e inválido.")
                exit()
            
            # 3c (Melhoria): Checa se o ID do servidor realmente existe
            if gene >= num_servidores:
                print(f"Erro de Sanidade: Gene '{gene}' no indivíduo {i} é um ID de servidor que não existe. IDs válidos são de 0 a {num_servidores - 1}.")
                exit()
    
    # Se a função chegou até aqui, a população passou em todas as checagens.
    # print("Sanity check concluído: A estrutura da população é válida.")
