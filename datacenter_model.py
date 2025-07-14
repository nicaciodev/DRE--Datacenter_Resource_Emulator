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
    'cs-01-host': 24, # Exemplo: todos os hosts cs-01 têm 32 pCPUs
    'cs-02-host': 24, # Exemplo: todos os hosts cs-02 têm 32 pCPUs
    's-hpbl': 16      # Exemplo: um modelo mais antigo com 24 pCPUs
}
# Taxa de superalocação de CPU (vCPU:pCPU ratio). 4:1 é um valor seguro e comum.
VCPU_PCPU_RATIO = 8
RAM_OVERCOMMIT_RATIO = 1.5

def _get_total_vcpus(hostname: str) -> int:
    """Consulta o HARDWARE_MAP, encontra os pCPUs e calcula o total de vCPUs."""
    for prefix, pcpus in HARDWARE_MAP.items():
        if hostname.startswith(prefix):
            return pcpus * VCPU_PCPU_RATIO
    print(f"AVISO: Modelo de host desconhecido '{hostname}'. Usando 32*4=128 como padrão.")
    return 32 * VCPU_PCPU_RATIO # Retorna um padrão se não encontrar

def carregar_cenario_vmware(caminho_servidores: str, caminho_vms: str) -> Optional[Dict[str, Any]]:
    """
    Carrega um cenário do VMware, calculando a capacidade de CPU e RAM com
    base nas taxas de superalocação.
    """
    mapeamento_servidores, mapeamento_vms, lista_servidores_obj, lista_vms_obj = {}, {}, [], []
    print("\n--- Carregando Cenário VMware com Cálculo de Capacidade Real (CPU e RAM) ---")
    try:
        with open(caminho_servidores, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                nome_servidor = row['Name']
                cpu_total = _get_total_vcpus(nome_servidor)
                
                # --- LÓGICA DE RAM CORRIGIDA ---
                ram_fisica_gb = _parse_memory_string_to_gb(row['Memory Size (MB)'])
                # Aplica a taxa de superalocação para obter a capacidade "alocável"
                ram_total_alocavel = int(ram_fisica_gb * RAM_OVERCOMMIT_RATIO)
                
                servidor_obj = ServidorFisico(i, cpu_total, ram_total_alocavel)
                lista_servidores_obj.append(servidor_obj)
                mapeamento_servidores[i] = nome_servidor
        print(f"Lidos {len(lista_servidores_obj)} servidores. Capacidade calculada com superalocação.")

        with open(caminho_vms, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                nome_vm, cpu_req, ram_req_gb = row['Name'], int(row['CPUs']), _parse_memory_string_to_gb(row['Memory Size'])
                vm_obj = MaquinaVirtual(i, cpu_req, ram_req_gb)
                lista_vms_obj.append(vm_obj)
                mapeamento_vms[i] = nome_vm
        print(f"Lidas {len(lista_vms_obj)} VMs.")

    # --- Verificação de Capacidade Total ---
        # Soma a capacidade total de todos os servidores carregados
        ram_total_dos_servidores = sum(serv.ram_total for serv in lista_servidores_obj)
        cpu_total_dos_servidores = sum(serv.cpu_total for serv in lista_servidores_obj)
        
        # Soma os recursos totais requeridos por todas as VMs
        ram_total_das_vms = sum(vm.ram_req for vm in lista_vms_obj)
        cpu_total_das_vms = sum(vm.cpu_req for vm in lista_vms_obj)

        # Verifica se a demanda total excede a capacidade total
        if (ram_total_das_vms > ram_total_dos_servidores or 
            cpu_total_das_vms > cpu_total_dos_servidores):
            
            print(f'''
            ERRO: As VMs não cabem no datacenter. A demanda total de recursos excede a capacidade.

            \t\t| Capacidade do DC \t| Demanda das VMs \t| Diferença
            {'-'*75}
            RAM (GB)\t| {ram_total_dos_servidores:<15} \t| {ram_total_das_vms:<15} \t| {ram_total_dos_servidores - ram_total_das_vms}
            {'-'*75}
            CPU (vCores)| {cpu_total_dos_servidores:<15} \t| {cpu_total_das_vms:<15} \t| {cpu_total_dos_servidores - cpu_total_das_vms}

            Programa encerrado.
            ''')
            # Em vez de sys.exit(), é mais limpo retornar None para o main.py lidar com a saída.
            return None

        return {
            "servidores": lista_servidores_obj, "vms": lista_vms_obj,
            "mapeamento_servidores": mapeamento_servidores, "mapeamento_vms": mapeamento_vms
        }
    except Exception as e:
        print(f"ERRO CRÍTICO ao carregar cenário: {e}")
        return None

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
