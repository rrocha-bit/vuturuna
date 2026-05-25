"""
FreeCAD Script - Sobrado com Garagem + Terreno completo
========================================================
Terreno trapezoidal:
  Frente (rua):       6.40 m  (eixo X)
  Profundidade esq:  31.00 m  (X=0,    lado esquerdo)
  Profundidade dir:  32.00 m  (X=6.40, lado direito)
  Fundo: diagonal conectando os dois lados

Larguras no eixo X:
  X=0.00 → X=4.90   casa (garagem + sobrado)
  X=4.90 → X=6.40   corredor lateral (1.50m)
  X=6.40             muro direito (32m profundidade)

Layout em Y (rua → fundo):
  Y=0.00 → Y=5.00   GARAGEM  (nível rua, Z=0)
  Y=5.00             muro de contenção do plato
  Y=5.00 → Y=22.23  SOBRADO  (plato Z=3.25m)

Eixos:
  X: largura  (0 → 6.40)
  Y: profundidade (0=rua, cresce para dentro)
  Z: altura   (0=nível da rua)
"""

import FreeCAD as App
import Part

# ─── parâmetros ───────────────────────────────────────────────────────────────
FRENTE      = 6.400    # largura total do terreno (X)
CASA_LARG   = 4.900    # largura da casa/garagem (X)
RECUO_LARG  = 1.500    # corredor lateral direito (X) = FRENTE - CASA_LARG

GAR_PROF    = 5.000    # profundidade da garagem (Y)
GAR_PE      = 2.800    # pé-direito da garagem
GAR_LAJE    = 0.200    # espessura laje teto garagem

SOB_PROF    = 17.230   # profundidade do sobrado (Y)
PLATO_Z     = 3.250    # altura do plato (Z)
PE_DIREITO  = 2.800    # pé-direito por andar
LAJE_ESP    = 0.200    # espessura das lajes
PAREDE_ESP  = 0.140    # espessura das paredes
MURO_ESP    = 0.150    # espessura dos muros do terreno

TERRENO_ESQ = 31.000   # profundidade lado esquerdo (X=0)
TERRENO_DIR = 32.000   # profundidade lado direito  (X=FRENTE)

MM = 1000.0

# ─── helpers ──────────────────────────────────────────────────────────────────
def box(x0, y0, z0, dx, dy, dz, name):
    solid = Part.makeBox(dx*MM, dy*MM, dz*MM,
                         App.Vector(x0*MM, y0*MM, z0*MM))
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = solid
    return obj

def poligono_extrude(vertices_xy, z0, altura, name):
    """Extruda um polígono XY de z0 até z0+altura."""
    pts = [App.Vector(x*MM, y*MM, z0*MM) for x, y in vertices_xy]
    pts.append(pts[0])
    wire  = Part.makePolygon(pts)
    face  = Part.Face(wire)
    solid = face.extrude(App.Vector(0, 0, altura*MM))
    obj   = doc.addObject("Part::Feature", name)
    obj.Shape = solid
    return obj

# ─── documento ────────────────────────────────────────────────────────────────
doc = App.newDocument("Sobrado_Garagem")

# Vértices do terreno completo (trapézio)
terreno_verts = [
    (0,      0),
    (FRENTE, 0),
    (FRENTE, TERRENO_DIR),
    (0,      TERRENO_ESQ),
]

# Vértices do terreno atrás da garagem (sem a faixa frontal de 5m)
terra_verts = [
    (0,      GAR_PROF),
    (FRENTE, GAR_PROF),
    (FRENTE, TERRENO_DIR),
    (0,      TERRENO_ESQ),
]

# ══════════════════════════════════════════════════════════════════════════════
# 1. TERRENO — massa de terra
# ══════════════════════════════════════════════════════════════════════════════

# Base plana (lâmina de 0.30m abaixo da rua) — todo o trapézio
poligono_extrude(terreno_verts, -0.30, 0.30, "Terreno_Base")

# Corpo de terra atrás da garagem: Z=0 → Z=PLATO_Z
poligono_extrude(terra_verts, 0, PLATO_Z, "Terreno_Corpo")

