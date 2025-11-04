# ANÁLISE CRÍTICA: Problemas Identificados no Notebook

**Data:** 2025-11-04
**Status:** ❌ **MÚLTIPLOS PROBLEMAS CRÍTICOS CONFIRMADOS**

---

## 🚨 RESUMO EXECUTIVO

Dos **10 pontos levantados**, **TODOS foram confirmados** como problemas reais.

**Gravidade:**
- 🔴 **Crítico** (invalida resultados): 5 problemas
- 🟠 **Alto** (distorce interpretação): 3 problemas
- 🟡 **Médio** (afeta usabilidade): 2 problemas

**Veredicto:** Notebook **NÃO está pronto** para apresentação sem correções.

---

## 🔴 PROBLEMAS CRÍTICOS (invalidam resultados)

### **1. AGREGAÇÃO INCORRETA** 🔴

**Problema:**
```python
# Código atual:
'Nivel 1': lambda x: ', '.join(x.dropna().unique())

# Resultado:
'Ausência, Trabalho Pago': 235,321 registos
'Trabalho Pago, Ausência': 220,786 registos
```

**Impacto:**
- São o **MESMO caso**, contados como diferentes
- 456,107 registos (~60% do dataset) duplicados nas estatísticas
- **Todas as contagens** por Nivel 1/2 estão **ERRADAS**

**Causa:**
- Concatena strings e depois faz `value_counts()` nelas
- Ordem importa: "A, B" ≠ "B, A"

**Solução correta:**
- **NÃO agregar** quando há múltiplos códigos incompatíveis
- OU escolher código **dominante** (mais horas, prioritário)
- OU manter 1 linha por código (sem agregação excessiva)

---

### **2. ATRASOS = 0** 🔴

**Problema:**
```
Atrasos: 0
Taxa de Atrasos: 0.00%
```

**Impacto:**
- Métrica fundamental **completamente errada**
- Análise de atrasos **inexistente**

**Causa:**
```python
num_atrasos = df[df['Nivel 1'] == 'Atraso'].shape[0]
num_presencas = df[df['Nivel 1'] == 'Trabalho Pago'].shape[0]
```
- Atrasos têm `Nivel 1 = 'Atraso'`
- Presenças têm `Nivel 1 = 'Trabalho Pago'`
- São categorias **separadas**!

**Solução:**
- Atrasos devem ser contados **separadamente**
- Taxa de Atrasos = Atrasos / (Atrasos + Presenças)

---

### **3. DADOS SINTÉTICOS NA ANÁLISE DE COHORTS** 🔴

**Problema:**
```
⚠️  Campo "data_ingresso" não encontrado
Criando datas sintéticas para demonstração...
```

**Impacto:**
- Toda a **análise de cohorts é FALSA**
- Baseada em datas **aleatórias inventadas**
- **INACEITÁVEL** numa análise séria

**Causa:**
- Campos `DtActivacao`, `DtDesactivacao`, `Activo?` **perdidos na agregação**
- Agregação (célula 10) só mantém 5 campos

**Solução:**
- **Corrigir agregação** para manter campos críticos
- **OU remover** secção de cohorts completamente

---

### **4. DISTRIBUIÇÃO DE INCOMPATIBILIDADES ERRADA** 🔴

**Problema:**
```
Distribuição por par incompatível:
   Presença: 56 casos
   Ausência: 44 casos
   Médica: 41 casos
```

**Impacto:**
- Output mostra **palavras isoladas**, não pares
- Deveria ser "Presença + Ausência Médica: 40 casos"
- **Impossível** interpretar quais são os pares problemáticos

**Causa:**
- Código faz `.str.split()` e conta palavras individuais
- Em vez de contar **pares completos**

**Solução:**
- Contar pares inteiros: "Categoria A + Categoria B"

---

### **5. NETWORK OVERLAPS 100% DOMINANTE** 🔴

**Problema:**
```
Top 20 pares:
  1. Carla (326 dias) + Mariana (6 dias): Overlap 100%
  2. ...todos com 100%...
```

**Impacto:**
- Métrica de overlap **captura casos irrelevantes**
- "Coincidências triviais" dominam resultados
- Pares genuinamente suspeitos **não são identificados**

**Causa:**
```python
overlap = cooccur / min(dias_i, dias_j)
```
- Fórmula privilegia quem tem **poucas faltas**
- Se B falta 6 dias e todos coincidem com A → 100%
- Mas não significa "padrão coordenado"

**Solução:**
- Usar **Jaccard Index** em vez de overlap mínimo
- OU filtrar: `min(dias_i, dias_j) >= threshold` (ex: ≥10 dias)
- OU usar **taxa de overlap média**: `cooccur / avg(dias_i, dias_j)`

---

## 🟠 PROBLEMAS ALTOS (distorcem interpretação)

### **6. BRADFORD SCORES EXTREMOS** 🟠

**Problema:**
```
Máximo Bradford: 290,080
Mediana: 144
37.7% com score >900
```

**Análise:**
- Score máximo é **322x** o threshold de "Preocupação Séria"
- Para ter 290k: ~54 spells × 100 dias OU ~38 spells × 200 dias
- **Possível**, mas extremo

