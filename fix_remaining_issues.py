#!/usr/bin/env python3
"""
Script para corrigir os problemas que o primeiro script não conseguiu encontrar.
"""

import json

print("=== CORRIGINDO PROBLEMAS RESTANTES ===\n")

# Carregar notebook
with open('analise_absentismo_avancada.ipynb', 'r') as f:
    nb = json.load(f)

print(f"Notebook atual: {len(nb['cells'])} células\n")

# ============================================================================
# PROBLEMA 1: Adicionar distribuição de incompatibilidades
# ============================================================================
print("PROBLEMA 1: Adicionando distribuição de incompatibilidades...")

# Procurar célula que exporta incompatibilidades
found = False
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if "df_incompativeis.to_excel('incompatibilidades_encontradas_v2.xlsx'" in source:
            print(f"  Encontrada célula de export em {i}")

            # Adicionar nova célula DEPOIS desta
            new_cell = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """# 1.3.4 Distribuição por par incompatível
if len(df_incompativeis) > 0:
    print('\\nDistribuição por par incompatível:')

    # Criar string do par COMPLETO (ordenado para evitar duplicatas)
    def create_pair_string(nivel1_list):
        # Ordenar para "A + B" = "B + A"
        if isinstance(nivel1_list, list):
            sorted_list = sorted(nivel1_list)
        else:
            sorted_list = sorted(str(nivel1_list).split(', '))
        return ' + '.join(sorted_list)

    df_incompativeis['par_completo'] = df_incompativeis['Nivel 1'].apply(create_pair_string)

    df_incompat_dist = df_incompativeis['par_completo'].value_counts().reset_index()
    df_incompat_dist.columns = ['Par Incompatível', 'Casos']

    print(f'\\nTop 10 pares incompatíveis:')
    for idx, row in df_incompat_dist.head(10).iterrows():
        print(f"  {row['Par Incompatível']:50s}: {row['Casos']:3d} casos")
else:
    print('\\n✓ Nenhuma incompatibilidade encontrada - análise de distribuição não necessária')
"""
            }

            nb['cells'].insert(i + 1, new_cell)
            print(f"  ✓ Célula de distribuição inserida em posição {i+1}")
            found = True
            break

if not found:
    print("  ⚠️ Não encontrei a célula de export de incompatibilidades")

# ============================================================================
# PROBLEMA 7: Adicionar validação de clustering
# ============================================================================
print("\nPROBLEMA 7: Adicionando validação de clustering...")

# Procurar o método elbow
found = False
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        # Procurar por célula que faz elbow method
        if 'elbow' in source.lower() and 'kmeans' in source.lower() and 'inertia' in source.lower():
            print(f"  Encontrada célula elbow method em {i}")

            # Adicionar nova célula DEPOIS do elbow
            new_cell = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """# 8.2 Validação de Clustering com Silhouette Score
print('\\nValidando escolha de K com Silhouette Score...\\n')

from sklearn.metrics import silhouette_score

# Testar de K=2 até K=10
silhouette_scores = []
K_range = range(2, 11)

for k in K_range:
    kmeans_test = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels_test = kmeans_test.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels_test)
    silhouette_scores.append(score)
    print(f'K={k}: Silhouette Score = {score:.3f}')

# Visualizar
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=list(K_range),
    y=silhouette_scores,
    mode='lines+markers',
    marker=dict(size=10, color='blue'),
    line=dict(width=2)
))

fig.update_layout(
    title='Silhouette Score por Número de Clusters',
    xaxis_title='Número de Clusters (K)',
    yaxis_title='Silhouette Score',
    height=400,
    showlegend=False
)

fig.show()

# Escolher K com melhor score
best_k = list(K_range)[silhouette_scores.index(max(silhouette_scores))]
best_score = max(silhouette_scores)
print(f'\\n💡 Melhor K por Silhouette: {best_k} (score={best_score:.3f})')

# Encontrar score do K que foi escolhido
if K_optimal >= 2 and K_optimal <= 10:
    chosen_score = silhouette_scores[K_optimal - 2]
    print(f'   K={K_optimal} (escolhido): score={chosen_score:.3f}')
"""
            }

            nb['cells'].insert(i + 1, new_cell)
            print(f"  ✓ Célula de validação inserida em posição {i+1}")
            found = True
            break

if not found:
    print("  ⚠️ Não encontrei a célula de elbow method")

# ============================================================================
# PROBLEMA 4: Adicionar seção de análise de atrasos
# ============================================================================
print("\nPROBLEMA 4: Adicionando seção de análise de atrasos...")

