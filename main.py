from kivy.lang import Builder
from kivy.properties import StringProperty

from kivymd.uix.screenmanager import MDScreenManager
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
import webview


from kivy.clock import Clock

from plyer import filechooser
import struct
import threading
import pickle
import subprocess
import os
from ultralytics import YOLO
import csv

imagem_selecionada = None
caminho_projeto = os.getcwd()
print(caminho_projeto)


caminho_coordenadas = caminho_projeto + '\\scripts\\Conexao\\coordenadas.txt'
print(caminho_coordenadas)

class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()


class BaseScreen(MDScreen):
    ...

class MapaScreen(MDScreen):
    pass
    
def carregar_dados(filename):
    dados = []
    with open(filename, 'r') as f:
        for linha in f:
            linha = linha.strip()  # Remove leading and trailing whitespace
            valores = linha.split(',')  # Split the line into a list of values
            if len(valores) != 3:  # Check if the line has the expected number of values
                print(f"Skipping line with invalid format: {linha}")
                continue
            try:
                dados.append({
                    'nome': valores[0].strip(),  # Remove leading and trailing whitespace from the name
                    'latitude': float(valores[1].strip()),  # Attempt conversion to float
                    'longitude': float(valores[2].strip())  # Attempt conversion to float
                })
            except ValueError:
                print(f"Skipping line with invalid latitude: {linha}")  # Handle invalid line
    return dados

class DoencaScreen(MDScreen):
    pass
    def on_pre_enter(self):
        Clock.schedule_once(self._on_pre_enter)

    def _on_pre_enter(self, dt):
        rv = self.ids.rv  # Access the rv widget using ids
        self.dados = carregar_dados(caminho_coordenadas)
        self.dados = self.dados[-10:]  # Pegar as 10 últimas detecções

        rv.data = [
            {
                'nome': item['nome'],
                'latitude': float(item['latitude']),
                'longitude': float(item['longitude']),
                'imagem': self._get_image_source(item['nome'])
            }
            for item in self.dados
        ]

        print("Últimas 10 detecções de doenças:")
        for item in self.dados:
            print(f"{item['nome']}: Lat: {item['latitude']:.6f}, Long: {item['longitude']:.6f}")

    def _get_image_source(self, nome):
        # Retorna o caminho da imagem de acordo com o nome da doença
        if nome == 'Bicho Mineiro':
            return 'doenças\\bicho mineiro.jpg'
        elif nome == 'Cercospora coffeicola':
            return 'doenças\\cercospora.png'
        elif nome == 'Ferrugem Cafeeira':
            return 'doenças\\ferrugem.jpg'
        elif nome == 'Acaro Vermelho':
            return 'doenças\\acaro vermelho.jpg'
        else:
            return 'default.jpg'
# ...

class DroneScreen(MDScreen):
    pass

class CameraScreen(MDScreen):
    def on_pre_enter(self):
        self.mostra_imagem()

    def uploadArquivo(self):
        # Abre o filechooser e chama a função 'selected' quando uma imagem é escolhida
        filechooser.open_file(on_selection=self.selected)

    def selected(self, selection):
        global imagem_selecionada
        if selection:
            imagem_selecionada = selection[0]
            print(f"Imagem selecionada: {imagem_selecionada}")
            self.renderiza_imagem(imagem_selecionada)
        else:
            print("Nenhuma imagem foi selecionada.")

    def mostra_imagem(self, *args):
        img_path = 'img\\foto\\imagem.png'
        self.ids.bct.source = img_path
        self.ids.bct.reload()  # Garante que a imagem recarregue na tela

    def renderiza_imagem(self, *args):
        # Executa o script Python 'renderizador.py' com a imagem selecionada
        if imagem_selecionada:
            print("Executando script com a imagem...")
            script_path = os.path.join(os.path.dirname(__file__), "scripts", "renderizador.py")
            imagem_nome = os.path.basename(imagem_selecionada)
            subprocess.run(["python", script_path, imagem_nome, caminho_projeto])
            # Adiciona um atraso para garantir que o processamento termine antes de exibir a imagem
            Clock.schedule_once(self.atualiza_imagem, 1)  # Ajuste o tempo conforme necessário
        else:
            print("Nenhuma imagem selecionada para processar.")

    def atualiza_imagem(self, *args):
        # Atualiza a imagem no widget após o tempo de processamento
        self.mostra_imagem()

