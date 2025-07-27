## DRE - Datacenter Resource Emulator
![Static Badge](https://img.shields.io/badge/Vers%C3%A3o-2.1-blue) ![GitHub](https://img.shields.io/github/license/nicaciodev/DRE--Datacenter_Resource_Emulator) ![Static Badge](https://img.shields.io/badge/Data-27%2F07%2F2025-green)

___

#### Tech-Challenge da Fase 02 da Post-Tech (FIAP)

>>>> "O desafio consiste em projetar, implementar e testar um sistema que
utilize Algoritmos Genéticos para otimizar uma função ou resolver um problema
complexo de otimização. Você pode escolher problemas como otimização de
rotas, **alocação de recursos** e design de redes neurais."
>>>> 
>>>> (FIAP, Pos-Tech, Fase2, Tech-Challenge, Instruções)*

#### [ RM363334 ]

#### Robson Nicácio R. dos Santos
___

## Objetivo
> Um simulador que utilize AGs para resolver o clássico problema de "Bin Packing" na alocação de novas máquinas virtuais.
> 
> O objetivo não é competir com as ferramentas operacionais do dia a dia como o VMware, mas sim focar em um problema de planejamento estratégico que elas não cobrem:
>
> Determinar o número mínimo de servidores físicos necessários para atender a novas demandas e otimizar a consolidação da infraestrutura.

## Documentação Completa

> A documentação completa se encontra no diretório [Docs](https://github.com/nicaciodev/DRE--Datacenter_Resource_Emulator/tree/main/Docs) deste projeto nos formatos: [Markdown](https://github.com/nicaciodev/DRE--Datacenter_Resource_Emulator/blob/main/Docs/DRE--Documentacao_Completa.md), [PDF](https://github.com/nicaciodev/DRE--Datacenter_Resource_Emulator/blob/main/Docs/DRE--Documentacao_Completa.pdf) e [HML].

## Resumo do Projeto
> O DRE (Datacenter Resource Emulator) é um projeto desenvolvido como parte do Tech Challenge da Pós-Graduação em "IA para Devs". A aplicação utiliza um Algoritmo Genético (AG) para resolver um problema clássico de otimização: a alocação de Máquinas Virtuais (VMs) em um número mínimo de Servidores Físicos, conhecido como Bin Packing Problem.

> O núcleo do projeto é um operador de crossover heurístico customizado, o D.O.A.C. (Dominant Optimal Anti-Cancer), que emprega estratégias como a herança de "genes dominantes" e o refinamento "anti-câncer" para acelerar a convergência e encontrar soluções de alta qualidade. Para validar sua eficácia, o desempenho do D.O.A.C. é comparado com uma abordagem de crossover convencional, o Crossover por Consenso (CPC).

> A simulação é visualizada em tempo real através de uma interface gráfica construída com Tkinter, exibindo a alocação das VMs e a evolução do fitness a cada geração.

[<img src="https://github.com/nicaciodev/DRE--Datacenter_Resource_Emulator/blob/main/Docs/Screenshot.png?raw=true" width=1579><br><sub>Screenshot</sub>](https://github.com/nicaciodev/DRE--Datacenter_Resource_Emulator/blob/main/Docs/Screenshot.png?raw=true)


## Questionário Sobre Projeto

* O que está sendo otimizando?

> A alocação de um conjunto de Máquinas Virtuais (VMs) em um parque de Servidores Físicos, buscando a consolidação mais eficiente possível da carga de trabalho.

* Qual é a variável à maximizar ou minimizar?

> A variável a ser minimizada é o número total de Servidores Físicos ativos necessários para hospedar todas as VMs.

* Qual é a representação da solução (genoma)?

> Uma lista de inteiros, onde o índice da lista representa o id da VM e o valor naquela posição representa o id do Servidor Físico onde ela está alocada.

* Qual é a função de fitness?

> A função calcula o número de servidores únicos utilizados em uma dada solução. Soluções que violam as restrições de capacidade (CPU ou RAM) de um servidor recebem uma penalidade, resultando em um fitness infinito (float('inf')), o que as remove da competição.

* Qual é o método de seleção?

> Seleção de elite. Os pais são sorteados aleatoriamente de um "pool" composto pelos 10% melhores indivíduos da população atual, que já está ordenada por fitness.

* Qual método de crossover será implementado?

> Foram implementados dois métodos para fins de comparação:

>> * D.O.A.C. (Dominant Optimal Anti-Cancer): O crossover principal, uma heurística customizada que prioriza a herança do servidor mais potente ("Gene Dominante") e refina a solução tentando esvaziar o servidor menos potente ("Anti-Câncer").

>> * Crossover por Consenso (CPC): Um método convencional que preserva as alocações em que ambos os pais concordam e resolve os "conflitos" herdando as características dos pais.

* Qual será o método de inicialização?

> A população inicial é gerada pelo método Round-Robin, que distribui as VMs de forma sequencial e uniforme entre todos os servidores disponíveis para criar uma solução inicial consistente e subótima, ideal para demonstrar a evolução do algoritmo.

* Qual o critério de parada?

> A simulação para sob duas condições: ao atingir o número máximo de gerações definido (ex: 1000) ou se o melhor fitness não apresentar melhoria por um número consecutivo de gerações (ex: 200), indicando a convergência da solução.

## Estrutura do Repositório

* `README.md`: Este arquivo, com a descrição e instruções do projeto.
* `Docs`: Documentação completa do projeto. 
* `LICENSE`: Contém a licença deste projeto.
* `main.py`: Arquivo principal do projeto DRE.
* `cenario_teste.json`: Arquivo que descreve um problema teste.
* `cenario_desafiador.json`: Arquivo que descreve um problema teste maior.
* `ExportList--servidores.csv`: Cenário real vmware - servidores.
* `ExportList--VMs.csv`: Cenário real vmware - VMs.
* `conda-environment.bash`: Gerar arquivos [conda-...] para ambientes diferentes.
* `conda-linux-64.txt`: Arquivo conda para ambiente linux.
* `conda-lock.yml`: Arquivo do conda-lock.
* `conda-osx-64.txt`: Arquivo conda para ambiente MAC.
* `conda-win-64.txt`: Arquivo conda para ambiente Windows.
* `environment.yml`: Gerência das libs utilizadas no Anaconda.
* `datacenter_model.py`: Define os objetos do datacenter.
* `genetic_algorithm.py`: Deine fitness, mutação, crossover etc.
* `visualization.py`: A funções para montar o dashborad.
* `Testes.txt`: Alguns resultados comparativos.


## Instalação via conda-lock
> A ferramenta conda-lock garante criar o ambiente diretamente a partir do arquivo de bloqueio mestre, garantindo a maior fidelidade ao ambiente de desenvolvimento original. 

> Os passos Seguintes são para um Sistema Operacional Linux Debian 12.

> Mais adiante existem explicações para utilização única do [anaconda] para outros sistemas operacionais.


#### Pré-requisitos
> Antes de começar, garanta que você tenha uma instalação do [Anaconda](https://www.anaconda.com/download/success), do qual instalaremos o conda-lock.

#### Passo 1: Obtenha o Código-Fonte
> Clone este repositório para a sua máquina local e navegue para a pasta do projeto.
```
git clone https://github.com/nicaciodev/DRE--Datacenter_Resource_Emulator.git &&\
cd DRE--Datacenter_Resource_Emulator
```

#### Passo 2: Instale o conda-lock
> Esta ferramenta precisa ser instalada uma única vez no seu ambiente base do Conda, ou seja, fora de ambientes virtuais (env).

```
conda install -c conda-forge conda-lock &&\
ln -s ~/anaconda3/bin/conda-lock ~/anaconda3/condabin/
```

#### Passo 3: Crie a ative o ambiente
> Este único comando lerá o arquivo conda-lock.yml, detectará sua 
> plataforma e instalará todos os pacotes corretos para criar o ambiente 
> fiap_tech_challenge_2.

```
conda-lock install --name fiap_tech_challenge_2 conda-lock.yml
```

> Após a criação, ative o ambiente:

```
conda activate fiap_tech_challenge_2
```

#### Passo 4: Executar o script principal
```
python main.py
```

## Instalação Via Anaconda - Alguns O.S.
#### Pré-requisitos
> Antes de começar, garanta que você tenha uma instalação do [Anaconda](https://www.anaconda.com/download/success) ou Miniconda em seu sistema. 
> Se não tiver, o [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main) é uma instalação leve e recomendada.

#### Passo 1: Obtenha o Código-Fonte
> Clone este repositório para a sua máquina local e navegue para a pasta do projeto.
```
git clone https://github.com/nicaciodev/DRE--Datacenter_Resource_Emulator.git 
cd DRE--Datacenter_Resource_Emulator
```

#### Passo 2: Crie o Ambiente Conda
> Os arquivos de ambiente (environment-[plataforma].txt) contêm a lista exata de todos os pacotes necessários para executar este projeto. 
> Use o comando correspondente ao seu sistema operacional para criar um ambiente isolado chamado fiap_tech_challenge_2.

###### Ativando o Motor Anterior do Anaconda
> Existe uma incompatibilidade entre o formato de arquivo detalhado 
> (bom para reprodutibilidade) e o novo motor Libmamba que está ativo 
> por padrão.
>
> No final isso será desfeito.

```
conda config --set solver classic
```

###### Se você usa Linux:
```
conda create --name fiap_tech_challenge_2 --file conda-linux-64.txt
```

###### Se você usa Windows:
```
conda create --name fiap_tech_challenge_2 --file conda-win-64.txt
```

###### Se você usa macOS (Intel):
```
conda create --name fiap_tech_challenge_2 --file conda-osx-64.txt
```

##### Obs.:
> Este comando pode levar alguns minutos, pois o Conda fará o download e a instalação 
> de todos os pacotes especificados.


###### Ativando o Motar Atual do Anaconda
> Para garantir que futuras operações do Conda sejam mais rápidas,
> como de fábrica.

```
conda config --set solver libmamba
```


#### Passo 3: Ative o Ambiente
> Após a criação, você precisa "entrar" no ambiente para poder usá-lo.
```
conda activate fiap_tech_challenge_2
```

> Após a ativação, você verá o nome do ambiente entre parênteses no início do seu 
> prompt do terminal, algo como (fiap_tech_challenge_2). 
> Isso indica que o ambiente está ativo e pronto para uso.

#### Passo 4: Executar o script principal
```
python main.py
```


## Conclusões
> O desenvolvimento do projeto DRE (Datacenter Resource Emulator) demonstrou com sucesso a aplicação prática e a eficácia de Algoritmos Genéticos para resolver um problema de otimização complexo e relevante no mundo real: a alocação de máquinas virtuais em servidores físicos.

#### Principais Conclusões:

> * Validação da Abordagem Genética: Os resultados obtidos provam que a abordagem evolucionária é não apenas viável, mas altamente eficaz para o Problema do Empacotamento. O algoritmo foi capaz de navegar por um vasto espaço de soluções possíveis e convergir consistentemente para um resultado ótimo, superando métodos convencionais.

> * A Superioridade da Heurística Customizada: A comparação direta entre o crossover convencional (CPC) e o crossover customizado (DOAC) foi a descoberta mais significativa do projeto. Enquanto o CPC obteve uma melhoria respeitável, o desempenho superior e a estabilidade do DOAC destacam uma conclusão fundamental em computação evolucionária: a incorporação de conhecimento específico do problema (heurísticas) nos operadores genéticos acelera drasticamente a convergência e eleva a qualidade da solução final. Estratégias como o "Gene Dominante" e o "Tratamento Anti-Câncer" não foram apenas metáforas, mas mecanismos eficazes que guiaram a busca para regiões mais promissoras do espaço de soluções.

> * No fim foi obtido uma ferramenta real para uso em um Datacenter real, visando prever alocações com a entrada de novos projetos no mesmo.


## Autor
___
| [<img src="https://avatars.githubusercontent.com/u/136343808?v=4" width=115><br><sub>Robson Nicácio</sub>](https://github.com/nicaciodev) |
| :---: |
