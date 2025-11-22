# 🎥✨ Organizador de Fundos ProPresenter

[![Versão](https://img.shields.io/badge/versão-1.0.0-blue)](https://github.com/anabe-apereira/organizador-backgrounds/releases)
[![Licença: MIT](https://img.shields.io/badge/Licença-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/anabe-apereira/organizador-backgrounds)

**Organizador de Fundos ProPresenter** é uma ferramenta profissional para **organização automática** de vídeos usados como fundos no ProPresenter, classificando-os por cores predominantes. Desenvolvido para produtoras de vídeo, igrejas e profissionais de mídia, este aplicativo agiliza significativamente o fluxo de trabalho de gerenciamento de mídia.

## 📋 Visão Geral

Este software foi projetado para:
- Automatizar a organização de bibliotecas de vídeos
- Melhorar a eficiência na produção de cultos e eventos
- Reduzir o tempo gasto na classificação manual de mídias
- Manter uma biblioteca visualmente organizada e de fácil navegação

---

## 🚀 Principais Recursos

### 🎨 Análise de Cores Avançada
- Identificação precisa de cores predominantes usando algoritmos de clusterização
- Suporte a múltiplas combinações de cores
- Detecção automática de preto e branco

### 📂 Gerenciamento Inteligente de Arquivos
- Organização automática em estrutura de pastas lógica
- Prevenção de duplicação de arquivos
- Manutenção de metadados originais

### 🖥️ Interface Profissional
- Design intuitivo e responsivo
- Barra de progresso em tempo real
- Log de atividades detalhado
- Suporte a temas claros e escuros (a partir da versão 1.0.0)

### ⚙️ Personalização
- Ajuste de sensibilidade de cores
- Configuração de pastas de origem e destino
- Opções avançadas para usuários experientes

### 📊 Relatórios
- Estatísticas de processamento
- Histórico de operações
- Logs detalhados para solução de problemas

---

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8 ou superior
- OpenCV (instalado automaticamente)
- NumPy (instalado automaticamente)
- Tkinter (geralmente incluído com Python)

### Instalação do Executável (Recomendado para Usuários Finais)

1. Baixe a versão mais recente do [Organizador de Fundos ProPresenter](https://github.com/anabe-apereira/organizador-backgrounds/releases)
2. Execute o instalador `OrganizadorFundos_Setup.exe`
3. Siga as instruções na tela
4. O aplicativo será instalado no Menu Iniciar e na Área de Trabalho

### Instalação via Código Fonte (Desenvolvedores)

```bash
# Clone o repositório
git clone https://github.com/anabe-apereira/organizador-backgrounds.git
cd organizador-backgrounds

# Crie um ambiente virtual (recomendado)
python -m venv venv
.\venv\Scripts\activate  # No Windows
# ou
source venv/bin/activate  # No Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
python organize_backgrounds.py
```

## 📦 Requisitos do Sistema

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
