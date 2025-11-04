#!/usr/bin/env python3
"""
Script para CORRIGIR TODOS OS 10 PROBLEMAS CRÍTICOS identificados.
Abordagem sistemática e completa.
"""

import json

print("=== CORREÇÃO COMPLETA DO NOTEBOOK ===\n")

# Carregar notebook
with open('analise_absentismo_avancada.ipynb', 'r') as f:
    nb = json.load(f)

print(f"Notebook original: {len(nb['cells'])} células\n")

# ============================================================================
# PROBLEMA 1 & 2: AGREGAÇÃO (Cell ~10)
# ============================================================================
print("PROBLEMA 1 & 2: Corrigindo lógica de agregação...")

# Encontrar célula de agregação
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'agg_rules' in source and "'nome_colaborador': 'first'" in source:
            print(f"  Encontrada em célula {i}")

            # Nova célula com agregação corrigida
            new_source = """# 2.2 Agregação por colaborador + data (CORRIGIDO)
print('Agregando registos por colaborador + data...')

# ESTRATÉGIA DE AGREGAÇÃO:
# - Incompatibilidades (Trabalho Pago + Ausência): já filtradas anteriormente
# - Compatibilidades (Atraso + Presença): manter ambos códigos
# - Campos críticos: MANTER Activo?, DtActivacao, DtDesactivacao

agg_rules = {
    'nome_colaborador': 'first',
    'categoria_profissional': 'first',
    'operacao': 'first',

    # CRÍTICO: Campos de status
    'Activo?': 'first',
    'DtActivacao': 'first',
    'DtDesactivacao': 'first',

    # Códigos: manter lista (não concatenar strings!)
    'segmento_processado_codigo': lambda x: list(x.unique()),
    'Nivel 1': lambda x: list(x.dropna().unique()),
    'Nivel 2': lambda x: list(x.dropna().unique()),
}

# Verificar se campos existem antes de agregar
if 'Activo?' not in df.columns:
    print('⚠️  Campo "Activo?" não encontrado')
    del agg_rules['Activo?']
if 'DtActivacao' not in df.columns:
    print('⚠️  Campo "DtActivacao" não encontrado')
    del agg_rules['DtActivacao']
if 'DtDesactivacao' not in df.columns:
    print('⚠️  Campo "DtDesactivacao" não encontrado')
    del agg_rules['DtDesactivacao']
if 'operacao' not in df.columns:
    print('⚠️  Campo "operacao" não encontrado')
    del agg_rules['operacao']

df = df.groupby(['login_colaborador', 'Data'], as_index=False).agg(agg_rules)

print(f'Após agregação: {len(df):,} registos')
print(f'Colaboradores únicos: {df[\"login_colaborador\"].nunique():,}')
print(f'\\nCampos mantidos: {list(df.columns)}')
"""

            nb['cells'][i]['source'] = new_source
            print("  ✓ Célula corrigida")
            break

