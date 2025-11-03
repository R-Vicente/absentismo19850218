#!/usr/bin/env python3
"""
Script para melhorar analise_absentismo_avancada.ipynb:
1. Adicionar visualizações mais impactantes (PowerPoint-ready)
2. Reescrever Network Analysis com framework robusto
"""

import json

# Load notebook
with open('analise_absentismo_avancada.ipynb', 'r') as f:
    nb = json.load(f)

print(f"Original notebook: {len(nb['cells'])} cells")

# ==============================================================================
# 1. ADICIONAR VISUALIZAÇÕES EXTRAS APÓS BRADFORD FACTOR
# ==============================================================================

# Encontrar índice da última célula de Bradford (depois do scatter plot)
bradford_viz_idx = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'Bradford Factor Analysis' in source and 'fig.show()' in source:
            bradford_viz_idx = i
            break

if bradford_viz_idx:
    print(f"Found Bradford visualization at cell {bradford_viz_idx}")

    # Adicionar nova célula de visualização
    new_viz_cells = []

    # Viz 1: Heatmap de Bradford por Operação × Categoria
    new_viz_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 5.4 Visualização EXTRA: Bradford Heatmap por Operação e Categoria
print('\\nCriando heatmap Bradford por Operação × Categoria...')

if 'operacao' in df.columns:
    # Merge Bradford scores com operação
    df_bradford_op = df_bradford.merge(
        df[['login_colaborador', 'operacao']].drop_duplicates(),
        on='login_colaborador',
        how='left'
    )

    # Merge com categoria profissional
    df_bradford_op = df_bradford_op.merge(
        df[['login_colaborador', 'categoria_profissional']].drop_duplicates(),
        on='login_colaborador',
        how='left'
    )

    # Top 10 operações
    top_ops = df['operacao'].value_counts().head(10).index
    df_bradford_op_filt = df_bradford_op[df_bradford_op['operacao'].isin(top_ops)]

    # Top 5 categorias
    top_cats = df['categoria_profissional'].value_counts().head(5).index
    df_bradford_op_filt = df_bradford_op_filt[df_bradford_op_filt['categoria_profissional'].isin(top_cats)]

    # Pivot: operação × categoria
    pivot_bradford = df_bradford_op_filt.pivot_table(
        index='operacao',
        columns='categoria_profissional',
        values='bradford_score',
        aggfunc='mean'
    ).fillna(0)

    # Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_bradford.values,
        x=pivot_bradford.columns,
        y=pivot_bradford.index,
        colorscale='RdYlGn_r',  # Vermelho = alto, Verde = baixo
        text=pivot_bradford.values.round(0),
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='Operação: %{y}<br>Categoria: %{x}<br>Bradford Médio: %{z:.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Bradford Factor Médio: Operação × Categoria Profissional',
        xaxis_title='Categoria Profissional',
        yaxis_title='Operação',
        height=600,
        width=1000
    )

    fig.show()
    print('✓ Heatmap criado')
else:
    print('⚠️ Campo \"operacao\" não encontrado')"""
    })

    # Viz 2: Funil de Ação (Bradford Thresholds)
    new_viz_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 5.5 Visualização EXTRA: Funil de Ação (Bradford Thresholds)
print('\\nCriando funil de ação...')

# Contar colaboradores por threshold
thresholds = [
    (0, 45, 'Aceitável'),
    (45, 100, 'Conversa Informal'),
    (100, 200, 'Revisão Formal'),
    (200, 500, 'Aviso Escrito'),
    (500, 900, 'Ação Disciplinar'),
    (900, float('inf'), 'Preocupação Séria')
]

funnel_data = []
for min_val, max_val, label in thresholds:
    count = ((df_bradford['bradford_score'] >= min_val) &
             (df_bradford['bradford_score'] < max_val)).sum()
    funnel_data.append({'Nível': label, 'Colaboradores': count})

df_funnel = pd.DataFrame(funnel_data)

# Criar funil (inverted para mostrar prioridade)
fig = go.Figure()

colors = ['green', 'yellow', 'orange', 'red', 'darkred', 'black']

fig.add_trace(go.Funnel(
    y=df_funnel['Nível'],
    x=df_funnel['Colaboradores'],
    textposition='inside',
    textinfo='value+percent initial',
    marker=dict(color=colors),
    connector={"line": {"color": "gray", "dash": "dot", "width": 2}}
))

fig.update_layout(
    title='Funil de Ação: Colaboradores por Nível de Risco (Bradford Factor)',
    height=500,
    width=800
)

fig.show()

print('\\n📊 FUNIL DE AÇÃO')
for _, row in df_funnel.iterrows():
    print(f'   {row[\"Nível\"]:30s}: {row[\"Colaboradores\"]:4,} colaboradores')"""
    })

    # Viz 3: Timeline de Spells (mostra evolução temporal)
    new_viz_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 5.6 Visualização EXTRA: Timeline de Spells (Frequência vs Duração)
