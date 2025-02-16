import os
import shutil

def clean_migrations(base_dir):
    # Delete migration files
    for root, dirs, files in os.walk(base_dir):
        if 'migrations' in dirs:
            migrations_path = os.path.join(root, 'migrations')
            for file_name in os.listdir(migrations_path):
                file_path = os.path.join(migrations_path, file_name)
                if file_name.endswith('.py') and file_name != '__init__.py':
                    try:
                        os.remove(file_path)
                        print(f"Arquivo de migração deletado: {file_path}")
                    except Exception as e:
                        print(f"Erro ao deletar {file_path}: {str(e)}")

        # Delete __pycache__ directories in migrations folders
        if 'migrations' in root and '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"Cache de migração deletado: {pycache_path}")
            except Exception as e:
                print(f"Erro ao deletar cache {pycache_path}: {str(e)}")

def recreate_init_files(base_dir):
    # Recreate __init__.py files in migrations folders
    for root, dirs, files in os.walk(base_dir):
        if 'migrations' in dirs:
            migrations_path = os.path.join(root, 'migrations')
            init_file = os.path.join(migrations_path, '__init__.py')
            if not os.path.exists(init_file):
                try:
                    open(init_file, 'a').close()
                    print(f"Arquivo __init__.py recriado em: {migrations_path}")
                except Exception as e:
                    print(f"Erro ao criar __init__.py em {migrations_path}: {str(e)}")

if __name__ == '__main__':
    base_dir = os.path.join('BackEnd', 'apps')
    print("Iniciando limpeza das migrações...")
    clean_migrations(base_dir)
    print("\nRecriando arquivos __init__.py...")
    recreate_init_files(base_dir)
    print("\nProcesso finalizado!")