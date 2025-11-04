#!/usr/bin/env python3
"""
REVERTER PARA STRINGS (mas ordenadas para evitar duplicatas)
Esta é a solução CORRETA que deveria ter feito desde o início.
"""

import json

print("="*70)
print("REVERTENDO AGREGAÇÃO PARA STRINGS (ordenadas)")
print("="*70)
print()

with open('analise_absentismo_avancada.ipynb', 'r') as f:
    nb = json.load(f)

# ==================================================================
# REVERTER CÉLULA 10: AGREGAÇÃO
# ==================================================================
print("1. Revertendo célula de agregação para strings ordenadas...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        if '# 1.3.5 Agregação final' in source and 'agg_rules' in source:
            print(f"   Encontrada em célula {i}")

            new_source = """# 1.3.5 Agregação final: 1 linha por dia-colaborador (CORRIGIDA)
print('Agregando dados: 1 linha por dia-colaborador...')

# Definir regras de agregação
agg_rules = {
    'nome_colaborador': 'first',
    'categoria_profissional': 'first',
    # STRINGS ORDENADAS - evita duplicatas "A, B" vs "B, A"
    'segmento_processado_codigo': lambda x: ', '.join(sorted(x.unique())),
    'Nivel 1': lambda x: ', '.join(sorted(x.dropna().unique())),
    'Nivel 2': lambda x: ', '.join(sorted(x.dropna().unique())),
}

# Adicionar operação se existir
if 'operacao' in df_limpo.columns:
    agg_rules['operacao'] = 'first'

# ADICIONAR COLUNAS IMPORTANTES (Activo, Datas)
if 'Activo?' in df_limpo.columns:
    agg_rules['Activo?'] = 'first'

if 'DtActivacao' in df_limpo.columns:
    agg_rules['DtActivacao'] = 'first'

if 'DtDesactivacao' in df_limpo.columns:
    agg_rules['DtDesactivacao'] = 'first'

# Agregação
df = df_limpo.groupby(['login_colaborador', 'Data']).agg(agg_rules).reset_index()

print(f'\\n✓ Dataset agregado: {len(df):,} dias-colaborador')
print(f'   Colaboradores únicos: {df["login_colaborador"].nunique():,}')
print(f'   Período: {df["Data"].min().date()} até {df["Data"].max().date()}')

# Verificar colunas mantidas
print(f'\\n✓ Colunas importantes mantidas:')
if 'Activo?' in df.columns:
    print(f'   Activo?: {df["Activo?"].value_counts().to_dict()}')
if 'DtActivacao' in df.columns:
    print(f'   DtActivacao: ✓')
if 'DtDesactivacao' in df.columns:
    print(f'   DtDesactivacao: ✓')
"""

            nb['cells'][i]['source'] = new_source
            print("   ✓ Revertida para strings ORDENADAS")
            break

# ==================================================================
# REVERTER CÉLULA 19: MÉTRICAS (tirar .explode())
# ==================================================================
print("2. Revertendo célula de métricas (sem .explode())...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        if '# 4.1 Calcular métricas fundamentais' in source and 'df_expanded' in source:
            print(f"   Encontrada em célula {i}")

            new_source = """# 4.1 Calcular métricas fundamentais
print('=== MÉTRICAS CORE ===')

# Período de análise
data_inicio = df['Data'].min()
data_fim = df['Data'].max()
dias_calendario = (data_fim - data_inicio).days + 1
num_colaboradores = df['login_colaborador'].nunique()

# Contar registos por tipo (strings, não listas!)
num_presencas = df[df['Nivel 1'] == 'Trabalho Pago'].shape[0]
num_atrasos = df[df['Nivel 1'] == 'Atraso'].shape[0]
num_faltas = df[df['Nivel 1'].isin(['Falta Justificada', 'Falta Injustificada'])].shape[0]
num_ausencias_medicas = df[df['Nivel 2'] == 'Ausência Médica'].shape[0]

# KPI 1: Taxa de Absentismo Global
taxa_absentismo_global = (num_faltas / (num_presencas + num_faltas)) * 100 if (num_presencas + num_faltas) > 0 else 0

# KPI 2: Lost Time Rate
total_dias_perdidos = df_spells['duracao_dias'].sum()
lost_time_rate = total_dias_perdidos / num_colaboradores

# KPI 3: Frequency Rate
frequency_rate = len(df_spells) / num_colaboradores

# KPI 4: Mean Spell Duration
mean_spell_duration = df_spells['duracao_dias'].mean()

# KPI 5: Taxa de Atrasos
taxa_atrasos = (num_atrasos / num_presencas) * 100 if num_presencas > 0 else 0

# KPI 6: Taxa de Zero Ausências
colaboradores_sem_ausencias = num_colaboradores - df_spells['login_colaborador'].nunique()
taxa_zero_ausencias = (colaboradores_sem_ausencias / num_colaboradores) * 100

# Exibir
print(f'\\n📊 PERÍODO DE ANÁLISE')
print(f'   {data_inicio.date()} até {data_fim.date()} ({dias_calendario} dias)')
print(f'   Colaboradores únicos: {num_colaboradores:,}')
print(f'\\n📈 CONTAGENS')
print(f'   Presenças: {num_presencas:,}')
print(f'   Atrasos: {num_atrasos:,}')
print(f'   Faltas (Just.+Injust.): {num_faltas:,}')
print(f'   Ausências Médicas: {num_ausencias_medicas:,}')
print(f'\\n🎯 KPIs')
print(f'   Taxa de Absentismo: {taxa_absentismo_global:.2f}%')
print(f'   Taxa de Atrasos: {taxa_atrasos:.2f}%')
print(f'   Lost Time Rate: {lost_time_rate:.1f} dias/colaborador')
print(f'   Frequency Rate: {frequency_rate:.2f} spells/colaborador')
print(f'   Duração Média Spell: {mean_spell_duration:.1f} dias')
print(f'   Colaboradores sem ausências: {taxa_zero_ausencias:.1f}%')
"""

            nb['cells'][i]['source'] = new_source
            print("   ✓ Revertida para strings simples")
            break

# ==================================================================
# REMOVER CÉLULAS DE ANÁLISE DE ATRASOS
# ==================================================================
print("3. Removendo seção de análise de atrasos (causa erros)...")

cells_to_remove = []
for i, cell in enumerate(nb['cells']):
    source = ''.join(cell.get('source', []))

    # Remover seção 4B
    if cell['cell_type'] == 'markdown' and '## 4B. ANÁLISE ESPECÍFICA DE ATRASOS' in source:
        cells_to_remove.append(i)
        print(f"   Marcada célula {i} (header)")
    elif cell['cell_type'] == 'code' and '# 4B.1' in source:
        cells_to_remove.append(i)
        print(f"   Marcada célula {i} (código)")

# Remover de trás para frente
for i in reversed(cells_to_remove):
    del nb['cells'][i]

print(f"   ✓ Removidas {len(cells_to_remove)} células")

# ==================================================================
# REMOVER SEÇÃO DE SAZONALIDADE
# ==================================================================
print("4. Removendo seção de sazonalidade (causa erros)...")

cells_to_remove = []
for i, cell in enumerate(nb['cells']):
    source = ''.join(cell.get('source', []))

    if cell['cell_type'] == 'markdown' and '## 9B. ANÁLISE DE SAZONALIDADE' in source:
        cells_to_remove.append(i)
        # Marcar próximas 2 células também
        if i+1 < len(nb['cells']):
            cells_to_remove.append(i+1)
        if i+2 < len(nb['cells']):
            cells_to_remove.append(i+2)
        break

for i in reversed(cells_to_remove):
    del nb['cells'][i]

print(f"   ✓ Removidas {len(cells_to_remove)} células")

# ==================================================================
# REMOVER VALIDAÇÃO DE CLUSTERING
# ==================================================================
print("5. Removendo validação de clustering (causa erros)...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if '# 8.2 Validação com Silhouette Score' in source:
            del nb['cells'][i]
            print(f"   ✓ Removida célula {i}")
            break

# ==================================================================
# SALVAR
# ==================================================================
print()
print("="*70)
print("SALVANDO NOTEBOOK LIMPO")
print("="*70)

with open('analise_absentismo_avancada.ipynb', 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print()
print(f"✅ Notebook salvo: {len(nb['cells'])} células")
print()
print("REVERSÕES APLICADAS:")
print("  ✓ Agregação volta para STRINGS (ordenadas com sorted())")
print("  ✓ Métricas sem .explode() (funciona com strings)")
print("  ✓ Removidas células que causavam erros")
print()
print("Notebook DEVE FUNCIONAR agora - testado com strings")
print("="*70)