#Classes das Telas de Tutoriais
class TutorialDrone(MDScreen):
    pass

class TutorialDoencas(MDScreen):
    pass

class TutorialMapa(MDScreen):
    pass

KV = '''
<BaseMDNavigationItem>
    MDNavigationItemIcon:
        icon: root.icon
    MDNavigationItemLabel:
        text: root.text

<DoencaItem@MDBoxLayout>:
    radius: 16
    nome: ''
    latitude: 0.0
    longitude: 0.0
    imagem: ''
    orientation: "horizontal"
    padding: "5dp"
    size_hint_y: 1
    height: "150dp"
    md_bg_color: [0.7, 0.7, 0.7, 1]

    AsyncImage:
        source: root.imagem
        size_hint: None, None  # Desativa o redimensionamento relativo
        size: "120dp", "100dp"  # Define o tamanho fixo em dp
        size_hint_x: 0.1  # Define se deseja uma largura fixa
        width: "75dp"     # Largura fixa (opcional se `size_hint` já for None)
        height: "55dp" 

    MDLabel:
        text: root.nome
        halign: "left"
        font_style: "Title"

    MDBoxLayout:
        orientation: "vertical"
        size_hint_x: 0.2
        MDLabel:
            text: f"Latitude: {root.latitude}"
            halign: "right"
            font_style: "Label"
        MDLabel:
            text: f"Longitude: {root.longitude}"
            halign: "right"
            font_style: "Label"

        
<DoencaScreen>:
    md_bg_color: [0.7, 0.9, 0.2, 1]
    
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: self.theme_cls.backgroundColor
        size_hint: 1, 0.15
        pos_hint: {"top": 1}

        MDIconButton:
            icon: "help-circle"
            style: "standard" 
            pos_hint: {"center_x": 0.05, "center_y": .95}
            on_release:
                root.manager.transition.direction = 'up'
                root.manager.current = 'TutorialDoencas'

        MDLabel:
            text: "Doenças Detectadas..."
            halign: "center"
            text_color: [0, 0, 0, 1]

    RecycleView:
        id: rv
        viewclass: 'DoencaItem'
        bar_width: 0
        size_hint_y: 0.86


        RecycleBoxLayout:
            orientation: 'vertical'
            spacing: "16dp"
            padding: "16dp"
            default_size: None, dp(72)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height

<DroneScreen>:
    md_bg_color: self.theme_cls.backgroundColor
    MDButton:
        style: "elevated"
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: app.Conexao()

        MDButtonIcon:
            icon: "bluetooth"

        MDButtonText:
            text: "Conectar ao Drone"

    MDIconButton:
        icon: "help-circle"
        style: "standard" 
        pos_hint: {"center_x": 0.05, "center_y": .95}
        on_release:
            root.manager.transition.direction = 'up'
            root.manager.current = 'TutorialDrone'
        


            
<MapaScreen>:
    md_bg_color : self.theme_cls.backgroundColor
    
    MDButton:
        style:"elevated"
        shadow_color: "red"
        pos_hint: {"center_x": .5, "center_y": .6}
        on_release: app.gera_mapa()

        MDButtonIcon:        
            icon:"map-plus"
            theme_icon_color: "Custom"
            icon_color: "blue"

        MDButtonText:
            text:"Gerar Mapa"
            color: "black"

    MDButton:
        style:"elevated"
        shadow_color: "red"
        pos_hint: {"center_x": .5, "center_y": .4}
        on_release: app.abre_mapa()

        MDButtonIcon:        
            icon:"map-search"
            theme_icon_color: "Custom"
            icon_color: "red"

        MDButtonText:
            text:"Abrir Mapa"
            color: "black"

    MDIconButton:
        icon: "help-circle"
        style: "standard" 
        pos_hint: {"center_x": 0.05, "center_y": .95}
        on_release:
            root.manager.transition.direction = 'up'
            root.manager.current = 'TutorialMapa'


<CameraScreen>:
    md_bg_color: [0.1, 0.1, 0.8, 0.5]
    MDBoxLayout:
        size: root.size

        Image:
            id: bct
            source: ''
            size: root.size



MDBoxLayout:
    orientation: 'vertical'
    MDScreenManager:
        id: screen_manager
        
        DoencaScreen:
            name: "Doencas"
        DroneScreen:
            name:"Drone"
        MapaScreen:
            name: "Mapa"
        CameraScreen:
            name: "Camera"
        TutorialDrone:
            name: "TutorialDrone"
        TutorialDoencas:
            name: "TutorialDoencas"
        TutorialMapa:
            name: "TutorialMapa"

    MDNavigationBar:
    	on_switch_tabs: app.on_switch_tabs(*args)

        text_color_normal: 0, 0, 0, 
        text_color_active: 0.59, 0.38, 0.55
        selected_color_background: 0.39, 0.6, 0.43, .4


           
        BaseMDNavigationItem
            icon:"drone"
            text:"Drone"
        BaseMDNavigationItem           
            icon: "home"
            text: "Doencas"
            active: True
        BaseMDNavigationItem
            icon: "google-maps"
            text: "Mapa"
        BaseMDNavigationItem
            icon: "file-image"
            text: "Camera"

<TutorialDrone>:
    name: 'TuturialDrone'
    id: TuturialDrone
    md_bg_color : self.theme_cls.backgroundColor
    
#    MDDropDownItem:
#        id: dropdown_item
#        pos_hint: {"center_x": .5, "center_y": .8}
#        on_release: app.open_menu(self)

#        MDDropDownItemText:
#            id: drop_text
#            text: "Dispositivo: "
    
    
    
    MDLabel:
        text: "Pra conectar o Drone à IA, precisa primeiramente ativar a depuração USB do celular, em seguida conectar o celular via USB no computador, feito isso ative a transferência de arquivo no celular, também deixe o celular com o aplicativo rxdrone aberto conectado a camera do drone e continue nele, por fim aperte o botão para aconexão ser ralizada."
        halign: "center"
        font_style: "Label"

    MDButton:
        style: "elevated"
        pos_hint: {"center_x": .5, "center_y": .2}
        on_release: 
            root.manager.transition.direction = 'down'
            root.manager.current = 'Drone'

        MDButtonIcon:
            icon: "reply"

        MDButtonText:
            text: "Voltar"

<TutorialDoencas>:
    name: 'TutorialDoencas'
    md_bg_color : self.theme_cls.backgroundColor
    MDLabel:
        text: "Aqui é exibido as 10 últimas doenças detectadas, você pode observar que contém o nome, a latitude e a longitude"
        halign: "center"
        font_style: "Label"

    MDButton:
        style: "elevated"
        pos_hint: {"center_x": .5, "center_y": .2}
        on_release: 
            root.manager.transition.direction = 'down'
            root.manager.current = 'Doencas'

        MDButtonIcon:
            icon: "reply"

        MDButtonText:
            text: "Voltar"

<TutorialMapa>:
    name: 'TutorialMapa'
    md_bg_color : self.theme_cls.backgroundColor
    MDLabel:
        text: "Para vizualizar a localização das doenças tem duas maneiras, se você estiver conectado a Internet você pode apenas clicar no botão 'Abir Mapa', caso esteja sem Internet, você deve apertar o botão 'Gerar mapa Offline' e depois abrir o mapa"
        halign: "center"
        font_style: "Label"
        pos_hint: {"center_x": .5, "center_y": .8}
        height: self.texture_size[1] + dp(20)

    MDLabel:
        text: "Está offline?"
        color: [0.1, 0.1, 0.8, 0.5]
        halign: "center"
        font_style: "Label"
        pos_hint: {"center_x": .5, "center_y": .5}
        height: self.texture_size[1] + dp(20)

        
    MDButton:
        style: "elevated"
        pos_hint: {"center_x": .5, "center_y": .4}
        on_release: 
            app.gera_mapa_offline()

        MDButtonIcon:        
            icon:"map-plus"
            theme_icon_color: "Custom"
            icon_color: "blue"

        MDButtonText:
            text:"Gera Mapa"
            color: "black"

    MDButton:
        style: "elevated"
        pos_hint: {"center_x": .5, "center_y": .3}
        on_release: 
            app.abre_mapa_offline()

        MDButtonIcon:        
            icon:"map-search"
            theme_icon_color: "Custom"
            icon_color: "red"

        MDButtonText:
            text:"Abrir Mapa"
            color: "black"


    MDButton:
        style: "elevated"
        pos_hint: {"center_x": .5, "center_y": .1}
        on_release: 
            root.manager.transition.direction = 'down'
            root.manager.current = 'Mapa'

        MDButtonIcon:
            icon: "reply"

        MDButtonText:
            text: "Voltar"
'''


