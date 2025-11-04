#!/usr/bin/env python3
"""
Script SIMPLES para aplicar as correções críticas ao notebook.
Vou mostrar cada mudança de forma clara.
"""

import json

print("="*70)
print("APLICANDO CORREÇÕES AO NOTEBOOK")
print("="*70)
print()

# Carregar notebook
with open('analise_absentismo_avancada.ipynb', 'r') as f:
    nb = json.load(f)

print(f"Notebook tem {len(nb['cells'])} células\n")

# ==================================================================
# CORREÇÃO 1: AGREGAÇÃO USA LISTAS EM VEZ DE STRINGS
# ==================================================================
print("CORREÇÃO 1: Agregação - mudar de strings para listas")
print("-" * 70)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        # Encontrar célula de agregação
        if "'Nivel 1': lambda x: ', '.join(x.dropna().unique())" in source:
            print(f"✓ Encontrada célula {i}: Agregação")
            print()
            print("ANTES:")
            print("  'Nivel 1': lambda x: ', '.join(x.dropna().unique())")
            print("  Problema: Cria strings como 'Atraso, Trabalho Pago'")
            print()
            print("DEPOIS:")
            print("  'Nivel 1': lambda x: list(x.dropna().unique())")
            print("  Solução: Cria listas ['Atraso', 'Trabalho Pago']")
            print()

            # Aplicar correção
            source = source.replace(
                "'Nivel 1': lambda x: ', '.join(x.dropna().unique())",
                "'Nivel 1': lambda x: list(x.dropna().unique())"
            )
            source = source.replace(
                "'Nivel 2': lambda x: ', '.join(x.dropna().unique())",
                "'Nivel 2': lambda x: list(x.dropna().unique())"
            )
            source = source.replace(
                "'segmento_processado_codigo': lambda x: ', '.join(x.unique())",
                "'segmento_processado_codigo': lambda x: list(x.unique())"
            )

            nb['cells'][i]['source'] = source
            print("✅ Correção aplicada!\n")
            break

