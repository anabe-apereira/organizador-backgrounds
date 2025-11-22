import os
import PyInstaller.__main__
import shutil
import sys

# Nome do aplicativo
APP_NAME = "OrganizadorFundos"

def main():
    try:
        # Limpar builds anteriores
        if os.path.exists('build'):
            print("Removendo pasta 'build' antiga...")
            shutil.rmtree('build')
        if os.path.exists('dist'):
            print("Removendo pasta 'dist' antiga...")
            shutil.rmtree('dist')
        
        # Certificar que o diretório de logs existe
        if not os.path.exists('logs'):
            print("Criando diretório 'logs'...")
            os.makedirs('logs')
        
        # Opções do PyInstaller
        pyinstaller_args = [
            'organize_backgrounds.py',
            '--name', APP_NAME,
            '--onefile',
            '--windowed',  # Não mostrar console
            '--icon=icon.ico',  # Incluir o ícone
            '--add-data=icon.ico;.',  # Incluir o ícone nos recursos
            '--hidden-import=sklearn.utils._cython_blas',
            '--hidden-import=sklearn.tree._utils',
            '--hidden-import=sklearn.tree._splitter',
            '--hidden-import=sklearn.tree._criterion',
            '--hidden-import=sklearn.utils._weight_vector',
            '--hidden-import=sklearn.metrics._pairwise_distances_reduction',
            '--hidden-import=sklearn.metrics._pairwise_fast',
            '--hidden-import=sklearn.neighbors._partition_nodes',
            '--hidden-import=sklearn.neighbors._quad_tree',
            '--hidden-import=scipy._lib.messagestream',
            '--clean',
            '--noconfirm'
        ]
        
        print("Iniciando a construção do executável...")
        # Executar o PyInstaller
        PyInstaller.__main__.run(pyinstaller_args)
        
        print(f"\n[SUCESSO] Build concluido com sucesso!")
        print(f"[INFO] O executavel esta na pasta 'dist' com o nome: {APP_NAME}.exe")
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante a construcao do executavel: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
