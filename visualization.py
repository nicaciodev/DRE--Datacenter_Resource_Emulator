# -*- coding: utf-8 -*-
"""
Módulo responsável por toda a lógica de visualização do projeto DRE.
Contém funções para desenhar o estado dos servidores, as VMs alocadas
e o gráfico de evolução do fitness usando Pygame e Matplotlib.
"""

import pygame
from typing import List, Tuple, Dict, Any

from datacenter_model import ServidorFisico, MaquinaVirtual

try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    matplotlib.use("Agg")
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# --- Constantes de Visualização ---
SERVER_WIDTH = 280
SERVER_HEIGHT = 220
PADDING = 20
BAR_HEIGHT = 20
VM_COLOR = (100, 150, 250)
VM_TEXT_COLOR = (255, 255, 255)

# --- Função Principal de Desenho do Datacenter ---

def draw_datacenter_state(screen: pygame.Surface, font: pygame.font.Font, servidores: List[ServidorFisico], best_solution: List[int], vms: List[MaquinaVirtual], plot_x_offset: int):
    """
    Desenha o estado completo do datacenter, alocando as VMs na melhor solução
    encontrada e mostrando o uso de recursos de cada servidor.
    """
    temp_servidores = [ServidorFisico(s.id, s.cpu_total, s.ram_total) for s in servidores]

    for vm_index, servidor_id in enumerate(best_solution):
        if 0 <= servidor_id < len(temp_servidores):
            try:
                temp_servidores[servidor_id].alocar_vm(vms[vm_index])
            except ValueError:
                pass

    # --- LÓGICA DE LAYOUT CORRIGIDA (PARA MÚLTIPLAS COLUNAS) ---
    x, y = PADDING, PADDING
    screen_height = screen.get_height()

    for servidor in temp_servidores:
        # Se o próximo servidor for sair da tela na vertical, pule para uma nova coluna
        if y + SERVER_HEIGHT > screen_height:
            y = PADDING
            x += SERVER_WIDTH + PADDING

        draw_servidor(screen, font, servidor, x, y)
        
        # Move a posição para baixo para o próximo servidor na mesma coluna
        y += SERVER_HEIGHT + PADDING
    # --- FIM DA LÓGICA DE LAYOUT ---


def draw_servidor(screen: pygame.Surface, font: pygame.font.Font, servidor: ServidorFisico, x: int, y: int):
    """
    Desenha um único servidor e seu estado na tela.
    """
    rect = pygame.Rect(x, y, SERVER_WIDTH, SERVER_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), rect, 2, border_radius=5)
    id_text = font.render(f"Servidor ID: {servidor.id} ({len(servidor.vms_hospedadas)} VMs)", True, (0,0,0))
    screen.blit(id_text, (x + 10, y + 10))

    cpu_percent = (servidor.cpu_usada / servidor.cpu_total) if servidor.cpu_total > 0 else 0
    draw_usage_bar(screen, font, f"CPU: {servidor.cpu_usada}/{servidor.cpu_total}", cpu_percent, x + 10, y + 40, (255, 100, 100))
    
    ram_percent = (servidor.ram_usada / servidor.ram_total) if servidor.ram_total > 0 else 0
    draw_usage_bar(screen, font, f"RAM: {servidor.ram_usada}/{servidor.ram_total} GB", ram_percent, x + 10, y + 85, (100, 100, 255))
    
    # --- LÓGICA DE DESENHO DAS VMS CORRIGIDA (PARA EVITAR ESTOURO) ---
    vm_x, vm_y = x + 10, y + 135
    server_bottom_limit = y + SERVER_HEIGHT - PADDING

    for vm in servidor.vms_hospedadas:
        # Verifica se a próxima VM a ser desenhada caberá no espaço visual
        if vm_y + 25 > server_bottom_limit:
            # Se não couber, desenha reticências e para de desenhar VMs
            ellipsis_text = font.render("...", True, (50, 50, 50))
            screen.blit(ellipsis_text, (vm_x, vm_y))
            break

        vm_rect = pygame.Rect(vm_x, vm_y, 60, 25)
        pygame.draw.rect(screen, VM_COLOR, vm_rect, border_radius=3)
        vm_text = font.render(f"VM {vm.id}", True, VM_TEXT_COLOR)
        screen.blit(vm_text, (vm_x + 5, vm_y + 5))
        
        vm_x += 60 + 5
        # Verifica se precisa quebrar a linha de VMs
        if vm_x + 60 > x + SERVER_WIDTH:
            vm_x = x + 10
            vm_y += 25 + 5
    # --- FIM DA LÓGICA DAS VMS ---

def draw_usage_bar(screen: pygame.Surface, font: pygame.font.Font, label: str, percent: float, x: int, y: int, color: Tuple[int, int, int]):
    BAR_WIDTH = SERVER_WIDTH - 20
    label_surface = font.render(label, True, (0,0,0))
    screen.blit(label_surface, (x, y))
    
    y_pos = y + font.get_height() - 1
    
    bg_rect = pygame.Rect(x, y_pos, BAR_WIDTH, BAR_HEIGHT)
    pygame.draw.rect(screen, (220, 220, 220), bg_rect, border_radius=3)
    
    fill_width = BAR_WIDTH * min(percent, 1.0)
    fill_rect = pygame.Rect(x, y_pos, fill_width, BAR_HEIGHT)
    pygame.draw.rect(screen, color, fill_rect, border_radius=3)

def draw_fitness_plot(screen: pygame.Surface, history: List[float], x_offset: int):
    if not MATPLOTLIB_AVAILABLE or not history:
        return

    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.plot(history)
    ax.set_title("Evolução do Fitness")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Nº de Servidores Usados")
    ax.grid(True)
    plt.tight_layout(pad=1.0)

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_argb()
    size = canvas.get_width_height()

    surf = pygame.image.fromstring(raw_data, size, "ARGB")
    screen.blit(surf, (x_offset, PADDING))
    
    plt.close(fig)
