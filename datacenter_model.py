# -*- coding: utf-8 -*-
"""
Módulo para modelar as entidades do datacenter para o projeto DRE.

Este arquivo define as classes para:
- MaquinaVirtual: Representa uma VM com seus requisitos de recursos.
- ServidorFisico: Representa um servidor físico com sua capacidade e estado atual.
- E funções para carregar cenários de simulação.
"""

import json
from typing import List, Dict, Any

# ===[ Definição da Classe MaquinaVirtual ]==============================================

class MaquinaVirtual:
    """
    Representa uma única Máquina Virtual (VM).
    Funciona como um "item" a ser alocado no problema de Bin Packing.
    """
    def __init__(self, vm_id: int, cpu_req: int, ram_req: int):
        """
        Inicializa uma VM.
        Args:
            vm_id (int): Identificador único da VM.
            cpu_req (int): Número de núcleos de CPU que a VM requer.
            ram_req (int): Quantidade de RAM (em GB) que a VM requer.
        """
        self.id = vm_id
        self.cpu_req = cpu_req
        self.ram_req = ram_req

    def __repr__(self) -> str:
        """Retorna uma representação em string do objeto, útil para debug."""
        return f"VM(ID: {self.id}, CPU: {self.cpu_req}, RAM: {self.ram_req}GB)"


# ===[ Definição da Classe ServidorFisico ]===============================================

class ServidorFisico:
    """
    Representa um único Servidor Físico (Host).
    Funciona como um "caixote" (bin) no problema de Bin Packing.
    """
    def __init__(self, servidor_id: int, cpu_total: int, ram_total: int):
        """
        Inicializa um Servidor Físico.
        Args:
            servidor_id (int): Identificador único do servidor.
            cpu_total (int): Número total de núcleos de CPU do servidor.
            ram_total (int): Quantidade total de RAM (em GB) do servidor.
        """
        self.id = servidor_id
        self.cpu_total = cpu_total
        self.ram_total = ram_total
        self.vms_hospedadas: List[MaquinaVirtual] = []

    @property
    def cpu_usada(self) -> int:
        """Calcula e retorna a quantidade de CPU atualmente em uso."""
        return sum(vm.cpu_req for vm in self.vms_hospedadas)

    @property
    def ram_usada(self) -> int:
        """Calcula e retorna a quantidade de RAM atualmente em uso."""
        return sum(vm.ram_req for vm in self.vms_hospedadas)

    @property
    def cpu_disponivel(self) -> int:
        """Calcula e retorna a quantidade de CPU ainda disponível."""
        return self.cpu_total - self.cpu_usada

    @property
    def ram_disponivel(self) -> int:
        """Calcula e retorna a quantidade de RAM ainda disponível."""
        return self.ram_total - self.ram_usada

    def pode_hospedar(self, vm: MaquinaVirtual) -> bool:
        """Verifica se há recursos suficientes para hospedar uma determinada VM."""
        return vm.cpu_req <= self.cpu_disponivel and vm.ram_req <= self.ram_disponivel

    def alocar_vm(self, vm: MaquinaVirtual):
        """Aloca uma VM neste servidor, se houver capacidade."""
        if self.pode_hospedar(vm):
            self.vms_hospedadas.append(vm)
        else:
            # Lança um erro se a alocação for inválida. Isso ajuda a detectar problemas.
            raise ValueError(f"Servidor {self.id} não tem capacidade para a VM {vm.id}.")

    def __repr__(self) -> str:
        """Retorna uma representação em string do objeto, útil para debug."""
        return (f"Servidor(ID: {self.id}, "
                f"CPU: {self.cpu_usada}/{self.cpu_total}, "
                f"RAM: {self.ram_usada}/{self.ram_total}GB, "
                f"VMs: {len(self.vms_hospedadas)})")


# ===[ Função para Carregar Cenário ]=====================================================

def carregar_cenario(caminho_arquivo: str) -> Dict[str, Any]:
    """
    Carrega a definição de um cenário (servidores e VMs) a partir de um arquivo JSON.
    
    Args:
        caminho_arquivo (str): O caminho para o arquivo .json do cenário.

    Returns:
        Dict[str, Any]: Um dicionário contendo a lista de objetos ServidorFisico
                        e a lista de objetos MaquinaVirtual.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        lista_servidores = [
            ServidorFisico(s['id'], s['cpu_total'], s['ram_total'])
            for s in dados['servidores']
        ]

        lista_vms = [
            MaquinaVirtual(vm['id'], vm['cpu_req'], vm['ram_req'])
            for vm in dados['vms_a_alocar']
        ]

        print(f"Cenário '{caminho_arquivo}' carregado com sucesso.")
        print(f"Encontrados {len(lista_servidores)} servidores e {len(lista_vms)} VMs para alocar.")
        
        return {'servidores': lista_servidores, 'vms': lista_vms}

    except FileNotFoundError:
        print(f"ERRO: Arquivo de cenário não encontrado em '{caminho_arquivo}'")
        return {'': '', '': ''}
    except KeyError as e:
        print(f"ERRO: Chave ausente no arquivo JSON: {e}")
        return {'': '', '': ''}
