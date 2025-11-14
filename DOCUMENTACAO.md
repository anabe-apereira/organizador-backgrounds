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
- ✅ Organização em pastas por cor predominante
- ✅ Suporte a combinações de duas cores
- ✅ Interface gráfica intuitiva
- ✅ Modo linha de comando para automação
- ✅ Opção de excluir arquivos da origem após cópia
- ✅ Suporte aos formatos: MP4, MOV, AVI, M4V

---

## ⚙️ Como funciona

### 1. Análise de vídeo
O programa amostra frames do vídeo em intervalos regulares e analisa cada pixel para determinar as cores presentes.

### 2. Detecção de cores
Utiliza o espaço de cor HSV (Hue, Saturation, Value) para detectar:
- **Cores primárias**: Vermelho, Laranja, Amarelo, Verde, Ciano, Azul, Violeta, Rosa
- **Cores neutras**: Branco, Preto
- **Combinações**: Quando duas cores são predominantes

### 3. Classificação
Baseado no percentual de cada cor detectada, o vídeo é classificado e movido para a pasta correspondente.

---

## 📊 Regras de classificação

### Limiar mínimo de cor
- **Percentual mínimo**: **8%**
- Uma cor precisa aparecer em pelo menos 8% dos pixels do vídeo para ser considerada relevante
- Este limiar evita que pequenos elementos ou ruídos afetem a classificação

### Lógica de classificação

#### 1. Cor única
Se apenas uma cor atinge o limiar mínimo:
```
Vídeo com 45% de azul → pasta /azul/
```

#### 2. Combinação de duas cores
Se exatamente duas cores atingem o limiar:
```
Vídeo com 25% rosa + 20% laranja → pasta /laranja-rosa/
```
**Importante**: As combinações seguem ordem alfabética para evitar duplicação:
- `laranja-rosa` ✅
- `rosa-laranja` ❌ (nunca será criado)

#### 3. Três ou mais cores
Se três ou mais cores atingem o limiar:
```
Vídeo com múltiplas cores → pasta /colorido/
```

#### 4. Sem cores detectadas
Se nenhuma cor atinge o limiar mínimo:
```
Vídeo sem cores predominantes → pasta /nao_identificado/
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
    'min_color_percent': 8,        # PERCENTUAL MÍNIMO para considerar uma cor (8%)
    'supported_formats': ('.mp4', '.mov', '.avi', '.m4v'),
    'saturation_threshold': 30,    # Saturação mínima para considerar colorido
    'value_threshold_white': 200,  # Valor mínimo para considerar branco
    'value_threshold_black': 30,   # Valor máximo para considerar preto
}
```

### Ajustes recomendados:

- **`min_color_percent`**: 
  - Aumente para ser mais restritivo (ex: 10-12%)
  - Diminua para ser mais inclusivo (ex: 5-6%)

- **`sample_frames`**:
  - Aumente para análise mais precisa (ex: 15-20)
  - Diminua para processamento mais rápido (ex: 5-8)

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

## � Estrutura de pastas criadas

O programa automaticamente cria esta estrutura na pasta de destino:

```
PastaDestino/
├── amarelo/
├── azul/
├── branco/
├── ciano/
├── laranja/
├── preto/
├── rosa/
├── verde/
├── vermelho/
├── violeta/
├── colorido/          # Vídeos com 3+ cores
├── nao_identificado/  # Vídeos sem cores predominantes
└── combinações/       # Pastas de duas cores
    ├── amarelo-azul/
    ├── amarelo-ciano/
    ├── amarelo-laranja/
    ├── amarelo-rosa/
    ├── amarelo-verde/
    ├── amarelo-vermelho/
    ├── amarelo-violeta/
    ├── azul-ciano/
    ├── azul-laranja/
    ├── azul-rosa/
    ├── azul-verde/
    ├── azul-vermelho/
    ├── azul-violeta/
    ├── ciano-laranja/
    ├── ciano-rosa/
    ├── ciano-verde/
    ├── ciano-vermelho/
    ├── ciano-violeta/
    ├── laranja-rosa/
    ├── laranja-verde/
    ├── laranja-vermelho/
    ├── laranja-violeta/
    ├── rosa-verde/
    ├── rosa-vermelho/
    ├── rosa-violeta/
    ├── verde-vermelho/
    ├── verde-violeta/
    └── vermelho-violeta/
```

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

### Vídeos indo para "nao_identificado"
- **Causa**: Nenhuma cor atingiu o limiar mínimo de 8%
- **Solução**: 
  - Reduza `min_color_percent` para 5-6%
  - Verifique se o vídeo realmente tem cores predominantes

### Muitos vídeos em "colorido"
- **Causa**: Vídeos com muitas cores variadas
- **Solução**: Aumente `min_color_percent` para 10-12%

### Performance lenta
- **Causa**: Vídeos grandes ou muitos arquivos
- **Solução**: 
  - Reduza `sample_frames` para 5-8
  - Reduza `resize_width` para 240

---

## 📝 Logs

O programa cria um arquivo de log em seu diretório pessoal:
- **Local**: `C:\Users\[SEU_USUARIO]\organize_backgrounds.log`
- **Conteúdo**: Registro detalhado de todos os processamentos
- **Uso**: Útil para identificar problemas ou verificar o que aconteceu

---

## 💡 Dicas de uso

1. **Teste primeiro**: Execute com alguns vídeos antes de processar toda sua coleção
2. **Backup**: Faça backup dos vídeos importantes antes de organizar
3. **Espaço em disco**: Verifique se há espaço suficiente na pasta de destino
4. **Nomes de arquivos**: Vídeos com nomes iguais receberão sufixo numérico (ex: `video(1).mp4`)
5. **Processamento em lote**: Ideal para organizar grandes coleções de uma vez
6. **Exclusão automática**: Use `--delete-source` com cuidado - faça backup antes!
7. **Verificação de logs**: Monitore o log para confirmar que as exclusões ocorreram corretamente

---

## 🆘 Suporte

Se encontrar problemas:

1. Verifique o arquivo de log em `C:\Users\[SEU_USUARIO]\organize_backgrounds.log`
2. Certifique-se de que os vídeos estão nos formatos suportados
3. Teste com uma pequena quantidade de vídeos primeiro
4. Verifique as permissões das pastas

---

## 📄 Licença

Este software é fornecido para uso pessoal e profissional. Sinta-se livre para modificar e distribuir conforme necessário.

---

**Versão**: 1.0  
**Última atualização**: 2024  
**Formatos suportados**: MP4, MOV, AVI, M4V  
**Requisitos mínimos**: Windows 10, 4GB RAM, 1GB espaço em disco
