import subprocess
import re
from pathlib import Path
import os

# Caminho para o arquivo requirements.txt
req_file = Path(r"C:\Projetos\Django_ERP\BackEnd\requirements.txt")

# Ler as dependências atuais
with open(req_file, 'r') as f:
    dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Remover versões específicas para verificar as mais recentes
clean_deps = []
for dep in dependencies:
    match = re.match(r'^([a-zA-Z0-9_.-]+)', dep)
    if match:
        clean_deps.append(match.group(1))

# Verificar versões atuais e mais recentes
print("Verificando pacotes desatualizados. Isso pode levar alguns minutos...")
updates_needed = []

for dep in clean_deps:
    try:
        # Obter versão instalada
        cmd_current = f"pip show {dep}"
        output = subprocess.check_output(cmd_current, shell=True, text=True)
        current_version = re.search(r'Version: (.+)', output).group(1)
        
        # Verificar versão mais recente - suprimindo avisos redirecionando stderr para DEVNULL
        cmd_latest = f"pip index versions {dep}"
        output = subprocess.check_output(
            cmd_latest, 
            shell=True, 
            text=True,
            stderr=subprocess.DEVNULL  # Suprimir mensagens de aviso
        )
        latest_version = re.search(r'Available versions: (.+)', output).group(1).split(',')[0].strip()
        
        if current_version != latest_version:
            updates_needed.append((dep, current_version, latest_version))
            print(f"{dep}: {current_version} -> {latest_version}")
    except:
        print(f"Não foi possível verificar {dep}")

# Perguntar se deseja atualizar
if updates_needed:
    resp = input("Deseja atualizar os pacotes? (s/n): ")
    if resp.lower() == 's':
        for dep, _, _ in updates_needed:
            try:
                print(f"Atualizando {dep}...")
                subprocess.run(f"pip install --upgrade {dep}", shell=True)
            except:
                print(f"Falha ao atualizar {dep}")
        
        # Atualizar o arquivo requirements.txt
        print("Atualizando requirements.txt...")
        subprocess.run("pip freeze > " + str(req_file), shell=True)
        print("Arquivo requirements.txt atualizado com sucesso!")
else:
    print("Todos os pacotes estão atualizados!")