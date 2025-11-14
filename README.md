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

Para criar um executável .exe, use o PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=NONE organize_backgrounds.py
```

O arquivo executável estará em `dist/organize_backgrounds.exe`.

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
