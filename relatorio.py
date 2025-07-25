# Arquivo [relatorio.py]

"""
Módulo responsável pela geração de relatórios do projeto DRE.
"""

# Importando:
import json

from typing import List
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from datacenter_model import ServidorFisico, MaquinaVirtual



def relatorio_logico_json(
    best_solution: List[int],
    nome_arquivo: str = "melhor_solucao_logica.json"
 ):
    """
    Gera um arquivo JSON 'cru', mostrando a lógica pura da alocação.

    O relatório mapeia cada ID de servidor em uso para uma lista
    de IDs de VMs que ele hospeda. Esta função é intencionalmente
    simples e não usa as classes do datacenter_model.
    """
    alocacao_por_servidor = {}

    # 1. Itera sobre a melhor solução para agrupar as VMs por servidor.
    # O índice (vm_id) é o ID da VM, o valor (server_id) é onde ela está.
    for vm_id, server_id in enumerate(best_solution):
        # A biblioteca JSON exige que as chaves do dicionário sejam strings.
        # Se server_id for um inteiro, ele será convertido automaticamente.
        server_id_str = str(server_id)

        # 2. Se for a primeira vez que vemos este servidor, cria uma lista vazia para ele.
        if server_id_str not in alocacao_por_servidor:
            alocacao_por_servidor[server_id_str] = []
        
        # 3. Adiciona o ID da VM à lista do servidor correspondente.
        alocacao_por_servidor[server_id_str].append(vm_id)

    # 4. Escreve o dicionário no arquivo JSON.
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(alocacao_por_servidor, f, indent=4, sort_keys=True)
        print(f"\nRelatório LÓGICO da melhor solução salvo em '{nome_arquivo}'")
    except Exception as e:
        print(f"\nOcorreu um erro ao salvar o relatório LÓGICO: {e}")


def relatorio_json(
    best_solution: List[int], 
    vms_a_alocar: List[MaquinaVirtual], 
    servidores: List[ServidorFisico],
    nome_arquivo: str = "melhor_solucao.json"
 ):
    """
    Gera um arquivo JSON detalhado com a melhor solução de alocação.

    O relatório mostra quais servidores estão em uso e a lista de VMs
    alocada em cada um, com seus respectivos detalhes.
    """
    servidores_report = {}

    # 1. Itera sobre a melhor solução para reconstruir o estado de alocação.
    # O índice (vm_index) representa a VM, e o valor (server_id) o servidor.
    for vm_index, server_id in enumerate(best_solution):
        # Pula se o ID do servidor for inválido (pouco provável, mas seguro)
        if server_id < 0 or server_id >= len(servidores):
            continue

        vm_obj = vms_a_alocar[vm_index]

        # 2. Se for a primeira vez que vemos este servidor, cria sua entrada no relatório.
        if server_id not in servidores_report:
            server_obj = servidores[server_id]
            servidores_report[server_id] = {
                "servidor_id": server_obj.id,
                "cpu_total": server_obj.cpu_total,
                "ram_total_gb": server_obj.ram_total,
                "vms_alocadas": []
            }

        # 3. Adiciona os detalhes da VM à lista do servidor correspondente.
        servidores_report[server_id]["vms_alocadas"].append({
            "vm_id": vm_obj.id,
            "cpu_req": vm_obj.cpu_req,
            "ram_req_gb": vm_obj.ram_req
        })

    # 4. Formata a saída final para o JSON.
    # Converte o dicionário de servidores em uma lista, que é mais comum em JSON.
    relatorio_final = {
        "servidores_em_uso": list(servidores_report.values())
    }

    # 5. Escreve o dicionário no arquivo JSON.
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            # O indent=4 formata o arquivo para ser facilmente legível por humanos.
            json.dump(relatorio_final, f, indent=4, ensure_ascii=False)
        print(f"\nRelatório da melhor solução salvo em '{nome_arquivo}'")
    except Exception as e:
        print(f"\nOcorreu um erro ao salvar o relatório JSON: {e}")


def gerar_relatorio_excel(
    best_solution: List[int],
    servidores: List[ServidorFisico],
    vms: List[MaquinaVirtual],
    nome_arquivo: str = "DRE_Relatorio_Final.xlsx"
 ):
    """
    Gera um relatório Excel detalhado com a alocação final, incluindo uso de recursos.
    VERSÃO CORRIGIDA: Inclui verificação de segurança para a planilha (ws).
    """
    print(f"\n--- Gerando Relatório Excel: '{nome_arquivo}' ---")

    # 1. Calcula o estado final
    uso_servidores = {s.id: {'cpu': 0, 'ram': 0, 'vms': []} for s in servidores}
    for vm_idx, s_id in enumerate(best_solution):
        if s_id != -1 and s_id in uso_servidores:
            vm = vms[vm_idx]
            uso_servidores[s_id]['cpu'] += vm.cpu_req
            uso_servidores[s_id]['ram'] += vm.ram_req
            uso_servidores[s_id]['vms'].append(vm)

    # 2. Cria e formata a planilha
    wb = Workbook()
    ws = wb.active
    
    # Verifica se a planilha (worksheet) foi criada com sucesso antes de usá-la.
    if ws is None:
        print("ERRO CRÍTICO: Não foi possível criar a planilha no arquivo Excel.")
        return

    ws.title = "Alocação Final de VMs"
    
    headers = ["Servidor Físico", "CPU Usada / Total", "Uso CPU (%)", "RAM Usada / Total (GB)", "Uso RAM (%)", "VM Alocada"]
    ws.append(headers)
    for cell in ws["1:1"]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 25
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 70

    # 3. Escreve os dados
    servidores_ordenados = sorted([s for s in servidores if uso_servidores[s.id]['vms']], key=lambda s: s.nome_real)

    for servidor in servidores_ordenados:
        uso = uso_servidores[servidor.id]
        vms_alocadas = sorted(uso['vms'], key=lambda vm: vm.nome_real)

        cpu_percent = (uso['cpu'] / servidor.cpu_total * 100) if servidor.cpu_total > 0 else 0
        ram_percent = (uso['ram'] / servidor.ram_total * 100) if servidor.ram_total > 0 else 0

        primeira_vm_nome = vms_alocadas[0].nome_real
        ws.append([
            servidor.nome_real,
            f"{uso['cpu']} / {servidor.cpu_total}",
            f"{cpu_percent:.2f}%",
            f"{uso['ram']} / {servidor.ram_total}",
            f"{ram_percent:.2f}%",
            primeira_vm_nome
        ])
        
        for vm in vms_alocadas[1:]:
            ws.append(['', '', '', '', '', vm.nome_real])
        
        ws.append([])

    # 4. Salva o arquivo
    try:
        wb.save(nome_arquivo)
        print(f"Relatório '{nome_arquivo}' salvo com sucesso!")
    except Exception as e:
        print(f"ERRO ao salvar o relatório Excel: {e}")