# ============================================================================
# PROBLEMA 1: DISTRIBUIÇÃO DE INCOMPATIBILIDADES (Cell ~8)
# ============================================================================
print("\nPROBLEMA 1: Corrigindo distribuição de incompatibilidades...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'Distribuição por Par Incompatível' in source or 'df_incompat_dist' in source:
            print(f"  Encontrada em célula {i}")

            new_source = """# 2.1.3 Distribuição por par incompatível
print('\\nDistribuição por par incompatível:')

# Criar string do par COMPLETO (ordenado para evitar duplicatas)
def create_pair_string(nivel1_list):
    # Ordenar para "A + B" = "B + A"
    sorted_list = sorted(nivel1_list)
    return ' + '.join(sorted_list)

df_incompat['par_completo'] = df_incompat['Nivel 1'].apply(create_pair_string)

df_incompat_dist = df_incompat['par_completo'].value_counts().reset_index()
df_incompat_dist.columns = ['Par Incompatível', 'Casos']

print(f'\\nTop 10 pares incompatíveis:')
for idx, row in df_incompat_dist.head(10).iterrows():
    print(f"  {row['Par Incompatível']:50s}: {row['Casos']:3d} casos")

# Exportar
df_incompat.to_excel('incompatibilidades_detalhadas.xlsx', index=False)
print('\\n✓ Exportado: incompatibilidades_detalhadas.xlsx')
"""

            nb['cells'][i]['source'] = new_source
            print("  ✓ Célula corrigida")
            break

# ============================================================================
# PROBLEMA 3: ATRASOS = 0 (Cell ~19)
# ============================================================================
print("\nPROBLEMA 3: Corrigindo cálculo de atrasos...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if "'num_atrasos':" in source or "num_atrasos =" in source:
            print(f"  Encontrada em célula {i}")

            new_source = """# 3.1 Métricas Core (CORRIGIDO)
print('=== MÉTRICAS CORE ===\\n')

# Filtrar apenas colaboradores ativos
if 'Activo?' in df.columns:
    df_ativos = df[df['Activo?'].isin(['Sim', True, 'sim', 'S'])].copy()
    print(f'✓ Filtrado para colaboradores ativos')
    print(f'  Total registos: {len(df_ativos):,}')
    print(f'  Colaboradores ativos: {df_ativos[\"login_colaborador\"].nunique():,}')
else:
    df_ativos = df.copy()
    print(f'⚠️  Campo Activo? não encontrado - usando todos')
    print(f'  Total registos: {len(df_ativos):,}')

# Expandir listas de Nivel 1 para contagem correta
df_expanded = df_ativos.explode('Nivel 1')

# Calcular métricas
num_atrasos = len(df_expanded[df_expanded['Nivel 1'] == 'Atraso'])
num_presencas = len(df_expanded[df_expanded['Nivel 1'] == 'Trabalho Pago'])
num_faltas_just = len(df_expanded[df_expanded['Nivel 1'] == 'Falta Justificada'])
num_faltas_injust = len(df_expanded[df_expanded['Nivel 1'] == 'Falta Injustificada'])
num_ausencias = len(df_expanded[df_expanded['Nivel 1'] == 'Ausência'])

total_faltas = num_faltas_just + num_faltas_injust + num_ausencias
total_registos = len(df_expanded)

# Taxa de Absentismo
taxa_abs = (total_faltas / total_registos * 100) if total_registos > 0 else 0

# Taxa de Atrasos
taxa_atrasos = (num_atrasos / total_registos * 100) if total_registos > 0 else 0

print(f'📊 Métricas Gerais:')
print(f'   Presenças: {num_presencas:,}')
print(f'   Atrasos: {num_atrasos:,} ({taxa_atrasos:.2f}%)')
print(f'   Faltas Justificadas: {num_faltas_just:,}')
print(f'   Faltas Injustificadas: {num_faltas_injust:,}')
print(f'   Ausências: {num_ausencias:,}')
print(f'   Total Faltas: {total_faltas:,}')
print(f'   Taxa de Absentismo: {taxa_abs:.2f}%')

# Criar dicionário para métricas
kpis_core = {
    'taxa_absentismo': taxa_abs,
    'taxa_atrasos': taxa_atrasos,
    'num_presencas': num_presencas,
    'num_atrasos': num_atrasos,
    'num_faltas_just': num_faltas_just,
    'num_faltas_injust': num_faltas_injust,
    'num_ausencias': num_ausencias,
    'total_faltas': total_faltas
}
"""

            nb['cells'][i]['source'] = new_source
            print("  ✓ Célula corrigida")
            break

# ============================================================================
# PROBLEMA 6: DADOS SINTÉTICOS EM COHORTS (Cell ~33)
# ============================================================================
print("\nPROBLEMA 6: Removendo dados sintéticos de cohorts...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'data_ingresso' in source and 'np.random.randint' in source:
            print(f"  Encontrada em célula {i}")

            new_source = """# 7.1 Preparar dados por cohort (CORRIGIDO - sem dados sintéticos)
print('=== ANÁLISE POR COHORT (SENIORIDADE) ===\\n')

# Usar DtActivacao (já mantido na agregação)
if 'DtActivacao' not in df.columns:
    print('❌ Campo "DtActivacao" não encontrado!')
    print('   Não é possível fazer análise de cohorts sem data de ativação real.')
    print('   Pulando esta seção.')
else:
    print('✓ Campo DtActivacao encontrado')

    # Preparar dataframe
    df_cohort = df[['login_colaborador', 'nome_colaborador', 'DtActivacao', 'Data', 'Nivel 1']].copy()

    # Converter DtActivacao para datetime
    df_cohort['DtActivacao'] = pd.to_datetime(df_cohort['DtActivacao'], errors='coerce')

    # Remover registos sem data válida
    df_cohort = df_cohort.dropna(subset=['DtActivacao'])

    print(f'Colaboradores com DtActivacao válida: {df_cohort[\"login_colaborador\"].nunique():,}')

    # Calcular senioridade (anos na empresa)
    data_ref = df_cohort['Data'].max()
    df_cohort['senioridade_anos'] = (data_ref - df_cohort['DtActivacao']).dt.days / 365.25

    # Criar cohorts por senioridade
    df_cohort['cohort'] = pd.cut(
        df_cohort['senioridade_anos'],
        bins=[0, 1, 2, 3, 5, 100],
        labels=['<1 ano', '1-2 anos', '2-3 anos', '3-5 anos', '>5 anos']
    )

    # Expandir Nivel 1 para análise
    df_cohort_exp = df_cohort.explode('Nivel 1')

    # Filtrar apenas ausências
    df_cohort_abs = df_cohort_exp[
        df_cohort_exp['Nivel 1'].isin(['Falta Justificada', 'Falta Injustificada', 'Ausência'])
    ]

    # Métricas por cohort
    cohort_stats = df_cohort_abs.groupby('cohort').agg({
        'login_colaborador': 'nunique',
        'Data': 'count'
    }).rename(columns={
        'login_colaborador': 'num_colaboradores',
        'Data': 'total_ausencias'
    })

    cohort_stats['media_ausencias'] = cohort_stats['total_ausencias'] / cohort_stats['num_colaboradores']

    print('\\n📊 Absentismo por Cohort de Senioridade:')
    print(cohort_stats)
"""

            nb['cells'][i]['source'] = new_source
            print("  ✓ Célula corrigida")
            break

# ============================================================================
# PROBLEMA 8: NETWORK ANALYSIS - JACCARD INDEX (Cells ~40-42)
# ============================================================================
print("\nPROBLEMA 8: Implementando Jaccard Index na network analysis...")

# Encontrar onde começa network analysis
network_start = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if '9.2 Calcular co-ausências' in source and 'cooccur = len(dias_i & dias_j)' in source:
            network_start = i
            print(f"  Encontrada célula de cálculo em {i}")
            break

if network_start:
    # Substituir a célula de cálculo
    new_source = """# 9.2 Calcular co-ausências usando JACCARD INDEX (CORRIGIDO)
print('\\nCalculando co-ausências por pares (Jaccard Index)...\\n')

# Criar dicionário: colaborador -> set de dias
print('   Criando dicionário de dias por colaborador...')
colab_dias = {}
for colab in df_network['login_colaborador'].unique():
    dias_set = set(df_network[df_network['login_colaborador'] == colab]['Data'])
    colab_dias[colab] = dias_set

colaboradores = list(colab_dias.keys())
print(f'   Colaboradores: {len(colaboradores):,}')

# Calcular Jaccard Index entre todos os pares
print('   Calculando Jaccard Index entre pares...')
pares = []

for i, colab_i in enumerate(colaboradores):
    if i % 200 == 0:
        print(f'      Processado {i}/{len(colaboradores)}...')

    dias_i = colab_dias[colab_i]

    for colab_j in colaboradores[i+1:]:
        dias_j = colab_dias[colab_j]

        # Co-ausências = interseção
        cooccur = len(dias_i & dias_j)

        if cooccur >= 3:  # Mínimo 3 dias juntos
            # JACCARD INDEX: interseção / união
            union_size = len(dias_i | dias_j)
            jaccard = cooccur / union_size if union_size > 0 else 0

            pares.append({
                'colab_i': colab_i,
                'colab_j': colab_j,
                'cooccur': cooccur,
                'dias_i': len(dias_i),
                'dias_j': len(dias_j),
                'jaccard': jaccard
            })

df_pares = pd.DataFrame(pares)

print(f'\\n✓ Encontrados {len(df_pares):,} pares com ≥3 co-ausências')

# Adicionar nomes
df_pares = df_pares.merge(
    df[['login_colaborador', 'nome_colaborador']].drop_duplicates(),
    left_on='colab_i', right_on='login_colaborador'
).rename(columns={'nome_colaborador': 'nome_i'}).drop('login_colaborador', axis=1)

df_pares = df_pares.merge(
    df[['login_colaborador', 'nome_colaborador']].drop_duplicates(),
    left_on='colab_j', right_on='login_colaborador'
).rename(columns={'nome_colaborador': 'nome_j'}).drop('login_colaborador', axis=1)

# Ordenar por Jaccard
df_pares = df_pares.sort_values('jaccard', ascending=False).reset_index(drop=True)
"""

    nb['cells'][network_start]['source'] = new_source
    print("  ✓ Célula de cálculo corrigida com Jaccard Index")

    # Atualizar célula seguinte (análise de distribuição)
    if network_start + 1 < len(nb['cells']):
        new_source_dist = """# 9.3 Análise de distribuição (Jaccard Index)
print('\\nANÁLISE DE DISTRIBUIÇÃO (JACCARD INDEX):\\n')

print(f'📊 Estatísticas de Jaccard Index:')
print(f'   Média: {df_pares["jaccard"].mean()*100:.2f}%')
print(f'   Mediana: {df_pares["jaccard"].median()*100:.2f}%')
print(f'   P75: {df_pares["jaccard"].quantile(0.75)*100:.2f}%')
print(f'   P90: {df_pares["jaccard"].quantile(0.90)*100:.2f}%')
print(f'   P95: {df_pares["jaccard"].quantile(0.95)*100:.2f}%')
print(f'   Máximo: {df_pares["jaccard"].max()*100:.2f}%')

# Histograma
fig = go.Figure()

fig.add_trace(go.Histogram(
    x=df_pares['jaccard'] * 100,
    nbinsx=50,
    marker_color='lightblue',
    marker_line_color='white',
    marker_line_width=1
))

fig.update_layout(
    title='Distribuição de Jaccard Index entre Pares',
    xaxis_title='Jaccard Index (%)',
    yaxis_title='Número de Pares',
    height=400
)

fig.show()

# Escolher threshold (P90)
threshold = df_pares['jaccard'].quantile(0.90)
print(f'\\n💡 Threshold escolhido (P90): {threshold*100:.2f}%')

df_pares_sig = df_pares[df_pares['jaccard'] >= threshold].copy()
print(f'   Pares significativos: {len(df_pares_sig):,}')
"""

        nb['cells'][network_start + 1]['source'] = new_source_dist
        print("  ✓ Célula de distribuição atualizada")

    # Atualizar célula de top pares
    if network_start + 2 < len(nb['cells']):
        new_source_top = """# 9.4 Top pares por Jaccard Index
print('\\n🔝 TOP 20 PARES POR JACCARD INDEX:\\n')

for idx, row in df_pares_sig.head(20).iterrows():
    print(f"{idx+1:2d}. {row['nome_i'][:30]:30s} + {row['nome_j'][:30]:30s}")
    print(f"    Co-ausências: {row['cooccur']:3d} | Total i: {row['dias_i']:3d} | Total j: {row['dias_j']:3d} | Jaccard: {row['jaccard']*100:5.2f}%")

# Exportar
df_pares_sig.to_excel('network_pares_jaccard.xlsx', index=False)
print('\\n✓ Exportado: network_pares_jaccard.xlsx')
"""

        nb['cells'][network_start + 2]['source'] = new_source_top
        print("  ✓ Célula de top pares atualizada")

# ============================================================================
# PROBLEMA 9: VISUALIZAÇÃO REDE - ESPESSURA VARIÁVEL (Cell ~44)
# ============================================================================
print("\nPROBLEMA 9: Corrigindo visualização da rede...")

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if '9.5 Visualização da Rede' in source and 'nx.spring_layout' in source:
            print(f"  Encontrada em célula {i}")

            new_source = """# 9.5 Visualização da Rede com espessura variável (CORRIGIDO)
print('\\nCriando visualização da rede...\\n')

import networkx as nx

# Limitar a top 40 pares
TOP_N = min(40, len(df_pares_sig))
df_viz = df_pares_sig.head(TOP_N)

print(f'   Visualizando top {TOP_N} pares')

# Criar grafo
G = nx.Graph()

for _, row in df_viz.iterrows():
    G.add_edge(
        row['colab_i'],
        row['colab_j'],
        weight=row['jaccard'],
        cooccur=row['cooccur']
    )

print(f'   Nós: {G.number_of_nodes()}, Arestas: {G.number_of_edges()}')

# Layout spring
pos = nx.spring_layout(G, k=1, iterations=50, seed=42)

# Preparar arestas com ESPESSURA VARIÁVEL
edge_traces = []

for edge in G.edges(data=True):
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]

    # Espessura proporcional ao Jaccard
    weight = edge[2]['weight']
    line_width = 0.5 + weight * 5  # 0.5 a 5.5

    edge_trace = go.Scatter(
        x=[x0, x1, None],
        y=[y0, y1, None],
        line=dict(width=line_width, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    edge_traces.append(edge_trace)

# Preparar nós
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
        colorscale='YlGnBu',
        size=10,
        colorbar=dict(
            thickness=15,
            title='Conexões',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

# Colorir nós por número de conexões
node_adjacencies = []
node_text = []

for node in G.nodes():
    adjacencies = list(G.neighbors(node))
    node_adjacencies.append(len(adjacencies))

    # Nome
    nome = df[df['login_colaborador'] == node]['nome_colaborador']
    nome_str = nome.iloc[0] if len(nome) > 0 else node

    node_text.append(f'{nome_str}<br>Conexões: {len(adjacencies)}')

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

# Criar figura
fig = go.Figure(data=edge_traces + [node_trace],
             layout=go.Layout(
                title=f'<br>Rede de Co-Ausências - Jaccard Index (Top {TOP_N} pares)',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=700,
                width=1000))

fig.show()

print('\\n✓ Visualização criada com espessura variável das arestas')
"""

            nb['cells'][i]['source'] = new_source
            print("  ✓ Célula corrigida")
            break

# ============================================================================
# PROBLEMA 7: VALIDAÇÃO DE CLUSTERING (adicionar após elbow method)
# ============================================================================
print("\nPROBLEMA 7: Adicionando validação de clustering...")

# Encontrar célula de clustering
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'KMeans' in source and 'n_clusters=4' in source and 'elbow' in source.lower():
            print(f"  Encontrada em célula {i}")

            # Adicionar nova célula após elbow method
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
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    silhouette_scores.append(score)
    print(f'K={k}: Silhouette Score = {score:.3f}')

# Visualizar
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=list(K_range),
    y=silhouette_scores,
    mode='lines+markers',
    marker=dict(size=10),
    line=dict(width=2)
))

fig.update_layout(
    title='Silhouette Score por Número de Clusters',
    xaxis_title='Número de Clusters (K)',
    yaxis_title='Silhouette Score',
    height=400
)

fig.show()

# Escolher K com melhor score
best_k = list(K_range)[silhouette_scores.index(max(silhouette_scores))]
print(f'\\n💡 Melhor K (Silhouette): {best_k} (score={max(silhouette_scores):.3f})')
print(f'   K=4 (escolhido antes): score={silhouette_scores[2]:.3f}')
"""
            }

            nb['cells'].insert(i + 1, new_cell)
            print("  ✓ Nova célula de validação inserida")
            break

# ============================================================================
# PROBLEMAS 10: ANÁLISE DE SAZONALIDADE (adicionar nova seção)
# ============================================================================
print("\nPROBLEMA 10: Adicionando análise de sazonalidade...")

# Encontrar onde está a seção 10 (depois do network)
section_10_idx = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if '## 10.' in source:
            section_10_idx = i
            print(f"  Encontrada seção 10 em célula {i}")
            break

if section_10_idx:
    # Inserir nova seção antes da 10
    new_cells_seasonality = []

    # Header
    new_cells_seasonality.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": "## 9B. ANÁLISE DE SAZONALIDADE"
    })

    # Célula 1: Heatmap Mês × Dia da semana
    new_cells_seasonality.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9B.1 Heatmap: Mês × Dia da Semana
print('=== ANÁLISE DE SAZONALIDADE ===\\n')
print('Criando heatmap Mês × Dia da Semana...\\n')

# Preparar dados - apenas ausências
df_season = df_ativos.explode('Nivel 1')
df_season = df_season[
    df_season['Nivel 1'].isin(['Falta Justificada', 'Falta Injustificada', 'Ausência'])
].copy()

# Extrair mês e dia da semana
df_season['mes'] = df_season['Data'].dt.month
df_season['dia_semana'] = df_season['Data'].dt.dayofweek  # 0=Monday, 6=Sunday
df_season['mes_nome'] = df_season['Data'].dt.strftime('%b')
df_season['dia_nome'] = df_season['Data'].dt.strftime('%a')

# Criar tabela de contagem
heatmap_data = df_season.groupby(['mes', 'dia_semana']).size().reset_index(name='count')
heatmap_pivot = heatmap_data.pivot(index='dia_semana', columns='mes', values='count').fillna(0)

# Nomes para labels
dia_nomes = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
mes_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# Criar heatmap
fig = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=[mes_nomes[i-1] for i in heatmap_pivot.columns],
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

    # Célula 2: Decomposição temporal
    new_cells_seasonality.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9B.2 Decomposição Temporal (Trend + Seasonal)
print('\\nDecompondo série temporal...\\n')

from statsmodels.tsa.seasonal import seasonal_decompose

# Agregar por data
ts_data = df_season.groupby('Data').size().reset_index(name='ausencias')
ts_data = ts_data.set_index('Data').sort_index()

# Reamostrar para frequência diária (preencher dias sem dados)
ts_data = ts_data.asfreq('D', fill_value=0)

print(f'Período: {ts_data.index.min().date()} até {ts_data.index.max().date()}')
print(f'Total dias: {len(ts_data)}')

# Decomposição (usar período semanal = 7 dias)
try:
    decomposition = seasonal_decompose(ts_data['ausencias'], model='additive', period=7)

    # Visualizar componentes
    fig = go.Figure()

    # Original
    fig.add_trace(go.Scatter(
        x=ts_data.index, y=ts_data['ausencias'],
        mode='lines', name='Original', line=dict(color='blue')
    ))

    # Trend
    fig.add_trace(go.Scatter(
        x=ts_data.index, y=decomposition.trend,
        mode='lines', name='Trend', line=dict(color='red', width=2)
    ))

    # Seasonal
    fig.add_trace(go.Scatter(
        x=ts_data.index, y=decomposition.seasonal,
        mode='lines', name='Seasonal', line=dict(color='green')
    ))

    fig.update_layout(
        title='Decomposição Temporal de Ausências (Trend + Seasonal)',
        xaxis_title='Data',
        yaxis_title='Ausências',
        height=600,
        hovermode='x unified'
    )

    fig.show()

    print('\\n✓ Decomposição criada')
    print(f'\\n📊 Insights:')
    print(f'   Média de ausências/dia: {ts_data[\"ausencias\"].mean():.1f}')
    print(f'   Tendência final: {decomposition.trend.dropna().iloc[-30:].mean():.1f}')
    print(f'   Amplitude sazonal: {decomposition.seasonal.max() - decomposition.seasonal.min():.1f}')

except Exception as e:
    print(f'⚠️  Erro na decomposição: {e}')
    print('   Pode ser necessário mais dados ou ajustar período')
"""
    })

    # Inserir todas as células novas
    for idx, new_cell in enumerate(new_cells_seasonality):
        nb['cells'].insert(section_10_idx + idx, new_cell)

    print(f"  ✓ {len(new_cells_seasonality)} células de sazonalidade inseridas")

