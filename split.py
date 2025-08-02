from kivy.clock import Clock
from cards_animation import Cards
from logic import distribuir_carta, calcular_pontos, mostrar_botao


class Split:
    def __init__(self, app):
        self.app = app
        self.cards = Cards(app)

    def realizar_split(self, instance):
        self.app.hit_feito_split1 = False
        self.app.hit_feito_split2 = False

        if self.app.dinheiro_jogador < self.app.valor_apostado:
            self.app.label_resultado.text = "Not enough money to split"
            return
        
        self.app.label_pontos_jogador.text = ""

        self.app.dinheiro_jogador -= self.app.valor_apostado
        self.app.label_dinheiro.text = f"Cash: {self.app.dinheiro_jogador}€"

        self.app.split_ativo = True
        self.app.aposta_split_1 = self.app.valor_apostado
        self.app.aposta_split_2 = self.app.valor_apostado

        self.app.mao_split_1 = [self.app.mao_jogador[0]]
        self.app.mao_split_2 = [self.app.mao_jogador[1]]
        self.app.mao_atual = 'split1'

        mostrar_botao(self.app.botao_split, False)

        self.atualizar_cartas_split()

        Clock.schedule_once(lambda dt: self.comprar_para_split('split1'), 0.5)

        self.app.mao_atual = 'split1'

    def atualizar_cartas_split(self):
        for img in self.app.cards_jogador:
            self.app.root.remove_widget(img)
        self.app.cards_jogador.clear()

        x_offset = 0.2
        for carta in self.app.mao_split_1:
            self.cards.animar_adicao_carta(carta, x_offset, 0.3, dono='jogador')
            x_offset += 0.04

        x_offset = 0.55
        for carta in self.app.mao_split_2:
            self.cards.animar_adicao_carta(carta, x_offset, 0.3, dono='jogador')
            x_offset += 0.04

    def comprar_para_split(self, mao):
        nova_carta = distribuir_carta(self.app.baralho_atual)
        if mao == 'split1':
            self.app.mao_split_1.append(nova_carta)
            self.app.hit_feito_split1 = True
            x_offset = 0.2 + (len(self.app.mao_split_1) - 1) * 0.04
            self.cards.animar_adicao_carta(nova_carta, x_offset, 0.3)

            if len(self.app.mao_split_1) == 2:
                mostrar_botao(self.app.botao_double, True)
            else:
                mostrar_botao(self.app.botao_double, False)
        else:
            self.app.mao_split_2.append(nova_carta)
            self.app.hit_feito_split2 = True
            x_offset = 0.55 + (len(self.app.mao_split_2) - 1) * 0.04
            self.cards.animar_adicao_carta(nova_carta, x_offset, 0.3)

            if len(self.app.mao_split_2) == 2:
                mostrar_botao(self.app.botao_double, True)
            else:
                mostrar_botao(self.app.botao_double, False)

        self.atualizar_pontos_split()

        pontos = calcular_pontos(self.app.mao_split_1 if mao == 'split1' else self.app.mao_split_2)
       
        if pontos > 21:
            self.app.label_resultado.text = f"BUST! Hand {mao[-1]} lost"
            if self.app.som_derrota:
                self.app.som_derrota.stop()
                self.app.som_derrota.play()
            Clock.schedule_once(lambda dt: self.proxima_mao_split(), 0.5)

    def atualizar_pontos_split(self):
        if self.app.mao_atual == 'split1':
            pontos = calcular_pontos(self.app.mao_split_1)
            self.app.label_pontos_split1.text = f"({pontos})"
        elif self.app.mao_atual == 'split2':
            pontos = calcular_pontos(self.app.mao_split_2)
            self.app.label_pontos_split2.text = f"({pontos})"

    def proxima_mao_split(self):
        if self.app.mao_atual == 'split1':
            self.app.mao_atual = 'split2'

            mostrar_botao(self.app.botao_hit, True)
            mostrar_botao(self.app.botao_stand, True)

            if not self.app.hit_feito_split2:
                mostrar_botao(self.app.botao_double, True)
            else:
                mostrar_botao(self.app.botao_double, False)

            self.comprar_para_split('split2')
        else:
            pontos1 = calcular_pontos(self.app.mao_split_1)
            pontos2 = calcular_pontos(self.app.mao_split_2)

            if pontos1 > 21 and pontos2 > 21:
                self.app.label_resultado.text = "BUST! Both hands lost"
                if self.app.som_derrota:
                    self.app.som_derrota.stop()
                    self.app.som_derrota.play()
                self.app.desativar_botoes()
            else:
                self.cards.revelar_carta_dealer(None)
                mostrar_botao(self.app.botao_stand, False)
                mostrar_botao(self.app.botao_novo_jogo, False)