**Causas prováveis:**
1. Período de 18 meses → muitos spells acumulados
2. Dataset inclui SÓ quem tem ausências (viés de seleção)
3. Definição de spell pode estar fragmentando demais

**Solução:**
- Verificar se há outliers genuínos (colaboradores problemáticos)
- OU rever definição de spell
- Contextualizar: mostrar % do **total** de colaboradores

---

### **7. VISUALIZAÇÃO DA REDE SEM VARIAÇÃO** 🟠

**Problema:**
```python
line=dict(width=0.5, color='#888')
```
- Todas as arestas têm **espessura fixa**
- Não reflete intensidade da conexão

**Impacto:**
- Rede não comunica informação visualmente
- Conexões fortes vs fracas **indistinguíveis**

**Solução:**
```python
# Espessura proporcional ao overlap
for edge in G.edges(data=True):
    width = 0.5 + edge[2]['weight'] * 5
```

---

### **8. FUNIL DE AÇÃO POUCO CLARO** 🟠

**Problema:**
- Visualização existe mas não é intuitiva
- Falta contexto sobre o que representam os números

**Solução:**
- Adicionar anotações explicativas
- Mostrar % do total
- OU remover se não acrescenta valor

---

## 🟡 PROBLEMAS MÉDIOS (afetam usabilidade)

### **9. AUSÊNCIA DE ANÁLISE DE SAZONALIDADE** 🟡

**Problema:**
- Nenhuma análise explícita de padrões temporais
- Não há:
  - Decomposição sazonal
  - Comparação mês a mês
  - Padrões semanais detalhados

**Impacto:**
- Pergunta fundamental não respondida: "Há padrões sazonais?"
- Impossível saber se há meses/dias críticos

**Solução:**
- Adicionar seção 11: ANÁLISE DE SAZONALIDADE
  - Heatmap: Mês × Dia da semana
  - Decomposição: Trend + Seasonality + Residual
  - Comparação entre meses/trimestres

---

### **10. CLUSTERING SEM VALIDAÇÃO** 🟡

**Problema:**
- Usa K=4 sem justificação
- Elbow method não é conclusivo visualmente
- Falta caracterização dos clusters

**Solução:**
- Adicionar **Silhouette Score** para validar K
- Criar **persona típica** de cada cluster
- Tabela comparativa: Cluster 1 vs 2 vs 3 vs 4

---

## 📊 IMPACTO NOS RESULTADOS

### **Métricas Afetadas:**

| Métrica | Status | Confiança |
|---------|--------|-----------|
| Taxa de Absentismo | ❌ Errada | 0% (agregação errada) |
| Taxa de Atrasos | ❌ Errada | 0% (sempre 0) |
| Bradford Factor | ⚠️ Inflacionado | 30% (falta contexto) |
| Network Overlaps | ❌ Inútil | 0% (captura casos irrelevantes) |
| Clustering | ⚠️ Não validado | 50% |
| Spells | ✅ OK | 90% |

### **Seções Válidas:**
- ✅ Conceito de Spells (metodologia correta)
- ✅ Frequency Rate (se ignorar agregação)
- ✅ Mean Spell Duration

### **Seções Inválidas:**
- ❌ Distribuição por Nivel 1/2 (agregação errada)
- ❌ Taxa de Atrasos (sempre 0)
- ❌ Análise de Cohorts (dados sintéticos)
- ❌ Network Top 20 (todos 100%)

---

## 🔧 PLANO DE CORREÇÃO

### **Fase 1: CORREÇÕES CRÍTICAS** (obrigatórias)

1. **Repensar agregação** (Problema #1)
   - Decisão: agregar ou não?
   - Se agregar: como resolver múltiplos códigos?

2. **Corrigir contagem de Atrasos** (Problema #2)
   - Separar Atrasos de Presenças
   - Recalcular taxa

3. **Remover/Corrigir Cohorts** (Problema #3)
   - OU: Manter DtActivacao na agregação
   - OU: Remover seção completamente

4. **Corrigir distribuição de incompatibilidades** (Problema #4)
   - Contar pares completos

5. **Reformular Network Analysis** (Problema #5)
   - Usar Jaccard OU filtrar min >= 10 dias
   - Remover licenças longas (>14 dias)

### **Fase 2: MELHORIAS** (recomendadas)

6. Contextualizar Bradford
7. Fix visualização rede (espessura)
8. Adicionar análise sazonalidade
9. Validar clustering (silhouette)

---

## 🎯 RECOMENDAÇÃO FINAL

**Notebook precisa de REESCRITA substancial antes de apresentação.**

**Prioridades:**
1. **Definir estratégia de agregação** (decisão chave)
2. Aplicar correções críticas (1-5)
3. Validar resultados
4. Depois: melhorias (6-9)

**Tempo estimado:**
- Correções críticas: 3-4 horas
- Melhorias: 1-2 horas
- **Total: ~5-6 horas de trabalho focado**

---

**Próximo passo:** Discutir estratégia de agregação e plano de reescrita.