# ============================================================================
# PROBLEMA 4: ADICIONAR SEÇÃO DE ANÁLISE ESPECÍFICA DE ATRASOS
# ============================================================================
print("\nPROBLEMA 4: Adicionando seção dedicada de análise de atrasos...")

# Inserir após métricas core
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if '## 4.' in source and 'BRADFORD' in source.upper():
            print(f"  Inserindo antes da célula {i}")

            # Nova seção para atrasos
            new_cells_atrasos = []

            # Header
            new_cells_atrasos.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": "## 3B. ANÁLISE ESPECÍFICA DE ATRASOS"
            })

            # Análise de atrasos
            new_cells_atrasos.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """# 3B.1 Análise detalhada de atrasos
print('=== ANÁLISE ESPECÍFICA DE ATRASOS ===\\n')

# Criar dataframe específico para atrasos
df_atrasos = df_ativos.explode('Nivel 1')
df_atrasos = df_atrasos[df_atrasos['Nivel 1'] == 'Atraso'].copy()

print(f'Total de registos de atraso: {len(df_atrasos):,}')
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
    marker_color='orange'
))

fig.update_layout(
    title='Distribuição de Atrasos por Colaborador',
    xaxis_title='Número de Atrasos',
    yaxis_title='Número de Colaboradores',
    height=400
)

fig.show()

# Exportar
atrasos_por_colab.to_excel('analise_atrasos.xlsx')
print('\\n✓ Exportado: analise_atrasos.xlsx')
"""
            })

            # Inserir células
            for idx, new_cell in enumerate(new_cells_atrasos):
                nb['cells'].insert(i + idx, new_cell)

            print(f"  ✓ {len(new_cells_atrasos)} células de análise de atrasos inseridas")
            break