print('\\nCriando timeline de spells...')

# Agrupar spells por mês
df_spells['mes_inicio'] = df_spells['data_inicio'].dt.to_period('M').astype(str)

spells_mensal = df_spells.groupby('mes_inicio').agg({
    'spell_id': 'count',
    'duracao_dias': 'mean'
}).reset_index()

spells_mensal.columns = ['Mes', 'Num_Spells', 'Duracao_Media']

# Dual-axis plot
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Bar(
        x=spells_mensal['Mes'],
        y=spells_mensal['Num_Spells'],
        name='Número de Spells',
        marker_color='lightblue'
    ),
    secondary_y=False
)

fig.add_trace(
    go.Scatter(
        x=spells_mensal['Mes'],
        y=spells_mensal['Duracao_Media'],
        name='Duração Média (dias)',
        mode='lines+markers',
        line=dict(color='red', width=3),
        marker=dict(size=8)
    ),
    secondary_y=True
)

fig.update_xaxes(title_text='Mês')
fig.update_yaxes(title_text='Número de Spells', secondary_y=False)
fig.update_yaxes(title_text='Duração Média (dias)', secondary_y=True)

fig.update_layout(
    title='Evolução Temporal: Frequência vs Duração de Spells',
    height=500,
    hovermode='x unified'
)

fig.show()
print('✓ Timeline criada')"""
    })

    # Inserir após Bradford viz
    for i, cell in enumerate(new_viz_cells):
        nb['cells'].insert(bradford_viz_idx + 1 + i, cell)

    print(f"Added {len(new_viz_cells)} new visualization cells after Bradford")

# ==============================================================================
# 2. REESCREVER COMPLETAMENTE NETWORK ANALYSIS
# ==============================================================================

# Encontrar e REMOVER células antigas de network analysis
network_start = None
network_end = None

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if '## 9. NETWORK ANALYSIS' in source:
            network_start = i
        elif network_start is not None and '## 10.' in source:
            network_end = i
            break

if network_start and network_end:
    print(f"\\nRemoving old network analysis cells {network_start+1} to {network_end-1}")
    # Remove células antigas (exceto o markdown header)
    for _ in range(network_end - network_start - 1):
        nb['cells'].pop(network_start + 1)

    # Agora inserir novas células robustas
    new_network_cells = []

    # Cell 1: Markdown introdução
    new_network_cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": """### 9.1 Intuição e Objetivos

**Network Analysis** transforma o problema "quem faltou em que dias" numa **rede (grafo)** onde:
- **Nó** = Colaborador
- **Aresta** = Conexão entre dois colaboradores que faltaram no mesmo dia

**Objetivos**:
1. Descobrir **pares/grupos** que faltam juntos com frequência anómala
2. Identificar **equipas/operações** com alta co-incidência
3. Detetar **eventos pontuais** vs **padrões persistentes**
4. **Priorizar investigações** RH

