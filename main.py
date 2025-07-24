# Arquivo [main.py] - Versão Final Refatorada com Classes (Corrigida)

import tkinter as tk
from datacenter_model import carregar_cenario_vmware, carregar_cenario
from genetic_algorithm import (
    generate_round_robin_population,
    swap_mutation,
    doac_cross,
    calculate_fitness,
    select_parents
)
from visualization import DatacenterVisualizer
from relatorio import relatorio_json, relatorio_logico_json

#===[ Constantes Globais ]================================================================
CENARIO_ATIVO = 'vmware'
CENARIO_FILE = 'cenario_desafiador.json'
ARQUIVO_SERVIDORES_VMWARE = 'ExportList--servidores.csv'
ARQUIVO_VMS_VMWARE = 'ExportList--VMs.csv'

POPULATION_SIZE = 100
N_GENERATIONS = 1000
MAX_GENS_NO_IMPROVEMENT = 200
MUTATION_PROBABILITY = 0.5
ELITISM_SIZE = 2

#===[ Classe para Orquestrar o Algoritmo Genético ]=======================================
class GeneticAlgorithmRunner:
    """
    Esta classe encapsula toda a lógica e o estado da simulação do AG.
    Isso organiza o código e resolve os alertas da IDE.
    """
    def __init__(self, root, app, vms, servidores):
        self.root = root
        self.app = app
        self.vms = vms
        self.servidores = servidores

        # Inicializa o estado do AG
        self.population = generate_round_robin_population(self.vms, self.servidores, POPULATION_SIZE)
        self.generation_count = 0
        self.last_best_fitness = float('inf')
        self.generations_without_improvement = 0
        self.best_solution_final = self.population[0]
        self.best_fitness_history = []

    def start(self):
        """Inicia o loop da simulação."""
        print("--- Iniciando Simulação do Algoritmo Genético ---")
        self._run_generation()

    def _run_generation(self):
        """Executa uma única geração do AG e agenda a próxima."""
        if self.generation_count < N_GENERATIONS and self.generations_without_improvement < MAX_GENS_NO_IMPROVEMENT:
            population_fitness = [calculate_fitness(individual, self.vms, self.servidores) for individual in self.population]
            sorted_pairs = sorted(zip(population_fitness, self.population), key=lambda pair: pair[0])
            sorted_population = [pair[1] for pair in sorted_pairs]
            
            best_solution_this_gen = sorted_population[0]
            best_fitness_this_gen = sorted_pairs[0][0]
            self.best_fitness_history.append(best_fitness_this_gen)
            
            if self.generation_count % 10 == 0:
                print(f"Geração {self.generation_count}: Melhor Fitness = {best_fitness_this_gen:.0f}")

            if best_fitness_this_gen < self.last_best_fitness:
                self.last_best_fitness = best_fitness_this_gen
                self.best_solution_final = best_solution_this_gen
                self.generations_without_improvement = 0
            else:
                self.generations_without_improvement += 1

            self.app.update_view(best_solution_this_gen, self.generation_count, best_fitness_this_gen, self.best_fitness_history)

            new_population = sorted_population[:ELITISM_SIZE]
            while len(new_population) < POPULATION_SIZE:
                parent1, parent2 = select_parents(sorted_population)
                child1, child2 = doac_cross(parent1, parent2, self.vms, self.servidores)
                child1 = swap_mutation(child1, self.vms, self.servidores, MUTATION_PROBABILITY)
                child2 = swap_mutation(child2, self.vms, self.servidores, MUTATION_PROBABILITY)
                new_population.append(child1)
                if len(new_population) < POPULATION_SIZE:
                    new_population.append(child2)
            
            self.population = new_population
            self.generation_count += 1
            
            self.root.after(1, self._run_generation)
        else:
            print("\n--- Simulação Finalizada ---")
            print(f"Melhor solução final encontrada com fitness de: {self.last_best_fitness:.0f}")
            relatorio_json(self.best_solution_final, self.vms, self.servidores, "solucao_final_detalhada.json")
            relatorio_logico_json(self.best_solution_final, "solucao_final_logica.json")
            
#===[ Função Principal ]=================================================================
def main():
    """
    Função principal que inicializa os componentes e inicia a aplicação.
    """
    print("--- Carregando Cenário ---")
    if CENARIO_ATIVO == 'vmware':
        datacenter_info = carregar_cenario_vmware(ARQUIVO_SERVIDORES_VMWARE, ARQUIVO_VMS_VMWARE)
    else:
        datacenter_info = carregar_cenario(CENARIO_FILE)

    if not datacenter_info or not datacenter_info.get('servidores'):
        print("Falha ao carregar o cenário. Encerrando o programa.")
        return
        
    vms = datacenter_info['vms']
    servidores = datacenter_info['servidores']
    servidores.sort(key=lambda s: s.id)
    vms.sort(key=lambda vm: vm.id)
    print("--- Cenário Carregado com Sucesso ---\n")

    root = tk.Tk()
    app = DatacenterVisualizer(root, servidores, vms)
    runner = GeneticAlgorithmRunner(root, app, vms, servidores)

    runner.start()
    root.mainloop()

# --- Ponto de Entrada do Programa ---
if __name__ == '__main__':
    main()