# ══════════════════════════════════════════════════════════════════════════════
# 2. MURO DIREITO — X=FRENTE, ao longo de toda a profundidade do terreno (32m)
#    Z=0 até PLATO_Z (altura do plato)
# ══════════════════════════════════════════════════════════════════════════════
box(FRENTE-MURO_ESP, 0, 0,  MURO_ESP, TERRENO_DIR, PLATO_Z,  "Muro_Direito")

# ══════════════════════════════════════════════════════════════════════════════
# 3. CORREDOR LATERAL DIREITO — entre a casa e o muro
#    X: CASA_LARG → FRENTE-MURO_ESP
#    Y: 0 → TERRENO_DIR (acompanha o comprimento do muro)
#    Z: 0 (nível do chão — apenas representado pelo terreno base)
# ══════════════════════════════════════════════════════════════════════════════
# O corredor é o espaço livre entre a casa (X=4.90) e o muro (X=6.40)
# Representado como laje de piso no nível da rua (faixa frontal)
# e no nível do plato (faixa dos fundos)
box(CASA_LARG, 0, 0,
    RECUO_LARG-MURO_ESP, GAR_PROF, 0.10,
    "Corredor_Piso_Frente")

box(CASA_LARG, GAR_PROF, PLATO_Z,
    RECUO_LARG-MURO_ESP, SOB_PROF, 0.10,
    "Corredor_Piso_Fundos")

# ══════════════════════════════════════════════════════════════════════════════
# 4. GARAGEM — X: 0→CASA_LARG (4.90m), Y: 0→GAR_PROF (5m)
# ══════════════════════════════════════════════════════════════════════════════
box(0, 0, 0, CASA_LARG, GAR_PROF, 0.15, "Garagem_Piso")
box(0, 0, 0.15, PAREDE_ESP, GAR_PROF, GAR_PE, "Garagem_Parede_Esq")



# ══════════════════════════════════════════════════════════════════════════════
# 5. ESCADA LATERAL — no corredor direito
#    X: CASA_LARG → FRENTE-MURO_ESP  (1.35m de largura)
#    Y: GAR_PROF → GAR_PROF + 4.55m  (4.55m de comprimento)
#    Z: sobe de 0 até PLATO_Z (3.25m) em degraus
#
#    Cada degrau:
#      profundidade (piso): 4.55 / N_DEG  metros
#      altura (espelho):    PLATO_Z / N_DEG metros
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# 6. SOBRADO — X: 0→CASA_LARG (4.90m), Y: GAR_PROF→GAR_PROF+SOB_PROF
# ══════════════════════════════════════════════════════════════════════════════
Y0        = GAR_PROF
GOURMET_P = 4.000                        # profundidade da área gourmet (fundos)
Y_DIV     = Y0 + SOB_PROF - GOURMET_P   # Y da parede divisória cozinha/gourmet = 18.23m
Y_FUNDO   = Y0 + SOB_PROF               # Y do fundo do sobrado = 22.23m

# Laje de piso (plato) — toda a área do sobrado
box(0, Y0, PLATO_Z, CASA_LARG, SOB_PROF, LAJE_ESP, "Sobrado_Laje_Piso")

# ── 1º ANDAR ─────────────────────────────────────────────────────────────────
Z1 = PLATO_Z + LAJE_ESP

# Parede frontal (Y=5m) — largura toda
box(0, Y0,                    Z1, CASA_LARG,  PAREDE_ESP, PE_DIREITO, "Andar_1_Parede_Front")

# Parede esquerda (X=0) — toda a profundidade do sobrado
box(0, Y0,                    Z1, PAREDE_ESP, SOB_PROF,   PE_DIREITO, "Andar_1_Parede_Esq")

# Parede direita (X=4,90) — só até a divisória (cozinha), gourmet aberta
box(CASA_LARG-PAREDE_ESP, Y0, Z1, PAREDE_ESP, SOB_PROF-GOURMET_P, PE_DIREITO, "Andar_1_Parede_Dir")

# Parede divisória cozinha/gourmet (Y=18,23m) — largura toda
box(0, Y_DIV-PAREDE_ESP,      Z1, CASA_LARG,  PAREDE_ESP, PE_DIREITO, "Andar_1_Parede_Div")

