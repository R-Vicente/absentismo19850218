#!/usr/bin/env python3
"""
Script para CORRIGIR completamente a network analysis.
Abordagem: SIMPLES e DIRETA, sem complicações.
"""

import json

with open('analise_absentismo_avancada.ipynb', 'r') as f:
    nb = json.load(f)

print(f"Notebook original: {len(nb['cells'])} células")

# Encontrar onde começa e termina network analysis
network_start = None
network_end = None

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if '## 9. NETWORK ANALYSIS' in source:
            network_start = i
            print(f"Network analysis começa na célula {i}")
        elif network_start is not None and '## 10.' in source:
            network_end = i
            print(f"Network analysis termina na célula {i}")
            break

if network_start and network_end:
    # Remover TODAS as células antigas da network analysis
    print(f"\nRemovendo células {network_start+1} até {network_end-1}")
    num_to_remove = network_end - network_start - 1
    for _ in range(num_to_remove):
        nb['cells'].pop(network_start + 1)

    print(f"Células removidas: {num_to_remove}")

    # Criar NOVAS células SIMPLES E CORRETAS
    new_cells = []

    # ========== CÉLULA 1: Preparar dados (só colaboradores ativos) ==========
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.1 Preparar dados: APENAS colaboradores ativos
print('=== NETWORK ANALYSIS: CO-AUSÊNCIAS ===\\n')

# Filtrar apenas ausências de colaboradores ativos
if 'Activo?' in df.columns:
    df_network = df[
        (df['Nivel 1'].isin(['Falta Justificada', 'Falta Injustificada', 'Ausência'])) &
        (df['Activo?'].isin(['Sim', True, 'sim', 'S']))
    ].copy()
    print(f'✓ Filtrado para colaboradores ativos')
else:
    df_network = df[
        df['Nivel 1'].isin(['Falta Justificada', 'Falta Injustificada', 'Ausência'])
    ].copy()
    print(f'⚠️  Campo Activo? não encontrado - usando todos')

print(f'Registos: {len(df_network):,}')
print(f'Colaboradores: {df_network["login_colaborador"].nunique():,}')
print(f'Período: {df_network["Data"].min().date()} até {df_network["Data"].max().date()}')"""
    })

    # ========== CÉLULA 2: Calcular co-ausências (método SIMPLES) ==========
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.2 Calcular co-ausências e métricas de overlap
print('\\nCalculando co-ausências por pares...\\n')

# Criar dicionário: colaborador -> set de dias
print('   Criando dicionário de dias por colaborador...')
colab_dias = {}
for colab in df_network['login_colaborador'].unique():
    dias_set = set(df_network[df_network['login_colaborador'] == colab]['Data'])
    colab_dias[colab] = dias_set

colaboradores = list(colab_dias.keys())
print(f'   Colaboradores: {len(colaboradores):,}')

# Calcular overlaps entre todos os pares
print('   Calculando overlaps entre pares...')
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
            # Overlap em relação ao menor
            overlap_pct = cooccur / min(len(dias_i), len(dias_j))

            pares.append({
                'colab_i': colab_i,
                'colab_j': colab_j,
                'cooccur': cooccur,
                'dias_i': len(dias_i),
                'dias_j': len(dias_j),
                'overlap_pct': overlap_pct
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

# Ordenar por overlap
df_pares = df_pares.sort_values('overlap_pct', ascending=False).reset_index(drop=True)"""
    })

    # ========== CÉLULA 3: Análise de distribuição ==========
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.3 Análise de distribuição para escolher threshold
print('\\nANÁLISE DE DISTRIBUIÇÃO:\\n')

print(f'📊 Estatísticas de Overlap:')
print(f'   Média: {df_pares["overlap_pct"].mean()*100:.1f}%')
print(f'   Mediana: {df_pares["overlap_pct"].median()*100:.1f}%')
print(f'   P75: {df_pares["overlap_pct"].quantile(0.75)*100:.1f}%')
print(f'   P90: {df_pares["overlap_pct"].quantile(0.90)*100:.1f}%')
print(f'   P95: {df_pares["overlap_pct"].quantile(0.95)*100:.1f}%')
print(f'   Máximo: {df_pares["overlap_pct"].max()*100:.1f}%')

# Histograma
fig = go.Figure()

fig.add_trace(go.Histogram(
    x=df_pares['overlap_pct'] * 100,
    nbinsx=50,
    marker_color='lightblue',
    marker_line_color='white',
    marker_line_width=1
))

fig.update_layout(
    title='Distribuição de Overlap % entre Pares',
    xaxis_title='Overlap %',
    yaxis_title='Número de Pares',
    height=400
)

fig.show()

# Escolher threshold (P90)
threshold = df_pares['overlap_pct'].quantile(0.90)
print(f'\\n💡 Threshold escolhido (P90): {threshold*100:.1f}%')

df_pares_sig = df_pares[df_pares['overlap_pct'] >= threshold].copy()
print(f'   Pares significativos: {len(df_pares_sig):,}')"""
    })

    # ========== CÉLULA 4: Top pares ==========
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.4 Top pares com maior overlap
print('\\n🔝 TOP 20 PARES POR OVERLAP:\\n')

for idx, row in df_pares_sig.head(20).iterrows():
    print(f"{idx+1:2d}. {row['nome_i'][:30]:30s} + {row['nome_j'][:30]:30s}")
    print(f"    Co-ausências: {row['cooccur']:3d} | Total i: {row['dias_i']:3d} | Total j: {row['dias_j']:3d} | Overlap: {row['overlap_pct']*100:5.1f}%")

# Exportar
df_pares_sig.to_excel('network_pares_significativos.xlsx', index=False)
print('\\n✓ Exportado: network_pares_significativos.xlsx')"""
    })

    # ========== CÉLULA 5: Visualização SIMPLES como Plotly example ==========
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": """# 9.5 Visualização da Rede (estilo Plotly example)
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
        weight=row['overlap_pct'],
        cooccur=row['cooccur']
    )

print(f'   Nós: {G.number_of_nodes()}, Arestas: {G.number_of_edges()}')

# Layout spring
pos = nx.spring_layout(G, k=1, iterations=50, seed=42)

# Preparar arestas
edge_x = []
edge_y = []

for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

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
fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title=f'<br>Rede de Co-Ausências (Top {TOP_N} pares)',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=700,
                width=1000))

fig.show()

print('\\n✓ Visualização criada')"""
    })

    # Inserir novas células
    for i, cell in enumerate(new_cells):
        nb['cells'].insert(network_start + 1 + i, cell)

    print(f"\\nInseridas {len(new_cells)} novas células")
    print(f"Notebook final: {len(nb['cells'])} células")

    # Salvar
    with open('analise_absentismo_avancada.ipynb', 'w') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print("\\n✓ Notebook corrigido e salvo!")
    print("\\nMUDANÇAS:")
    print("  - Removida construção de matriz (tinha bug de overflow)")
    print("  - Método SIMPLES com sets (garantido correto)")
    print("  - Visualização estilo Plotly example (limpa)")
    print("  - 5 células novas (em vez de 11)")

else:
    print("\\n❌ Não encontrei seção de network analysis")