# ==================================================================
# CORREÇÃO 2: MÉTRICAS - EXPANDIR LISTAS ANTES DE CONTAR
# ==================================================================
print()
print("CORREÇÃO 2: Métricas - contar corretamente atrasos e tipos")
print("-" * 70)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        # Encontrar célula de métricas
        if "# 4.1 Calcular métricas fundamentais" in source and "num_atrasos = df[df['Nivel 1'] == 'Atraso'].shape[0]" in source:
            print(f"✓ Encontrada célula {i}: Métricas Core")
            print()
            print("PROBLEMA:")
            print("  Nivel 1 agora é LISTA, não string")
            print("  df['Nivel 1'] == 'Atraso' nunca vai encontrar nada!")
            print()
            print("SOLUÇÃO:")
            print("  Expandir as listas primeiro com .explode()")
            print("  Depois filtrar normalmente")
            print()

            # Nova versão da célula
            new_source = """# 4.1 Calcular métricas fundamentais
print('=== MÉTRICAS CORE ===')

# Período de análise
data_inicio = df['Data'].min()
data_fim = df['Data'].max()
dias_calendario = (data_fim - data_inicio).days + 1
num_colaboradores = df['login_colaborador'].nunique()

# ⚠️ IMPORTANTE: Expandir listas de Nivel 1 e Nivel 2 para contagem correta
df_expanded = df.copy()

# Se Nivel 1 for lista, expandir
if isinstance(df_expanded['Nivel 1'].iloc[0], list):
    df_expanded = df_expanded.explode('Nivel 1')

# Se Nivel 2 for lista, expandir
if isinstance(df_expanded['Nivel 2'].iloc[0], list):
    df_expanded = df_expanded.explode('Nivel 2')

# Contar registos por tipo (agora vai funcionar!)
num_presencas = df_expanded[df_expanded['Nivel 1'] == 'Trabalho Pago'].shape[0]
num_atrasos = df_expanded[df_expanded['Nivel 1'] == 'Atraso'].shape[0]
num_faltas = df_expanded[df_expanded['Nivel 1'].isin(['Falta Justificada', 'Falta Injustificada'])].shape[0]
num_ausencias_medicas = df_expanded[df_expanded['Nivel 2'] == 'Ausência Médica'].shape[0]

# KPI 1: Taxa de Absentismo Global
# % Absentismo = Total de Faltas / (Presenças + Total de Faltas)
taxa_absentismo_global = (num_faltas / (num_presencas + num_faltas)) * 100

# KPI 2: Lost Time Rate (dias perdidos por FTE)
total_dias_perdidos = df_spells['duracao_dias'].sum()
lost_time_rate = total_dias_perdidos / num_colaboradores

# KPI 3: Frequency Rate (spells por colaborador)
frequency_rate = len(df_spells) / num_colaboradores

# KPI 4: Mean Spell Duration
mean_spell_duration = df_spells['duracao_dias'].mean()

# KPI 5: Taxa de Atrasos
# % Atrasos = Atrasos / (Presenças + Atrasos) - faz mais sentido
taxa_atrasos = (num_atrasos / (num_presencas + num_atrasos)) * 100 if (num_presencas + num_atrasos) > 0 else 0

# KPI 6: Taxa de Zero Ausências
colaboradores_sem_ausencias = num_colaboradores - df_spells['login_colaborador'].nunique()
taxa_zero_ausencias = (colaboradores_sem_ausencias / num_colaboradores) * 100

# Exibir resultados
print(f'\\n📊 PERÍODO DE ANÁLISE')
print(f'   {data_inicio.date()} até {data_fim.date()} ({dias_calendario} dias)')
print(f'   Colaboradores únicos: {num_colaboradores:,}')
print(f'\\n📈 MÉTRICAS PRINCIPAIS')
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
            print("✅ Correção aplicada!\n")
            break

# ==================================================================
# CORREÇÃO 3: NETWORK ANALYSIS - JACCARD INDEX
# ==================================================================
print()
print("CORREÇÃO 3: Network Analysis - Jaccard Index em vez de Overlap %")
print("-" * 70)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        # Encontrar célula de network
        if "overlap_pct = cooccur / min(len(dias_i), len(dias_j))" in source:
            print(f"✓ Encontrada célula {i}: Network Analysis")
            print()
            print("PROBLEMA:")
            print("  overlap_pct = cooccur / min(dias_i, dias_j)")
            print("  Dá 100% para casos triviais")
            print()
            print("SOLUÇÃO:")
            print("  jaccard = cooccur / (dias_i ∪ dias_j)")
            print("  Métrica mais realista")
            print()

            # Substituir overlap por jaccard
            source = source.replace(
                "overlap_pct = cooccur / min(len(dias_i), len(dias_j))",
                "# Jaccard Index = interseção / união\n        union_size = len(dias_i | dias_j)\n        jaccard = cooccur / union_size if union_size > 0 else 0"
            )

            source = source.replace(
                "'overlap_pct': overlap_pct",
                "'jaccard': jaccard"
            )

            source = source.replace(
                "# Ordenar por overlap",
                "# Ordenar por Jaccard Index"
            )

            source = source.replace(
                "df_pares_sig = df_pares.sort_values('overlap_pct', ascending=False)",
                "df_pares_sig = df_pares.sort_values('jaccard', ascending=False)"
            )

            nb['cells'][i]['source'] = source
            print("✅ Correção aplicada!\n")
            break

# ==================================================================
# SALVAR
# ==================================================================
print()
print("="*70)
print("SALVANDO NOTEBOOK CORRIGIDO")
print("="*70)

with open('analise_absentismo_avancada.ipynb', 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print()
print("✅ CONCLUÍDO!")
print()
print("RESUMO DAS CORREÇÕES:")
print("  1. Agregação: strings → listas")
print("  2. Métricas: .explode() antes de contar")
print("  3. Network: Overlap % → Jaccard Index")
print()
print("Agora podes abrir o notebook e ver as mudanças!")
print("="*70)
