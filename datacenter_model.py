"""
Módulo para modelar as entidades do datacenter para o projeto DRE.

Este arquivo define as classes para:
- MaquinaVirtual: Representa uma VM com seus requisitos de recursos.
- ServidorFisico: Representa um servidor físico com sua capacidade e estado atual.
- E funções para carregar cenários de simulação.
"""



# Importando
import json, csv
from typing import List, Dict, Any, Optional



# ===[ Definição da Classe MaquinaVirtual ]==============================================

# Em datacenter_model.py, substitua a classe MaquinaVirtual

class MaquinaVirtual:
    """
    Representa uma única Máquina Virtual (VM).
    Funciona como um "item" a ser alocado no problema de Bin Packing.
    """
    def __init__(self, vm_id: int, cpu_req: int, ram_req: int, nome_real: Optional[str] = None):
        """
        Inicializa uma VM.
        Args:
            vm_id (int): Identificador único da VM.
            cpu_req (int): Número de núcleos de CPU que a VM requer.
            ram_req (int): Quantidade de RAM (em GB) que a VM requer.
            nome_real (Optional[str]): O nome original da VM vindo do arquivo.
        """
        self.id = vm_id
        self.cpu_req = cpu_req
        self.ram_req = ram_req
        self.nome_real = nome_real if nome_real else f"VM_{vm_id}"

    def __repr__(self) -> str:
        """Retorna uma representação em string do objeto, útil para debug."""
        return f"VM(ID: {self.id}, CPU: {self.cpu_req}, RAM: {self.ram_req}GB)"


# ===[ Definição da Classe ServidorFisico ]===============================================

class ServidorFisico:
    """
    Representa um único Servidor Físico (Host).
    VERSÃO ATUALIZADA: Inclui métodos para desalocar e resetar VMs.
    """
    def __init__(self, servidor_id: int, cpu_total: int, ram_total: int, nome_real: Optional[str] = None):
        self.id = servidor_id
        self.cpu_total = cpu_total
        self.ram_total = ram_total
        self.nome_real = nome_real if nome_real else f"Servidor_{servidor_id}"
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
            raise ValueError(f"Servidor {self.id} não tem capacidade para a VM {vm.id}.")

    # --- NOVO MÉTODO ---
    def desalocar_vm(self, vm: MaquinaVirtual):
        """Remove uma VM deste servidor."""
        try:
            self.vms_hospedadas.remove(vm)
        except ValueError:
            # Opcional: Avisar se a VM não foi encontrada, útil para debug.
            print(f"AVISO: Tentativa de remover a VM {vm.id} do Servidor {self.id}, mas ela não estava lá.")

    # --- NOVO MÉTODO ---
    def resetar(self):
        """Remove todas as VMs deste servidor, deixando-o vazio."""
        self.vms_hospedadas.clear()

    def __repr__(self) -> str:
        """Retorna uma representação em string do objeto, útil para debug."""
        return (f"Servidor(ID: {self.id}, "
                f"CPU: {self.cpu_usada}/{self.cpu_total}, "
                f"RAM: {self.ram_usada}/{self.ram_total}GB, "
                f"VMs: {len(self.vms_hospedadas)})")


# ===[ Função para Carregar Cenário ]=====================================================

def _parse_memory_string_to_gb(mem_str: str) -> int:
    """
    Função auxiliar para converter strings de memória (ex: "4 GB", "8,192.00 MB")
    em um número inteiro de GIGABYTES (GB).
    """
    mem_str = mem_str.lower().replace(',', '').strip()
    try:
        if 'gb' in mem_str:
            num_part = mem_str.replace('gb', '').strip()
            return int(float(num_part)) # O valor já está em GB
        elif 'mb' in mem_str:
            num_part = mem_str.replace('mb', '').strip()
            # Converte MB para GB e arredonda para baixo (int)
            return int(float(num_part) / 1024)
        else:
            # Assume que um valor sem unidade está em GB
            return int(float(mem_str))
    except (ValueError, TypeError):
        return 0

# Dicionário para mapear o hardware real.
# ADICIONE AQUI OS SEUS OUTROS MODELOS DE SERVIDOR E SEUS PROCESSADORES LÓGICOS
HARDWARE_MAP = {
    # prefixo: {'pCPUs': <cores>, 'ram_gb': <ram>}
    'cs-01-host': {'pCPUs': 24, 'ram_gb': 382},
    'cs-02-host': {'pCPUs': 24, 'ram_gb': 382},
    's-hpbl':     {'pCPUs': 16, 'ram_gb': 256}
}
# Taxa de superalocação de CPU (vCPU:pCPU ratio). 4:1 é um valor seguro e comum.
VCPU_PCPU_RATIO = 8
RAM_OVERCOMMIT_RATIO = 1.5

