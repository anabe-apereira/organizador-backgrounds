# Organizador de Fundos ProPresenter

Documentação completa para uso do executável de organização automática de vídeos por cor predominante.

## 📋 Sumário

- [O que faz](#o-que-faz)
- [Como funciona](#como-funciona)
- [Regras de classificação](#regras-de-classificação)
- [Instalação e uso](#instalação-e-uso)
- [Parâmetros configuráveis](#parâmetros-configuráveis)
- [Estrutura de pastas criadas](#estrutura-de-pastas-criadas)
- [Solução de problemas](#solução-de-problemas)

---

## 🎯 O que faz

O Organizador de Fundos é uma ferramenta automática que analisa vídeos e os organiza em pastas baseado na cor predominante detectada em cada arquivo. Ideal para organizar fundos de vídeos para ProPresenter ou qualquer outro sistema que necessite de classificação por cores.

### Funcionalidades principais:
- ✅ Análise automática de cores em vídeos
- ✅ Organização em pastas por cor predominante (100% em português)
- ✅ Detecção de preto-branco e vídeos coloridos
- ✅ Interface gráfica intuitiva com descrições detalhadas
- ✅ Modo linha de comando para automação
- ✅ Opção de excluir arquivos da origem após cópia
- ✅ Suporte aos formatos: MP4, MOV, AVI, M4V
- ✅ Ajuste automático de pasta de origem após processamento

---

## ⚙️ Como funciona

### 1. Análise de vídeo
O programa amostra frames do vídeo em intervalos regulares e analisa cada pixel para determinar as cores presentes.

### 2. Detecção de cores
Utiliza o espaço de cor HSV (Hue, Saturation, Value) para detectar:
- **Cores primárias**: Vermelho, Laranja, Amarelo, Verde, Azul, Violeta
- **Cores neutras**: Preto-branco (detectado por valor e saturação)
- **Múltiplas cores**: Quando várias cores são predominantes

### 3. Classificação
Baseado no percentual de cada cor detectada, o vídeo é classificado e movido para a pasta correspondente.

---

## 📊 Regras de classificação

### Limiar mínimo de cor
- **Percentual mínimo**: **20%** (padrão)
- Uma cor precisa aparecer em pelo menos 20% dos pixels do vídeo para ser considerada relevante
- Este limiar evita que pequenos elementos ou ruídos afetem a classificação
- **Ajustável**: Pode ser modificado na interface ou no código

### Lógica de classificação

#### 1. Cor única predominante
Se apenas uma cor atinge o limiar mínimo (>50%):
```
Vídeo com 45% de azul → pasta /azul/
```

#### 2. Múltiplas cores sem predominância clara
Se múltiplas cores mas nenhuma >50%:
```
Vídeo com múltiplas cores → pasta /colorido/
```

#### 3. Sem cores detectadas
Se nenhuma cor atinge o limiar mínimo:
```
Vídeo sem cores predominantes → pasta /nao-identificado/
```

---

## 🚀 Instalação e uso

### Opção 1: Usar o executável (recomendado)

1. **Baixe o executável** `OrganizadorFundos.exe` (ou similar)
2. **Execute o arquivo** com duplo clique
3. **Interface gráfica**:
   - Clique em "Procurar..." para selecionar a pasta com seus vídeos
   - Clique em "Procurar..." para selecionar onde deseja organizar os vídeos
   - Opcional: Marque "Sobrescrever arquivos existentes" se desejar substituir
   - Opcional: Marque "Excluir arquivos da pasta de origem após cópia" para remover os originais
   - Clique em "Iniciar Organização"

### Opção 2: Modo linha de comando

Para automação ou scripts:

```bash
# Básico
OrganizadorFundos.exe --src "C:\MeusVideos" --dst "C:\VideosOrganizados"

# Com sobrescrita
OrganizadorFundos.exe --src "C:\MeusVideos" --dst "C:\VideosOrganizados" --overwrite

# Excluindo arquivos da origem após cópia
OrganizadorFundos.exe --src "C:\MeusVideos" --dst "C:\VideosOrganizados" --delete-source

# Com sobrescrita e exclusão dos originais
OrganizadorFundos.exe --src "C:\MeusVideos" --dst "C:\VideosOrganizados" --overwrite --delete-source
```

### Opção 3: Executar o código Python

Se você tem Python instalado:

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar interface gráfica
python organize_backgrounds.py

# Executar linha de comando
python organize_backgrounds.py --src "C:\MeusVideos" --dst "C:\VideosOrganizados"

# Com exclusão dos originais
python organize_backgrounds.py --src "C:\MeusVideos" --dst "C:\VideosOrganizados" --delete-source
```

---

## ⚙️ Parâmetros configuráveis

Você pode ajustar estes parâmetros editando o arquivo `organize_backgrounds.py` antes de compilar:

```python
DEFAULT_CONFIG = {
    'sample_frames': 10,           # Número de frames analisados por vídeo
    'resize_width': 320,           # Redimensionamento para processamento mais rápido
    'min_color_percent': 20,       # PERCENTUAL MÍNIMO para considerar uma cor (20%)
    'supported_formats': ('.mp4', '.mov', '.avi', '.m4v'),
    'color_ranges': {
        'vermelho': [(0, 10), (170, 179)],
        'laranja': [(11, 25)],
        'amarelo': [(26, 35)],
        'verde': [(36, 85)],
        'azul': [(101, 140)],
        'violeta': [(141, 160)],
    },
    'saturation_threshold': 30,    # Saturação mínima para considerar colorido
    'value_threshold_white': 200,  # Valor mínimo para considerar branco
    'value_threshold_black': 30,   # Valor máximo para considerar preto
}
```

### Ajustes recomendados:

- **`min_color_percent`**: 
  - Aumente para ser mais restritivo (ex: 25-30%)
  - Diminua para ser mais inclusivo (ex: 15-18%)
  - Padrão: 20%

- **`sample_frames`**:
  - Aumente para análise mais precisa (ex: 15-20)
  - Diminua para processamento mais rápido (ex: 5-8)
  - Padrão: 10

---

## �️ Exclusão automática dos arquivos de origem

O programa oferece a opção de **excluir automaticamente** os arquivos da pasta de origem após a cópia bem-sucedida para a pasta de destino.

### Como funciona:
- ✅ **Segurança**: A exclusão só ocorre **APÓS** a cópia ser concluída com sucesso
- ✅ **Verificação**: Se a cópia falhar, o arquivo original NÃO será excluído
- ✅ **Log**: Todas as exclusões são registradas no log

### Quando usar:
- **Backup completo**: Quando você já tem backup dos vídeos
- **Liberação de espaço**: Para liberar espaço no disco de origem
- **Organização definitiva**: Quando não precisa mais dos arquivos na pasta original

### Como ativar:

#### Interface gráfica:
1. Marque a opção: "Excluir arquivos da pasta de origem após cópia" (texto em vermelho)
2. Prossiga normalmente com a organização

#### Linha de comando:
```bash
# Adicione o parâmetro --delete-source
OrganizadorFundos.exe --src "C:\Origem" --dst "C:\Destino" --delete-source
```

### ⚠️ Aviso importante:
- **Não há desfazer**: Uma vez excluídos, os arquivos não podem ser recuperados
- **Backup recomendado**: Faça backup antes de usar esta opção
- **Teste primeiro**: Teste com poucos arquivos antes de usar em grande escala

### Erros na exclusão:
Se ocorrer erro ao excluir um arquivo, o programa:
- Registra o erro no log: `⚠️ Erro ao excluir original: [detalhes]`
- Continua processando os demais arquivos
- Não interrompe o processo geral

---

## 📂 Estrutura de pastas criadas

O programa automaticamente cria esta estrutura na pasta de destino (100% em português):

```
PastaDestino/
├── amarelo/           # Vídeos predominantemente amarelos
├── azul/              # Vídeos predominantemente azuis
├── laranja/           # Vídeos predominantemente laranjas
├── verde/             # Vídeos predominantemente verdes
├── vermelho/          # Vídeos predominantemente vermelhos
├── violeta/           # Vídeos predominantemente violetas
├── preto-branco/      # Vídeos em preto, branco ou tons de cinza
├── colorido/          # Vídeos com múltiplas cores predominantes
└── nao-identificado/  # Vídeos sem cores predominantes claras
```

**Atualização**: O sistema foi atualizado para usar apenas nomes em português, eliminando pastas em inglês.

---

## 🔧 Solução de problemas

### Erro: "A pasta de origem não existe"
- **Causa**: Caminho digitado incorretamente ou pasta não existe
- **Solução**: Verifique o caminho e use o botão "Procurar..." para selecionar

### Erro: "Nenhum arquivo de vídeo encontrado"
- **Causa**: Pasta não contém vídeos nos formatos suportados
- **Solução**: Verifique se os arquivos são .mp4, .mov, .avi ou .m4v

### Erro: "Arquivo não encontrado" ou "Could not open video"
- **Causa**: Arquivo foi movido/deletado durante o processamento ou está corrompido
- **Solução**: 
  - Verifique se os arquivos ainda existem na pasta de origem
  - Reinicie o processo se arquivos foram movidos manualmente
  - O programa agora trata estes erros automaticamente e continua o processamento

### Erro de logging no executável
- **Causa**: Configuração de logging pode falhar em alguns ambientes
- **Solução**: O programa tem fallback automático e continua funcionando

### Erro: "Permissão negada"
- **Causa**: Sem permissão para escrever na pasta de destino
- **Solução**: Escolha outra pasta ou execute como administrador

### Vídeos indo para "nao-identificado"
- **Causa**: Nenhuma cor atingiu o limiar mínimo de 20%
- **Solução**: 
  - Reduza `min_color_percent` para 15-18%
  - Verifique se o vídeo realmente tem cores predominantes

### Muitos vídeos em "colorido"
- **Causa**: Vídeos com muitas cores variadas ou limiar muito baixo
- **Solução**: Aumente `min_color_percent` para 25-30%

### Performance lenta
- **Causa**: Vídeos grandes ou muitos arquivos
- **Solução**: 
  - Reduza `sample_frames` para 5-8
  - Reduza `resize_width` para 240

---

## 📝 Logs

O programa cria arquivos de log automaticamente:
- **Local**: `./logs/logs_YYYY-MM-DD_HH-MM-SS.txt`
- **Relativo ao executável**: Mesma pasta onde está o `OrganizadorFundos.exe`
- **Conteúdo**: Registro detalhado de todos os processamentos
- **Uso**: Útil para identificar problemas ou verificar o que aconteceu

A primeira linha do log sempre mostra: `Arquivo de log criado: [caminho completo]`

---

## 💡 Dicas de uso

1. **Teste primeiro**: Execute com alguns vídeos antes de processar toda sua coleção
2. **Backup**: Faça backup dos vídeos importantes antes de organizar
3. **Espaço em disco**: Verifique se há espaço suficiente na pasta de destino
4. **Nomes de arquivos**: Vídeos com nomes iguais receberão sufixo numérico (ex: `video(1).mp4`)
5. **Processamento em lote**: Ideal para organizar grandes coleções de uma vez
6. **Exclusão automática**: Use `--delete-source` com cuidado - faça backup antes!
7. **Verificação de logs**: Monitore o log para confirmar que as exclusões ocorreram corretamente
8. **Ajuste automático**: Após processar, o campo de origem ajusta automaticamente para a pasta pai
9. **Configuração de cores**: Use a aba "Parâmetros" para ajustar sensibilidade e outras configurações

---

## 🆘 Suporte

Se encontrar problemas:

1. Verifique o arquivo de log na pasta `logs` ao lado do executável
2. Certifique-se de que os vídeos estão nos formatos suportados (.mp4, .mov, .avi, .m4v)
3. Teste com uma pequena quantidade de vídeos primeiro
4. Verifique as permissões das pastas
5. Confirme se o percentual mínimo de cor (`min_color_percent`) está adequado

---

## 📄 Licença

Este software é fornecido para uso pessoal e profissional. Sinta-se livre para modificar e distribuir conforme necessário.

---

**Versão**: 1.0.0  
**Última atualização**: Novembro 2024  
**Formatos suportados**: MP4, MOV, AVI, M4V  
**Requisitos mínimos**: Windows 10, 4GB RAM, 1GB espaço em disco  
**Idioma das pastas**: 100% português
