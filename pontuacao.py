from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from logic import calcular_pontos


class Pontuacao:
    def __init__(self, app):
        self.app = app

    def mostrar_pontuacoes(self, instance):
        pontuacoes = []
        for nome in self.app.store:
            pontos = self.app.store.get(nome)['pontos']
            pontuacoes.append((nome, pontos))

        pontuacoes.sort(key=lambda x: x[1], reverse=True)

        layout_popup = FloatLayout()

        fundo = Image(
            source='images/bets.png',
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
            allow_stretch=True,
            keep_ratio=False
        )
        layout_popup.add_widget(fundo)

        scroll = ScrollView(size_hint=(.9, .75), pos_hint={"center_x": 0.5, "top": 0.9})

        box = BoxLayout(orientation='vertical', size_hint_y=None, padding=10, spacing=10)
        box.bind(minimum_height=box.setter('height'))

        linha_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        label_nome_header = Label(text="PLAYER:", font_size='25sp', color=(1, 1, 0, 1), halign="left")
        label_pontos_header = Label(text="HIGHEST BET:", font_size='25sp', color=(1, 1, 0, 1), halign="right")
        linha_header.add_widget(label_nome_header)
        linha_header.add_widget(label_pontos_header)
        box.add_widget(linha_header)

        linha_widget = Widget(size_hint_y=None, height=2)
        with linha_widget.canvas:
            Color(1, 1, 1, 1)
            linha_widget.line = Rectangle(size=(500, 2), pos=(0, 0))

        def atualizar_linha(instance, value):
            linha_widget.line.size = (linha_widget.width, 2)
            linha_widget.line.pos = linha_widget.pos

        linha_widget.bind(size=atualizar_linha, pos=atualizar_linha)
        box.add_widget(linha_widget)

        if pontuacoes:
            for nome, pontos in pontuacoes:
                linha = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
                label_nome = Label(text=nome, font_size='15sp', color=(1, 1, 1, 1), halign="left")
                label_pontos = Label(text=str(pontos), font_size='15sp', color=(1, 1, 1, 1), halign="right")
                linha.add_widget(label_nome)
                linha.add_widget(label_pontos)
                box.add_widget(linha)
        else:
            label_vazio = Label(text="No bets found", size_hint_y=None, height=30, font_size='15sp',
                                color=(1, 0.5, 0.5, 1))
            box.add_widget(label_vazio)

        scroll.add_widget(box)

        botao_fechar = Button(text="Close", size_hint=(.4, .12), pos_hint={"x": 0.05, "y": 0.03},
                              border=(0, 0, 0, 0), background_color=(0.8, 0.1, 0.1, 1),
                              font_size='18sp', bold=True)
        botao_limpar = Button(text="Clear Bets", size_hint=(.4, .12), pos_hint={"x": 0.55, "y": 0.03},
                              border=(0, 0, 0, 0), background_color=(0.2, 0.6, 0.2, 1),
                              font_size='18sp', bold=True)

        layout_popup.add_widget(scroll)
        layout_popup.add_widget(botao_fechar)
        layout_popup.add_widget(botao_limpar)

        popup = Popup(title="", content=layout_popup, size_hint=(0.7, 0.7), auto_dismiss=False)

        botao_fechar.bind(on_press=popup.dismiss)

        def confirmar_limpeza(instance):
            layout_confirma = FloatLayout()

            with layout_confirma.canvas.before:
                Color(0.1, 0.1, 0.1, 1)
                rect = Rectangle(size=layout_confirma.size, pos=layout_confirma.pos)
            layout_confirma.bind(size=lambda inst, val: setattr(rect, 'size', inst.size),
                                 pos=lambda inst, val: setattr(rect, 'pos', inst.pos))

            label_confirma = Label(text="Are you sure?", font_size='20sp', color=(1, 1, 1, 1),
                                   halign="center", valign="middle",
                                   size_hint=(.9, .4), pos_hint={"center_x": 0.5, "top": 0.95},
                                   text_size=(400, None))

            botao_sim = Button(text="Yes", size_hint=(.4, .2), pos_hint={"x": 0.05, "y": 0.05},
                               border=(0, 0, 0, 0), background_color=(0.7, 0.2, 0.2, 1),
                               font_size='18sp', bold=True)
            botao_nao = Button(text="No", size_hint=(.4, .2), pos_hint={"x": 0.55, "y": 0.05},
                               border=(0, 0, 0, 0), background_color=(0.2, 0.6, 0.2, 1),
                               font_size='18sp', bold=True)

            layout_confirma.add_widget(label_confirma)
            layout_confirma.add_widget(botao_sim)
            layout_confirma.add_widget(botao_nao)

            popup_confirma = Popup(title="", content=layout_confirma, size_hint=(0.6, 0.4), auto_dismiss=False)

            def apagar_ficheiro(inst):
                self.app.store.clear()
                popup_confirma.dismiss()
                popup.dismiss()
                self.mostrar_pontuacoes(None)

            botao_sim.bind(on_press=apagar_ficheiro)
            botao_nao.bind(on_press=popup_confirma.dismiss)
            popup_confirma.open()

        botao_limpar.bind(on_press=confirmar_limpeza)
        popup.open()

    def atualizar_pontos(self, *args):
        if not self.app.split_ativo:
            self.app.label_pontos_jogador.text = f"({calcular_pontos(self.app.mao_jogador)})"
        if self.app.mostrar_segunda_carta:
            self.app.label_pontos_dealer.text = f"({calcular_pontos(self.app.mao_dealer)})"
        elif self.app.mao_dealer:
            self.app.label_pontos_dealer.text = f"({calcular_pontos([self.app.mao_dealer[0]])})"
        else:
            self.app.label_pontos_dealer.text = ""