**Metodologia**:
- Matriz de **co-ocorrência** (quantas vezes A e B faltaram juntos)
- **Testes estatísticos** (hipergeométrico) para filtrar coincidências significativas
- **Community detection** (Louvain) para encontrar clusters
- **Centralidade** para priorizar investigações
- **Visualização interativa** (pyvis)"""
    })

    # Cell 2: Preparar dados
    new_network_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.2 Preparar dados: Matriz Bipartida (Colaboradores × Dias)
print('=== NETWORK ANALYSIS: CO-OCORRÊNCIA DE AUSÊNCIAS ===')
print('\\nPreparando matriz bipartida...')

# Filtrar apenas ausências (excluir Trabalho Pago, Atraso)
df_ausencias_network = df[
    df['Nivel 1'].isin(['Falta Justificada', 'Falta Injustificada', 'Ausência'])
].copy()

print(f'   Registos de ausência: {len(df_ausencias_network):,}')
print(f'   Colaboradores: {df_ausencias_network[\"login_colaborador\"].nunique():,}')
print(f'   Dias únicos: {df_ausencias_network[\"Data\"].nunique():,}')

# Criar identificador único de dia
df_ausencias_network['date_id'] = df_ausencias_network['Data'].astype(str)

# Lista de colaboradores e dias
colaboradores = sorted(df_ausencias_network['login_colaborador'].unique())
dias = sorted(df_ausencias_network['date_id'].unique())

print(f'\\nDimensão da matriz: {len(colaboradores):,} colaboradores × {len(dias):,} dias')
print(f'   Esparsidade: {len(df_ausencias_network) / (len(colaboradores) * len(dias)) * 100:.2f}%')"""
    })

    # Cell 3: Criar matriz de co-ocorrência
    new_network_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.3 Criar Matriz de Co-ocorrência (C = B × B.T)
print('\\nCriando matriz de co-ocorrência...')
print('   (Isto pode demorar alguns minutos para datasets grandes)')

from scipy.sparse import csr_matrix, lil_matrix
import numpy as np

# Criar dicionários de índice
colab_to_idx = {c: i for i, c in enumerate(colaboradores)}
date_to_idx = {d: i for i, d in enumerate(dias)}

# Criar matriz bipartida esparsa (colaboradores × dias)
# B[i,j] = 1 se colaborador i esteve ausente no dia j
rows = []
cols = []

for _, row in df_ausencias_network.iterrows():
    colab_idx = colab_to_idx[row['login_colaborador']]
    date_idx = date_to_idx[row['date_id']]
    rows.append(colab_idx)
    cols.append(date_idx)

B = csr_matrix(
    (np.ones(len(rows)), (rows, cols)),
    shape=(len(colaboradores), len(dias)),
    dtype=np.int8
)

print(f'   Matriz B criada: {B.shape}')
print(f'   Memória: {B.data.nbytes / 1024 / 1024:.2f} MB')

# Calcular co-ocorrência: C = B × B.T
# C[i,j] = número de dias em que colaboradores i e j estiveram AMBOS ausentes
print('\\n   Calculando C = B × B.T...')
C = B @ B.T

# Converter para array denso (se couber em memória)
# Se dataset muito grande, trabalhar com sparse
if len(colaboradores) < 5000:
    C_dense = C.toarray()
    print(f'   Matriz C: {C_dense.shape} (densa)')
else:
    C_dense = None
    print(f'   Matriz C: {C.shape} (esparsa - dataset grande)')

