#!/usr/bin/env python3
"""
Integrar lógica de hierarquias no notebook principal
"""

import json

with open('analise_absentismo_avancada.ipynb', 'r') as f:
    nb = json.load(f)

print("Integrando lógica de hierarquias no notebook principal...")
print(f"Células originais: {len(nb['cells'])}")

# Encontrar célula de agregação (1.3.5)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if '# 1.3.5 Agregação final' in source:
            print(f"\nEncontrada célula de agregação em posição {i}")

            # Substituir por NOVA lógica
            new_source = """# 1.3.5 Aplicar Hierarquias e Criar Dataframes Separados
print('\\n=== APLICANDO HIERARQUIAS DE SEPARAÇÃO ===')

# ============================================================================
# PASSO 1: Identificar combinações existentes
# ============================================================================
print('\\n1. Identificando combinações...')

dias_mult = df_limpo.groupby(['login_colaborador', 'Data']).size()
dias_mult = dias_mult[dias_mult > 1].reset_index()

print(f'   Dias com múltiplos registos: {len(dias_mult):,}')

# Método rápido: pré-filtrar e agrupar
dias_mult_idx = list(zip(dias_mult['login_colaborador'], dias_mult['Data']))
df_mult_only = df_limpo[df_limpo.set_index(['login_colaborador', 'Data']).index.isin(dias_mult_idx)]

df_combos = df_mult_only.groupby(['login_colaborador', 'Data']).agg({
    'Nivel 1': lambda x: ' + '.join(sorted(x.unique())),
    'Nivel 2': lambda x: ' + '.join(sorted(x.unique()))
}).reset_index()

df_combos.columns = ['login_colaborador', 'Data', 'combo_n1', 'combo_n2']

print(f'\\n   Combinações Nivel 1 encontradas:')
for combo, count in df_combos['combo_n1'].value_counts().head(10).items():
    print(f'      {combo:50s}: {count:,}')

# ============================================================================
# PASSO 2: Identificar casos a ELIMINAR
# ============================================================================
print('\\n2. Identificando casos a eliminar...')

# Nivel 1 - casos raros
eliminar_n1 = df_combos[
    df_combos['combo_n1'].isin([
        'Falta Injustificada + Trabalho Pago',
        'Falta Justificada + Trabalho Pago',
        'Atraso + Falta Justificada'
    ])
]

print(f'   Nivel 1 - casos raros: {len(eliminar_n1)}')

# Nivel 2 - problemas específicos
patterns = [
    'Feriado \\\\+ Presença',
    'Férias \\\\+ Presença',
    'Folga \\\\+ Presença',
    'Falta Injustificada \\\\+ Presença',
    'Assistência Familiar \\\\+ Presença',
    'Atraso \\\\+ Ausência Médica',
    'Ausência Justificada \\\\+ Presença'
]

eliminar_n2 = df_combos[
    df_combos['combo_n2'].str.contains('|'.join(patterns), na=False, regex=True)
]

print(f'   Nivel 2 - problemas: {len(eliminar_n2)}')

# Total
eliminar_total = pd.concat([
    eliminar_n1[['login_colaborador', 'Data']],
    eliminar_n2[['login_colaborador', 'Data']]
]).drop_duplicates()

print(f'   🔴 TOTAL A ELIMINAR: {len(eliminar_total)} dias')

# ============================================================================
# PASSO 3: ELIMINAR casos
# ============================================================================
print('\\n3. Eliminando casos problemáticos...')

idx_eliminar = df_limpo.set_index(['login_colaborador', 'Data']).index.isin(
    list(zip(eliminar_total['login_colaborador'], eliminar_total['Data']))
)

df_limpo = df_limpo[~idx_eliminar].copy()

print(f'   ✓ Eliminados {idx_eliminar.sum():,} registos')
print(f'   ✓ df_limpo: {len(df_limpo):,} registos restantes')

# ============================================================================
# PASSO 4: SEPARAR df_atrasos
# ============================================================================
print('\\n4. Separando dataframe de atrasos...')

dias_atraso = df_combos[df_combos['combo_n1'] == 'Atraso + Trabalho Pago']

print(f'   Dias "Atraso + Trabalho Pago": {len(dias_atraso):,}')

# df_atrasos: copiar linhas onde Nivel 1 = 'Atraso'
idx_atrasos = df_limpo.set_index(['login_colaborador', 'Data']).index.isin(
    list(zip(dias_atraso['login_colaborador'], dias_atraso['Data']))
) & (df_limpo['Nivel 1'] == 'Atraso')

df_atrasos = df_limpo[idx_atrasos].copy()

print(f'   ✓ df_atrasos criado: {len(df_atrasos):,} registos')

# Remover atrasos do principal
df_limpo = df_limpo[~idx_atrasos].copy()

print(f'   ✓ Atrasos removidos do df principal: {len(df_limpo):,} registos restantes')

# ============================================================================
# PASSO 5: AGREGAR ambos os dataframes
# ============================================================================
print('\\n5. Agregando dataframes...')

# Regras de agregação (strings ordenadas)
agg_rules = {
    'nome_colaborador': 'first',
    'categoria_profissional': 'first',
    'segmento_processado_codigo': lambda x: ', '.join(sorted(x.unique())),
    'Nivel 1': lambda x: ', '.join(sorted(x.unique())),
    'Nivel 2': lambda x: ', '.join(sorted(x.unique())),
}

# Campos opcionais
for col in ['operacao', 'Activo?', 'DtActivacao', 'DtDesactivacao']:
    if col in df_limpo.columns:
        agg_rules[col] = 'first'

# Agregar df principal (absentismo)
df = df_limpo.groupby(['login_colaborador', 'Data']).agg(agg_rules).reset_index()

print(f'   ✓ df (principal - absentismo): {len(df):,} dias-colaborador')
print(f'     Colaboradores: {df[\"login_colaborador\"].nunique():,}')

# Agregar df_atrasos
df_atrasos = df_atrasos.groupby(['login_colaborador', 'Data']).agg(agg_rules).reset_index()

print(f'   ✓ df_atrasos: {len(df_atrasos):,} dias-colaborador')
print(f'     Colaboradores com atrasos: {df_atrasos[\"login_colaborador\"].nunique():,}')

# ============================================================================
# RESUMO
# ============================================================================
print('\\n' + '='*70)
print('✅ SEPARAÇÃO CONCLUÍDA')
print('='*70)
print(f'df (absentismo)       : {len(df):,} dias-colaborador (SEM atrasos)')
print(f'df_atrasos            : {len(df_atrasos):,} dias-colaborador')
print(f'Dias eliminados       : {len(eliminar_total)}')
print(f'Período               : {df[\"Data\"].min().date()} até {df[\"Data\"].max().date()}')
print('='*70)
"""

            nb['cells'][i]['source'] = new_source
            print("✓ Célula substituída com nova lógica")
            break

# Salvar
with open('analise_absentismo_avancada.ipynb', 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\n✅ Notebook atualizado: {len(nb['cells'])} células")
print("\nNOVA LÓGICA:")
print("  1. Identifica combinações")
print("  2. Elimina casos raros/problemáticos")
print("  3. Separa df_atrasos")
print("  4. Agrega ambos com strings ordenadas")
print("\nOUTPUTS:")
print("  - df: absentismo (sem atrasos)")
print("  - df_atrasos: só atrasos")
