#!/usr/bin/env python3
"""
Substituir código lento por código otimizado no notebook de combinações
"""

import json

with open('analise_combinacoes.ipynb', 'r') as f:
    nb = json.load(f)

print("Substituindo código de testes de incompatibilidades...")

# Encontrar célula 5 (teste de incompatibilidades)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        if '# 5. Testar incompatibilidades' in source:
            print(f"Encontrada célula {i}")

            # Código OTIMIZADO
            new_source = """# 5. Testar incompatibilidades (VERSÃO OTIMIZADA)
print('Testando incompatibilidades nos dias duplicados...\\n')

# PRÉ-FILTRAR apenas dias duplicados
dias_dup_list = list(zip(dias_duplicados['login_colaborador'], dias_duplicados['Data']))
df_dup = df[df.set_index(['login_colaborador', 'Data']).index.isin(dias_dup_list)].copy()

print(f'   Registos a testar: {len(df_dup):,}')

# PRÉ-AGRUPAR dados (UMA vez!)
df_dup_grouped = df_dup.groupby(['login_colaborador', 'Data']).agg({
    'Nivel 2': lambda x: list(x.dropna().unique()),
    'segmento_processado_codigo': lambda x: list(x.unique()),
    'nome_colaborador': 'first'
}).reset_index()

df_dup_grouped.columns = ['login_colaborador', 'Data', 'categorias_nivel2', 'codigos', 'nome']

print(f'   Dias únicos a testar: {len(df_dup_grouped):,}')

# Identificar incompatibilidades
print('\\nTestando pares de categorias...')
dias_incompativeis = []

for idx, row in df_dup_grouped.iterrows():
    if idx % 5000 == 0 and idx > 0:
        print(f'   Processados {idx:,}/{len(df_dup_grouped):,} dias...')

    login = row['login_colaborador']
    data = row['Data']
    categorias = row['categorias_nivel2']
    codigos = row['codigos']
    nome = row['nome']

    # Testar todos os pares
    incompativel_encontrado = False
    pares_incompativeis = []

    for i, cat1 in enumerate(categorias):
        for cat2 in categorias[i+1:]:
            key = tuple(sorted([cat1, cat2]))
            if key in compat_dict and compat_dict[key] == 0:
                incompativel_encontrado = True
                pares_incompativeis.append(f'{cat1} + {cat2}')

    if incompativel_encontrado:
        dias_incompativeis.append({
            'login_colaborador': login,
            'Data': data,
            'nome_colaborador': nome,
            'categorias': ', '.join(categorias),
            'codigos': ', '.join(codigos),
            'pares_incompativeis': ' | '.join(pares_incompativeis)
        })

df_incompativeis = pd.DataFrame(dias_incompativeis)

print(f'\\n✓ Teste concluído')
print(f'🔴 INCOMPATIBILIDADES ENCONTRADAS: {len(df_incompativeis)}')

if len(df_incompativeis) > 0:
    print(f'\\nPrimeiros 10 casos:')
    print(df_incompativeis[['Data', 'nome_colaborador', 'pares_incompativeis']].head(10))
"""

            nb['cells'][i]['source'] = new_source
            print("✓ Código otimizado aplicado")
            break

# Salvar
with open('analise_combinacoes.ipynb', 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("\n✅ Notebook atualizado com código OTIMIZADO")
print("Agora deve ser RÁPIDO!")
