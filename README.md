# 🎥✨ Organizador de Fundos ProPresenter
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/anabe-apereira/organizador-backgrounds)

Aplicativo para **organizar automaticamente** vídeos usados como fundos no ProPresenter, separando-os por cores predominantes.  
Ideal para agilizar fluxos de mídia e manter bibliotecas visualmente organizadas! 🎨📁

---

## 🚀 Funcionalidades

- 🎞️ **Análise automática de vídeos** para identificar cores predominantes  
- 🗂️ **Organização em pastas** por cor única ou combinações  
- 🖥️ **Interface gráfica amigável**  
- 🧰 **Modo linha de comando** para automação  
- 🎧 **Suporte a vários formatos de vídeo** (mp4, mov, avi, m4v)  
- 📝 **Geração de log detalhado** para auditoria

---

## 📦 Requisitos

- 🐍 Python **3.9+**
- 📄 Bibliotecas listadas no `requirements.txt`

---

## 🔧 Instalação

1. 🡇 Clone este repositório ou baixe os arquivos  
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## ▶️ Como Usar

### 🖱️ Interface Gráfica

Abra o app sem argumentos:

```bash
python organize_backgrounds.py
```

### 🖥️ Linha de Comando

```bash
python organize_backgrounds.py --src "caminho/para/origem" --dst "caminho/para/destino" [--overwrite]
```

**Parâmetros:**
- 📁 `--src`: pasta de origem com os vídeos  
- 📁 `--dst`: pasta destino dos vídeos organizados  
- 🔄 `--overwrite`: sobrescreve arquivos existentes (opcional)

---

## 🌈 Pastas de Saída

Os vídeos serão organizados em:

- 🎨 Cores únicas:  
  `branco/`, `vermelho/`, `laranja/`, `amarelo/`, `verde/`, `ciano/`, `azul/`, `violeta/`, `preto/`, `rosa/`
- 🌓 Combinações:  
  `cor1-cor2/` (ex: `azul-amarelo/`)
- 🌈 `colorido/`: mais de 3 cores predominantes  
- ❓ `nao_identificado/`: vídeos sem classificação possível

---

## 🧪 Criando um Executável (Windows)

Instale o PyInstaller:

```bash
pip install pyinstaller
```

Gere o executável:

```bash
pyinstaller --onefile --windowed --icon=NONE --add-data "requirements.txt;." organize_backgrounds.py
```

### 📁 Versão robusta com `.spec`

Crie um arquivo `organizer.spec`:

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

📂 O arquivo final estará em:  
`dist/OrganizadorFundos.exe`

---

## ⚙️ Personalização

Edite parâmetros no início do arquivo `organize_backgrounds.py`:

```python
DEFAULT_CONFIG = {
    'sample_frames': 10,      # Número de quadros a serem amostrados
    'resize_width': 320,      # Largura para redimensionar os quadros
    'min_color_percent': 8,   # Percentual mínimo para considerar uma cor
    # ... outros parâmetros
}
```

---

## 📜 Logs

Um arquivo `organize.log` é gerado automaticamente com informações detalhadas do processamento.

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**.