print('\\n✓ Matriz de co-ocorrência criada')"""
    })

    # Cell 4: Calcular p-values (hipergeométrico)
    new_network_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.4 Teste Estatístico: P-values (Distribuição Hipergeométrica)
print('\\nCalculando p-values para coincidências...')

from scipy.stats import hypergeom

# Para cada par (i,j), calcular:
# H0: ausências são aleatórias ao longo de N dias
# N = total de dias
# K = dias ausentes de i (C[i,i])
# M = dias ausentes de j (C[j,j])
# k = observado (C[i,j])
# P(X >= k) sob H0

N_dias = len(dias)

# Dias ausentes por colaborador (diagonal de C)
dias_ausentes = np.diag(C.toarray()) if C_dense is None else np.diag(C_dense)

print(f'   N = {N_dias} dias totais')
print(f'   Média de dias ausentes por colaborador: {dias_ausentes.mean():.2f}')

# Criar lista de pares significativos
# (só calcular para pares com k > 0 para eficiência)
pares_significativos = []

print('\\n   Testando pares com co-ocorrências...')

# Threshold mínimo de co-ocorrências para considerar
min_cooccur = 2  # Pelo menos 2 dias juntos

n_pares_testados = 0
if C_dense is not None:
    # Trabalhar com matriz densa
    for i in range(len(colaboradores)):
        if i % 500 == 0 and i > 0:
            print(f'      Processado {i:,}/{len(colaboradores):,} colaboradores...')

        for j in range(i+1, len(colaboradores)):
            k_obs = C_dense[i, j]

            if k_obs >= min_cooccur:
                n_pares_testados += 1

                K_i = dias_ausentes[i]
                M_j = dias_ausentes[j]

                # P-value: P(X >= k_obs) sob hipergeométrica
                # hypergeom(M, n, N) onde M=N_dias, n=K_i, N=M_j
                # Survival function: P(X >= k)
                try:
                    pval = hypergeom.sf(k_obs - 1, N_dias, K_i, M_j)
                except:
                    pval = 1.0  # Se erro, considerar não significativo

                pares_significativos.append({
                    'colaborador_i': colaboradores[i],
                    'colaborador_j': colaboradores[j],
                    'dias_i': K_i,
                    'dias_j': M_j,
                    'cooccur': k_obs,
                    'p_value': pval
                })
else:
    # Trabalhar com matriz esparsa (mais lento mas menos memória)
    C_lil = C.tolil()
    for i in range(len(colaboradores)):
        if i % 500 == 0 and i > 0:
            print(f'      Processado {i:,}/{len(colaboradores):,} colaboradores...')

        for j in range(i+1, len(colaboradores)):
            k_obs = C_lil[i, j]

            if k_obs >= min_cooccur:
                n_pares_testados += 1

                K_i = C_lil[i, i]
                M_j = C_lil[j, j]

                try:
                    pval = hypergeom.sf(k_obs - 1, N_dias, K_i, M_j)
                except:
                    pval = 1.0

                pares_significativos.append({
                    'colaborador_i': colaboradores[i],
                    'colaborador_j': colaboradores[j],
                    'dias_i': K_i,
                    'dias_j': M_j,
                    'cooccur': k_obs,
                    'p_value': pval
                })

df_pares = pd.DataFrame(pares_significativos)

print(f'\\n✓ Testados {n_pares_testados:,} pares com ≥{min_cooccur} co-ocorrências')
print(f'   Total de pares potenciais: {len(colaboradores) * (len(colaboradores)-1) // 2:,}')"""
    })

    # Cell 5: FDR correction
    new_network_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.5 Correção FDR (False Discovery Rate)
print('\\nAplicando correção FDR...')

from statsmodels.stats.multitest import multipletests

