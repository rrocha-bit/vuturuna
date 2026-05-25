"""
FreeCAD Script - Sobrado com Garagem
=====================================
Garagem: nível da rua, 5,00m de profundidade
Plato do terreno: 3,25m acima do nível da garagem
Sobrado: 2 andares, 17,23m x 4,90m

Dimensões:
  Largura (X):      17,23 m
  Profundidade (Y):  4,90 m
  Desnível plato:    3,25 m
  Garagem (Z):       5,00 m de profundidade (escavação / nível rua)
  Pé-direito por andar: 2,80 m (padrão)
  Laje:              0,20 m

Origem (0,0,0) = canto inferior esquerdo da garagem, ao nível da rua.

Para executar:
  1. Abra o FreeCAD
  2. Menu: Macro > Macros... > Criar / abrir este arquivo
  3. Clique em Executar  (ou: freecadcmd sobrado_com_garagem.py)
"""

import FreeCAD as App
import Part

# ─── parâmetros ───────────────────────────────────────────────────────────────
COMP   = 17.230   # comprimento (eixo X)  [m]
LARG   = 4.900    # largura     (eixo Y)  [m]

GAR_PROF   = 5.000   # profundidade da garagem abaixo da rua (eixo Z negativo) [m]
GAR_PE     = 2.800   # pé-direito interno da garagem [m]  (Z = 0 é nível rua)
GAR_LAJE   = 0.200   # espessura da laje sobre a garagem [m]

PLATO_DESNIVEL = 3.250   # desnível do plato em relação ao piso da garagem (nível rua) [m]
# O piso do sobrado fica em Z = PLATO_DESNIVEL
# A laje da garagem vai de Z=0 até Z=GAR_LAJE;
# o preenchimento de terra/contenção fica entre Z=GAR_LAJE e Z=PLATO_DESNIVEL

PE_DIREITO = 2.800   # pé-direito de cada andar do sobrado [m]
LAJE_ESP   = 0.200   # espessura das lajes entre andares e cobertura [m]
PAREDE_ESP = 0.200   # espessura das paredes externas [m]

# Escala de exibição: FreeCAD usa mm internamente → multiplicar por 1000
MM = 1000.0

# ─── helper ───────────────────────────────────────────────────────────────────
def box(x0, y0, z0, dx, dy, dz, name):
    """Cria um sólido caixa e o adiciona ao documento."""
    solid = Part.makeBox(dx * MM, dy * MM, dz * MM,
                         App.Vector(x0 * MM, y0 * MM, z0 * MM))
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = solid
    return obj

# ─── documento ────────────────────────────────────────────────────────────────
doc = App.newDocument("Sobrado_Garagem")

# ══════════════════════════════════════════════════════════════════════════════
# 1. GARAGEM  (Z negativo = abaixo do nível da rua)
# ══════════════════════════════════════════════════════════════════════════════
# Piso da garagem: Z = -GAR_PROF  até  Z = -GAR_PROF + 0.10 (piso de concreto)
box(0, 0, -GAR_PROF,        COMP, LARG, 0.10,         "Garagem_Piso")

# Paredes laterais da garagem (esquerda e direita em Y)
box(0, 0,            -GAR_PROF,  COMP, PAREDE_ESP, GAR_PROF,  "Garagem_Parede_Frente")
box(0, LARG-PAREDE_ESP, -GAR_PROF, COMP, PAREDE_ESP, GAR_PROF, "Garagem_Parede_Fundo")

# Paredes laterais em X
box(0,              0, -GAR_PROF,  PAREDE_ESP, LARG, GAR_PROF, "Garagem_Parede_Esq")
box(COMP-PAREDE_ESP, 0, -GAR_PROF, PAREDE_ESP, LARG, GAR_PROF, "Garagem_Parede_Dir")

# Laje de cobertura da garagem / piso rua  (Z=0 até Z=GAR_LAJE)
box(0, 0, 0,  COMP, LARG, GAR_LAJE,  "Garagem_Laje_Cobertura")

# ══════════════════════════════════════════════════════════════════════════════
# 2. MURO DE CONTENÇÃO / ATERRO  (entre laje garagem e plato)
#    Representado como volume sólido (terra + contenção lateral)
# ══════════════════════════════════════════════════════════════════════════════
ATERRO_H = PLATO_DESNIVEL - GAR_LAJE   # altura do aterro
if ATERRO_H > 0:
    box(0, 0, GAR_LAJE,  COMP, LARG, ATERRO_H,  "Aterro_Plato")

# ══════════════════════════════════════════════════════════════════════════════
# 3. SOBRADO  (Z_BASE = PLATO_DESNIVEL)
# ══════════════════════════════════════════════════════════════════════════════
Z_SOBRADO = PLATO_DESNIVEL   # piso do 1º andar do sobrado

for andar in range(1, 3):   # andares 1 e 2
    Z_base = Z_SOBRADO + (andar - 1) * (PE_DIREITO + LAJE_ESP)
    label  = f"Andar_{andar}"

    # Laje de piso do andar (exceto o 1º que usa o plato)
    if andar > 1:
        box(0, 0, Z_base - LAJE_ESP,  COMP, LARG, LAJE_ESP,
            f"Laje_Piso_Andar{andar}")

    # Paredes externas (4 faces, espessura = PAREDE_ESP)
    box(0, 0,                Z_base,  COMP, PAREDE_ESP,        PE_DIREITO, f"{label}_Parede_Front")
    box(0, LARG-PAREDE_ESP,  Z_base,  COMP, PAREDE_ESP,        PE_DIREITO, f"{label}_Parede_Back")
    box(0, 0,                Z_base,  PAREDE_ESP,        LARG,  PE_DIREITO, f"{label}_Parede_Esq")
    box(COMP-PAREDE_ESP, 0,  Z_base,  PAREDE_ESP,        LARG,  PE_DIREITO, f"{label}_Parede_Dir")

# Laje de cobertura (topo do 2º andar)
Z_cobertura = Z_SOBRADO + 2 * (PE_DIREITO + LAJE_ESP) - LAJE_ESP
box(0, 0, Z_cobertura,  COMP, LARG, LAJE_ESP,  "Laje_Cobertura")

# ══════════════════════════════════════════════════════════════════════════════
# 4. Finalizar
# ══════════════════════════════════════════════════════════════════════════════
doc.recompute()

try:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass  # modo headless (freecadcmd): sem GUI

# Exportar automaticamente para STEP se rodando em linha de comando
import os
step_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sobrado_com_garagem.step")
try:
    import Import
    Import.export(doc.Objects, step_path)
    print(f"Modelo exportado para: {step_path}")
except Exception as e:
    print(f"Export STEP não disponível neste ambiente: {e}")

print("Script concluído com sucesso.")
print(f"  Garagem      : {COMP} x {LARG} x {GAR_PROF} m  (abaixo da rua)")
print(f"  Plato/desnível: {PLATO_DESNIVEL} m acima da garagem")
print(f"  Sobrado      : {COMP} x {LARG}, 2 andares de {PE_DIREITO} m pé-direito")
Z_total = PLATO_DESNIVEL + 2 * (PE_DIREITO + LAJE_ESP)
print(f"  Altura total acima da rua: {Z_total:.2f} m")
