#!/usr/bin/env python3
"""
Corrigir célula 9 - distribuição de incompatibilidades
"""

import json

with open('analise_absentismo_avancada.ipynb', 'r') as f:
    nb = json.load(f)

print("Procurando célula problemática...")

# Procurar a célula que adicionei (1.3.6)
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))

        if '# 1.3.6 Distribuição por par incompatível (COMPLETO)' in source:
            print(f"Encontrada célula problemática em posição {i}")
            print("Removendo célula duplicada...")

            # Remover esta célula - já existe código equivalente na célula anterior
            del nb['cells'][i]

            print("✓ Célula removida")
            break

# Salvar
with open('analise_absentismo_avancada.ipynb', 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print()
print("="*70)
print(f"Notebook corrigido: {len(nb['cells'])} células")
print()
print("NOTA: A distribuição por pares já existe na célula anterior")
print("      usando a coluna 'pares_incompativeis'")
print("="*70)
