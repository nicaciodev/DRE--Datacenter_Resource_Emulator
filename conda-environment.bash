#!/bin/bash

# Gerando o arquivo lock
conda-lock lock -f environment.yml --platform linux-64 --platform win-64 --platform osx-64

# Renderizando:
conda-lock render --platform linux-64 
conda-lock render --platform win-64 
conda-lock render --platform osx-64 
mv conda-linux-64.lock conda-linux-64.txt
sed -i 's/@EXPLICIT//' conda-linux-64.txt
mv conda-osx-64.lock conda-osx-64.txt
sed -i 's/@EXPLICIT//' conda-osx-64.txt
mv conda-win-64.lock conda-win-64.txt
sed -i 's/@EXPLICIT//' conda-win-64.txt

# Atualizando o ambiente:
conda env update --name fiap_tech_challenge_2 --file conda-linux-64.txt --prune
