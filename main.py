import sys
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.core.audio import SoundLoader
from split import Split
from pontuacao import Pontuacao
from cards_animation import Cards
from logic import nova_partida, distribuir_carta, calcular_pontos, determinar_resultado, recurso_caminho, mostrar_botao


class BlackjackApp(App):
    def build(self):
        self.root = FloatLayout()

        self.split = Split(self)
        self.pontuacao = Pontuacao(self)
        self.cards = Cards(self)

        self.cards_jogador = []
        self.cards_dealer = []

        self.mao_split_1 = []
        self.mao_split_2 = []
        self.mao_atual = None
        self.split_ativo = False

        self.hit_feito_mao_normal = False
        self.hit_feito_split1 = False
        self.hit_feito_split2 = False

        self.aposta_split_1 = 0
        self.aposta_split_2 = 0

        self.cards_on_table = []

        self.store = JsonStore("pontos.json")

        self.indice_som = 0
        self.sons_deal = [SoundLoader.load(recurso_caminho('sounds/deal1.wav')),
                          SoundLoader.load(recurso_caminho('sounds/deal2.wav')),
                          SoundLoader.load(recurso_caminho('sounds/deal3.wav'))]
        
        self.som_blackjack = SoundLoader.load(recurso_caminho('sounds/blackjack.wav'))
        self.som_empate = SoundLoader.load(recurso_caminho('sounds/draw.wav'))
        self.som_vitoria = SoundLoader.load(recurso_caminho('sounds/win.wav'))
        self.som_derrota = SoundLoader.load(recurso_caminho('sounds/lose.wav'))
        
        self.musica_fundo = SoundLoader.load(recurso_caminho('sounds/background.wav'))
        if self.musica_fundo:
            self.musica_fundo.loop = True
            self.musica_fundo.play()

        self.mao_jogador = []
        self.mao_dealer = []
        self.baralho_atual = []
        self.cards_on_table = []
        self.dinheiro_jogador = 1000
        self.valor_apostado = 0
        self.valor_insurance = 0
        self.insurance_ativado = False
        self.mostrar_segunda_carta = False
        self.dealer_segunda_carta_img = None

        self.mesa_path = recurso_caminho("images/blackjk.png")
        self.hit_path = recurso_caminho("images/hit.png")
        self.stand_path = recurso_caminho("images/stand.png")
        self.split_path = recurso_caminho("images/split.png")
        self.double_path = recurso_caminho("images/double.png")
        self.newgame_path = recurso_caminho("images/newgame.png")
        self.checkbt = recurso_caminho("images/checkBT.png")
        self.verso_path = recurso_caminho("images/verso.png")
        self.yes = recurso_caminho("images/yes.png")
        self.no = recurso_caminho("images/no.png")

        Window.clearcolor = (0, 0.4, 0, 1)

        self.bg = Image(
            source=self.mesa_path,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
            allow_stretch=True,
            keep_ratio=False
        )
        self.root.add_widget(self.bg)

        self.label_dinheiro = Label(
            text=f"Cash: {self.dinheiro_jogador}€", size_hint=(.35, .07), 
            pos_hint={"x": .70, "y": .91}, color=(1, 1, 1, 1), bold=True, font_size='22sp',
            halign="center", valign="middle"
        )
        self.label_dinheiro.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.label_resultado = Label(
            text="", size_hint=(.4, .1),
            pos_hint={"x": .3, "y": .88}, color=(1, 1, 0, 1), font_size='20sp',
            halign="center", valign="middle"
        )
        self.label_resultado.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.label_pontos_jogador = Label(
            text="", size_hint=(.3, .1),
            pos_hint={"x": .1, "y": .40}, color=(1, 1, 1, 1), font_size='40sp',
            halign="center", valign="middle"
        )
        self.label_pontos_jogador.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.label_pontos_dealer = Label(
            text="", size_hint=(.3, .1),
            pos_hint={"x": .1, "y": .70}, color=(1, 1, 1, 1), font_size='40sp',
            halign="center", valign="middle"
        )
        self.label_pontos_dealer.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.label_pay_insurance = Label(
            text="", size_hint=(.3, .1),
            pos_hint={"x": .76, "y": .66}, color=(1, 1, 0, 1), bold=True, font_size='20sp',
            halign="center", valign="middle"
        )
        self.label_pay_insurance.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.label_pontos_split1 = Label(
            text="", size_hint=(.3, .1),
            pos_hint={"x": .03, "y": .40}, color=(1, 1, 1, 1), font_size='40sp',
            halign="center", valign="middle"
        )
        self.label_pontos_split1.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.label_pontos_split2 = Label(
            text="", size_hint=(.3, .1),
            pos_hint={"x": .38, "y": .40}, color=(1, 1, 1, 1), font_size='40sp',
            halign="center", valign="middle"
        )
        self.label_pontos_split2.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))


        self.aposta_input = TextInput(
            hint_text="Bet €", multiline=False,
            size_hint=(.15, .07), pos_hint={"x": .75, "y": .81},
            font_size='18sp', background_color=(0, 0.3, 0, 0.8),
            foreground_color=(1, 1, 0.8, 1), cursor_color=(1, 1, 1, 1),
            hint_text_color=(1, 1, 1, 0.5), padding=(10, 10)
        )

        self.nome_input = TextInput(
            hint_text="Player Name", multiline=False,
            size_hint=(.15, .07), pos_hint={"x": .1, "y": .81},
            font_size='18sp', background_color=(0, 0.3, 0, 0.8),
            foreground_color=(1, 1, 0.8, 1), cursor_color=(1, 1, 1, 1),
            hint_text_color=(1, 1, 1, 0.5), padding=(10, 10)
        )

        self.botao_sair = Button(text="Exit", size_hint=(.1, .1), pos_hint={"x": .8, "y": .45},
                                background_color=(0, 0.3, 0, 0.8), color=(1, 1, 1, 1),
                                font_size='30sp', on_press=self.fechar_app)
        self.botao_novo_jogo = Button(background_normal=self.newgame_path, background_down=self.newgame_path,
                                      border=(0, 0, 0, 0), size_hint=(.3, .1), pos_hint={"center_x": 0.5, "y": .01}, 
                                      on_press=self.iniciar_jogo)
        self.botao_hit = Button(background_normal=self.hit_path, background_down=self.hit_path,
                                border=(0, 0, 0, 0), size_hint=(.25, .1), pos_hint={"x": .05, "y": .18},
                                on_press=self.hit_pressed, disabled=True)
        self.botao_stand = Button(background_normal=self.stand_path, background_down=self.stand_path,
                                  border=(0, 0, 0, 0), size_hint=(.25, .1), pos_hint={"x": .7, "y": .18},
                                  on_press=self.stand_pressed, disabled=True)
        self.botao_double = Button(background_normal=self.double_path, background_down=self.double_path,
                                   border=(0, 0, 0, 0), size_hint=(.25, .1), pos_hint={"center_x": 0.5, "y": .18},
                                   on_press=self.double_down_pressed, disabled=True)
        self.botao_insurance_sim = Button(background_normal=self.yes, background_down=self.yes, border=(0, 0, 0, 0),
                                          size_hint=(.05, .08), pos_hint={"x": .88, "y": .60}, 
                                          disabled=True, on_press=self.ativar_insurance)
        self.botao_insurance_nao = Button(background_normal=self.no, background_down=self.no, border=(0, 0, 0, 0),
                                          size_hint=(.05, .08), pos_hint={"x": .88, "y": .50}, 
                                          disabled=True, on_press=self.rejeitar_insurance)
        self.botao_mostrar_pontuacoes = Button(background_normal=self.checkbt, background_down=self.checkbt,
                                                size_hint=(.2, .1), border=(0, 0, 0, 0), pos_hint={"x": .78, "y": .01}, 
                                                on_press=self.pontuacao.mostrar_pontuacoes)
        self.botao_split = Button(background_normal=self.split_path, background_down=self.split_path,
                                  border=(0, 0, 0, 0), size_hint=(.25, .1), pos_hint={"x": .05, "y": .01},
                                    on_press=self.split.realizar_split, disabled=True)

        self.botao_sair.opacity = 0
        self.botao_sair.disabled = True
        self.botao_novo_jogo.opacity = 1
        self.botao_hit.opacity = 0
        self.botao_stand.opacity = 0
        self.botao_double.opacity = 0
        self.botao_insurance_sim.opacity = 0
        self.botao_insurance_nao.opacity = 0
        self.botao_split.opacity = 0

        self.root.add_widget(self.botao_sair)
        self.root.add_widget(self.label_pontos_split1)
        self.root.add_widget(self.label_pontos_split2)
        self.root.add_widget(self.botao_split)
        self.root.add_widget(self.nome_input)
        self.root.add_widget(self.botao_mostrar_pontuacoes)
        self.root.add_widget(self.label_dinheiro)
        self.root.add_widget(self.label_resultado)
        self.root.add_widget(self.label_pontos_jogador)
        self.root.add_widget(self.label_pontos_dealer)
        self.root.add_widget(self.aposta_input)
        self.root.add_widget(self.botao_novo_jogo)
        self.root.add_widget(self.botao_hit)
        self.root.add_widget(self.botao_stand)
        self.root.add_widget(self.botao_double)
        self.root.add_widget(self.label_pay_insurance)
        self.root.add_widget(self.botao_insurance_sim)
        self.root.add_widget(self.botao_insurance_nao)

        return self.root

    def _update_rect(self, instance, value):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size

    def desativar_botoes(self):
        mostrar_botao(self.botao_hit, False)
        mostrar_botao(self.botao_stand, False)
        mostrar_botao(self.botao_double, False)
        mostrar_botao(self.botao_split, False)
        mostrar_botao(self.botao_novo_jogo, True)
        mostrar_botao(self.botao_insurance_sim, False)
        mostrar_botao(self.botao_insurance_nao, False)

    def hit_pressed(self, instance):
        mostrar_botao(self.botao_split, False)

        mao = (
            self.mao_split_1 if self.split_ativo and self.mao_atual == 'split1'
            else self.mao_split_2 if self.split_ativo
            else self.mao_jogador
        )

        if self.split_ativo:
            nova_carta = distribuir_carta(self.baralho_atual)
            mao.append(nova_carta)

            if self.mao_atual == 'split1':
                self.hit_feito_split1 = True
            else:
                self.hit_feito_split2 = True

            mostrar_botao(self.botao_double, False)

            x_offset_base = 0.2 if self.mao_atual == 'split1' else 0.55
            x_offset = x_offset_base + (len(mao) - 1) * 0.04
            self.cards.animar_adicao_carta(nova_carta, x_offset, 0.3)

            self.split.atualizar_pontos_split()

            pontos = calcular_pontos(mao)

            if pontos > 21:
                self.label_resultado.text = f"BUST! Hand {self.mao_atual[-1]} lost"
                if self.som_derrota:
                    self.som_derrota.stop()
                    self.som_derrota.play()
                self.split.proxima_mao_split()
            elif pontos == 21:
                self.stand_pressed(None)
        else:
            nova_carta = distribuir_carta(self.baralho_atual)
            self.mao_jogador.append(nova_carta)

            self.hit_feito_mao_normal = True
            mostrar_botao(self.botao_double, False)

            x_offset = 0.32 + (len(self.mao_jogador) - 1) * 0.04
            self.cards.animar_adicao_carta(nova_carta, x_offset, 0.3)
            self.pontuacao.atualizar_pontos()

            pontos = calcular_pontos(self.mao_jogador)

            if pontos > 21:
                resultado = determinar_resultado(self.mao_jogador, self.mao_dealer)
                self.label_resultado.text = resultado
                if self.som_derrota:
                    self.som_derrota.stop()
                    self.som_derrota.play()
                self.desativar_botoes()
            elif pontos == 21:
                self.stand_pressed(None)

    def stand_pressed(self, instance):
        mostrar_botao(self.botao_split, False)
        mostrar_botao(self.botao_hit, False)
        mostrar_botao(self.botao_stand, False)
        mostrar_botao(self.botao_double, False)
        mostrar_botao(self.botao_split, False)

        if self.split_ativo:
            self.split.proxima_mao_split()
        else:
            self.cards.revelar_carta_dealer(instance)
            mostrar_botao(self.botao_novo_jogo, False)

    def double_down_pressed(self, instance):
        mostrar_botao(self.botao_split, False)

        mao = (
            self.mao_split_1 if self.split_ativo and self.mao_atual == 'split1'
            else self.mao_split_2 if self.split_ativo
            else self.mao_jogador
        )

        if self.split_ativo:
            mao_ativa = mao
            aposta_mao = self.aposta_split_1 if self.mao_atual == 'split1' else self.aposta_split_2

            if self.dinheiro_jogador < aposta_mao:
                self.label_resultado.text = "Not enough money to double down"
                return
            
            self.dinheiro_jogador -= aposta_mao
            self.label_dinheiro.text = f"Cash: {self.dinheiro_jogador}€"
            aposta_mao *= 2

            if self.mao_atual == 'split1':
                self.aposta_split_1 = aposta_mao
            else:
                self.aposta_split_2 = aposta_mao

            nova_carta = distribuir_carta(self.baralho_atual)
            mao_ativa.append(nova_carta)

            x_offset_base = 0.2 if self.mao_atual == 'split1' else 0.55
            x_offset = x_offset_base + (len(mao_ativa) - 1) * 0.04
            self.cards.animar_adicao_carta(nova_carta, x_offset, 0.3)

            self.split.atualizar_pontos_split()

            mostrar_botao(self.botao_hit, False)
            mostrar_botao(self.botao_stand, False)
            mostrar_botao(self.botao_double, False)
            mostrar_botao(self.botao_novo_jogo, False)

            pontos = calcular_pontos(mao_ativa)

            if pontos > 21:
                self.label_resultado.text = f"BUST! Hand {self.mao_atual[-1]} lost"
                if self.som_derrota:
                    self.som_derrota.stop()
                    self.som_derrota.play()
                self.split.proxima_mao_split()
            else:
                if self.mao_atual == 'split1':
                    self.mao_atual = 'split2'
                    mostrar_botao(self.botao_hit, True)
                    mostrar_botao(self.botao_stand, True)
                    Clock.schedule_once(lambda dt: self.split.comprar_para_split('split2'), 0.5)  
                else:
                    Clock.schedule_once(self.cards.revelar_carta_dealer, 1.0)
        else:
            if self.dinheiro_jogador < self.valor_apostado:
                self.label_resultado.text = "No money to double down"
                return

            self.label_resultado.text = ""
            self.dinheiro_jogador -= self.valor_apostado
            self.valor_apostado *= 2
            self.label_dinheiro.text = f"Cash: {self.dinheiro_jogador}€"

            carta = distribuir_carta(self.baralho_atual)
            self.mao_jogador.append(carta)

            x_offset = 0.33 + (len(self.mao_jogador) - 1) * 0.04
            self.cards.animar_adicao_carta(carta, x_offset, 0.28, rotacionar=True)

            self.pontuacao.atualizar_pontos()

            mostrar_botao(self.botao_hit, False)
            mostrar_botao(self.botao_stand, False)
            mostrar_botao(self.botao_double, False)
            mostrar_botao(self.botao_novo_jogo, False)

            pontos = calcular_pontos(self.mao_jogador)

            if pontos > 21:
                resultado = determinar_resultado(self.mao_jogador, self.mao_dealer)
                self.label_resultado.text = resultado

                if self.som_derrota:
                    self.som_derrota.stop()
                    self.som_derrota.play()

                self.desativar_botoes()
            else:
                Clock.schedule_once(self.cards.revelar_carta_dealer, 1.0)

    def ativar_insurance(self, instance):
        self.valor_insurance = self.valor_apostado // 2
        self.dinheiro_jogador -= self.valor_insurance
        self.label_dinheiro.text = f"Cash: {self.dinheiro_jogador}€"
        self.insurance_ativado = True
        mostrar_botao(self.botao_insurance_sim, False)
        mostrar_botao(self.botao_insurance_nao, False)
        mostrar_botao(self.botao_hit, True)
        mostrar_botao(self.botao_stand, True)
        mostrar_botao(self.botao_double, True)
        self.label_pay_insurance.text = ""
        self.label_resultado.text = ""
        self.cards.verificar_blackjack_dealer()

    def rejeitar_insurance(self, instance):
        self.insurance_ativado = False
        mostrar_botao(self.botao_insurance_sim, False)
        mostrar_botao(self.botao_insurance_nao, False)
        mostrar_botao(self.botao_hit, True)
        mostrar_botao(self.botao_stand, True)
        mostrar_botao(self.botao_double, True)
        self.label_pay_insurance.text = ""
        self.label_resultado.text = ""
        if len(self.mao_jogador) == 2 and self.mao_jogador[0]['valor'] == self.mao_jogador[1]['valor']:
            mostrar_botao(self.botao_split, True)

    def iniciar_jogo(self, instance):
        self.nome_jogador = self.nome_input.text.strip()

        if self.verificar_dinheiro():
            return

        if not self.nome_jogador:
            self.label_resultado.text = "No player name"
            return

        try:
            aposta = int(self.aposta_input.text)
        except ValueError:
            self.label_resultado.text = "Invalid bet"
            return

        if aposta <= 0 or aposta > self.dinheiro_jogador:
            self.label_resultado.text = "Invalid bet"
            return
        
        self.label_pontos_split1.text = ""
        self.label_pontos_split2.text = ""

        for img in self.cards_jogador:
            self.root.remove_widget(img)
        self.cards_jogador.clear()

        for img in self.cards_dealer:
            self.root.remove_widget(img)
        self.cards_dealer.clear()

        for img in self.cards_on_table:
            self.root.remove_widget(img)
        self.cards_on_table.clear()

        self.hit_feito_mao_normal = False
        self.hit_feito_split1 = False
        self.hit_feito_split2 = False

        self.split_ativo = False
        self.mao_split_1 = []
        self.mao_split_2 = []
        self.mao_atual = None

        self.valor_apostado = aposta
        self.dinheiro_jogador -= aposta
        self.label_dinheiro.text = f"Cash: {self.dinheiro_jogador}€"
        self.label_resultado.text = ""
        self.label_pontos_dealer.text = ""
        self.label_pontos_jogador.text = ""
        self.mostrar_segunda_carta = False
        self.insurance_ativado = False
        self.valor_insurance = 0

        mostrar_botao(self.botao_hit, False)
        mostrar_botao(self.botao_stand, False)
        mostrar_botao(self.botao_double, False)
        mostrar_botao(self.botao_novo_jogo, False)

        self.baralho_atual = nova_partida()
        self.mao_jogador.clear()
        self.mao_dealer.clear()

        for carta_widget in self.cards_on_table:
            self.root.remove_widget(carta_widget)
        self.cards_on_table.clear()

        self.dealer_segunda_carta_img = None

        Clock.schedule_once(self.cards.dar_primeira_jogador, 0.5)

    def fechar_app(self, instance):
        App.get_running_app().stop()
        Window.close()
        sys.exit()

    def verificar_dinheiro(self):
        if self.dinheiro_jogador <= 0:
            self.label_resultado.text = "You're out of money!"
            mostrar_botao(self.botao_sair, mostrar=True)
            return 1
        return 0

if __name__ == "__main__":
    BlackjackApp().run()
