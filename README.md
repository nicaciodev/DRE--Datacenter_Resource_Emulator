## DRE - Datacenter Resource Emulator
![Static Badge](https://img.shields.io/badge/Vers%C3%A3o-1.3-blue) ![GitHub](https://img.shields.io/github/license/nicaciodev/DRE--Datacenter_Resource_Emulator) ![Static Badge](https://img.shields.io/badge/Data-14%2F07%2F2025-green)

___

#### Tech-Challenge da Fase 02 da Post-Tech (FIAP)

>>>> *"O desafio consiste em projetar, implementar e testar um sistema que
utilize Algoritmos Genéticos para otimizar uma função ou resolver um problema
complexo de otimização. Você pode escolher problemas como otimização de
rotas, alocação de recursos e design de redes neurais."
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

## Instalação via conda-lock
> A ferramenta conda-lock garante criar o ambiente diretamente a partir 
> do arquivo de bloqueio mestre, garantindo a maior fidelidade ao ambiente de desenvolvimento original. 


#### Pré-requisitos
> Antes de começar, garanta que você tenha uma instalação do [Anaconda](https://www.anaconda.com/download/success).

#### Passo 1: Obtenha o Código-Fonte
> Clone este repositório para a sua máquina local e navegue para a pasta do projeto.
```
<<<<<<< HEAD
git clone https://github.com/nicaciodev/DRE--Datacenter_Resource_Emulator.git &&\
cd DRE--Datacenter_Resource_Emulator
```

#### Passo 2: Instale o conda-lock
> Esta ferramenta precisa ser instalada uma única vez no seu ambiente 
> base do Conda.

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

## Instalação Via Anaconda 
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


## Estrutura do Repositório

* `README.md`: Este arquivo, com a descrição e instruções do projeto.
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
* `historico.txt`: História e experimentos.
* `visualization.py`: A funções para montar o dashborad.

## Autor
___
| [<img src="https://avatars.githubusercontent.com/u/136343808?v=4" width=115><br><sub>Robson Nicácio</sub>](https://github.com/nicaciodev) |
| :---: |