def _get_total_vcpus(hostname: str) -> int:
    """Consulta o HARDWARE_MAP, encontra os pCPUs e calcula o total de vCPUs."""
    # <<< CORREÇÃO: A variável do loop foi renomeada para 'hardware_info' para clareza
    for prefix, hardware_info in HARDWARE_MAP.items():
        if hostname.startswith(prefix):
            # <<< CORREÇÃO: Acessa a chave 'pCPUs' do dicionário antes de multiplicar
            return hardware_info['pCPUs'] * VCPU_PCPU_RATIO
            
    print(f"AVISO: Modelo de host desconhecido '{hostname}'. Usando 32*8=256 como padrão.")
    # <<< CORREÇÃO: Usando o VCPU_PCPU_RATIO para consistência
    return 32 * VCPU_PCPU_RATIO # Retorna um padrão se não encontrar

# No arquivo datacenter_model.py, substitua a função inteira por esta:

# Em datacenter_model.py, substitua a função carregar_cenario_vmware

def carregar_cenario_vmware(caminho_servidores: str, caminho_vms: str) -> Dict[str, Any]:
    """
    Carrega o cenário a partir de arquivos CSV do VMware.
    """
    # --- Processamento dos Servidores ---
    lista_servidores = []
    try:
        with open(caminho_servidores, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                hostname = row['Name'].strip()
                
                # Usa sua função auxiliar original para CPU
                capacidade_cpu = _get_total_vcpus(hostname)
                
                # Lógica corrigida para RAM, usando o novo HARDWARE_MAP
                hardware_info = next((hw for prefix, hw in HARDWARE_MAP.items() if hostname.startswith(prefix)), None)
                if hardware_info is None:
                    # Garante que o padrão seja consistente com a função _get_total_vcpus
                    capacidade_ram = 128 
                else:
                    capacidade_ram = hardware_info['ram_gb']

                servidor_id = i
                lista_servidores.append(
                    ServidorFisico(servidor_id, capacidade_cpu, capacidade_ram, nome_real=hostname)
                )
    except FileNotFoundError:
        print(f"ERRO: Arquivo de servidores não encontrado em '{caminho_servidores}'")
        return {'servidores': [], 'vms': []}
    print(f"Lidos {len(lista_servidores)} servidores. Capacidade calculada com superalocação.")

    # --- Processamento das VMs (lógica de unicidade mantida) ---
    lista_vms = []
    vm_mapa_nomes = {}
    vm_id_counter = 0
    try:
        with open(caminho_vms, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    nome_vm_real = row['Name'].strip()
                    if not nome_vm_real or nome_vm_real in vm_mapa_nomes:
                        if nome_vm_real: print(f"AVISO: Nome de VM duplicado ignorado: '{nome_vm_real}'")
                        continue

                    req_ram = _parse_memory_string_to_gb(row['Memory Size'])
                    req_cpu = int(row['CPUs'])
                    
                    lista_vms.append(
                        MaquinaVirtual(
                            vm_id=vm_id_counter,
                            cpu_req=req_cpu,
                            ram_req=req_ram,
                            nome_real=nome_vm_real
                        )
                    )
                    vm_mapa_nomes[nome_vm_real] = vm_id_counter
                    vm_id_counter += 1
                except (ValueError, KeyError) as e:
                    print(f"AVISO: Pulando linha de VM inválida: {row} | Erro: {e}")
    except FileNotFoundError:
        print(f"ERRO: Arquivo de VMs não encontrado em '{caminho_vms}'")
        return {'servidores': [], 'vms': []}
        
    print(f"Lidas {len(lista_vms)} VMs únicas.")
    return {'servidores': lista_servidores, 'vms': lista_vms}

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

        ram_total_dos_servidores = 0
        ram_total_das_vms = 0
        cpu_total_dos_servidores = 0
        cpu_total_das_vms = 0

        for serv in lista_servidores:
            ram_total_dos_servidores += serv.ram_total
            cpu_total_dos_servidores += serv.cpu_total

        for vm in lista_vms:
            ram_total_das_vms += vm.ram_req
            cpu_total_das_vms += vm.cpu_req

        if (
            ram_total_das_vms > ram_total_dos_servidores or
            cpu_total_das_vms > cpu_total_dos_servidores
        ): 
            print(f'''
            As VMs não cabem no datacenter.

            \t\t| DC  \t| VMs\t| Diferença
            {'-'*50}
            RAM \t| {ram_total_dos_servidores} \t| {ram_total_das_vms} \t| {ram_total_dos_servidores - ram_total_das_vms}
            {'-'*50}
            CPU \t| {cpu_total_dos_servidores} \t| {cpu_total_das_vms} \t| {cpu_total_dos_servidores - cpu_total_das_vms}

            Programa encerrado.
            ''')
            exit()
        
        return {'servidores': lista_servidores, 'vms': lista_vms}

    except FileNotFoundError:
        print(f"ERRO: Arquivo de cenário não encontrado em '{caminho_arquivo}'")
        return {'': '', '': ''}
    except KeyError as e:
        print(f"ERRO: Chave ausente no arquivo JSON: {e}")
        return {'': '', '': ''}
