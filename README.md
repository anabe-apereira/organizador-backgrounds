# 🎥✨ Organizador de Fundos ProPresenter

[![Versão](https://img.shields.io/badge/versão-1.0.0-blue)](https://github.com/anabe-apereira/organizador-backgrounds/releases)
[![Licença: MIT](https://img.shields.io/badge/Licença-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
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
- Python 3.9 ou superior
- OpenCV (instalado automaticamente)
- NumPy (instalado automaticamente)
- scikit-learn (instalado automaticamente)
- tqdm (instalado automaticamente)
- Pillow (instalado automaticamente)
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
- 💾 **4GB RAM** recomendado
- 💿 **1GB espaço em disco** para o executável

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

- 🎨 **Cores únicas** (100% em português):
  `amarelo/`, `azul/`, `laranja/`, `verde/`, `vermelho/`, `violeta/`, `preto-branco/`
- 🌈 **colorido/**: vídeos com múltiplas cores predominantes
- ❓ **nao-identificado/**: vídeos sem classificação possível

**Nota**: O sistema foi atualizado para usar apenas nomes em português, eliminando pastas em inglês como `red/`, `green/`, `cyan/`, etc.

---

## 🧪 Criando um Executável (Windows)

**Método recomendado**: Use o script `build.py` incluído no projeto

```bash
# Instale o PyInstaller
pip install pyinstaller

# Execute o script de build
python build.py
```

O script `build.py` automaticamente:
- ✅ Limpa builds anteriores
- ✅ Inclui todas as dependências necessárias
- ✅ Adiciona o ícone do aplicativo
- ✅ Configura imports ocultos do sklearn

**Resultado**: `dist/OrganizadorFundos.exe`

---

## ⚙️ Personalização

Edite parâmetros no início do arquivo `organize_backgrounds.py`:

```python
DEFAULT_CONFIG = {
    'sample_frames': 10,      # Número de quadros a serem amostrados
    'resize_width': 320,      # Largura para redimensionar os quadros
    'min_color_percent': 20,  # Percentual mínimo para considerar uma cor
    'supported_formats': ('.mp4', '.mov', '.avi', '.m4v'),
    'color_ranges': {
        'vermelho': [(0, 10), (170, 179)],
        'laranja': [(11, 25)],
        'amarelo': [(26, 35)],
        'verde': [(36, 85)],
        'azul': [(101, 140)],
        'violeta': [(141, 160)],
    },
    'saturation_threshold': 30,
    'value_threshold_black': 30,
    'value_threshold_white': 200,
}
```

---

## 📜 Logs

Um arquivo de log é gerado automaticamente em:
- **Local**: `./logs/logs_YYYY-MM-DD_HH-MM-SS.txt`
- **Relativo**: Pasta `logs` no mesmo diretório do executável
- **Conteúdo**: Registro detalhado do processamento e erros

A primeira linha do log sempre mostra o caminho completo do arquivo gerado.

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**.
