# Organizador de Fundos ProPresenter

Aplicativo para organizar automaticamente vídeos usados como fundos no ProPresenter, separando-os por cores predominantes.

## Funcionalidades

- Análise de vídeos para identificar cores predominantes
- Organização em pastas por cor única ou combinação de cores
- Interface gráfica amigável
- Modo linha de comando para automação
- Suporte a múltiplos formatos de vídeo (mp4, mov, avi, m4v)
- Geração de log detalhado

## Requisitos

- Python 3.9 ou superior
- Bibliotecas listadas em `requirements.txt`

## Instalação

1. Clone este repositório ou faça o download dos arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como Usar

### Interface Gráfica

Execute o aplicativo sem argumentos para abrir a interface gráfica:

```bash
python organize_backgrounds.py
```

### Linha de Comando

```bash
python organize_backgrounds.py --src "caminho/para/origem" --dst "caminho/para/destino" [--overwrite]
```

Parâmetros:
- `--src`: Caminho para a pasta de origem contendo os vídeos
- `--dst`: Caminho para a pasta de destino onde os vídeos organizados serão salvos
- `--overwrite`: Opcional. Se especificado, sobrescreve arquivos existentes

### Pastas de Saída

Os vídeos serão organizados nas seguintes pastas:
- Pastas de cores únicas: `branco/`, `vermelho/`, `laranja/`, `amarelo/`, `verde/`, `ciano/`, `azul/`, `violeta/`, `preto/`, `rosa/`
- Pastas de combinação: `cor1-cor2/` (ex: `azul-amarelo/`)
- `colorido/`: Para vídeos com mais de 3 cores predominantes
- `nao_identificado/`: Para vídeos que não puderam ser classificados

## Gerando um Executável (Windows)

Para criar um executável .exe, use o PyInstaller com as opções recomendadas:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=NONE --add-data "requirements.txt;." organize_backgrounds.py
```

Para um executável mais robusto, crie um arquivo `organizer.spec`:

```python
# organizer.spec
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(['organize_backgrounds.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=['tkinter', 'cv2', 'numpy', 'sklearn', 'tqdm'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='OrganizadorFundos',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          windowed=True,
          icon='NONE')
```

Depois execute:
```bash
pyinstaller organizer.spec
```

O arquivo executável estará em `dist/OrganizadorFunds.exe`.

## Personalização

Você pode ajustar os parâmetros de detecção de cores modificando as constantes no início do arquivo `organize_backgrounds.py`:

```python
DEFAULT_CONFIG = {
    'sample_frames': 10,        # Número de quadros a serem amostrados
    'resize_width': 320,        # Largura para redimensionar os quadros
    'min_color_percent': 8,     # Percentual mínimo para considerar uma cor
    # ... outros parâmetros
}
```

## Logs

Um arquivo `organize.log` é criado no diretório de execução com informações detalhadas do processamento.

## Licença

Este projeto está licenciado sob a licença MIT.
