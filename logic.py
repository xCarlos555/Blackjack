import random
import sys
import os


naipes = ['Copas', 'Ouros', 'Espadas', 'Paus']
valores = {'Ás': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, 
           '7': 7, '8': 8, '9': 9, '10': 10, 'Conde': 10, 'Dama': 10, 'Rei': 10}

def recurso_caminho(relativo):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relativo)
    
    return os.path.join(os.path.abspath("."), relativo)

def caminho_carta(carta):
    valor = carta['valor'].lower()
    naipe = carta['naipe'].lower()
    conversao = {'ás': 'as', 'conde': 'conde', 'dama': 'dama', 'rei': 'rei'}
    valor = conversao.get(valor, valor)

    return recurso_caminho(f"images/{naipe}_{valor}.png")

def distribuir_carta(baralho):
    carta = baralho.pop(random.randint(0, len(baralho) - 1))
    return carta
    
def calcular_pontos(mao):
    total = sum(c['pontos'] for c in mao)
    ases = sum(1 for c in mao if c['valor'] == 'Ás')

    while total > 21 and ases:
        total -= 10
        ases -= 1
    return total

def mostrar_botao(botao, mostrar=True):
    botao.disabled = not mostrar
    botao.opacity = 1 if mostrar else 0

def criar_baralho():
    baralho = [{'valor': v, 'naipe': s, 'pontos': valores[v]} for s in naipes for v in valores]
    return baralho

def nova_partida():
    baralho = criar_baralho()
    random.shuffle(baralho)
    return baralho

def dealer_joga(baralho, mao):
    while calcular_pontos(mao) < 17:
        mao.append(distribuir_carta(baralho))
    return mao

def determinar_resultado(jogador, dealer):
    pontos_jogador = calcular_pontos(jogador)
    pontos_dealer = calcular_pontos(dealer)

    if pontos_jogador > 21:
        return "BUST! Dealer WINS"
    elif pontos_dealer > 21:
        return "BUST! Player WINS"
    elif pontos_jogador > pontos_dealer:
        return "Player WINS!"
    elif pontos_jogador < pontos_dealer:
        return "Dealer WINS!"
    else:
        return "DRAW"

def guardar_pontuacao(store, nome, pontos):
    if not nome:
        return
    
    if store.exists(nome):
        pontos_anteriores = store.get(nome)['pontos']
        if pontos > pontos_anteriores:
            store.put(nome, pontos=pontos)
    else:
        store.put(nome, pontos=pontos)

def avaliar_mao_jogador(mao_jogador, mao_dealer):
    pj = calcular_pontos(mao_jogador)
    pd = calcular_pontos(mao_dealer)

    if pd > 21:
        if pj > 21:
            return "DEALER WINS"
        else:
            return "PLAYER WINS"

    if pj > 21:
        return "DEALER WINS"
    elif pj > pd:
        return "PLAYER WINS"
    elif pj < pd:
        return "DEALER WINS"
    return "DRAW"
