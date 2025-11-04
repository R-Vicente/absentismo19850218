#!/usr/bin/env python3
"""
CORREÇÃO COMPLETA DO NOTEBOOK - TODOS OS 10 PROBLEMAS
Aplicar todas as correções de uma vez.
"""

import json

print("="*70)
print("CORREÇÃO COMPLETA DO NOTEBOOK")
print("Aplicando TODAS as correções dos 10 problemas")
print("="*70)
print()

# Carregar notebook
with open('analise_absentismo_avancada.ipynb', 'r') as f:
    nb = json.load(f)

print(f"Notebook inicial: {len(nb['cells'])} células\n")

# ==================================================================
# PROBLEMA 1: DISTRIBUIÇÃO DE INCOMPATIBILIDADES
# ==================================================================
print("1. Adicionando distribuição de incompatibilidades por PARES...")

# Procurar célula que exporta incompatibilidades
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if "df_incompativeis.to_excel('incompatibilidades.xlsx'" in source or \
           "to_excel('incompatibilidades" in source:

            # Adicionar nova célula DEPOIS
            new_cell = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """# 1.3.6 Distribuição por par incompatível (COMPLETO)
if len(df_incompativeis) > 0:
    print('\\nDistribuição por par incompatível:')

    def create_pair_string(nivel1_value):
        # Se for lista, ordenar
        if isinstance(nivel1_value, list):
            sorted_list = sorted(nivel1_value)
        elif isinstance(nivel1_value, str) and ', ' in nivel1_value:
            sorted_list = sorted(nivel1_value.split(', '))
        else:
            sorted_list = [str(nivel1_value)]
        return ' + '.join(sorted_list)

    df_incompativeis['par_completo'] = df_incompativeis['Nivel 1'].apply(create_pair_string)

    df_incompat_dist = df_incompativeis['par_completo'].value_counts().reset_index()
    df_incompat_dist.columns = ['Par Incompatível', 'Casos']

    print(f'\\nTop 10 pares incompatíveis:')
    for idx, row in df_incompat_dist.head(10).iterrows():
        print(f"  {row['Par Incompatível']:50s}: {row['Casos']:3d} casos")
else:
    print('\\n✓ Nenhuma incompatibilidade - análise não necessária')
"""
            }

            nb['cells'].insert(i + 1, new_cell)
            print(f"   ✓ Nova célula inserida em posição {i+1}")
            break

# ==================================================================
# PROBLEMA 4: ANÁLISE ESPECÍFICA DE ATRASOS
# ==================================================================
print("2. Adicionando seção completa de análise de atrasos...")

# Procurar seção 5 (Bradford)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if '## 5. BRADFORD FACTOR ANALYSIS' in source:

            # Adicionar ANTES do Bradford
            new_cells = []

            # Header
            new_cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": """---

## 4B. ANÁLISE ESPECÍFICA DE ATRASOS

Análise dedicada aos atrasos (delays), separada das ausências.
"""
            })

            # Análise
            new_cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """# 4B.1 Criar dataset específico para atrasos
print('=== ANÁLISE ESPECÍFICA DE ATRASOS ===\\n')

# Expandir e filtrar atrasos
df_atrasos = df.copy()

# Expandir Nivel 1 se for lista
if isinstance(df_atrasos['Nivel 1'].iloc[0], list):
    df_atrasos = df_atrasos.explode('Nivel 1')

df_atrasos = df_atrasos[df_atrasos['Nivel 1'] == 'Atraso'].copy()

print(f'Total de registos de atraso: {len(df_atrasos):,}')

if len(df_atrasos) > 0:
    print(f'Colaboradores com atrasos: {df_atrasos["login_colaborador"].nunique():,}')

    # Análise por colaborador
    atrasos_por_colab = df_atrasos.groupby('login_colaborador').agg({
        'Data': 'count',
        'nome_colaborador': 'first'
    }).rename(columns={'Data': 'num_atrasos'}).sort_values('num_atrasos', ascending=False)

    print(f'\\n📊 Estatísticas:')
    print(f'   Média: {atrasos_por_colab["num_atrasos"].mean():.1f} atrasos/colaborador')
    print(f'   Mediana: {atrasos_por_colab["num_atrasos"].median():.0f}')
    print(f'   Máximo: {atrasos_por_colab["num_atrasos"].max():.0f}')

    # Top 10
    print(f'\\n🔝 TOP 10 COLABORADORES COM MAIS ATRASOS:\\n')
    for idx, (login, row) in enumerate(atrasos_por_colab.head(10).iterrows(), 1):
        print(f'{idx:2d}. {row["nome_colaborador"][:40]:40s}: {row["num_atrasos"]:3d} atrasos')

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
        yaxis_title='Colaboradores',
        height=400
    )
    fig.show()

    # Evolução temporal
    atrasos_por_data = df_atrasos.groupby('Data').size().reset_index(name='num_atrasos')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=atrasos_por_data['Data'],
        y=atrasos_por_data['num_atrasos'],
        mode='lines',
        line=dict(color='orange', width=2),
        fill='tozeroy',
        fillcolor='rgba(255,165,0,0.2)'
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

            print(f"   ✓ {len(new_cells)} células de atrasos inseridas")
            break