# SEM parede de fundo (Y=22,23m) — área gourmet aberta
# SEM parede direita na área gourmet

# Laje topo 1º andar
box(0, Y0, Z1+PE_DIREITO, CASA_LARG, SOB_PROF, LAJE_ESP, "Laje_Andar1_Topo")

# ── 2º ANDAR ─────────────────────────────────────────────────────────────────
# Convenções:
#   Paredes no eixo X (correm em X): definidas por (x0, y_face, largura_x, espessura_y)
#   Paredes no eixo Y (correm em Y): definidas por (x_face, y0, espessura_x, comprimento_y)
#   Cantos: a parede que "fecha" o canto inclui a espessura; a outra para antes.
#   Regra adotada: paredes em Y incluem os cantos (esticam); paredes em X param na face interna.
#
# Coordenadas absolutas relevantes:
#   Y0   = 5,00   (frente sobrado)
#   Y_FUNDO = 22,23 (fundo sobrado)
#   BANHO_X_EXT = 2,26  (face externa Banho_Parede_Esq)
#   BANHO_X0    = 2,46  (face interna Banho_Parede_Esq)
#   BANHO_Y_FIM = 12,37 (fundo banheiro)

Z2 = PLATO_Z + LAJE_ESP + PE_DIREITO + LAJE_ESP

PORTA_LARG  = 0.900
PORTA_ALT   = 2.100

BANHO_X_EXT = CASA_LARG - PAREDE_ESP - 2.240 - PAREDE_ESP  # X=2,26
BANHO_X0    = CASA_LARG - PAREDE_ESP - 2.240               # X=2,46
BANHO_Y_FIM = Y0 + 4.870 + 2.500                           # Y=12,37

# ── Paredes externas do 2º andar ─────────────────────────────────────────────

# Parede frontal com porta de entrada da suíte (0,80x2,10) em X=1,28→2,08
# Trecho esquerdo: X=0→1,28
box(0,    Y0, Z2,  1.280,                  PAREDE_ESP, PE_DIREITO,  "Andar_2_Parede_Front_Esq")
# Trecho direito: X=2,08→4,90
box(2.080, Y0, Z2,  CASA_LARG-2.080,       PAREDE_ESP, PE_DIREITO,  "Andar_2_Parede_Front_Dir")
# Verga acima da porta: X=1,28→2,08, Z=porta até teto
box(1.280, Y0, Z2+2.100,  0.800, PAREDE_ESP, PE_DIREITO-2.100,     "Andar_2_Parede_Front_Verga")

# Parede fundo: X=0→4,90, Y=22,09→22,23
box(0, Y_FUNDO-PAREDE_ESP, Z2,  CASA_LARG, PAREDE_ESP, PE_DIREITO,  "Andar_2_Parede_Back")

# Parede esquerda A: X=0→0,14, Y=5,14→8,75  (após front, até Y875)
box(0, Y0+PAREDE_ESP, Z2,  PAREDE_ESP, 3.750-PAREDE_ESP, PE_DIREITO, "Andar_2_Parede_Esq_A")

# Parede esquerda B: X=0→0,14, Y=11,55→22,09  (após Y1161, até back)
# Y1161 termina em Y0+6.410+P = 11,41+0,14 = 11,55
box(0, Y0+6.410+PAREDE_ESP, Z2,  PAREDE_ESP, SOB_PROF-(6.410+PAREDE_ESP)-PAREDE_ESP, PE_DIREITO, "Andar_2_Parede_Esq_B")

# Parede direita A: X=4,76→4,90, Y=5,14→9,67  (após front, até face externa Y987)
# Y987 face externa = Y0+4,670
box(CASA_LARG-PAREDE_ESP, Y0+PAREDE_ESP, Z2,  PAREDE_ESP, 4.670-PAREDE_ESP, PE_DIREITO, "Andar_2_Parede_Dir_A")

# Parede direita B: X=4,76→4,90, Y=12,51→22,09  (após BanhoFundo, até back)
box(CASA_LARG-PAREDE_ESP, BANHO_Y_FIM+PAREDE_ESP, Z2, PAREDE_ESP, SOB_PROF-(4.670+PAREDE_ESP)-(2.500+PAREDE_ESP*2)-PAREDE_ESP, PE_DIREITO, "Andar_2_Parede_Dir_B")