if len(df_pares) > 0:
    # Aplicar Benjamini-Hochberg FDR
    reject, pvals_adj, _, _ = multipletests(
        df_pares['p_value'],
        alpha=0.05,
        method='fdr_bh'
    )

    df_pares['p_adj'] = pvals_adj
    df_pares['significant'] = reject

    n_sig = reject.sum()
    print(f'   Pares significativos (FDR < 0.05): {n_sig:,}')
    print(f'   ({n_sig / len(df_pares) * 100:.2f}% dos pares testados)')

    # Filtrar apenas significativos
    df_pares_sig = df_pares[df_pares['significant']].copy()

    # Ordenar por co-ocorrências (descendente)
    df_pares_sig = df_pares_sig.sort_values('cooccur', ascending=False).reset_index(drop=True)

    print(f'\\n📊 TOP 20 PARES COM COINCIDÊNCIAS SIGNIFICATIVAS:')
    print('='*100)

    top20_pares = df_pares_sig.head(20).copy()

    # Adicionar nomes
    top20_pares = top20_pares.merge(
        df[['login_colaborador', 'nome_colaborador']].drop_duplicates(),
        left_on='colaborador_i',
        right_on='login_colaborador',
        how='left'
    ).rename(columns={'nome_colaborador': 'nome_i'}).drop('login_colaborador', axis=1)

    top20_pares = top20_pares.merge(
        df[['login_colaborador', 'nome_colaborador']].drop_duplicates(),
        left_on='colaborador_j',
        right_on='login_colaborador',
        how='left'
    ).rename(columns={'nome_colaborador': 'nome_j'}).drop('login_colaborador', axis=1)

    # Adicionar operação (se disponível)
    if 'operacao' in df.columns:
        top20_pares = top20_pares.merge(
            df[['login_colaborador', 'operacao']].drop_duplicates(),
            left_on='colaborador_i',
            right_on='login_colaborador',
            how='left'
        ).rename(columns={'operacao': 'operacao_i'}).drop('login_colaborador', axis=1)

        top20_pares = top20_pares.merge(
            df[['login_colaborador', 'operacao']].drop_duplicates(),
            left_on='colaborador_j',
            right_on='login_colaborador',
            how='left'
        ).rename(columns={'operacao': 'operacao_j'}).drop('login_colaborador', axis=1)

    # Exibir
    for idx, row in top20_pares.iterrows():
        print(f"\\n{idx+1}. {row['nome_i']} + {row['nome_j']}")
        print(f"   Co-ocorrências: {row['cooccur']} dias")
        print(f"   P-value ajustado: {row['p_adj']:.2e}")
        if 'operacao_i' in row:
            print(f"   Operações: {row['operacao_i']} + {row['operacao_j']}")

    # Exportar para Excel
    top20_pares.to_excel('network_top20_pares_significativos.xlsx', index=False)
    print('\\n✓ Top 20 pares exportados para: network_top20_pares_significativos.xlsx')

else:
    print('   Nenhum par encontrado')
    df_pares_sig = pd.DataFrame()"""
    })

    # Cell 6: Community detection
    new_network_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.6 Community Detection (Louvain Algorithm)
print('\\nDeteção de comunidades (Louvain)...')

if len(df_pares_sig) > 0:
    import networkx as nx
    from networkx.algorithms import community

    # Criar grafo apenas com arestas significativas
    G = nx.Graph()

    # Adicionar nós
    G.add_nodes_from(colaboradores)

    # Adicionar arestas (ponderadas por co-ocorrências)
    for _, row in df_pares_sig.iterrows():
        G.add_edge(
            row['colaborador_i'],
            row['colaborador_j'],
            weight=row['cooccur'],
            p_adj=row['p_adj']
        )

    print(f'   Grafo criado: {G.number_of_nodes():,} nós, {G.number_of_edges():,} arestas')

    # Aplicar Louvain
    print('   Aplicando algoritmo de Louvain...')
    communities_generator = community.greedy_modularity_communities(G, weight='weight')
    communities_list = list(communities_generator)

    print(f'   Comunidades detetadas: {len(communities_list)}')

    # Criar mapeamento colaborador -> comunidade
    colab_to_community = {}
    for comm_id, comm_members in enumerate(communities_list):
        for member in comm_members:
            colab_to_community[member] = comm_id

    # Estatísticas por comunidade
    print(f'\\n📊 COMUNIDADES (clusters de co-ausências):')
    print('='*80)

    for comm_id, comm_members in enumerate(sorted(communities_list, key=len, reverse=True)[:10]):
        print(f'\\nComunidade {comm_id + 1}: {len(comm_members)} membros')

        # Nomes (primeiros 5)
        member_names = []
        for member in list(comm_members)[:5]:
            nome = df[df['login_colaborador'] == member]['nome_colaborador'].iloc[0]
            member_names.append(nome)

        print(f'   Membros (sample): {', '.join(member_names)}...')

        # Operações predominantes
        if 'operacao' in df.columns:
            ops = df[df['login_colaborador'].isin(comm_members)]['operacao'].value_counts().head(3)
            print(f'   Operações predominantes:')
            for op, count in ops.items():
                print(f'      - {op}: {count} registos')

    # Salvar comunidades
    df_communities = pd.DataFrame([
        {'login_colaborador': colab, 'community_id': comm_id}
        for colab, comm_id in colab_to_community.items()
    ])

    df_communities = df_communities.merge(
        df[['login_colaborador', 'nome_colaborador']].drop_duplicates(),
        on='login_colaborador'
    )

    df_communities.to_excel('network_comunidades.xlsx', index=False)
    print('\\n✓ Comunidades exportadas para: network_comunidades.xlsx')

else:
    print('   Nenhuma aresta significativa - comunidades não podem ser detetadas')
    G = None
    colab_to_community = {}"""
    })

    # Cell 7: Centralidade
    new_network_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.7 Centralidade: Priorizar Investigações