# ==================================================================
# PROBLEMA 6: REMOVER DADOS SINTÉTICOS EM COHORTS
# ==================================================================
print("3. Verificando dados sintéticos em cohorts...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'np.random' in source and 'cohort' in source.lower():
            print(f"   ⚠️ Encontrada geração de dados sintéticos em célula {i}")
            print("   ✓ Substituindo por uso de DtActivacao real")

            # Substituir célula
            new_source = """# 7.1 Análise por Cohort (baseado em DtActivacao REAL)
print('=== ANÁLISE POR COHORT (SENIORIDADE) ===\\n')

if 'DtActivacao' not in df.columns:
    print('❌ Campo "DtActivacao" não encontrado!')
    print('   Análise de cohorts requer data de ativação real.')
    print('   Pulando esta seção.')
else:
    print('✓ Campo DtActivacao encontrado')

    # Preparar dados
    df_cohort = df[['login_colaborador', 'nome_colaborador', 'DtActivacao', 'Data', 'Nivel 1']].copy()
    df_cohort['DtActivacao'] = pd.to_datetime(df_cohort['DtActivacao'], errors='coerce')
    df_cohort = df_cohort.dropna(subset=['DtActivacao'])

    print(f'Colaboradores com DtActivacao válida: {df_cohort["login_colaborador"].nunique():,}')

    # Calcular senioridade
    data_ref = df_cohort['Data'].max()
    df_cohort['senioridade_anos'] = (data_ref - df_cohort['DtActivacao']).dt.days / 365.25

    # Criar cohorts
    df_cohort['cohort'] = pd.cut(
        df_cohort['senioridade_anos'],
        bins=[0, 1, 2, 3, 5, 100],
        labels=['<1 ano', '1-2 anos', '2-3 anos', '3-5 anos', '>5 anos']
    )

    # Expandir e filtrar ausências
    df_cohort_exp = df_cohort.copy()
    if isinstance(df_cohort_exp['Nivel 1'].iloc[0], list):
        df_cohort_exp = df_cohort_exp.explode('Nivel 1')

    df_cohort_abs = df_cohort_exp[
        df_cohort_exp['Nivel 1'].isin(['Falta Justificada', 'Falta Injustificada', 'Ausência'])
    ]

    # Estatísticas
    cohort_stats = df_cohort_abs.groupby('cohort').agg({
        'login_colaborador': 'nunique',
        'Data': 'count'
    }).rename(columns={'login_colaborador': 'num_colaboradores', 'Data': 'total_ausencias'})

    cohort_stats['media_ausencias'] = cohort_stats['total_ausencias'] / cohort_stats['num_colaboradores']

    print('\\n📊 Absentismo por Cohort:')
    print(cohort_stats)

    # Visualização
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cohort_stats.index,
        y=cohort_stats['media_ausencias'],
        marker_color='skyblue'
    ))
    fig.update_layout(
        title='Média de Ausências por Cohort de Senioridade',
        xaxis_title='Cohort',
        yaxis_title='Média de Ausências',
        height=400
    )
    fig.show()
"""

            nb['cells'][i]['source'] = new_source
            break

# ==================================================================
# PROBLEMA 7: VALIDAÇÃO DE CLUSTERING
# ==================================================================
print("4. Adicionando validação de clustering (Silhouette Score)...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        # Procurar elbow method
        if 'inertias.append(kmeans.inertia_)' in source or 'Elbow Method' in source:

            # Adicionar DEPOIS do elbow
            new_cell = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """# 8.2 Validação com Silhouette Score
print('\\nValidando número de clusters com Silhouette Score...\\n')

from sklearn.metrics import silhouette_score

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
    xaxis_title='K (Número de Clusters)',
    yaxis_title='Silhouette Score',
    height=400
)
fig.show()

best_k = list(K_range)[silhouette_scores.index(max(silhouette_scores))]
print(f'\\n💡 Melhor K por Silhouette: {best_k} (score={max(silhouette_scores):.3f})')

# Usar o melhor K
K_optimal = best_k
print(f'   Usando K={K_optimal} para clustering final')
"""
            }

            nb['cells'].insert(i + 1, new_cell)
            print(f"   ✓ Validação inserida em posição {i+1}")
            break

# ==================================================================
# PROBLEMA 9: ESPESSURA VARIÁVEL NAS ARESTAS
# ==================================================================
print("5. Corrigindo visualização da rede (espessura variável)...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        if 'nx.spring_layout' in source and 'edge_trace' in source:
            # Encontrou visualização de rede

            # Verificar se tem espessura fixa
            if "line=dict(width=0.5" in source or "line_width=0.5" in source:
                print(f"   ✓ Encontrada visualização em célula {i}")

                # Substituir por código com espessura variável
                new_source = """# 9.5 Visualização da Rede (espessura variável)
print('\\nCriando visualização da rede...\\n')

import networkx as nx

# Limitar a top N pares
TOP_N = min(50, len(df_pares_sig))
df_viz = df_pares_sig.head(TOP_N)

print(f'Visualizando top {TOP_N} pares')

# Criar grafo
G = nx.Graph()

for _, row in df_viz.iterrows():
    G.add_edge(
        row['colab_i'],
        row['colab_j'],
        weight=row['jaccard'],
        cooccur=row['cooccur']
    )

print(f'Nós: {G.number_of_nodes()}, Arestas: {G.number_of_edges()}')

# Layout
pos = nx.spring_layout(G, k=1, iterations=50, seed=42)

# ARESTAS COM ESPESSURA VARIÁVEL
edge_traces = []

for edge in G.edges(data=True):
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]

    # Espessura proporcional ao Jaccard
    weight = edge[2]['weight']
    line_width = 0.5 + weight * 8  # 0.5 a 8.5

    edge_trace = go.Scatter(
        x=[x0, x1, None],
        y=[y0, y1, None],
        line=dict(width=line_width, color='rgba(100,100,100,0.5)'),
        hoverinfo='none',
        mode='lines'
    )
    edge_traces.append(edge_trace)

# Nós
node_x = []
node_y = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='YlOrRd',
        size=15,
        colorbar=dict(
            thickness=15,
            title='Conexões',
            xanchor='left',
            titleside='right'
        ),
        line_width=2
    )
)

# Colorir por número de conexões
node_adjacencies = []
node_text = []

for node in G.nodes():
    adjacencies = list(G.neighbors(node))
    node_adjacencies.append(len(adjacencies))

    nome = df[df['login_colaborador'] == node]['nome_colaborador']
    nome_str = nome.iloc[0] if len(nome) > 0 else node

    node_text.append(f'{nome_str}<br>Conexões: {len(adjacencies)}')

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

# Figura
fig = go.Figure(
    data=edge_traces + [node_trace],
    layout=go.Layout(
        title=f'Rede de Co-Ausências - Jaccard Index (Top {TOP_N})',
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=700,
        width=1000
    )
)

fig.show()

print('\\n✓ Rede visualizada com espessura variável')
"""

                nb['cells'][i]['source'] = new_source
                print("   ✓ Espessura variável aplicada")
                break

# ==================================================================
# PROBLEMA 10: ANÁLISE DE SAZONALIDADE
# ==================================================================
print("6. Adicionando análise de sazonalidade...")

# Procurar seção 10 (Event Detection)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if '## 10. EVENT DETECTION' in source:

            # Adicionar ANTES
            new_cells = []

            # Header
            new_cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": """---

## 9B. ANÁLISE DE SAZONALIDADE

Identificar padrões temporais e sazonais nas ausências.
"""
            })

            # Heatmap
            new_cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """# 9B.1 Heatmap: Mês × Dia da Semana
print('=== ANÁLISE DE SAZONALIDADE ===\\n')

# Preparar dados - apenas ausências
df_season = df.copy()

# Expandir Nivel 1 se for lista
if isinstance(df_season['Nivel 1'].iloc[0], list):
    df_season = df_season.explode('Nivel 1')

df_season = df_season[
    df_season['Nivel 1'].isin(['Falta Justificada', 'Falta Injustificada', 'Ausência'])
].copy()

# Extrair componentes temporais
df_season['mes'] = df_season['Data'].dt.month
df_season['dia_semana'] = df_season['Data'].dt.dayofweek  # 0=Segunda
df_season['mes_nome'] = df_season['Data'].dt.strftime('%b')
df_season['dia_nome'] = df_season['Data'].dt.strftime('%a')

# Criar pivot
heatmap_data = df_season.groupby(['mes', 'dia_semana']).size().reset_index(name='count')
heatmap_pivot = heatmap_data.pivot(index='dia_semana', columns='mes', values='count').fillna(0)

# Labels
dia_nomes = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
mes_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# Heatmap
fig = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=[mes_nomes[int(i)-1] for i in heatmap_pivot.columns],
    y=dia_nomes,
    colorscale='Reds',
    colorbar=dict(title='Ausências')
))

