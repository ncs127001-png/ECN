# Reimprimir de forma compacta y robusta las capas resultantes
import numpy as np

M13 = np.zeros((13, 13), dtype=int)
c = 6
M13[c-1:c+2, c-1:c+2] = [[7, 8, 9], [4, 5, 6], [1, 2, 3]]

def expandir(matriz, ka, kn):
    oa = (13 - ka) // 2
    on = (13 - kn) // 2
    sub = matriz[oa:oa+ka, oa:oa+ka]
    for i in range(ka):
        sf = int(np.sum(sub[i, :]))
        matriz[oa+i, oa+ka] = sf
        matriz[oa+i, oa-1] = sf
    for j in range(ka):
        sc = int(np.sum(sub[:, j]))
        matriz[oa+ka, oa+j] = sc
        matriz[oa-1, oa+j] = sc
    dp = int(np.trace(sub))
    ds = int(np.trace(np.fliplr(sub)))
    matriz[on, on] = ds
    matriz[on, on+kn-1] = dp
    matriz[on+kn-1, on] = dp
    matriz[on+kn-1, on+kn-1] = ds

for k_ant, k_nue in [(3, 5), (5, 7), (7, 9), (9, 11), (11, 13)]:
    expandir(M13, k_ant, k_nue)

# Imprimir sólo el perímetro final 13x13 y los vectores clave para no saturar
print("Esquinas del Anillo Negro (13x13):")
print(f"Sup.Izq: {M13[0,0]} | Sup.Der: {M13[0,12]} | Inf.Izq: {M13[12,0]} | Inf.Der: {M13[12,12]}")
print("\nFila Superior Completa (Anillo 5):")
print(M13[0, :])
