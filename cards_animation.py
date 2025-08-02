from kivy.uix.image import Image
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.animation import Animation
from kivy.clock import Clock
from logic import caminho_carta, distribuir_carta, calcular_pontos, guardar_pontuacao, determinar_resultado, mostrar_botao, avaliar_mao_jogador


class Cards:
    def __init__(self, app):
        self.app = app

    def animar_adicao_carta(self, carta, x_offset, y_destino, rotacionar=False, dono='jogador'):
        som_atual = self.app.sons_deal[self.app.indice_som]
        if som_atual:
            som_atual.stop()
            som_atual.play()
        self.app.indice_som = (self.app.indice_som + 1) % len(self.app.sons_deal)

        img_path = caminho_carta(carta)
        carta_img = Image(source=img_path, size_hint=(.15, .25), pos_hint={"x": x_offset, "y": 1.2}, opacity=0)

        if rotacionar:
            with carta_img.canvas.before:
                PushMatrix()
                carta_img.rotation = Rotate(angle=90, origin=carta_img.center)
            with carta_img.canvas.after:
                PopMatrix()

            def atualizar_origem(*args):
                carta_img.rotation.origin = carta_img.center
            carta_img.bind(pos=atualizar_origem, size=atualizar_origem)

        self.app.root.add_widget(carta_img)

        if dono == 'dealer':
            self.app.cards_dealer.append(carta_img)
        else:
            self.app.cards_jogador.append(carta_img)

        anim = Animation(opacity=1, duration=0.2) + Animation(pos_hint={"x": x_offset, "y": y_destino}, duration=0.3)
        anim.bind(on_complete=self.app.pontuacao.atualizar_pontos)
        anim.start(carta_img)

    def dar_primeira_jogador(self, dt):
        carta = distribuir_carta(self.app.baralho_atual)
        # carta = {'valor': '6', 'naipe': 'Espadas', 'pontos': 6}
        self.app.mao_jogador.append(carta)
        x_offset = 0.32 + (len(self.app.mao_jogador) - 1) * 0.04
        self.animar_adicao_carta(carta, x_offset, 0.3, dono='jogador')
        
        Clock.schedule_once(self.dar_primeira_dealer, 1.0)

    def dar_primeira_dealer(self, dt):
        carta = distribuir_carta(self.app.baralho_atual)
        self.app.mao_dealer.append(carta)
        x_offset = 0.32 + (len(self.app.mao_dealer) - 1) * 0.04
        self.animar_adicao_carta(carta, x_offset, 0.6, dono='dealer')
        
        Clock.schedule_once(self.dar_segunda_jogador, 1.0)

    def dar_segunda_jogador(self, dt):
        carta = distribuir_carta(self.app.baralho_atual)
        self.app.mao_jogador.append(carta)
        x_offset = 0.32 + (len(self.app.mao_jogador) - 1) * 0.04
        self.animar_adicao_carta(carta, x_offset, 0.3, dono='jogador')
        
        Clock.schedule_once(self.dar_segunda_dealer, 1.0)

    def dar_segunda_dealer(self, dt):
        carta = distribuir_carta(self.app.baralho_atual)
        self.app.mao_dealer.append(carta)
        x_offset = 0.32 + (len(self.app.mao_dealer) - 1) * 0.04
        self.app.dealer_segunda_carta_img = Image(source=self.app.verso_path, 
                                                size_hint=(.15, .25), pos_hint={"x": x_offset, "y": 0.6})
        self.app.root.add_widget(self.app.dealer_segunda_carta_img)
        self.app.cards_on_table.append(self.app.dealer_segunda_carta_img)

        self.app.pontuacao.atualizar_pontos()

        if calcular_pontos(self.app.mao_jogador) == 21:
            ganho = int(self.app.valor_apostado * 2.5)
            self.app.dinheiro_jogador += ganho
            self.app.label_dinheiro.text = f"Cash: {self.app.dinheiro_jogador}€"
            self.app.label_resultado.text = "BLACKJACK! PLAYER WINS!"
            self.app.desativar_botoes()

            if self.app.som_blackjack:
                self.app.som_blackjack.stop()
                self.app.som_blackjack.play()

            guardar_pontuacao(self.app.store, self.app.nome_jogador, self.app.dinheiro_jogador)

        if self.app.label_resultado.text != "BLACKJACK! PLAYER WINS!" and self.app.mao_dealer\
                and self.app.mao_dealer[0]['valor'].lower() == 'ás' and \
                    self.app.dinheiro_jogador >= self.app.valor_apostado // 2:
            self.app.label_pay_insurance.text = "Pay Insurance?"
            mostrar_botao(self.app.botao_insurance_sim, True)
            mostrar_botao(self.app.botao_insurance_nao, True)
            mostrar_botao(self.app.botao_novo_jogo, False)
            mostrar_botao(self.app.botao_hit, False)
            mostrar_botao(self.app.botao_stand, False)
            mostrar_botao(self.app.botao_double, False)
            self.app.label_resultado.text = "Dealer has Ace.\nPay Insurance?"
        else:
            if len(self.app.mao_jogador) == 2 \
                    and self.app.mao_jogador[0]['valor'] == self.app.mao_jogador[1]['valor']:
                mostrar_botao(self.app.botao_split, True)

        if self.app.insurance_ativado == False and self.app.label_resultado.text != "BLACKJACK! PLAYER WINS!"\
            and self.app.label_resultado.text != "Dealer has Ace.\nPay Insurance?":
            mostrar_botao(self.app.botao_hit, True)
            mostrar_botao(self.app.botao_stand, True)

            if not self.app.hit_feito_mao_normal:
                mostrar_botao(self.app.botao_double, True)
            else:
                mostrar_botao(self.app.botao_double, False)

    def animacao_dealer(self):
        pontos_dealer = calcular_pontos(self.app.mao_dealer)

        if pontos_dealer < 17:
            carta = distribuir_carta(self.app.baralho_atual)
            self.app.mao_dealer.append(carta)
            x_offset = 0.32 + (len(self.app.mao_dealer) - 1) * 0.04
            self.animar_adicao_carta(carta, x_offset, 0.6, dono='dealer')
            Clock.schedule_once(lambda dt: self.animacao_dealer(), 1.2)
        else:
            total_ganho = 0
            mensagens = []

            if self.app.split_ativo:
                for idx, mao in enumerate([self.app.mao_split_1, self.app.mao_split_2], start=0):
                    aposta_mao = self.app.aposta_split_1 if idx == 0 else self.app.aposta_split_2
                    resultado = avaliar_mao_jogador(mao, self.app.mao_dealer)

                    if "PLAYER WINS" in resultado:
                        total_ganho += aposta_mao * 2
                        mensagens.append(f"Hand {idx + 1}: WIN")
                    elif "DRAW" in resultado:
                        total_ganho += aposta_mao
                        mensagens.append(f"Hand {idx + 1}: DRAW")
                    else:
                        mensagens.append(f"Hand {idx + 1}: LOSE")
            else:
                resultado = determinar_resultado(self.app.mao_jogador, self.app.mao_dealer).upper()
                if "PLAYER WINS" in resultado:
                    total_ganho += self.app.valor_apostado * 2
                    mensagens.append("WIN")
                    if self.app.som_vitoria:
                        self.app.som_vitoria.stop()
                        self.app.som_vitoria.play()
                elif "DRAW" in resultado:
                    total_ganho += self.app.valor_apostado
                    mensagens.append("DRAW")
                    if self.app.som_empate:
                        self.app.som_empate.stop()
                        self.app.som_empate.play()
                else:
                    mensagens.append("LOSE")
                    if self.app.som_derrota:
                        self.app.som_derrota.stop()
                        self.app.som_derrota.play()

            self.app.dinheiro_jogador += total_ganho
            self.app.label_dinheiro.text = f"Cash: {self.app.dinheiro_jogador}€"
            self.app.label_resultado.text = "   |   ".join(mensagens)
            self.app.desativar_botoes()
            guardar_pontuacao(self.app.store, self.app.nome_jogador, self.app.dinheiro_jogador)

    
    def verificar_blackjack_dealer(self):
        pontos = calcular_pontos(self.app.mao_dealer)
        if pontos == 21:
            self.revelar_carta_dealer(None)
            if self.app.insurance_ativado:
                ganho = self.app.valor_insurance * 2
                self.app.dinheiro_jogador += ganho
            self.app.label_dinheiro.text = f"Cash: {self.app.dinheiro_jogador}€"
            self.app.desativar_botoes()
            guardar_pontuacao(self.app.store, self.app.nome_jogador, self.app.dinheiro_jogador)
        else:
            self.app.label_resultado.text = "Dealer has no Blackjack\nInsurance lost!"
            self.app.label_dinheiro.text = f"Cash: {self.app.dinheiro_jogador}€"
            if len(self.app.mao_jogador) == 2 and \
                    self.app.mao_jogador[0]['valor'] == self.app.mao_jogador[1]['valor']:
                mostrar_botao(self.app.botao_split, True)
    
    def revelar_carta_dealer(self, instance):
        if self.app.mostrar_segunda_carta:
            return

        self.app.mostrar_segunda_carta = True

        if self.app.dealer_segunda_carta_img:
            anim = Animation(opacity=0, duration=0.3)

            def trocar_para_carta_real(animation, widget):
                nova_path = caminho_carta(self.app.mao_dealer[1])
                widget.source = nova_path
                Animation(opacity=1, duration=0.3).start(widget)
                self.app.pontuacao.atualizar_pontos()
                Clock.schedule_once(lambda dt: self.animacao_dealer(), 1.0)

            anim.bind(on_complete=trocar_para_carta_real)
            anim.start(self.app.dealer_segunda_carta_img)
        else:
            self.app.pontuacao.atualizar_pontos()
            Clock.schedule_once(lambda dt: self.animacao_dealer(), 1.0)