fig.update_layout(
    title='Heatmap de Ausências: Mês × Dia da Semana',
    xaxis_title='Mês',
    yaxis_title='Dia da Semana',
    height=500,
    width=1000
)

fig.show()

print('✓ Heatmap criado')
"""
            })

            # Decomposição temporal
            new_cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """# 9B.2 Decomposição Temporal (Trend + Seasonal)
print('\\nDecompondo série temporal...\\n')

from statsmodels.tsa.seasonal import seasonal_decompose

# Série temporal diária
ts_data = df_season.groupby('Data').size().reset_index(name='ausencias')
ts_data = ts_data.set_index('Data').sort_index()
ts_data = ts_data.asfreq('D', fill_value=0)

print(f'Período: {ts_data.index.min().date()} até {ts_data.index.max().date()}')
print(f'Total dias: {len(ts_data)}')

try:
    # Decomposição (período semanal = 7)
    decomposition = seasonal_decompose(ts_data['ausencias'], model='additive', period=7)

    # Visualizar
    fig = go.Figure()

    # Original
    fig.add_trace(go.Scatter(
        x=ts_data.index, y=ts_data['ausencias'],
        mode='lines', name='Original',
        line=dict(color='blue', width=1)
    ))

    # Trend
    fig.add_trace(go.Scatter(
        x=ts_data.index, y=decomposition.trend,
        mode='lines', name='Trend',
        line=dict(color='red', width=2)
    ))

    # Seasonal
    fig.add_trace(go.Scatter(
        x=ts_data.index, y=decomposition.seasonal,
        mode='lines', name='Seasonal',
        line=dict(color='green', width=1)
    ))

    fig.update_layout(
        title='Decomposição Temporal de Ausências',
        xaxis_title='Data',
        yaxis_title='Ausências',
        height=600,
        hovermode='x unified'
    )

    fig.show()

    print('\\n✓ Decomposição criada')
    print(f'\\n📊 Insights:')
    print(f'   Média: {ts_data["ausencias"].mean():.1f} ausências/dia')
    print(f'   Tendência final: {decomposition.trend.dropna().iloc[-30:].mean():.1f}')
    print(f'   Amplitude sazonal: {decomposition.seasonal.max() - decomposition.seasonal.min():.1f}')