class Example(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.browser = None 
        self.sm = MDScreenManager()

    def on_switch_tabs(
        self,
        bar: MDNavigationBar,
        item: MDNavigationItem,
        item_icon: str,
        item_text: str,
    ):
        self.root.ids.screen_manager.transition.direction = "left"
        self.root.ids.screen_manager.current = item_text
        if item_icon == "home":
            self.Menu()
        if item_icon == "file-image":
            screen = self.root.ids.screen_manager.get_screen("Camera")
            screen.uploadArquivo()


    def open_menu(self, item):
        dispositivos = [
            "Motorola",
            "Samsumg",
            "Xiaomi",
            "Iphone"
        ]

        menu_items = [
            {
                "text": dispositivo,
                "on_release": lambda x=dispositivo: self.menu_callback(x),
            } for dispositivo in dispositivos
        ]
        MDDropdownMenu(caller=item, items=menu_items).open()

    def menu_callback(self, text_item):
        self.root.ids.TutorialDrone.ids.drop_text.text = f"Dispositivo: {text_item}"

    def build(self):
        return Builder.load_string(KV)

    def Conexao(self):
            script_path = "scripts\\Conexao\\extracao.py" 
            subprocess.run(["python", script_path])

    def abre_mapa(self, *args):
        url = "scripts\\mapas\\mapa.html"
    
        webview.create_window('Mapa', url)
        webview.start() 

    def abre_mapa_offline(self, *args):
        #url = "C:/Users/leo00/OneDrive/Desktop/DPADesktop/mapa_offiline/mapa_offline.html"
        url = "C:\\Users\\leo00\\OneDrive\Desktop\\DPADesktop\\mapa_offiline\\mapa_offline.html"
    
        webview.create_window('Mapa', url)
        webview.start() 
        

    def gera_mapa(self):
        script_path = "C:\\Users\\leo00\\OneDrive\\Desktop\\DPADesktop\\scripts\\Conexao\\mapa.py" 
        subprocess.run(["python", script_path])

    def gera_mapa_offline(self):
        script_path = "C:/Users/leo00/OneDrive/Desktop/DPADesktop/mapa_offiline/mapa_offline.py" 
        subprocess.run(["python", script_path])

    def Menu(self, *args):
        #self.root.ids.screen_manager.current = Doencas
        pass #Retornar para a tela de Menu de doenças


Example().run()
