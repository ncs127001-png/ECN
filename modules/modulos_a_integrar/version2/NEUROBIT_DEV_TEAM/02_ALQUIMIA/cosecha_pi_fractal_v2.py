#!/usr/bin/env python3
import os

def pi_digit_generator():
    k, a, b, a1, b1 = 2, 4, 1, 12, 4
    while True:
        p, q, k = k * k, 2 * k + 1, k + 1
        a, b, a1, b1 = a1, b1, p * a + q * a1, p * b + q * b1
        d, d1 = a // b, a1 // b1
        while d == d1:
            yield int(d)
            a, a1 = 10 * (a % b), 10 * (a1 % b1)
            d, d1 = a // b, a1 // b1

def teosophic_reduce(n):
    if n == 0: return 0
    while n > 9:
        n = sum(int(digit) for digit in str(n))
    return n

def cosecha_pi_genesis(max_muestras=5, bits_counter=13):
    max_counter = (2 ** bits_counter) - 1
    os.makedirs("cosecha_pi", exist_ok=True)
    print("🌌 Iniciando Cosecha Fractal de Pi (v2 - Génesis Puro)...")
    for muestra_actual in range(1, max_muestras + 1):
        filename = f"cosecha_pi/Cosecha_PI_muestra_{muestra_actual}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            print(f"📂 Purificando y abriendo: {filename}")
            pi_stream = pi_digit_generator()
            next(pi_stream) 
            a = next(pi_stream); b = next(pi_stream); nxt = next(pi_stream)
            counter = 1
            while counter <= max_counter:
                red = teosophic_reduce(a + b + nxt)
                f.write(f"{counter:013b} | {a},{b},{nxt} | red.{red}\n")
                a = b; b = nxt; nxt = next(pi_stream)
                counter += 1
        print(f"✅ Muestra {muestra_actual} completada.")
    print("🕊️ Gran Obra completada.")

if __name__ == "__main__":
    cosecha_pi_genesis()
