# Arquivo: visualization4.py
# VERSÃO 4 FINAL: Polimento da interface, com importação direta e overflow corrigido.

import tkinter as tk
from tkinter import ttk
from typing import List, Dict
from datacenter_model import ServidorFisico, MaquinaVirtual

# --- Importações do Gráfico (agora são obrigatórias) ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# --- Constantes de Visualização ---
SERVER_FRAME_WIDTH = 280
SERVER_FRAME_HEIGHT = 200
VM_GRID_COLUMNS = 4
VM_BOX_WIDTH = 60
VM_BOX_HEIGHT = 20

# --- Classe auxiliar para o Gráfico ---
class FitnessPlot:
    def __init__(self, parent_frame):
        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plot(self, history: List[float]):
        self.ax.clear()
        self.ax.plot(history)
        self.ax.set_title("Evolução do Fitness"); self.ax.set_xlabel("Geração")
        self.ax.set_ylabel("Nº de Servidores"); self.ax.grid(True)
        self.fig.tight_layout(pad=1.0); self.canvas.draw()

class DatacenterVisualizer:
    def __init__(self, root: tk.Tk, servidores: List[ServidorFisico], vms: List[MaquinaVirtual]):
        self.root = root
        self.servidores_base = servidores
        self.vms_base = vms
        self.root.title("DRE - Datacenter Resource Emulator (Tkinter)")
        self.root.geometry("1280x740")

        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.canvas.yview)
        scrollable_frame = ttk.Frame(self.canvas)
        scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        right_frame = ttk.Frame(main_frame, width=420, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        right_frame.pack_propagate(False)

        status_frame = ttk.LabelFrame(right_frame, text="Status da Simulação", padding=10)
        status_frame.pack(fill=tk.X, anchor="n")
        self.gen_label = ttk.Label(status_frame, text="Geração Atual: 0", font=("Consolas", 12))
        self.gen_label.pack(anchor="w")
        self.fitness_label = ttk.Label(status_frame, text="Melhor Fitness: N/A", font=("Consolas", 12))
        self.fitness_label.pack(anchor="w")

        plot_frame = ttk.Frame(right_frame, padding=(0, 10, 0, 0))
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.fitness_plot = FitnessPlot(plot_frame)
        
        self.server_widgets = {}
        for i, servidor in enumerate(self.servidores_base):
            server_frame = ttk.LabelFrame(scrollable_frame, text=f"Servidor ID: {servidor.id}", width=SERVER_FRAME_WIDTH, height=SERVER_FRAME_HEIGHT, padding=5)
            server_frame.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            server_frame.grid_propagate(False)
            
            cpu_label = ttk.Label(server_frame, text=f"CPU: 0/{servidor.cpu_total}")
            cpu_label.pack(anchor="w")
            cpu_canvas = tk.Canvas(server_frame, width=250, height=18, bg="#E0E0E0", highlightthickness=1, highlightbackground="grey")
            cpu_canvas.pack(anchor="w", pady=(0, 5))

            ram_label = ttk.Label(server_frame, text=f"RAM: 0/{servidor.ram_total} GB")
            ram_label.pack(anchor="w")
            ram_canvas = tk.Canvas(server_frame, width=250, height=18, bg="#E0E0E0", highlightthickness=1, highlightbackground="grey")
            ram_canvas.pack(anchor="w", pady=(0, 5))

            vm_canvas = tk.Canvas(server_frame, background="#FFFFFF", highlightthickness=0)
            vm_canvas.pack(fill="both", expand=True, pady=(5,0))

            self.server_widgets[servidor.id] = {
                "cpu_label": cpu_label, "cpu_canvas": cpu_canvas,
                "ram_label": ram_label, "ram_canvas": ram_canvas,
                "vm_canvas": vm_canvas
            }
    
    def _on_mousewheel(self, event):
        if hasattr(event, 'delta') and event.delta != 0:
             self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        elif event.num == 4: self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: self.canvas.yview_scroll(1, "units")

    def update_view(self, best_solution: List[int], generation: int, best_fitness: float, history: List[float]):
        uso_servidores = {s.id: {'cpu': 0, 'ram': 0, 'vms': []} for s in self.servidores_base}
        for vm_idx, s_id in enumerate(best_solution):
            if s_id != -1 and s_id in uso_servidores:
                vm = self.vms_base[vm_idx]
                uso_servidores[s_id]['cpu'] += vm.cpu_req
                uso_servidores[s_id]['ram'] += vm.ram_req
                uso_servidores[s_id]['vms'].append(vm.id)

        for servidor in self.servidores_base:
            widgets = self.server_widgets[servidor.id]
            uso = uso_servidores[servidor.id]
            
            widgets["cpu_label"].config(text=f"CPU: {uso['cpu']}/{servidor.cpu_total}")
            cpu_canvas = widgets["cpu_canvas"]
            cpu_canvas.delete("all")
            cpu_percent = (uso['cpu'] / servidor.cpu_total) if servidor.cpu_total > 0 else 0
            cpu_canvas.create_rectangle(0, 0, 250 * cpu_percent, 18, fill="#FF6464", outline="")
            
            widgets["ram_label"].config(text=f"RAM: {uso['ram']}/{servidor.ram_total} GB")
            ram_canvas = widgets["ram_canvas"]
            ram_canvas.delete("all")
            ram_percent = (uso['ram'] / servidor.ram_total) if servidor.ram_total > 0 else 0
            ram_canvas.create_rectangle(0, 0, 250 * ram_percent, 18, fill="#6464FF", outline="")

            vm_canvas = widgets["vm_canvas"]
            vm_canvas.delete("all")
            vms_alocadas = sorted(uso['vms'])
            
            vm_canvas.update_idletasks()
            canvas_height = vm_canvas.winfo_height()
            vms_por_linha = max(1, (vm_canvas.winfo_width() - 4) // (VM_BOX_WIDTH + 5))
            max_linhas = max(0, canvas_height // (VM_BOX_HEIGHT + 5))
            max_vms_visiveis = max_linhas * vms_por_linha

            x, y = 2, 2
            for i, vm_id in enumerate(vms_alocadas):
                # <<< CORREÇÃO DO OVERFLOW: Reserva espaço para a mensagem "e mais..." >>>
                if max_vms_visiveis > 0 and i >= (max_vms_visiveis - 1) and len(vms_alocadas) > max_vms_visiveis:
                    vms_restantes = len(vms_alocadas) - i
                    vm_canvas.create_text(x, y + 10, text=f"...e mais {vms_restantes}", anchor="w", font=("Consolas", 10))
                    break
                
                vm_canvas.create_rectangle(x, y, x + VM_BOX_WIDTH, y + VM_BOX_HEIGHT, fill="#6496FA", outline="")
                vm_canvas.create_text(x + VM_BOX_WIDTH / 2, y + VM_BOX_HEIGHT / 2, text=f"VM {vm_id}", fill="#FFFFFF", font=("Consolas", 10))
                x += VM_BOX_WIDTH + 5
                if x + VM_BOX_WIDTH > vm_canvas.winfo_width():
                    x = 2; y += VM_BOX_HEIGHT + 5
        
        self.gen_label.config(text=f"Geração Atual: {generation}")
        self.fitness_label.config(text=f"Melhor Fitness: {best_fitness:.2f}")

        if self.fitness_plot and history:
            self.fitness_plot.update_plot(history)

        self.root.update()