# Procurar seção 5 (Bradford)
found = False
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if '## 5. BRADFORD FACTOR ANALYSIS' in source:
            print(f"  Encontrada seção Bradford em {i}")

            # Adicionar ANTES da seção Bradford
            new_cells = []

            # Header
            new_cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": "## 4B. ANÁLISE ESPECÍFICA DE ATRASOS"
            })

            # Análise
            new_cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """# 4B.1 Análise detalhada de atrasos
print('=== ANÁLISE ESPECÍFICA DE ATRASOS ===\\n')

# Criar dataframe específico para atrasos
# Usar df_ativos se existir, senão df
df_base = df_ativos if 'df_ativos' in locals() else df

df_atrasos = df_base.copy()

# Expandir Nivel 1 se for lista
if df_atrasos['Nivel 1'].dtype == 'object' and isinstance(df_atrasos['Nivel 1'].iloc[0], list):
    df_atrasos = df_atrasos.explode('Nivel 1')

df_atrasos = df_atrasos[df_atrasos['Nivel 1'] == 'Atraso'].copy()

print(f'Total de registos de atraso: {len(df_atrasos):,}')

if len(df_atrasos) > 0:
    print(f'Colaboradores com atrasos: {df_atrasos[\"login_colaborador\"].nunique():,}')

    # Análise por colaborador
    atrasos_por_colab = df_atrasos.groupby('login_colaborador').agg({
        'Data': 'count',
        'nome_colaborador': 'first'
    }).rename(columns={'Data': 'num_atrasos'}).sort_values('num_atrasos', ascending=False)

    print(f'\\n📊 Estatísticas de Atrasos:')
    print(f'   Média de atrasos por colaborador: {atrasos_por_colab[\"num_atrasos\"].mean():.1f}')
    print(f'   Mediana: {atrasos_por_colab[\"num_atrasos\"].median():.0f}')
    print(f'   Máximo: {atrasos_por_colab[\"num_atrasos\"].max():.0f}')

    # Top 10 com mais atrasos
    print(f'\\n🔝 TOP 10 COLABORADORES COM MAIS ATRASOS:\\n')
    for idx, (login, row) in enumerate(atrasos_por_colab.head(10).iterrows(), 1):
        print(f'{idx:2d}. {row[\"nome_colaborador\"][:40]:40s}: {row[\"num_atrasos\"]:3d} atrasos')

    # Distribuição
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=atrasos_por_colab['num_atrasos'],
        nbinsx=30,
        marker_color='orange',
        marker_line_color='white',
        marker_line_width=1
    ))

    fig.update_layout(
        title='Distribuição de Atrasos por Colaborador',
        xaxis_title='Número de Atrasos',
        yaxis_title='Número de Colaboradores',
        height=400
    )

    fig.show()

    # Análise temporal
    atrasos_por_data = df_atrasos.groupby('Data').size().reset_index(name='num_atrasos')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=atrasos_por_data['Data'],
        y=atrasos_por_data['num_atrasos'],
        mode='lines',
        line=dict(color='orange'),
        name='Atrasos'
    ))

    fig2.update_layout(
        title='Evolução Temporal de Atrasos',
        xaxis_title='Data',
        yaxis_title='Número de Atrasos',
        height=400,
        hovermode='x unified'
    )

    fig2.show()

    # Exportar
    atrasos_por_colab.to_excel('analise_atrasos.xlsx')
    print('\\n✓ Exportado: analise_atrasos.xlsx')

else:
    print('⚠️  Nenhum atraso encontrado no dataset')
"""
            })

            # Inserir células
            for idx, new_cell in enumerate(new_cells):
                nb['cells'].insert(i + idx, new_cell)

            print(f"  ✓ {len(new_cells)} células de análise de atrasos inseridas")
            found = True
            break

if not found:
    print("  ⚠️ Não encontrei a seção Bradford")

# ============================================================================
# VERIFICAR SE SAZONALIDADE FOI ADICIONADA
# ============================================================================
print("\nVERIFICANDO: Análise de sazonalidade...")

found_seasonality = False
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if '9B. ANÁLISE DE SAZONALIDADE' in source:
            print(f"  ✓ Seção de sazonalidade encontrada em célula {i}")
            found_seasonality = True
            break

if not found_seasonality:
    print("  ⚠️ Seção de sazonalidade não foi adicionada pelo script anterior")

# ============================================================================
# SALVAR
# ============================================================================
print("\n" + "="*70)
print("SALVANDO NOTEBOOK...")

with open('analise_absentismo_avancada.ipynb', 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"✓ Notebook salvo!")
print(f"  Total de células: {len(nb['cells'])}")

print("\n" + "="*70)
print("CORREÇÕES APLICADAS:\n")
print("✓ Adicionada distribuição de incompatibilidades (mostra pares completos)")
print("✓ Adicionada validação de clustering com Silhouette Score")
print("✓ Adicionada seção completa de análise de atrasos")
print("\n" + "="*70)