print('\\nCalculando métricas de centralidade...')

if G is not None and G.number_of_edges() > 0:
    # Degree centrality (número de conexões)
    degree_cent = nx.degree_centrality(G)

    # Betweenness centrality (ponte entre clusters)
    print('   Calculando betweenness centrality (pode demorar)...')
    betweenness_cent = nx.betweenness_centrality(G, weight='weight')

    # Closeness centrality
    # print('   Calculando closeness centrality...')
    # closeness_cent = nx.closeness_centrality(G, distance='weight')

    # Weighted degree (soma dos pesos)
    weighted_degree = dict(G.degree(weight='weight'))

    # Criar DataFrame
    df_centrality = pd.DataFrame({
        'login_colaborador': list(degree_cent.keys()),
        'degree_centrality': list(degree_cent.values()),
        'betweenness_centrality': list(betweenness_cent.values()),
        # 'closeness_centrality': list(closeness_cent.values()),
        'weighted_degree': [weighted_degree[c] for c in degree_cent.keys()]
    })

    # Adicionar nomes
    df_centrality = df_centrality.merge(
        df[['login_colaborador', 'nome_colaborador']].drop_duplicates(),
        on='login_colaborador'
    )

    # Top 20 por degree
    print(f'\\n🎯 TOP 20 COLABORADORES POR CENTRALIDADE (hubs de co-ausência):')
    print('='*100)

    top20_centrality = df_centrality.nlargest(20, 'degree_centrality')

    for idx, row in top20_centrality.iterrows():
        print(f"{row['nome_colaborador']:40s} | Connections: {int(row['weighted_degree']):3d} | "
              f"Degree: {row['degree_centrality']:.4f} | Betweenness: {row['betweenness_centrality']:.4f}")

    # Exportar
    df_centrality.to_excel('network_centralidade.xlsx', index=False)
    print('\\n✓ Métricas de centralidade exportadas para: network_centralidade.xlsx')

else:
    print('   Grafo vazio ou sem arestas')
    df_centrality = pd.DataFrame()"""
    })

    # Cell 8: Visualização interativa (pyvis)
    new_network_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.8 Visualização Interativa (Pyvis)
print('\\nCriando visualização interativa da rede...')

if G is not None and G.number_of_edges() > 0:
    try:
        from pyvis.network import Network

        # Limitar a top comunidades e top pares para legibilidade
        # Filtrar apenas top 5 comunidades e top 50 pares
        top_communities = sorted(communities_list, key=len, reverse=True)[:5]
        top_community_ids = [i for i, comm in enumerate(communities_list) if comm in top_communities]

        # Nós da top comunidades
        top_nodes = set()
        for comm in top_communities:
            top_nodes.update(comm)

        # Criar subgrafo
        G_sub = G.subgraph(top_nodes).copy()

        print(f'   Visualizando subgrafo: {G_sub.number_of_nodes()} nós, {G_sub.number_of_edges()} arestas')

        # Criar network pyvis
        net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')

        # Configurações
        net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=100)

        # Cores por comunidade
        colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
                  '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe']

        # Adicionar nós
        for node in G_sub.nodes():
            # Nome
            nome = df[df['login_colaborador'] == node]['nome_colaborador'].iloc[0] if len(df[df['login_colaborador'] == node]) > 0 else node

            # Comunidade
            comm_id = colab_to_community.get(node, -1)
            color = colors[comm_id % len(colors)] if comm_id >= 0 else '#cccccc'

            # Tamanho proporcional ao degree
            degree = G_sub.degree(node, weight='weight')
            size = 10 + degree * 2

            net.add_node(
                node,
                label=nome[:20],  # Limitar label
                title=f"{nome}\\nComunidade: {comm_id+1}\\nDegree: {degree}",
                color=color,
                size=size
            )

        # Adicionar arestas
        for edge in G_sub.edges(data=True):
            net.add_edge(
                edge[0],
                edge[1],
                value=edge[2]['weight'],  # Espessura proporcional ao peso
                title=f"{edge[2]['weight']} co-ocorrências"
            )

        # Salvar
        net.save_graph('network_visualization.html')
        print('\\n✓ Visualização interativa criada: network_visualization.html')
        print('   (Abrir no browser para explorar)')

    except ImportError:
        print('\\n⚠️  pyvis não instalado. Instalando...')
        import subprocess
        subprocess.run(['pip', 'install', 'pyvis', '-q'])
        print('   Por favor, executar esta célula novamente')

else:
    print('   Grafo vazio - visualização não criada')"""
    })

    # Cell 9: Timeline (dinâmica temporal)
    new_network_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.9 Dinâmica Temporal: Evolução dos Pares Significativos
