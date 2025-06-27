# -*- coding: utf-8 -*-
"""
Módulo responsável por toda a lógica de visualização do projeto DRE.
"""
import pygame
from typing import List, Tuple
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
# ALTERADO: Altura ajustada para caber 3 servidores na vertical
SERVER_WIDTH = 300
SERVER_HEIGHT = 220
PADDING = 20
BAR_HEIGHT = 20
VM_COLOR = (100, 150, 250)
VM_TEXT_COLOR = (255, 255, 255)
STATS_BOX_HEIGHT = 120
PLOT_AREA_WIDTH = 400

# --- Função Principal de Desenho do Datacenter ---

def draw_datacenter_state(screen: pygame.Surface, font: pygame.font.Font, servidores: List[ServidorFisico], best_solution: List[int], vms: List[MaquinaVirtual], plot_x_offset: int, scroll_x: int) -> int:
    """
    Desenha o estado do datacenter em uma superfície rolável (viewport).
    """
    viewport_rect = pygame.Rect(0, 0, plot_x_offset - PADDING, screen.get_height())

    # --- LÓGICA DE LAYOUT CORRIGIDA (PARA MÚLTIPLAS COLUNAS) ---
    # Calcula a largura e o número de colunas necessárias para o "mundo"
    servidores_por_coluna = viewport_rect.height // (SERVER_HEIGHT + PADDING)
    if servidores_por_coluna == 0: servidores_por_coluna = 1
    num_colunas = -(-len(servidores) // servidores_por_coluna) # Truque para arredondar para cima
    total_world_width = num_colunas * (SERVER_WIDTH + PADDING) + PADDING

    world_surface = pygame.Surface((total_world_width, viewport_rect.height))
    world_surface.fill(screen.get_at((1,1)))

    temp_servidores = [ServidorFisico(s.id, s.cpu_total, s.ram_total) for s in servidores]
    for vm_index, servidor_id in enumerate(best_solution):
        if 0 <= servidor_id < len(temp_servidores):
            try:
                temp_servidores[servidor_id].alocar_vm(vms[vm_index])
            except ValueError: pass
    
    # Desenha os servidores no "mundo" preenchendo as colunas de cima para baixo
    x, y = PADDING, PADDING
    for servidor in temp_servidores:
        draw_servidor(world_surface, font, servidor, x, y)
        y += SERVER_HEIGHT + PADDING
        if y + SERVER_HEIGHT > viewport_rect.height:
            y = PADDING
            x += SERVER_WIDTH + PADDING
    # --- FIM DA LÓGICA DE LAYOUT ---

    max_scroll_x = total_world_width - viewport_rect.width
    if max_scroll_x < 0: max_scroll_x = 0
    scroll_x = max(0, min(scroll_x, max_scroll_x))
    
    screen.blit(world_surface, viewport_rect.topleft, (scroll_x, 0, viewport_rect.width, viewport_rect.height))

    return scroll_x

# O resto do arquivo permanece o mesmo
def draw_servidor(screen: pygame.Surface, font: pygame.font.Font, servidor: ServidorFisico, x: int, y: int):
    rect = pygame.Rect(x, y, SERVER_WIDTH, SERVER_HEIGHT)
    pygame.draw.rect(screen, (245, 245, 245), rect, border_radius=5)
    pygame.draw.rect(screen, (50, 50, 50), rect, 2, border_radius=5)
    id_text = font.render(f"Servidor ID: {servidor.id} ({len(servidor.vms_hospedadas)} VMs)", True, (0,0,0))
    screen.blit(id_text, (x + 10, y + 10))
    cpu_percent = (servidor.cpu_usada / servidor.cpu_total) if servidor.cpu_total > 0 else 0
    draw_usage_bar(screen, font, f"CPU: {servidor.cpu_usada}/{servidor.cpu_total}", cpu_percent, x + 10, y + 40, (255, 100, 100))
    ram_percent = (servidor.ram_usada / servidor.ram_total) if servidor.ram_total > 0 else 0
    draw_usage_bar(screen, font, f"RAM: {servidor.ram_usada}/{servidor.ram_total} GB", ram_percent, x + 10, y + 80, (100, 100, 255))
    vm_x, vm_y = x + 10, y + 135
    server_bottom_limit = y + SERVER_HEIGHT - PADDING
    for vm in servidor.vms_hospedadas:
        if vm_y + 25 > server_bottom_limit:
            ellipsis_text = font.render("...", True, (50, 50, 50))
            screen.blit(ellipsis_text, (vm_x, vm_y))
            break
        vm_rect = pygame.Rect(vm_x, vm_y, 60, 25)
        pygame.draw.rect(screen, VM_COLOR, vm_rect, border_radius=3)
        vm_text = font.render(f"VM {vm.id}", True, VM_TEXT_COLOR)
        screen.blit(vm_text, (vm_x + 5, vm_y + 5))
        vm_x += 60 + 5
        if vm_x + 60 > x + SERVER_WIDTH:
            vm_x = x + 10
            vm_y += 25 + 5

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

def draw_fitness_plot(screen: pygame.Surface, history: List[float], x_offset: int) -> int:
    if not MATPLOTLIB_AVAILABLE or not history:
        return 0
    fig_width = 400 / 100
    fig, ax = plt.subplots(figsize=(fig_width, 4.5), dpi=100)
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
    return size[0]

def draw_stats_box(screen: pygame.Surface, font: pygame.font.Font, generation: int, best_fitness: float, x_offset: int, box_width: int):
    if box_width == 0: return
    y_pos = PADDING + 450 + PADDING
    stats_rect = pygame.Rect(x_offset, y_pos, box_width, STATS_BOX_HEIGHT)
    pygame.draw.rect(screen, (240, 240, 240), stats_rect)
    pygame.draw.rect(screen, (50, 50, 50), stats_rect, 2, border_radius=5)
    title_text = font.render("Status da Simulação:", True, (0,0,0))
    screen.blit(title_text, (x_offset + PADDING, y_pos + PADDING))
    gen_text = font.render(f"Geração Atual: {generation}", True, (50,50,50))
    screen.blit(gen_text, (x_offset + PADDING, y_pos + PADDING + 30))
    fitness_text = font.render(f"Melhor Fitness: {best_fitness:.2f}", True, (50,50,50))
    screen.blit(fitness_text, (x_offset + PADDING, y_pos + PADDING + 55))