# ── Paredes da suíte ─────────────────────────────────────────────────────────
# Parede esq da suíte = Andar_2_Parede_Esq_A

# Y875: X=0→1,14, Y=8,75→8,89  (corre em X, inclui canto esq, para antes de X114)
box(0, Y0+3.750, Z2,  1.140-PAREDE_ESP, PAREDE_ESP, PE_DIREITO, "Suite_Parede_Y875")

# X114: X=1,00→1,14, Y=8,89→11,41  (corre em Y, começa após Y875, para antes de Y1161)
box(1.140-PAREDE_ESP, Y0+3.750+PAREDE_ESP, Z2,  PAREDE_ESP, 2.660-PAREDE_ESP, PE_DIREITO, "Suite_Parede_X114")

# Y1161: X=1,14→2,38, Y=11,41→11,55  (corre em X, começa após X114, até face externa BanhoEsq)
box(1.140, Y0+6.410, Z2,  BANHO_X_EXT-1.140, PAREDE_ESP, PE_DIREITO, "Suite_Parede_Y1161")

# Y987: X=2,38→4,90, Y=9,67→9,81  (corre em X, inclui canto dir)
box(BANHO_X_EXT, Y0+4.670, Z2,  CASA_LARG-BANHO_X_EXT, PAREDE_ESP, PE_DIREITO, "Suite_Parede_Y987")

# BanhoEsq: X=2,38→2,52, Y=9,81→11,55  (corre em Y, começa após Y987, termina em Y1161)
# Com porta centralizada no vão interno Y=9,87→11,41 (comprimento interno = 1,54m)
PORTA_Y = Y0 + 4.670 + PAREDE_ESP + (1.540 - PORTA_LARG) / 2  # centralizada no vão interno
box(BANHO_X_EXT, Y0+4.670+PAREDE_ESP, Z2,  PAREDE_ESP, PORTA_Y-(Y0+4.670+PAREDE_ESP), PE_DIREITO, "Banho_Parede_Esq_Bot")
box(BANHO_X_EXT, PORTA_Y+PORTA_LARG,  Z2,  PAREDE_ESP, (Y0+6.410)-(PORTA_Y+PORTA_LARG), PE_DIREITO, "Banho_Parede_Esq_Top")
box(BANHO_X_EXT, PORTA_Y, Z2+PORTA_ALT,  PAREDE_ESP, PORTA_LARG, PE_DIREITO-PORTA_ALT, "Banho_Parede_Esq_Verga")

# BanhoFundo: X=2,38→4,90, Y=12,37→12,51
box(BANHO_X_EXT, BANHO_Y_FIM, Z2,  CASA_LARG-BANHO_X_EXT, PAREDE_ESP, PE_DIREITO, "Banho_Parede_Fundo")

# Laje topo 2º andar (cobertura)
box(0, Y0, Z2+PE_DIREITO, CASA_LARG, SOB_PROF, LAJE_ESP, "Laje_Andar2_Topo")

# ══════════════════════════════════════════════════════════════════════════════
# 7. Finalizar
# ══════════════════════════════════════════════════════════════════════════════
doc.recompute()

try:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass

print("Concluído!")
print(f"  Terreno   : {FRENTE}m frente | esq {TERRENO_ESQ}m | dir {TERRENO_DIR}m | fundo diagonal")
print(f"  Casa      : {CASA_LARG}m largura  |  corredor direito {RECUO_LARG}m  |  muro dir {MURO_ESP}m")
print(f"  Garagem   : {CASA_LARG} x {GAR_PROF} m | Z=0 (nível rua) | pé-direito {GAR_PE}m")
print(f"  Plato     : Z = {PLATO_Z} m")
print(f"  Sobrado   : {CASA_LARG} x {SOB_PROF} m | 2 andares | Y={GAR_PROF}→{GAR_PROF+SOB_PROF}m")
Z_topo = PLATO_Z + LAJE_ESP + 2*(PE_DIREITO + LAJE_ESP)
print(f"  Topo sobrado: Z = {Z_topo:.2f} m")