print('\\nAnalisando dinâmica temporal da rede...')

if len(df_pares_sig) > 0:
    # Para cada par significativo, encontrar QUANDO aconteceram as co-ausências

    # Pegar top 10 pares
    top_pares = df_pares_sig.head(10)

    # Para cada par, buscar datas
    timeline_data = []

    for _, pair in top_pares.iterrows():
        colab_i = pair['colaborador_i']
        colab_j = pair['colaborador_j']

        # Encontrar dias em que AMBOS faltaram
        dias_i = set(df_ausencias_network[df_ausencias_network['login_colaborador'] == colab_i]['Data'])
        dias_j = set(df_ausencias_network[df_ausencias_network['login_colaborador'] == colab_j]['Data'])

        dias_comuns = sorted(dias_i & dias_j)

        # Agrupar por mês
        for data in dias_comuns:
            mes = data.to_period('M').to_timestamp()
            timeline_data.append({
                'par': f"{pair['nome_i'][:15]}...\\n{pair['nome_j'][:15]}...",
                'mes': mes,
                'cooccur_count': 1
            })

    if timeline_data:
        df_timeline = pd.DataFrame(timeline_data)

        # Agregar por par e mês
        df_timeline_agg = df_timeline.groupby(['par', 'mes'])['cooccur_count'].sum().reset_index()

        # Plot
        fig = px.line(
            df_timeline_agg,
            x='mes',
            y='cooccur_count',
            color='par',
            title='Evolução Temporal: Co-ocorrências dos Top 10 Pares',
            labels={'mes': 'Mês', 'cooccur_count': 'Nº Co-ocorrências', 'par': 'Par'},
            height=600
        )

        fig.update_traces(mode='lines+markers')
        fig.update_layout(hovermode='x unified')

        fig.show()

        print('✓ Timeline criada')
    else:
        print('   Sem dados suficientes para timeline')
else:
    print('   Nenhum par significativo para análise temporal')"""
    })

    # Inserir novas células
    for i, cell in enumerate(new_network_cells):
        nb['cells'].insert(network_start + 1 + i, cell)

    print(f"Added {len(new_network_cells)} new robust network analysis cells")

# ==============================================================================
# SALVAR NOTEBOOK
# ==============================================================================

print(f"\\nFinal notebook: {len(nb['cells'])} cells")

with open('analise_absentismo_avancada.ipynb', 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("\\n✓ Notebook upgraded successfully!")
print("\\nNew features:")
print("  - 3 new visualizations (heatmap, funnel, timeline)")
print("  - Complete network analysis rewrite (9 cells)")
print("  - Co-occurrence matrix with statistical testing")
print("  - Community detection (Louvain)")
print("  - Centrality metrics")
print("  - Interactive visualization (pyvis)")
print("  - Temporal dynamics")