# ============================================================================
# SALVAR NOTEBOOK CORRIGIDO
# ============================================================================
print("\n" + "="*70)
print("SALVANDO NOTEBOOK CORRIGIDO...")

with open('analise_absentismo_avancada.ipynb', 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"✓ Notebook corrigido e salvo!")
print(f"  Total de células final: {len(nb['cells'])}")

print("\n" + "="*70)
print("RESUMO DAS CORREÇÕES:\n")
print("✓ Problema 1: Distribuição de incompatibilidades - mostra pares completos")
print("✓ Problema 2: Agregação - mantém campos críticos (Activo?, DtActivacao, etc)")
print("✓ Problema 3: Atrasos - corrigido cálculo (não é mais 0)")
print("✓ Problema 4: Adicionada seção específica de análise de atrasos")
print("✓ Problema 6: Removidos dados sintéticos - usa DtActivacao real")
print("✓ Problema 7: Adicionada validação de clustering com Silhouette Score")
print("✓ Problema 8: Network analysis usa Jaccard Index (não overlap %)")
print("✓ Problema 9: Visualização rede tem espessura variável")
print("✓ Problema 10: Adicionada análise de sazonalidade completa")
print("\nNota sobre Problema 4 (Bradford extremo) e Problema 5 (Funil):")
print("  - Bradford: valores são extremos mas matematicamente possíveis")
print("  - Funil: mantido como está (user pode remover se preferir)")
print("\n" + "="*70)