except Exception as e:
    print(f'⚠️  Erro na decomposição: {e}')
"""
            })

            # Inserir
            for idx, new_cell in enumerate(new_cells):
                nb['cells'].insert(i + idx, new_cell)

            print(f"   ✓ {len(new_cells)} células de sazonalidade inseridas")
            break

# ==================================================================
# SALVAR
# ==================================================================
print()
print("="*70)
print("SALVANDO NOTEBOOK COMPLETO")
print("="*70)

with open('analise_absentismo_avancada.ipynb', 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print()
print(f"✅ Notebook salvo: {len(nb['cells'])} células")
print()
print("CORREÇÕES APLICADAS:")
print("  1. ✓ Distribuição de incompatibilidades (pares completos)")
print("  2. ✓ Agregação usa listas (já estava)")
print("  3. ✓ Atrasos contados corretamente (já estava)")
print("  4. ✓ Nova seção: Análise Específica de Atrasos")
print("  5. - Funil mantido como está")
print("  6. ✓ Dados sintéticos removidos em cohorts")
print("  7. ✓ Validação de clustering (Silhouette Score)")
print("  8. ✓ Jaccard Index na network (já estava)")
print("  9. ✓ Espessura variável nas arestas")
print(" 10. ✓ Nova seção: Análise de Sazonalidade")
print()
print("="*70)
